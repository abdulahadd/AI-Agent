#!/usr/bin/env python3
"""
AI Sales Agent for Call Center
Connects to LiveKit server and handles voice conversations with real people.
"""

import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesAgent:
    """AI Sales Agent that handles voice conversations"""
    
    def __init__(self):
        self.agent_name = os.getenv("AGENT_NAME", "SalesAgent")
        self.voice = os.getenv("AGENT_VOICE", "alloy")
        self.language = os.getenv("AGENT_LANGUAGE", "en")
        
        # Sales script/pitch (optimized for quick calls < 1 minute)
        self.sales_script = """
        Hi! This is Sarah from TechSolutions. 
        
        We help businesses increase productivity by 40% with automation. 
        Interested in a quick 2-minute demo?
        """
        
        # System prompt for the AI (optimized for quick calls < 1 minute)
        self.system_prompt = f"""
        You are {self.agent_name}, a professional and friendly sales representative. 
        
        IMPORTANT: Keep calls under 1 minute. Be direct and concise.
        
        Your goal:
        1. Quick introduction (already done in opening)
        2. Present value: 40% productivity increase with automation
        3. If interested: Schedule 2-minute demo call
        4. If not interested: Thank them and end politely
        
        Guidelines:
        - Be BRIEF - get to the point fast
        - One sentence responses when possible
        - Don't repeat information
        - Respect "no" immediately
        - If interested, get contact info quickly
        
        Remember: These are short calls. Efficiency is key!
        """

    async def entrypoint(self, ctx: JobContext):
        """Main entrypoint for the agent"""
        logger.info(f"{self.agent_name} starting conversation...")
        
        # Wait for participant to join
        await ctx.wait_for_participant()
        
        # Create voice assistant with OpenAI integration
        assistant = VoiceAssistant(
            vad=silero.VAD.load(),        # Voice Activity Detection
            stt=openai.STT(),             # Speech-to-Text (OpenAI Whisper)
            llm=openai.LLM(model="gpt-4o-mini"),  # Language Model (cheapest, best for scale)
            tts=openai.TTS(voice=self.voice),  # Text-to-Speech
        )
        
        # Set up the conversation
        assistant.start(
            ctx.room,
            system_prompt=self.system_prompt,
            initial_message=self.sales_script,
        )
        
        logger.info(f"{self.agent_name} conversation started successfully!")
        
        # Keep the agent running
        await assistant.aclose()

async def main():
    """Main function to start the agent"""
    
    # Load environment variables
    load_dotenv()
    
    # Get LiveKit configuration
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([livekit_url, livekit_api_key, livekit_api_secret]):
        logger.error("Missing LiveKit configuration. Please check your .env file.")
        return
    
    # Create the sales agent
    sales_agent = SalesAgent()
    
    # Start the worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=sales_agent.entrypoint,
            prewarm_fnc=None,
        )
    )

if __name__ == "__main__":
    asyncio.run(main())
