# Quick Start Guide - Running Your First Agent

## Prerequisites Check

First, make sure these are running:
```bash
# Check if LiveKit and Redis are running
docker ps

# You should see:
# - livekit-server
# - livekit-redis
```

If not running:
```bash
docker-compose up -d
```

## Step 1: Set Up Environment Variables

1. Go to the `agents/` directory:
```bash
cd agents
```

2. Copy the example env file:
```bash
cp env.example .env
```

3. Edit `.env` and add your **Groq API key**:
```bash
# Open .env in your editor
# Add your actual OpenAI API key:
GROQ_API_KEY=sk-your-actual-key-here
```

**Important:** You need:
- ✅ LiveKit URL, API Key, Secret (already in env.example)
- ✅ **GROQ API Key** (you must add this!)

## Step 2: Install Dependencies

```bash
# Make sure you're in the agents/ directory
pip install -r requirements.txt
```

This installs:
- `livekit-agents` - Core agent framework
- `livekit-plugins-groq`  STT and LLM
<!-- - `livekit-plugins-openai` - GPT and TTS
- `livekit-plugins-deepgram` - Speech-to-text -->
- `livekit-plugins-silero` - Voice detection

## Step 3: Run the Agent

```bash
python agent.py dev
```

**What you should see:**
```
INFO: Connecting to LiveKit server at ws://localhost:7880...
INFO: Worker started, waiting for jobs...
INFO: Ready to handle conversations!
```

The agent is now:
- ✅ Connected to LiveKit
- ✅ Waiting for rooms/calls
- ✅ Ready to handle conversations

**The agent will stay running** - this is normal! It's waiting for work.

## Step 4: Test It!

### Option A: Using LiveKit Playground

1. Open browser: http://localhost:7880
2. Click "Create Room" or use an existing room
3. Your agent should automatically join!
4. Connect as a participant and start talking

### Option B: Using the Test Script

I've created `test_agent.py` - run it in another terminal:
```bash
python test_agent.py
```

## Troubleshooting

### "Missing LiveKit configuration"
- Make sure you have a `.env` file in `agents/` directory
- Check that `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` are set

### "Connection refused"
- Make sure LiveKit server is running: `docker ps`
- Check the URL matches: `ws://localhost:7880`

### "OpenAI API error"
- Make sure your `GROQ_API_KEY` is set in `.env`
- We are using free tier Groq key for now

### Agent connects but nothing happens
- This is normal! It's waiting for a room to be created
- Create a room using LiveKit Playground or test script

## Understanding the Logs

When a call starts, you'll see:
```
INFO: SalesAgent starting conversation...
INFO: Waiting for participant...
INFO: Participant joined!
INFO: SalesAgent conversation started successfully!
```

Then the agent will:
1. Say the initial greeting (sales_script)
2. Listen for the person's response
3. Process STT and then LLM
4. Respond naturally
5. Continue the conversation

## Stop the Agent

Press `Ctrl+C` in the terminal running the agent.


