# How to Get Your OpenAI API Key (Step-by-Step)

## Step 1: Create an Account / Sign In

1. Go to: **https://platform.openai.com/**
2. Click **"Sign up"** (if new) or **"Log in"** (if you have an account)
3. Complete registration (email verification)

## Step 2: Add Payment Method

⚠️ **Important:** OpenAI requires payment info even for testing (they have free credits for new users)

1. Click your profile icon (top right)
2. Go to **"Billing"** or **"Settings"** → **"Billing"**
3. Click **"Add payment method"**
4. Add a credit card (they give you $5 free credit to start!)

## Step 3: Get Your API Key

1. Go to: **https://platform.openai.com/api-keys**
2. Click **"Create new secret key"**
3. Give it a name (optional, like "Call Center Agent")
4. Copy the key immediately - it starts with `sk-` and you'll only see it once!
5. **Save it somewhere safe!**

## Step 4: Add to Your Project

```bash
cd agents
cp env.example .env
```

Then edit `.env` and add:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Step 5: Set Usage Limits (Recommended)

1. Go to **"Usage limits"** in billing settings
2. Set a **hard limit** (e.g., $10/month) to prevent surprises
3. Get alerts when you hit certain amounts

---

# Cost Estimates for Your Call Center

## What You'll Pay For

### 1. **GPT-4 (Conversations)** - Main Cost
- **Price:** ~$0.03 per 1,000 input tokens, ~$0.06 per 1,000 output tokens
- **Average call:** ~500-1000 tokens per minute of conversation
- **10-minute call:** ~$0.50-1.00

### 2. **Whisper STT (Speech-to-Text)**
- **Price:** $0.006 per minute
- **10-minute call:** ~$0.06

### 3. **TTS (Text-to-Speech)**
- **Price:** $0.015 per 1,000 characters
- **Average 10-minute call:** ~$0.10-0.20 (agent speaks maybe 500 words)

## Real-World Cost Examples

### Scenario 1: Testing (Low Volume)
- **10 test calls** (5 minutes each)
- **Cost:** ~$5-10 total
- **Mostly GPT-4 costs**

### Scenario 2: Small Operation (100 calls/day)
- **100 calls/day × 5 minutes = 500 minutes**
- **GPT-4:** ~$50/day ($1,500/month)
- **STT/TTS:** ~$10/day ($300/month)
- **Total:** ~$1,800/month

### Scenario 3: Production Scale (1,000 calls/day)
- **1,000 calls/day × 5 minutes = 5,000 minutes**
- **GPT-4:** ~$500/day ($15,000/month) ⚠️
- **STT/TTS:** ~$100/day ($3,000/month)
- **Total:** ~$18,000/month

## Cost Optimization Tips

### 1. **Use GPT-3.5-turbo for cheaper calls**
- Switch to `gpt-3.5-turbo` instead of `gpt-4`
- **Cost:** ~90% cheaper!
- Still very good quality
- Change in `agent.py`: `model="gpt-3.5-turbo"`

### 2. **Set Budget Limits**
- Set hard limits in OpenAI dashboard
- Get alerts at 50%, 75%, 90% of budget

### 3. **Monitor Usage**
- Check dashboard regularly
- Track cost per call
- Optimize prompts to be shorter

### 4. **Start Small**
- Test with GPT-3.5-turbo first
- Use GPT-4 only for important calls
- Scale based on results

## Recommended Setup for Testing

```python
# In agent.py, change this line:
llm=openai.LLM(model="gpt-3.5-turbo"),  # Cheaper for testing
```

**Cost for testing (GPT-3.5-turbo):**
- 10 test calls: ~$1-2
- 100 calls: ~$10-20

## My Recommendation

**For Testing/Development:**
1. Use **GPT-3.5-turbo** ($0.0005 per 1K tokens - 60x cheaper!)
2. Set **$10 monthly limit**
3. Test thoroughly before scaling

**For Production:**
1. Start with **GPT-3.5-turbo** for most calls
2. Use **GPT-4** only for complex/important calls
3. Monitor and optimize based on ROI

## Free Credits

OpenAI often gives:
- **$5 free credit** when you add payment method
- Enough for ~50-100 test calls with GPT-3.5-turbo

## Bottom Line

**Testing:** ~$5-10 should get you started  
**Small scale:** ~$1,500-2,000/month  
**Large scale:** ~$15,000-20,000/month (but you'd have revenue from calls)

**Best strategy:** Start with GPT-3.5-turbo, set limits, test thoroughly!


