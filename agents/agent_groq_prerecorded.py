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
import logging
import os
import wave
from typing import Literal

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, JobRequest, WorkerType
from livekit import rtc  # low-level audio primitives (AudioSource, AudioFrame, etc.)
from livekit.plugins import groq  # STT / LLM provider (not fully used yet)
from livekit.agents import llm
from livekit.plugins import silero
# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
# Load environment variables
load_dotenv()
vad = silero.VAD.load()
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class GroqPreRecordedAgent:
    """
    High-level flow (target behavior):

    1. Wait for participant to join the LiveKit room.
    2. Play a pre-recorded pitch (always the same script).
    3. Listen to the user's reply (via Groq STT).
    4. Classify reply as POSITIVE or NEGATIVE.
       - First via a simple keyword check (cheap, local).
       - Optionally fall back to a tiny Groq LLM call for fuzzy cases.
    5. Play one of two pre-recorded responses:
       - POSITIVE  -> "I am connecting you forward"
       - NEGATIVE  -> "Okay. Thank you for your time"
    6. End the call / hand off.

    This class currently wires only the skeleton and logging so you can see
    what will happen where. The actual audio + STT + LLM calls are marked
    with clear TODO comments.
    """

    def __init__(self) -> None:
        # Basic agent identity (optional, for logging / future use).
        self.agent_name = os.getenv("AGENT_NAME", "SalesAgent")

        # Where your audio files live.
        self.audio_dir = os.path.join(os.path.dirname(__file__), "audio")
        # After conversion we'll have:
        #   - pitch.wav              (full pitch)
        #   - positive_reponse.wav   ("I am connecting you forward")
        #   - negative_reponse.wav   ("Okay. Thank you for your time")
        self.pitch_path = os.path.join(self.audio_dir, "pitch.wav")
        self.positive_path = os.path.join(self.audio_dir, "positive_reponse.wav")
        self.negative_path = os.path.join(self.audio_dir, "negative_reponse.wav")

        # NOTE: We are not constructing groq.STT() or groq.LLM() yet, because
        # the audio pipeline is not wired. When we hook in real STT/LLM, we'll
        # likely add something like:
        #
        self.stt = groq.STT(model="whisper-large-v3-turbo", language="en")
        self.classifier_llm = groq.LLM(model="llama-3.1-8b-instant")
        #   self.classifier_llm = groq.LLM(model="llama-3.1-8b-instant")
        #
        # and then use them in the TODO sections below.

    # ------------------------------------------------------------------
    # Classification logic (keyword-first, LLM-later)
    # ------------------------------------------------------------------

    async def classify_with_llm(self, transcript: str) -> Literal["POSITIVE", "NEGATIVE"]:
        # 1. Define messages list using the [content] list format your environment requires
        system_msg = (
            "Classify sales call intent as 'POSITIVE' or 'NEGATIVE'. "
            "POSITIVE: Interest, consent, or willingness to listen. "
            "NEGATIVE: Refusal, busy, driving, or asking to stop. "
            "Output ONLY 'POSITIVE' or 'NEGATIVE'."
        )
    
        messages = [
            llm.ChatMessage(
                role="system",
                content= [system_msg]
            ),
            llm.ChatMessage(
                role="user",
                content=[f"Is this response positive or negative?: '{transcript}'"]
            )
        ]

        # 2. Pass messages as a POSITIONAL argument, not a keyword argument
        chat_ctx = llm.ChatContext(messages) 
        
        logger.info(f"[SalesAgent] Sending to Groq: {transcript}")

        try:
            # 3. Call the LLM
            # Note: If your Groq plugin is older, you may need to use 'chat_ctx=chat_ctx' 
            # but the actual context creation is the part that was failing.
            stream = self.classifier_llm.chat(chat_ctx=chat_ctx)
            response = await stream.collect()
            
            # 4. Extract content safely
            if hasattr(response, "content"):
                label = response.content.strip().upper()
            elif hasattr(response, "choices"):
                label = response.choices[0].message.content.strip().upper()
            else:
                # Last resort: cast the response to string
                label = str(response).strip().upper()
                
            logger.info(f"[SalesAgent] LLM Result: {label}")
            return "NEGATIVE" if "NEGATIVE" in label else "POSITIVE"
            
        except Exception as e:
            logger.error(f"[SalesAgent] LLM process failed: {e}")
            return "NEGATIVE"

    def classify_transcript_keyword_first(
        self, transcript: str
    ) -> Literal["POSITIVE", "NEGATIVE"]:
        """
        Classify the user's reply with the rule you defined:

        - If transcript is empty (silence) -> NEGATIVE.
        - If transcript clearly contains a negative phrase -> NEGATIVE.
        - Otherwise -> POSITIVE (default).

        Later, we can add a *fallback* Groq LLM call *only* when this simple
        logic returns POSITIVE but we want extra safety for weird wording.
        """
        normalized = (transcript or "").strip().lower()

        if not normalized:
            logger.info("Transcript is empty -> treat as NEGATIVE (silence).")
            return "NEGATIVE"

        negative_phrases = [
            "no",	
            "not interested",
            "don't want it",
            "dont want it",
            "no thanks",
            "no thank you",
            "stop calling",
            "remove me",
            "don't call again",
            "dont call again",
            "hang up",
            "not interested in that	",
            "not interested in this",
            "dont need it",
            "don't need it",
        ]

        # Exact "no" is a strong signal, but we don't want to match words
        # like "knowledge" accidentally, so keep it separate.
        if normalized == "no" or normalized.startswith("no"):
            logger.info("Transcript contains explicit 'no' -> NEGATIVE.")
            return "NEGATIVE"

        # for phrase in negative_phrases:
        #     if phrase in normalized:
        #         logger.info("Transcript matched negative phrase '%s' -> NEGATIVE.", phrase)
        #         return "NEGATIVE"

        logger.info("Transcript did not match any negative phrase -> POSITIVE by default.")
        return "POSITIVE"

    # Entry point – this is what LiveKit calls for each job
    # ------------------------------------------------------------------

    async def entrypoint(self, ctx: JobContext) -> None:
     
        logger.info("[%s] Worker started, waiting for participant...", self.agent_name)

        # 1. Play the pitch
        await self._play_wav_to_room(ctx.room, self.pitch_path, label="pitch")

        # 2. Initialize VAD (Silero is excellent for this)
        local_vad = silero.VAD.load()

        logger.info("[%s] Listening for user response...", self.agent_name)
        user_transcript = ""
     
        #need to integrate it with VC dial
       
        try:
            # 1. Find the user's audio track
            audio_track = None
            for participant in ctx.room.remote_participants.values():
                for track_pub in participant.track_publications.values():
                    if track_pub.kind == rtc.TrackKind.KIND_AUDIO:
                        audio_track = track_pub.track
                        break
                if audio_track: break

            if audio_track:
                import numpy as np
                audio_stream = rtc.AudioStream(audio_track)
                frames = []
                user_started_talking = False
                
                # Sensitivity settings
                VOLUME_THRESHOLD = 0.01  # Lowered slightly for better detection
                SILENCE_TIMEOUT = 2.0    # Giving user 2 seconds to breathe
                
                logger.info("[%s] Energy-Based Listener started. Speak now!", self.agent_name)
                last_speech_time = asyncio.get_event_loop().time()

                async for event in audio_stream:
                    # Calculate volume
                    audio_data = np.frombuffer(event.frame.data, dtype=np.int16)
                    volume = np.sqrt(np.mean(audio_data.astype(np.float32)**2)) / 32768.0
                    
                    if volume > VOLUME_THRESHOLD:
                        if not user_started_talking:
                            logger.info("!!! SOUND DETECTED (Vol: %.4f) !!!", volume)
                            user_started_talking = True
                        
                        frames.append(event.frame)
                        last_speech_time = asyncio.get_event_loop().time()
                    
                    elif user_started_talking:
                        frames.append(event.frame)
                        if asyncio.get_event_loop().time() - last_speech_time > SILENCE_TIMEOUT:
                            logger.info("Silence detected. Processing STT...")
                            break
                
                await audio_stream.aclose()

                if frames:
                    logger.info("[%s] Sending %d frames to Groq STT...", self.agent_name, len(frames))
                    
                    # Create a single buffer from the frames
                    # Note: Groq plugin usually takes an AudioFrame or a stream
                    # We'll recognize the list of frames
                    stt_res = await self.stt.recognize(buffer=frames)
                    
                    if stt_res.alternatives:
                        user_transcript = stt_res.alternatives[0].text
                        logger.info("[%s] Transcribed: %s", self.agent_name, user_transcript)
            else:
                logger.warning("[%s] No audio track found to listen to!", self.agent_name)

        except Exception as e:
            logger.error("[%s] STT/VAD Error: %s", self.agent_name, e)


        logger.info("[%s] Final Transcript: %r", self.agent_name, user_transcript)

        # 4. Classification and Response (Rest of your code...)
        decision = self.classify_transcript_keyword_first(user_transcript)
        # ... rest of your flow
        if decision == "POSITIVE" and user_transcript.strip():
            logger.info("[%s] Keywords were neutral; asking LLM for fuzzy check...", self.agent_name)
            decision = await self.classify_with_llm(user_transcript)
     
        # Check if the user hung up
        if not ctx.room.remote_participants:
            logger.info("User hung up before we could respond. Closing job.")
            return

        # 5) Play the corresponding pre-recorded response
        if decision == "POSITIVE":
            await self._play_wav_to_room(
                ctx.room,
                self.positive_path,
                label="positive_response (\"I am connecting you forward\")",
            )
        else:
            await self._play_wav_to_room(
                ctx.room,
                self.negative_path,
                label="negative_response (\"Okay. Thank you for your time\")",
            )

        # 6) End – in a future iteration we might signal a transfer here
        logger.info("[%s] Call flow complete; worker will now finish job.", self.agent_name)

    
    async def _play_wav_to_room(
        self,
        room: rtc.Room,
        wav_path: str,
        label: str = "audio",
    ) -> None:
        if not os.path.exists(wav_path):
            logger.warning("[%s] WAV file not found at %s", self.agent_name, wav_path)
            return

        with wave.open(wav_path, "rb") as wf:
            num_channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            
            # Use 20ms frames
            frame_duration_ms = 20
            samples_per_frame = int(sample_rate * (frame_duration_ms / 1000))
            
            source = rtc.AudioSource(sample_rate, num_channels)
            track = rtc.LocalAudioTrack.create_audio_track(label, source)
            options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
            publication = await room.local_participant.publish_track(track, options)
            
            # High-precision timing
            start_time = asyncio.get_event_loop().time()
            frames_sent = 0

            while True:
                raw_data = wf.readframes(samples_per_frame)
                if not raw_data:
                    break
                
                # Ensure the buffer is the correct size (padding if necessary)
                expected_len = samples_per_frame * num_channels * 2 # 2 bytes per sample
                # Padding the last frame if it's too short
                if len(raw_data) < expected_len:
                    raw_data += b'\x00' * (expected_len - len(raw_data))

                frame = rtc.AudioFrame(
                    data=raw_data,
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    samples_per_channel=samples_per_frame,
                )

                await source.capture_frame(frame)
                frames_sent += 1
                #await asyncio.sleep(frame_duration_ms / 1000)
                # Calculate exactly when the NEXT frame should be sent
                next_frame_time = start_time + (frames_sent * frame_duration_ms / 1000)
                now = asyncio.get_event_loop().time()
                sleep_time = next_frame_time - now
            
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            # Unpublish track to clean up
            await room.local_participant.unpublish_track(publication.sid)
            logger.info("[%s] Finished playing %s", self.agent_name, label)

"""
Below we wire this agent into the LiveKit Agents CLI using WorkerOptions.

This lets you run:

    python agent_groq_prerecorded.py 

which starts a worker, just like agents/agent.py.
"""


async def main_entrypoint(ctx: JobContext):
    """
    LiveKit will call this for each job when running in dev/worker mode.
    This is the entrypoint that gets called when a room is assigned to this worker.
    """
    logger.info(f"--- Job Received: {ctx.job.id} ---")
    
    # 1. Initialize the agent class FIRST so we can use its properties
    agent = GroqPreRecordedAgent()

    # 2. Connect the agent to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    
    # 3. Wait until a participant is present
    await ctx.wait_for_participant()
    
    # 4. FIX: Use 'agent.agent_name' instead of 'self.agent_name'
    logger.info("[%s] Participant joined; starting scripted flow.", agent.agent_name)

    # 5. Run the flow
    await agent.entrypoint(ctx)

async def request_handler(job_request: JobRequest):
    # This log will tell us if the worker even SEES the request
    logger.info(f"--- DEBUG: Received request for room: {job_request.room.name} ---")
    
    # Accept the job immediately
    await job_request.accept(name="sales-agent")

if __name__ == "__main__":
   # 1. Force check of environment variables here
    url = os.getenv("LIVEKIT_URL")
    key = os.getenv("LIVEKIT_API_KEY")
    
    if not url or not key:
        logger.error("Worker cannot start: LIVEKIT_URL or API_KEY is missing from ENV")
    else:
        logger.info(f"Starting worker on {url} with key {key}")

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=main_entrypoint,
            request_fnc=request_handler,
            worker_type=WorkerType.ROOM,
            # THESE TWO ARE THE FIX:
            host="0.0.0.0", 
            port=52338
        )
    )

