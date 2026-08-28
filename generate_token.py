import os
from dotenv import load_dotenv
from livekit import api

load_dotenv()

async def create_token():
    # Fetch credentials from your .env
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')
    
    # Define the room name (must match what the agent is looking for)
    room_name = "test-room"
    participant_identity = "host-user"

    token = api.AccessToken(api_key, api_secret) \
        .with_identity(participant_identity) \
        .with_name("Test User") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
        ))
    
    print("\n--- COPY THIS TOKEN ---")
    print(token.to_jwt())
    print("-----------------------\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_token())