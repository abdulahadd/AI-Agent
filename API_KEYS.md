# API Keys Needed - Quick Guide

## ✅ What You Already Have

**LiveKit Keys** - Already set up! You don't need to do anything.
- These are in your `config/livekit.yaml` and `env.example`
- They're for your local server, already working

## 🔑 What You Need to Get

### OpenAI API Key (REQUIRED)

**Why:** Your agent uses OpenAI for everything:
- GPT-4 for conversations
- OpenAI Whisper for speech-to-text (STT)
- OpenAI TTS for text-to-speech

**How to get it:**
1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Add it to your `.env` file:**
```bash
cd agents
cp env.example .env
# Edit .env and add:
OPENAI_API_KEY=sk-your-actual-key-here
```

## Summary

**To test right now:**
1. ✅ LiveKit keys - Already have them
2. ⚠️ OpenAI key - **Get this one** (5 minutes)

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

