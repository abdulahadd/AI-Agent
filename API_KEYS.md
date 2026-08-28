# API Keys Needed - Quick Guide

## ✅ What You Already Have

**LiveKit Keys** - Already set up! You don't need to do anything.
- These are in your `config/livekit.yaml` and `env.example`
- They're for your local server, already working

## 🔑 What You Need to Get

### Groq Key (REQUIRED)

**Why:** Your agent uses Groq for everything:
- GPT-4 for conversations
- Groq Whisper for speech-to-text (STT)
- Groq 'openai/gpt-oss-20b'

**How to get it:**
1. Go to: https://console.groq.com
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Add it to your `.env` file:**
```bash
cd agents
cp env.example .env
# Edit .env and add:
GROQ_API_KEY=sk-your-actual-key-here
```

## Summary

**To test right now:**
1. ✅ LiveKit keys - Already have them
2. ⚠️ Groq key - **Get this one** (5 minutes)

**That's it!** Just one API key needed - everything uses OpenAI now.

## About Pricing

**Note:** OpenAI TTS is NOT free - both STT and TTS cost money, but:
- Very cheap (pay per use)
- Around $0.006 per 1000 characters for TTS
- Around $0.006 per minute for Whisper STT
- GPT-4 is the main cost (but that's your AI brain!)

**Why switch to OpenAI STT?**
- ✅ One API key instead of two
- ✅ Same pricing model
- ✅ Consistent quality from one provider

