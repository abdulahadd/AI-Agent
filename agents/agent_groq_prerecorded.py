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

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
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
        #   self.stt = groq.STT(model="whisper-large-v3-turbo", language="en")
        #   self.classifier_llm = groq.LLM(model="llama-3.1-8b-instant")
        #
        # and then use them in the TODO sections below.

    # ------------------------------------------------------------------
    # Classification logic (keyword-first, LLM-later)
    # ------------------------------------------------------------------

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
        if normalized == "no" or normalized.startswith("no,"):
            logger.info("Transcript contains explicit 'no' -> NEGATIVE.")
            return "NEGATIVE"

        for phrase in negative_phrases:
            if phrase in normalized:
                logger.info("Transcript matched negative phrase '%s' -> NEGATIVE.", phrase)
                return "NEGATIVE"

        logger.info("Transcript did not match any negative phrase -> POSITIVE by default.")
        return "POSITIVE"

    # Entry point – this is what LiveKit calls for each job
    # ------------------------------------------------------------------

    async def entrypoint(self, ctx: JobContext) -> None:
        """
        Main entrypoint for this worker.

        At runtime, LiveKit will:
        - Assign a room/job to this worker.
        - Call this function with a JobContext.
        """
        logger.info("[%s] Worker started, waiting for participant...", self.agent_name)

        
        # 2) Play the pre-recorded pitch to the room
        #
        # This now REALLY streams audio from self.pitch_path into the LiveKit room.
        await self._play_wav_to_room(ctx.room, self.pitch_path, label="pitch")

        # 3) Listen for user's reply with Groq STT (TODO)
        #
        # Target behavior:
        #   - Subscribe to participant's audio track.
        #   - Capture a short window (~2–5 seconds) after the pitch.
        #   - Send that audio to groq.STT() and get a transcript string.
        #
        # For now, we simulate a transcript so we can demonstrate
        # how classification and decision-making will look.
        simulated_transcript = "oh okay"  # TODO: replace with real STT result
        logger.info(
            "[%s] TODO: Replace simulated transcript with Groq STT result. Current simulated transcript: %r",
            self.agent_name,
            simulated_transcript,
        )

        # 4) Classify transcript (keyword-first)
        decision = self.classify_transcript_keyword_first(simulated_transcript)
        logger.info("[%s] Classification decision: %s", self.agent_name, decision)

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

    # ------------------------------------------------------------------
    # Helper: play a WAV file into the current room
    # ------------------------------------------------------------------

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
            samples_per_channel = int(sample_rate * (frame_duration_ms / 1000))
            
            source = rtc.AudioSource(sample_rate, num_channels)
            track = rtc.LocalAudioTrack.create_audio_track(label, source)
            await room.local_participant.publish_track(track)

            # Calculation: 2 bytes per sample * channels * samples_per_channel
            # For 48k stereo: 2 * 2 * 960 = 3840 bytes
            expected_byte_size = 2 * num_channels * samples_per_channel

            while True:
                raw_data = wf.readframes(samples_per_channel)
                if not raw_data:
                    break
                
                # Padding the last frame if it's too short
                if len(raw_data) < expected_byte_size:
                    raw_data += b'\x00' * (expected_byte_size - len(raw_data))

                frame = rtc.AudioFrame(
                    data=raw_data,
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    samples_per_channel=samples_per_channel,
                )

                await source.capture_frame(frame)
                await asyncio.sleep(frame_duration_ms / 1000)

            # Unpublish track to clean up
            await room.local_participant.unpublish_track(track.sid)
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
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
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

