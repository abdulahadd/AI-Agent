# Quick Cost Guide - At a Glance

## How to Get API Key (5 minutes)

1. Go to: **https://platform.openai.com/api-keys**
2. Sign up / Log in
3. Click **"Create new secret key"**
4. Copy it (starts with `sk-`)
5. Add to `agents/.env`: `OPENAI_API_KEY=sk-your-key`

**They give you $5 free credit when you add payment!**

## Quick Cost Estimates (Less Than 1 Minute Calls)

### GPT-4 (Current Setting)
- **$0.05-0.10 per call** (under 1 minute)
- Most expensive part
- **100 calls:** ~$5-10
- **1,000 calls:** ~$50-100
- **10,000 calls:** ~$500-1,000

### GPT-3.5-turbo (Recommended)
- **$0.005-0.01 per call** (under 1 minute)
- 10x cheaper!
- Still excellent quality
- **100 calls:** ~$0.50-1.00
- **1,000 calls:** ~$5-10
- **10,000 calls:** ~$50-100

### STT + TTS (Speech Services)
- **~$0.01-0.02 per call** (under 1 minute)
- Very cheap!

## Total Cost Per Call (Under 1 Minute)

**With GPT-4:**
- **Total:** ~$0.06-0.12 per call
- 1,000 calls: ~$60-120/month
- 10,000 calls: ~$600-1,200/month

**With GPT-3.5-turbo:**
- **Total:** ~$0.015-0.03 per call
- 1,000 calls: ~$15-30/month
- 10,000 calls: ~$150-300/month

## My Recommendation

**For Testing:**
- Use GPT-3.5-turbo
- $5 free credit = **~300-500 free test calls!**
- Set $10 monthly limit

**For Production:**
- GPT-3.5-turbo is perfect for short calls
- **10,000 calls/month costs only ~$150-300**
- Much more cost-effective than longer calls

## Why Short Calls Are Great

✅ **Cheaper:** Less tokens = less cost  
✅ **Faster:** Quick interactions  
✅ **Efficient:** Get to the point faster  
✅ **Scalable:** Can handle more volume

**10,000 short calls < 1 min = ~$150-300/month**  
**vs 1,000 long calls 10 min = ~$500-1,000/month**

Short calls are way more cost-effective! 🎉

## Real Numbers for Your Scale

**Small (1,000 calls/day):**
- GPT-3.5: ~$450/month
- GPT-4: ~$1,800/month

**Medium (5,000 calls/day):**
- GPT-3.5: ~$2,250/month
- GPT-4: ~$9,000/month

**Bottom line:** With short calls, GPT-3.5-turbo makes this VERY affordable!
