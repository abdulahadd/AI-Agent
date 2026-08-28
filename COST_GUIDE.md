# COST_GUIDE.md

# AI Cost Guide

This document explains the expected AI inference costs for the AI Sales Lead Screening project.

---

# Models Used

| Purpose               | Model                    |
| --------------------- | ------------------------ |
| Speech-to-Text (STT)  | `whisper-large-v3-turbo` |
| Intent Classification | `openai/gpt-oss-20b`     |

---

# Workflow

```
Customer Audio
      │
      ▼
Whisper STT
      │
      ▼
Transcript
      │
      ▼
Keyword Classifier
      │
      ├──────────────► Match Found
      │                    │
      │                    ▼
      │              Return Result
      │
      ▼
No Match
      │
      ▼
GPT OSS 20B
      │
      ▼
POSITIVE / NEGATIVE
```

The LLM is **only used when the keyword classifier cannot confidently classify the transcript**, significantly reducing overall inference costs.

---

# LLM Prompt

```text
Classify sales call intent as 'POSITIVE' or 'NEGATIVE'.

POSITIVE:
Interest, consent, or willingness to listen.

NEGATIVE:
Refusal, busy, driving, or asking to stop.

Output ONLY 'POSITIVE' or 'NEGATIVE'.
```

The model returns exactly one word:

```
POSITIVE
```

or

```
NEGATIVE
```

---

# Official Pricing

## GPT OSS 20B

| Item          |              Price |
| ------------- | -----------------: |
| Input Tokens  | $0.075 / 1 Million |
| Output Tokens |  $0.30 / 1 Million |

## Whisper Large V3 Turbo

| Item                |              Price |
| ------------------- | -----------------: |
| Audio Transcription | $0.04 / audio hour |

---

# STT Cost Calculation

Average audio length:

```
10 seconds
```

Groq pricing:

```
$0.04 per hour
```

1 hour = 3600 seconds

Cost per second:

```
0.04 / 3600
= $0.00001111
```

Cost for one 10-second transcription:

```
10 × 0.00001111
= $0.00011111
```

## STT Cost Per Call

| Audio Length |          Cost |
| ------------ | ------------: |
| 10 sec       | **$0.000111** |

---

# Monthly STT Cost

For 30,000 calls/month:

```
30,000 × $0.00011111
= $3.3333
```

## Total Monthly STT Cost

**≈ $3.33/month**

---

# LLM Cost Assumptions

The intent classifier prompt is intentionally very small.

Typical request:

| Component                  | Estimated Tokens |
| -------------------------- | ---------------: |
| Prompt                     |            40–50 |
| Transcript (10 sec speech) |            20–60 |
| Total Input                |             ~100 |
| Output                     |              1–3 |

To keep budgeting conservative, we assume:

```
100 input tokens
2 output tokens
```

---

# Cost Per LLM Request

## Input

```
100 / 1,000,000
× $0.075

= $0.0000075
```

## Output

```
2 / 1,000,000
× $0.30

= $0.0000006
```

## Total

```
$0.0000081
```

Per classification.

---

# Monthly LLM Cost

If every call reaches the LLM:

```
30,000 × $0.0000081

= $0.243
```

Rounded:

**≈ $0.24/month**

---

# Cost with Keyword Filtering

The system performs keyword classification before calling the LLM.

Only uncertain transcripts are sent to GPT OSS 20B.

| Calls Sent to LLM | Monthly Cost |
| ----------------: | -----------: |
|     30,000 (100%) |        $0.24 |
|      15,000 (50%) |        $0.12 |
|       9,000 (30%) |        $0.07 |
|       6,000 (20%) |        $0.05 |
|       3,000 (10%) |        $0.02 |

The keyword filter makes LLM costs almost negligible.

---

# Total Monthly Cost

## Worst Case

All calls use Whisper and GPT.

| Component   |            Cost |
| ----------- | --------------: |
| Whisper STT |           $3.33 |
| GPT OSS 20B |           $0.24 |
| **Total**   | **$3.57/month** |

---

## Typical Production Scenario

If only 30% of calls require the LLM:

| Component   |            Cost |
| ----------- | --------------: |
| Whisper STT |           $3.33 |
| GPT OSS 20B |           $0.07 |
| **Total**   | **$3.40/month** |

---

# Important Notes

* Whisper transcription is charged by audio duration, **not by tokens**.
* GPT OSS 20B is charged separately for input and output tokens.
* These calculations assume an average audio duration of **10 seconds**.
* These calculations assume an average of **100 input tokens** and **2 output tokens** for each LLM request.
* Actual LLM cost may vary slightly depending on transcript length, but even doubling the transcript length would only increase the LLM cost by a few cents per month at this scale.
* The STT cost dominates the total monthly AI cost (>90% of total spend).

---

# Estimated Monthly Budget

| Monthly Calls |   STT | LLM (100%) |     Total |
| ------------: | ----: | ---------: | --------: |
|        30,000 | $3.33 |      $0.24 | **$3.57** |

This architecture is highly cost-efficient because:

* Speech transcription is inexpensive.
* Intent classification uses a lightweight prompt.
* Most requests are handled by the keyword classifier.
* GPT OSS 20B is only invoked when keyword classification is inconclusive.
