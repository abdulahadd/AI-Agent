# Architecture Explained

## How This System Works (Step by Step)

```
┌─────────────┐
│   Person    │  (Making/Receiving a call)
└──────┬──────┘
       │
       │ Audio Stream
       ▼
┌─────────────────────────────────┐
│      LiveKit Server             │  (Real-time communication hub)
│  - Creates a "Room" per call    │
│  - Manages audio streams         │
│  - Routes to available agents    │
└──────┬──────────────────────────┘
       │
       │ Assigns job to agent
       ▼
┌─────────────────────────────────┐
│    Python Agent (Worker)        │  (Your agent.py script)
│                                  │
│  1. Connects to LiveKit         │
│  2. Waits for jobs (rooms)      │
│  3. Joins room when assigned    │
│  4. Waits for participant       │
│  5. Starts conversation         │
└──────┬──────────────────────────┘
       │
       │ Processing Pipeline:
       ▼
┌─────────────────────────────────┐
│    Voice Processing             │
│                                  │
│  Audio → STT (Speech-to-Text)   │
│    ↓                             │
│  Text → GPT-4 (Understand/Reply)│
│    ↓                             │
│  Text → TTS (Text-to-Speech)   │
│    ↓                             │
│  Audio → Back to Person          │
└─────────────────────────────────┘
```

## Key Concepts

### 1. **LiveKit Server** (Already Running)
   - Your "central hub" for real-time communication
   - Each call = 1 "Room"
   - Manages WebSocket connections
   - Uses Redis for coordination

### 2. **Agent Worker** (What you're about to run)
   - Your `agent.py` script connects to LiveKit as a "worker"
   - A worker is like an employee waiting for tasks
   - When a new room/call is created, LiveKit assigns it to your worker
   - The worker then handles that conversation

### 3. **The Flow**
   ```
   1. Something creates a LiveKit room (could be ViciDial, web app, etc.)
   2. LiveKit sees your worker is available
   3. LiveKit assigns the room to your worker
   4. Your agent's `entrypoint()` function is called
   5. Agent joins the room and waits for participant
   6. When person joins, conversation starts
   7. VoiceAssistant handles all the voice processing automatically
   ```

## How to Test This

### Option 1: Test with LiveKit Playground (Easiest)
1. Run your agent (instructions below)
2. Open LiveKit Playground: http://localhost:7880
3. Create a test room
4. Your agent should join automatically
5. Connect as a participant and talk!

### Option 2: Test with a Simple Script
See `test_agent.py` - I'll create this for you

### Option 3: Test with Web Browser
Create a simple HTML page that connects to LiveKit

## Current Setup Status

✅ **What's Working:**
- LiveKit Server (docker-compose up)
- Redis (running)
- Agent code is ready

⏳ **What You Need:**
- Run the agent script
- Set up .env file with API keys
- Connect something to create rooms

## Next Steps After This Works

1. **ViciDial Integration**: Bridge ViciDial calls → LiveKit rooms
2. **Backend API**: Create rooms programmatically
3. **Dashboard**: Monitor active calls, agent status
4. **Call Recording**: Save conversations
5. **Analytics**: Track call metrics


