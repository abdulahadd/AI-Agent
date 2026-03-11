# Plan: Groq LLM + STT, No TTS (Pre-recorded Audio Only)

**Status:** Planning only — no implementation yet.

---

## 1. Goal

- **LLM:** Not used for classification (keyword-based only).
- **STT:** Groq Whisper (one key; same as Groq if we add LLM later).
- **TTS:** **None.** All agent speech is fixed and pre-recorded:
  - **Pitch:** Same every time (one audio file).
  - **If user says yes / positive:** Play: *"I am connecting you forward"* (one audio file).
  - **If user says no / negative:** Play: *"Okay. Thank you for your time"* (one audio file).

---

## 2. Why This Approach

- **Cost:** No TTS API cost; Groq TTS was ~$495/month at 30K calls.
- **Predictability:** Same pitch and two short responses; easy to record and replace.
- **Simplicity:** No dynamic speech generation; only STT + intent + play one of three clips.

---

## 3. High-Level Flow (Target Behavior)

```
1. Agent joins room → wait for participant.
2. Play pre-recorded PITCH (full script) once.
3. Listen for user (STT).
4. Classify: POSITIVE (default) vs NEGATIVE (only if clear rejection) — see § 3.1.
5. Play one of two pre-recorded responses:
   - Positive → "I am connecting you forward"
   - Negative → "Okay. Thank you for your time"
6. End (e.g. disconnect or hand off to verifier/supervisor).
```

### 3.1 Classification rule (decided)

- **Default = POSITIVE.** If the person said something that is **not** a negative phrase, we treat the response as positive.
- **NEGATIVE when** (1) user said a negative phrase, or (2) user said nothing (silence).
- **Examples of NEGATIVE** (treated as negative):
  - "no"
  - "not interested"
  - "don't want it"
  - Silence / no speech / empty transcript
  - Any phrase that clearly indicates the user does not want the offer.
- **Examples of POSITIVE** (treated as positive):
  - "oh" (or "Oh")
  - "yes", "sure", "okay", "tell me more"
  - Anything that is **not** a clear rejection and **not** silence.

**Implementation:** Use simple keyword/phrase matching. If transcript is empty or silence → NEGATIVE. If transcript matches a negative phrase → NEGATIVE. Otherwise → POSITIVE. No LLM needed for classification (saves cost and latency).

---

## 4. What We Need to Do (Checklist)

### 4.1 Dependencies and config

- [ ] Add Groq plugin: `livekit-plugins-groq` (LLM + STT).
- [ ] Keep `livekit-plugins-silero` for VAD (or use Groq STT in streaming mode if it replaces need for VAD where applicable).
- [ ] Remove or make optional: `livekit-plugins-openai` for this agent (or keep only if we still use OpenAI for something).
- [ ] Env: `GROQ_API_KEY` in `agents/.env`; document in `env.example`.

### 4.2 Audio assets (pre-recorded)

- [ ] **Pitch:** One audio file (e.g. WAV/MP3) of the full pitch:
  - *"Hello, this is [Agent name] on a recorded line, how are you? Based on our records you may qualify for the state approved final expense program..."*  
  - Same script every time; one file.
- [ ] **Positive response:** One short file: *"I am connecting you forward"*.
- [ ] **Negative response:** One short file: *"Okay. Thank you for your time"*.
- [ ] Decide format (e.g. 16 kHz or 48 kHz, mono) and where to store (e.g. `agents/audio/`).
- [ ] Ensure licensing/rights if using a voice talent.

### 4.3 Architecture: custom flow vs VoiceAssistant

- **Current:** `VoiceAssistant(STT, LLM, TTS)` — expects TTS to generate speech from text every turn.
- **Target:** No TTS; we only play three fixed files. So we **cannot** use `VoiceAssistant` as-is.

**Options:**

- **Option A – Custom pipeline (recommended):**
  - Do **not** use `VoiceAssistant`.
  - Implement a custom `entrypoint` that:
    1. Waits for participant.
    2. Plays pitch file (e.g. via LiveKit audio track / `AudioSource` or agent playout helpers).
    3. Subscribes to participant audio → runs **Groq STT** on it.
    4. When user has finished speaking (VAD or STT end-of-utterance):
       - Get transcript.
       - Classify intent (positive vs negative) via **keyword list** (negative phrases only; default = positive).
       - Play the corresponding pre-recorded response file.
    5. Then end call or hand off.
  - References: LiveKit Python “playing audio” examples, `AgentPlayout` / `AudioSource`, and docs for publishing local audio tracks.

- **Option B – VoiceAssistant with “fake” TTS:**
  - Implement a custom TTS-like component that, instead of calling a TTS API, always returns pre-recorded audio (e.g. pitch for first turn, then one of two clips based on last LLM output). This is more invasive and may not match VoiceAssistant’s turn-taking model (e.g. it expects text to speak each time). **Less recommended** unless we confirm VoiceAssistant supports this pattern.

**Recommendation:** Plan for **Option A** (custom pipeline with Groq STT + keyword classification + pre-recorded audio playback).

### 4.4 Classification: keyword-based (no LLM)

- **No LLM.** Classify with a negative-phrase list only:
  - Input: transcript of user’s reply after the pitch.
  - Output: “positive” or “negative” (or structured, e.g. `{"intent": "positive"}`).
- No system prompt to minimize tokens and cost (e.g. “You are a classifier. Reply only with POSITIVE or NEGATIVE based on whether the person said yes / is interested / qualifies.”).
- Alternatively, use simple keyword logic (e.g. “yes”, “sure”, “ok”, “connect” → positive; else negative) to avoid LLM cost on some or all calls; document this in the plan as an option.

### 4.5 STT (Groq)

- Use Groq STT (e.g. Whisper Large V3 Turbo or Distil-Whisper for English) in the custom pipeline.
- Integrate so that:
  - We get a transcript after the user speaks (and we have a way to know “user finished” — e.g. silence/VAD or STT end-of-utterance).
- Respect Groq’s minimum billing (e.g. 10 seconds) when estimating cost; our flow stays the same.

### 4.6 Playback (pre-recorded audio)

- **Pitch:** Play once when the participant is present (and optionally when we consider “call started”).
- **Responses:** Play **only one** of the two short clips per call, based on intent.
- Implementation steps:
  - Load three audio files (pitch, positive, negative).
  - Use LiveKit’s mechanism to publish audio (e.g. `AudioSource` + push frames, or an agent playout helper that accepts file or stream).
  - Ensure correct sample rate and frame size (e.g. 20 ms) as per LiveKit/docs.
  - Play pitch first; after user speaks and we classify, play the chosen response clip then finish.

### 4.7 Edge cases and behavior

- **No user speech (silence / timeout):** Treat as **NEGATIVE** (e.g. → play negative response clip, or play “Thank you for your time”).
- **Unclear / multiple utterances:** Treat as positive unless one utterance clearly matches a negative phrase (e.g. see § 3.1; “positive only if clearly yes”).
- **Barge-in:** Decide if we allow user to interrupt the pitch; if yes, we may need to stop pitch playback and then classify from partial transcript.
- **Verifier handoff:** “I am connecting you forward” implies a transfer; document how that will be implemented (e.g. LiveKit room transfer, SIP transfer, or external system) — out of scope for this plan but should be noted.

---

## 5. How We Will Do It (Implementation Order)

1. **Setup**
   - Add `livekit-plugins-groq`, `GROQ_API_KEY`, and update `env.example` / README.

2. **Audio assets**
   - Create `agents/audio/` (or agreed path).
   - Record or generate three files (pitch, positive, negative); document format and location.

3. **Proof of concept**
   - Small script or branch: join room, play one WAV (e.g. pitch) via LiveKit, then disconnect. Confirm playback works.

4. **Custom agent flow**
   - New entrypoint (or new agent file) that:
     - Waits for participant.
     - Plays pitch.
     - Listens with Groq STT (and VAD if needed).
     - Gets transcript → matches negative-phrase list → chooses positive or negative.
     - Plays the correct pre-recorded response.
     - Ends.

5. **Integration**
   - Replace or parallel the current OpenAI-based agent (e.g. `agent.py` vs `agent_groq_prerecorded.py`) and document how to run each.

6. **Cost and ops**
   - Update COST_GUIDE or LLM_COST_COMPARISON: no TTS; Groq LLM + Groq STT only; mention pre-recorded audio.
   - Document how to add or change the three audio files.

---

## 6. Cost Snapshot (Recap)

- **LLM:** $0 (classification is keyword-based; no LLM call).
- **STT (Groq Whisper):** ~$1.67 (Distil) or ~$3.33 (Turbo) per month for 30K × 10 s.
- **TTS:** $0 (pre-recorded only).
- **Total:** ~$1.67–$3.33/month for 30K calls.

---

## 7. Open Decisions (Before Implementation)

1. **Classification:** **Decided** — keyword-based; negative phrases only; default = positive (see § 3.1).
2. **Pitch playback:** Exact trigger (e.g. as soon as participant joins, or after a short delay).
3. **Barge-in:** Allow user to interrupt pitch or not.
4. **File format and location:** WAV/MP3, sample rate, and path (e.g. `agents/audio/pitch.wav`).
5. **Verifier handoff:** Out of scope for this doc but should be specified elsewhere (e.g. “after positive clip, signal to transfer to supervisor”).

---

## 8. What We Are Not Doing (Yet)

- No code changes until this plan is agreed.
- No TTS API; no dynamic speech generation.
- No change to LiveKit server or Docker unless we need to (e.g. for transfer).

---

**Next step:** Confirm this plan (and open decisions), then implement in the order above.
