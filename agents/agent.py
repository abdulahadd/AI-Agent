#!/usr/bin/env python3
"""
Groq-based sales agent with *planned* pre-recorded audio.

IMPORTANT
---------
- This file is a starting point for the design we discussed:
  - Groq STT (Speech-to-Text)
  - Keyword + (later) LLM-based classification
  - Pre-recorded pitch + two fixed response clips instead of TTS
- Right now this implementation:
  - Connects to LiveKit and waits for a participant.
  - Shows clearly (in logs and comments) where to:
    - Play the pitch audio.
    - Run STT with Groq.
    - Call the LLM classifier as a fallback.
    - Play the POSITIVE / NEGATIVE response clips.
  - Uses placeholder logic instead of real audio playback / STT / LLM,
    so you can understand the flow safely before wiring everything in.

"""
import asyncio
import io
import logging
import os
import re
import wave
from typing import Literal

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobRequest,
    WorkerOptions,
    WorkerType,
    cli,
    llm,
)
from livekit.plugins import groq, silero

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqPreRecordedAgent:
    def __init__(self) -> None:
        self.agent_name = os.getenv("AGENT_NAME", "SalesAgent")
        self.audio_dir = os.path.join(os.path.dirname(__file__), "audio")
        self.pitch_path = os.path.join(self.audio_dir, "pitch.wav")
        self.positive_path = os.path.join(self.audio_dir, "positive_reponse.wav")
        self.negative_path = os.path.join(self.audio_dir, "negative_reponse.wav")

        self.stt = groq.STT(model="whisper-large-v3-turbo", language="en")
        self.classifier_llm = groq.LLM(model="openai/gpt-oss-20b")

    async def classify_with_llm(self, transcript: str) -> Literal["POSITIVE", "NEGATIVE"]:
        system_msg = (
            "Classify sales call intent as 'POSITIVE' or 'NEGATIVE'. "
            "POSITIVE: Interest, consent, or willingness to listen. "
            "NEGATIVE: Refusal, busy, driving, or asking to stop. "
            "Output ONLY 'POSITIVE' or 'NEGATIVE'."
        )
        messages = [
            llm.ChatMessage(role="system", content=[system_msg]),
            llm.ChatMessage(
                role="user",
                content=[f"Is this response positive or negative?: '{transcript}'"],
            ),
        ]
        chat_ctx = llm.ChatContext(messages)

        try:
            stream = self.classifier_llm.chat(chat_ctx=chat_ctx)
            response = await stream.collect()

            if hasattr(response, "content"):
                label = response.content.strip().upper()
            elif hasattr(response, "choices"):
                label = response.choices[0].message.content.strip().upper()
            else:
                label = str(response).strip().upper()

            return "NEGATIVE" if "NEGATIVE" in label else "POSITIVE"
        except Exception as e:
            logger.error(f"[{self.agent_name}] LLM process failed: {e}")
            return "NEGATIVE"

    def classify_transcript_fast(
        self, transcript: str
    ) -> Literal["POSITIVE", "NEGATIVE", "AMBIGUOUS"]:
        """
        Evaluates the transcript using regex before invoking the LLM.
        Returns POSITIVE or NEGATIVE for clear matches, or AMBIGUOUS to trigger LLM.
        """
        normalized = (transcript or "").strip().lower()

        if not normalized:
            return "NEGATIVE"

        negative_patterns = [
            r"\bno\b",
            r"\bnot interested\b",
            r"\bdon'?t want\b",
            r"\bno thanks\b",
            r"\bstop calling\b",
            r"\bremove me\b",
            r"\bdon'?t call\b",
            r"\bhang up\b",
            r"\bdon'?t need\b",
        ]

        for pattern in negative_patterns:
            if re.search(pattern, normalized):
                logger.info(f"[{self.agent_name}] Matched negative pattern '{pattern}'")
                return "NEGATIVE"

        # 2. Clear Positive Patterns (Bypasses LLM latency)
        positive_patterns = [
            r"\byes\b",
            r"\byep\b",
            r"\byeah\b",
            r"\bsure\b",
            r"\bok\b",
            r"\bokay\b",
            r"\bgo ahead\b",
            r"\btell me more\b",
            r"\bi'?m listening\b",
            r"\bsounds good\b",
            r"\bwhat is it\b",
            r"\bwhy not\b",
            r"\balright\b",
        ]

        for pattern in positive_patterns:
            if re.search(pattern, normalized):
                logger.info(f"[{self.agent_name}] Fast-path match: POSITIVE ('{pattern}')")
                return "POSITIVE"

        # 3. If neither rules match, send to LLM
        logger.info(f"[{self.agent_name}] Ambiguous response ('{normalized}'). Sending to LLM...")
        return "AMBIGUOUS"

    async def _get_remote_audio_track(self, room: rtc.Room, timeout: float = 10.0) -> rtc.Track:
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            for participant in room.remote_participants.values():
                for track_pub in participant.track_publications.values():
                    if track_pub.kind == rtc.TrackKind.KIND_AUDIO and track_pub.track:
                        return track_pub.track
            await asyncio.sleep(0.2)
        return None

    async def entrypoint(self, ctx: JobContext) -> None:
        logger.info("[%s] Worker started. Playing pitch...", self.agent_name)

        # 1. Play pitch audio
        await self._play_wav_to_room(ctx.room, self.pitch_path, label="pitch")

        # 2. Wait for incoming audio track
        audio_track = await self._get_remote_audio_track(ctx.room, timeout=5.0)
        user_transcript = ""

        if audio_track:
            import numpy as np

            audio_stream = rtc.AudioStream(audio_track)
            frames = []
            user_started_talking = False

            VOLUME_THRESHOLD = 0.015
            SILENCE_TIMEOUT = 1.8
            last_speech_time = asyncio.get_event_loop().time()

            logger.info("[%s] Listening for user response...", self.agent_name)

            async for event in audio_stream:
                audio_data = np.frombuffer(event.frame.data, dtype=np.int16)
                volume = (
                    np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)) / 32768.0
                )

                if volume > VOLUME_THRESHOLD:
                    if not user_started_talking:
                        logger.info("Speech detected (Volume: %.4f)", volume)
                        user_started_talking = True

                    frames.append(event.frame)
                    last_speech_time = asyncio.get_event_loop().time()

                elif user_started_talking:
                    frames.append(event.frame)
                    if (
                        asyncio.get_event_loop().time() - last_speech_time
                        > SILENCE_TIMEOUT
                    ):
                        logger.info("Silence threshold met. Processing STT...")
                        break

            await audio_stream.aclose()

            if frames:
                # Merge frame buffers into a single AudioFrame for Groq STT
                combined_data = bytearray()
                for f in frames:
                    combined_data.extend(f.data)

                merged_frame = rtc.AudioFrame(
                    data=bytes(combined_data),
                    sample_rate=frames[0].sample_rate,
                    num_channels=frames[0].num_channels,
                    samples_per_channel=len(combined_data) // (2 * frames[0].num_channels),
                )

                stt_res = await self.stt.recognize(buffer=merged_frame)
                if stt_res.alternatives:
                    user_transcript = stt_res.alternatives[0].text
                    logger.info("[%s] Transcribed: %s", self.agent_name, user_transcript)
        else:
            logger.warning("[%s] No audio track available from participant.", self.agent_name)

        # 3. Decision pipeline
        decision = self.classify_transcript_fast(user_transcript)
        
        # If ambiguous, fall back to LLM reasoning
        if decision == "AMBIGUOUS":
            decision = await self.classify_with_llm(user_transcript)

        if not ctx.room.remote_participants:
            logger.info("Participant disconnected. Terminating job.")
            return

        # 4. Play response clip
        if decision == "POSITIVE":
            await self._play_wav_to_room(
                ctx.room,
                self.positive_path,
                label="positive_response",
            )
        else:
            await self._play_wav_to_room(
                ctx.room,
                self.negative_path,
                label="negative_response",
            )

        logger.info("[%s] Execution flow finished.", self.agent_name)

    async def _play_wav_to_room(
        self,
        room: rtc.Room,
        wav_path: str,
        label: str = "audio",
    ) -> None:
        if not os.path.exists(wav_path):
            logger.warning("[%s] File missing: %s", self.agent_name, wav_path)
            return

        with wave.open(wav_path, "rb") as wf:
            num_channels = wf.getnchannels()
            sample_rate = wf.getframerate()

            frame_duration_ms = 20
            samples_per_frame = int(sample_rate * (frame_duration_ms / 1000))

            source = rtc.AudioSource(sample_rate, num_channels)
            track = rtc.LocalAudioTrack.create_audio_track(label, source)
            options = rtc.TrackPublishOptions(
                source=rtc.TrackSource.SOURCE_MICROPHONE
            )
            publication = await room.local_participant.publish_track(
                track, options
            )

            start_time = asyncio.get_event_loop().time()
            frames_sent = 0

            while True:
                raw_data = wf.readframes(samples_per_frame)
                if not raw_data:
                    break

                expected_len = samples_per_frame * num_channels * 2
                if len(raw_data) < expected_len:
                    raw_data += b"\x00" * (expected_len - len(raw_data))

                frame = rtc.AudioFrame(
                    data=raw_data,
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    samples_per_channel=samples_per_frame,
                )

                await source.capture_frame(frame)
                frames_sent += 1

                next_frame_time = start_time + (
                    frames_sent * frame_duration_ms / 1000
                )
                sleep_time = next_frame_time - asyncio.get_event_loop().time()

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            await room.local_participant.unpublish_track(publication.sid)


async def main_entrypoint(ctx: JobContext):

    logger.info("Connecting agent to room: %s", ctx.room.name)
    

    logger.info("Connecting to room: %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

    logger.info("Waiting for participant...")
    
    try:
        participant = await asyncio.wait_for(
            ctx.wait_for_participant(), 
            timeout=15.0
        )
        logger.info("Participant connected. Starting agent entrypoint...")
    except asyncio.TimeoutError:
        logger.error("No participant connected within timeout. Terminating job.", ctx.room.name)
        return
        
    agent = GroqPreRecordedAgent()
    await agent.entrypoint(ctx)


async def request_handler(job_request: JobRequest):
    # Accept ALL incoming jobs (including SIP dispatch calls)
    logger.info("Accepting job request for room: %s", job_request.room.name)
    await job_request.accept()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=main_entrypoint,
            agent_name="sales-agent",
        )
    )