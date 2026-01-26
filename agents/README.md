# AI Sales Agent

Python-based AI voice agent for call center operations using LiveKit.

## Features

- **Real-time Voice Processing**: Speech-to-text and text-to-speech
- **GPT-4 Integration**: Intelligent conversation handling
- **Voice Activity Detection**: Knows when to speak and when to listen
- **Sales Script Management**: Customizable sales pitches
- **Professional Conversation Flow**: Handles objections and follow-ups

## Quick Start

### 1. Set up Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
# - Add your OpenAI API key
# - Verify LiveKit configuration
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Agent

```bash
python agent.py
```

### 4. Test with Docker

```bash
# Build the agent image
docker build -t sales-agent .

# Run the agent
docker run --env-file .env sales-agent
```

## Configuration

### Environment Variables

- `LIVEKIT_URL`: LiveKit server WebSocket URL
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret
- `OPENAI_API_KEY`: OpenAI API key for GPT integration
- `AGENT_NAME`: Name of the agent
- `AGENT_VOICE`: TTS voice (alloy, echo, fable, onyx, nova, shimmer)
- `AGENT_LANGUAGE`: Language code (en, es, fr, etc.)

### Sales Script

Edit the `sales_script` in `agent.py` to customize your sales pitch.

### System Prompt

Modify the `system_prompt` to change the agent's behavior and conversation style.

## Architecture

```
ViciDial → LiveKit Server → Python Agent
                    ↓
              (Voice Processing)
                    ↓
              (GPT-4 Response)
                    ↓
              (TTS Output)
```

## Integration with ViciDial

The agent is designed to receive calls from ViciDial through LiveKit:

1. ViciDial makes outbound calls
2. Connected calls are routed to LiveKit
3. LiveKit creates a room for each call
4. Python agent joins the room
5. Agent handles the conversation
6. Call data is logged for analytics

## Scaling

To handle 1000+ concurrent calls:

1. Run multiple agent instances
2. Use Docker Swarm or Kubernetes
3. Load balance through LiveKit
4. Monitor with Redis for agent availability

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check LiveKit server is running
2. **No Audio**: Verify microphone permissions
3. **Poor Recognition**: Check internet connection for STT
4. **Slow Responses**: Consider upgrading OpenAI plan

### Logs

Check logs for detailed debugging information:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python agent.py
```



