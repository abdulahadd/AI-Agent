# Setting Up and Running Your Agent

## Visual Flow

```
┌─────────────────────────────────────────────────────────┐
│                   YOUR SETUP                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Terminal 1:                                           │
│  ┌────────────────────┐                                │
│  │ docker-compose up  │  → LiveKit Server              │
│  └────────────────────┘     Redis                       │
│                                                          │
│  Terminal 2:                                           │
│  ┌────────────────────┐                                │
│  │  python agent.py   │  → Agent Worker                │
│  │  (waits for calls) │     Connected to LiveKit       │
│  └────────────────────┘                                  │
│                                                          │
│  Terminal 3 (Optional):                                 │
│  ┌────────────────────┐                                │
│  │ python test_agent  │  → Creates test room           │
│  │   .py              │     Triggers agent to join      │
│  └────────────────────┘                                  │
└─────────────────────────────────────────────────────────┘
```

## Step-by-Step Instructions

### 1. Check Prerequisites

Open a terminal and verify LiveKit is running:

```bash
docker ps
```

You should see `livekit-server` and `livekit-redis` running.

### 2. Prepare the Agent

```bash
cd agents

# Create .env file if you haven't
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Install Python Dependencies

```bash
# Make sure you're in agents/ directory
pip install -r requirements.txt
```

### 4. Run the Agent

```bash
python agent.py
```

**Expected output:**
```
INFO:__main__:Connecting to LiveKit server...
INFO:livekit.agents:Worker started
INFO:livekit.agents:Waiting for jobs...
```

**This is correct!** The agent is now:
- ✅ Connected to LiveKit
- ✅ Waiting for rooms/calls
- ⏳ Ready to handle conversations

**Don't close this terminal!** The agent needs to keep running.

### 5. Test the Agent

You have 3 options:

#### Option A: LiveKit Playground (Easiest)

1. Open browser: http://localhost:7880
2. You'll see the LiveKit dashboard
3. Create or join a room
4. Your agent will automatically join
5. Connect as a participant and talk!

#### Option B: Python Test Script

In a **new terminal** (keep agent.py running):

```bash
# From project root
python test_agent.py
```

This creates a test room that your agent will join automatically.

#### Option C: Manual Room Creation

Use LiveKit API or webhooks to create rooms programmatically.

## What Happens When a Call Starts

1. **Room Created**: Something creates a LiveKit room (test script, web app, ViciDial)
2. **Agent Assigned**: LiveKit sees your agent is available and assigns the room
3. **Agent Joins**: Your `entrypoint()` function runs
4. **Waits**: Agent waits for a participant to join
5. **Conversation Starts**: When participant joins:
   - Agent says: "Hello! My name is Sarah..."
   - Listens for response
   - Processes with GPT-4
   - Responds naturally
   - Continues conversation

## Understanding the Agent Code

### `agent.py` - Main Agent

```python
# 1. Agent connects to LiveKit
cli.run_app(WorkerOptions(...))

# 2. When a room is assigned, this runs:
async def entrypoint(ctx):
    await ctx.wait_for_participant()  # Wait for person
    
    # 3. Create voice assistant
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),      # Knows when to listen
        stt=deepgram.STT(),         # Converts speech to text
        llm=openai.LLM(),           # Generates responses
        tts=openai.TTS(),           # Converts text to speech
    )
    
    # 4. Start conversation
    assistant.start(ctx.room, ...)
```

### How VoiceAssistant Works

The `VoiceAssistant` class handles everything automatically:

```
Person speaks
    ↓
[VAD detects speech] → Starts listening
    ↓
[STT converts to text] → "Hello, I'm interested..."
    ↓
[GPT-4 processes] → Generates response
    ↓
[TTS converts to speech] → Agent speaks
    ↓
Cycle repeats
```

You don't need to manage audio streams, the `VoiceAssistant` does it all!

## Common Questions

**Q: Do I need to create rooms manually?**
A: For testing, yes (use test script or Playground). In production, ViciDial or your backend will create rooms automatically.

**Q: Can one agent handle multiple calls?**
A: By default, one agent = one call. See `scaling_example.py` for multi-call handling, or run multiple agent instances.

**Q: How do I see what the agent is doing?**
A: Check the terminal running `agent.py` - it logs everything.

**Q: The agent connects but nothing happens?**
A: Normal! It's waiting for a room. Create a room using Playground or test script.

**Q: How do I stop the agent?**
A: Press `Ctrl+C` in the terminal running `agent.py`.

## Next Steps

Once you can run the agent and test it:
1. ✅ Understand the flow
2. ✅ Test conversations
3. ⏭️ Integrate with ViciDial (create rooms from calls)
4. ⏭️ Build backend API (programmatic room creation)
5. ⏭️ Add monitoring dashboard


