# AI Call Center System

A scalable AI-powered call center system using LiveKit, ViciDial, and GPT agents.

## Architecture

- **LiveKit Server**: Real-time audio streaming and communication
- **Python AI Agents**: GPT-powered voice agents for sales calls
- **ViciDial Integration**: Call management and routing
- **NestJS Backend**: API and management layer
- **React Frontend**: Dashboard and monitoring

## 🚀 Quick Start

**New to this project?** Start here:
1. 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand how it works
2. 🏃 Read [QUICK_START.md](QUICK_START.md) - Get your first agent running
3. 📚 Read [agents/SETUP_GUIDE.md](agents/SETUP_GUIDE.md) - Detailed setup instructions

### 1. Start LiveKit Server & Redis

```bash
docker-compose up -d
```

### 2. Verify Server is Running

```bash
# Check containers are running
docker ps

# Check server health
curl http://localhost:7880/

# Check logs
docker-compose logs livekit-server
```

### 3. Run Your First Agent

```bash
cd agents
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

pip install -r requirements.txt
python agent.py
```

### 4. Test the Agent

**Easiest way:** Open http://localhost:7880 in your browser (LiveKit Playground)

Or use the test script:
```bash
python test_agent.py  # In a new terminal
```

## Project Structure

```
├── config/              # LiveKit server configuration
├── agents/              # Python AI agents
│   ├── agent.py        # Main sales agent (run this!)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── env.example      # Copy to .env and add your keys
│   └── SETUP_GUIDE.md   # Detailed setup instructions
├── ARCHITECTURE.md      # How the system works (read this!)
├── QUICK_START.md       # Quick start guide
├── test_agent.py        # Test script to create rooms
├── backend/             # NestJS API server (coming soon)
├── frontend/            # React dashboard (coming soon)
├── docker-compose.yml   # LiveKit + Redis
└── README.md
```

## Development

- LiveKit Server: `http://localhost:7880`
- Redis: `localhost:6379`
- WebSocket: `ws://localhost:7881`
