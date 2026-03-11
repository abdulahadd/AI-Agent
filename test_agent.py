#!/usr/bin/env python3
import asyncio
import os
import sys
import json
from dotenv import load_dotenv
from livekit import api, rtc

load_dotenv()

async def test_agent():
    # 1. Setup Connection
    ws_url = os.getenv("LIVEKIT_URL", "ws://127.0.0.1:7880").strip()
    http_url = ws_url.replace("ws://", "http://").replace("wss://", "https://")
    api_key = os.getenv("LIVEKIT_API_KEY").strip()
    api_secret = os.getenv("LIVEKIT_API_SECRET").strip()
    
    # 2. Initialize API
    lk_api = api.LiveKitAPI(http_url, api_key, api_secret)
    room_name = f"test-room-{int(asyncio.get_event_loop().time())}"
    
    print(f"🧪 Starting Test: {room_name}")

    try:
        print("Step 1: Creating Room...")
        await lk_api.room.create_room(api.CreateRoomRequest(name=room_name))
 
        print("Step 2: Triggering Agent via Metadata...")
        meta_data = json.dumps({"agent_name": "sales-agent"})
        
        await lk_api.room.update_room_metadata(
        api.UpdateRoomMetadataRequest(
            room=room_name,
            metadata=meta_data
        ))
        print("Step 3: Joining as participant...")
        token = api.AccessToken(api_key, api_secret) \
        .with_identity("test-user") \
        .with_grants(api.VideoGrants(room_join=True, room=room_name)) \
        .to_jwt()

        room = rtc.Room()
        print("✅ Metadata updated successfully.")

        @room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print("🔊 SUCCESS: Receiving Audio from Agent!")

        await room.connect(ws_url, token)
        print("✅ Participant Connected. CHECK YOUR AGENT TERMINAL!")

        # 6. STAY CONNECTED
        await asyncio.sleep(60)
        await room.disconnect()
        print("✅ Participant Disconnected.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await lk_api.aclose()
        print("--- TEST FINISHED ---")

if __name__ == "__main__":
    asyncio.run(test_agent())
    