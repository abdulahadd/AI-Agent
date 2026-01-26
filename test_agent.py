#!/usr/bin/env python3
"""
Simple test script to create a LiveKit room and connect as a participant.
This lets you test your agent without needing ViciDial or a full web app.

Run this while your agent.py is running in another terminal.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

try:
    from livekit import api, rtc
except ImportError:
    print("⚠️  Missing 'livekit' package for client connection")
    print("   Installing... (you only need this for testing)")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "livekit"])
    from livekit import api, rtc

load_dotenv()

async def test_agent():
    """Create a room and connect as a test participant"""
    
    # Get LiveKit credentials
    livekit_url = os.getenv("LIVEKIT_URL", "ws://localhost:7880").replace("ws://", "http://").replace("wss://", "https://")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ Error: Missing LIVEKIT_API_KEY or LIVEKIT_API_SECRET")
        print("   Make sure your .env file has these values")
        return
    
    # Create LiveKit client
    livekit_client = api.LiveKitAPI(livekit_url, api_key, api_secret)
    
    print("🧪 Agent Test Script")
    print("=" * 50)
    
    # Create a test room
    room_name = f"test-room-{asyncio.get_event_loop().time()}"
    print(f"📞 Creating room: {room_name}")
    
    try:
        # Create the room
        room = await livekit_client.room.create_room(
            api.CreateRoomRequest(
                name=room_name,
                empty_timeout=300,  # Room stays alive for 5 minutes
            )
        )
        print(f"✅ Room created: {room.name}")
        print(f"   Room SID: {room.sid}")
        
        # Generate token for participant
        token = api.AccessToken(api_key, api_secret) \
            .with_identity("test-user") \
            .with_name("Test User") \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )) \
            .to_jwt()
        
        print(f"\n🔑 Generated participant token")
        print(f"\n📋 Room Details:")
        print(f"   Room Name: {room_name}")
        print(f"   LiveKit URL: {livekit_url}")
        print(f"   Token: {token[:50]}...")
        
        print(f"\n✅ Your agent should have automatically joined this room!")
        print(f"   Check the agent.py terminal for logs.")
        
        # Option to connect as participant
        print(f"\n💡 To test the conversation:")
        print(f"   1. Your agent is waiting in the room")
        print(f"   2. Open: http://localhost:7880")
        print(f"   3. Join room '{room_name}' as a participant")
        print(f"   4. Start talking!")
        
        print(f"\n⏳ Room will stay alive for 5 minutes...")
        print(f"   Press Ctrl+C to exit (room will be cleaned up)")
        
        # Keep script running
        await asyncio.sleep(300)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Make sure LiveKit server is running: docker ps")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 Starting agent test...")
    print("   Make sure agent.py is running in another terminal!\n")
    
    try:
        asyncio.run(test_agent())
    except KeyboardInterrupt:
        print("\n👋 Test finished")
        sys.exit(0)

