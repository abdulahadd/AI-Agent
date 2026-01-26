# Testing Your Agent (Without ViciDial)

This guide shows you how to test your agent right now, without ViciDial.

## Why Test This Way?

You're right - **ViciDial will handle making calls** and only pass **picked-up calls** to LiveKit rooms. That's perfect! But for now, we'll simulate that by:
1. Creating a LiveKit room (simulating a picked-up call)
2. Having your agent join it automatically
3. You joining as a participant (the "person" on the call)
4. Testing the conversation

This is exactly what will happen with ViciDial, just without the actual phone call part!

## Testing Options

### Option 1: LiveKit Playground (Easiest - Recommended!)

This is the **easiest way** to test:

1. **Start your agent** (Terminal 1):
   ```bash
   cd agents
   python agent.py
   ```
   You should see: `Worker started, waiting for jobs...`

2. **Open LiveKit Playground**:
   - Open browser: http://localhost:7880
   - You'll see the LiveKit dashboard/playground

3. **Create or join a room**:
   - Click "Create Room" or use an existing room
   - Your agent will **automatically join**!

4. **Join as participant**:
   - Connect to the room as a participant
   - Enable your microphone
   - **Start talking!** The agent should respond.

**Why this is great:**
- ✅ No code needed
- ✅ Visual interface
- ✅ See who's in the room
- ✅ Easy to test multiple times

### Option 2: Test Script (`test_agent.py`)

This simulates what ViciDial will do - create a room programmatically:

1. **Start your agent** (Terminal 1):
   ```bash
   cd agents
   python agent.py
   ```

2. **Run the test script** (Terminal 2):
   ```bash
   # From project root
   python test_agent.py
   ```

3. **What happens:**
   - Script creates a LiveKit room
   - Your agent automatically joins
   - Script prints room name and instructions
   - Join the room via Playground (http://localhost:7880) using the room name

## Step-by-Step: Your First Test

### Prerequisites Check

```bash
# 1. Make sure LiveKit is running
docker ps
# Should see: livekit-server and livekit-redis

# 2. Make sure you have .env file
cd agents
ls .env  # Should exist

# 3. Check .env has OpenAI key
# OPENAI_API_KEY should have your actual key
```

### Run the Test

**Terminal 1 - Start Agent:**
```bash
cd agents
python agent.py
```

**Expected output:**
```
INFO: Connecting to LiveKit server at ws://localhost:7880...
INFO: Worker started
INFO: Waiting for jobs...
```

**✅ Good!** Agent is now waiting.

**Terminal 2 - Test It:**

**Option A - Playground (Easiest):**
1. Open: http://localhost:7880
2. Create/join a room
3. Agent joins automatically
4. Connect as participant and talk!

**Option B - Test Script:**
```bash
python test_agent.py
# Follow the instructions it prints
```

## What You Should See

### In Agent Terminal:

When a room is created and you join:
```
INFO: SalesAgent starting conversation...
INFO: Waiting for participant...
INFO: Participant joined!
INFO: SalesAgent conversation started successfully!
```

Then the agent will:
1. Say: "Hello! My name is Sarah, and I'm calling from TechSolutions..."
2. Wait for your response
3. Process with GPT-4
4. Respond naturally
5. Continue the conversation

### In Browser/Playground:

- You'll see the agent in the room (usually named "SalesAgent" or similar)
- You can see when audio is being transmitted
- You can talk and hear the agent's voice response

## Troubleshooting

### Agent doesn't join the room?

**Check:**
1. Agent terminal shows "Worker started"?
2. Agent terminal shows "Waiting for jobs"?
3. No errors in agent terminal?

**Fix:**
- Make sure agent is actually running (check terminal 1)
- Check LiveKit server is running: `docker ps`
- Try restarting the agent

### Agent joins but doesn't talk?

**Check:**
- Do you see "Participant joined!" in agent logs?
- Is your microphone enabled in the browser?
- Are you actually speaking?

**Fix:**
- Wait a moment - agent might be processing
- Make sure microphone permissions are granted
- Speak clearly - the agent is listening!

### "Missing OpenAI API key" error?

**Fix:**
1. Go to `agents/` directory
2. Edit `.env` file
3. Add: `OPENAI_API_KEY=sk-your-actual-key-here`
4. Restart agent

### Connection errors?

**Check:**
- LiveKit server running? `docker ps`
- `.env` file has correct `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`?
- URL format: `ws://localhost:7880` (not `http://`)

## Understanding the Test Flow

```
You (via Playground/test script)
    ↓
Creates LiveKit Room
    ↓
LiveKit Server: "Hey agent worker, new room available!"
    ↓
Your agent.py: "Got it! Joining room..."
    ↓
Agent joins room → Waits for participant
    ↓
You join as participant
    ↓
Agent: "Hello! My name is Sarah..."
    ↓
Conversation starts!
```

This is **exactly** what will happen with ViciDial:
- Instead of you creating the room, ViciDial will
- Instead of you joining manually, the called person's audio will join
- The flow is the same!

## Next Steps After Testing

Once you can successfully:
- ✅ Start the agent
- ✅ Create a room
- ✅ Have agent join automatically
- ✅ Have a conversation

You're ready for:
1. **ViciDial Integration** - Connect real phone calls
2. **Improve the agent** - Better prompts, handling edge cases
3. **Add monitoring** - Track call metrics
4. **Scale** - Run multiple agents

## Tips

- **Test different scenarios**: Try being interested, not interested, asking questions
- **Watch the logs**: Agent terminal shows everything happening
- **Test multiple times**: Create new rooms, test different responses
- **Adjust the script**: Modify `sales_script` in `agent.py` to test different openings


