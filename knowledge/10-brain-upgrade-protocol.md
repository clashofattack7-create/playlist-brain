# 🧠 BRAIN UPGRADE PROTOCOL — how the Brain learns from YOUR output

> **Purpose:** every trading output you give me is the brain's live memory. It is merged into the
> knowledge base (D:\dsh\DSH\playlist-brain\) — never answered in chat and then forgotten. The plan
> builds on yesterday, and the lessons compound.

## 1. What counts as "your output" (triggers)

| Trigger | Example |
|---|---|
| Position updates | entered / added / reduced / squared, at what price & time |
| Fills & exits | entry print, SL hit, target hit, trailing exit |
| Uploads | option-chain screenshots, chart screenshots, bhavcopy files, broker P&L |
| Corrections | "no—the gap was bigger", "wrong date", "that level is wrong" |
| News / events you tell me | RBI, budget, results, circuit news |
| Day-end results | final P/L, what happened vs the plan |
| Tool changes you verify | a script now works / breaks; a route got blocked |

## 2. Where it goes

| Output | File | Holds |
|---|---|---|
| Working state | `knowledge\<NN>-<type>-<today>.md` (next number after the latest) | today's refreshed plan / chart-read / OI map / live decision |
| Raw results + the day's story | `journal\<YYYY-MM-DD>.md` | plan vs actual: bias, entry/SL/target, outcome ₹, which rule did it |
| Durable lessons | `lessons\<NN>-<slug>.md` | one lesson per file, dedup'd, dated, class-cited |
| Pipeline / tool truth | `BRAIN.md` | sources, status, expiry facts — update when verified or broken |

## 3. Rules

1. **Merge immediately** — on any upload or position change mid-session: update the working state
   first, then re-issue the decision. Never answer from stale state.
2. **Never overwrite** — history is append-only. New day = new file; update = edit today's working
   state or create the next `<NN>`.
3. **Only record what the user actually sent** — never invent positions, results, or messages.
4. **Every entry carries** date + source (message / upload) + the class citation where it applies.
5. **Closed corpus still governs** — lessons are the user's *observed results*, not new market theory.
   If a result contradicts the rulebook, mark it **OPEN QUESTION**; never silently rewrite a rule.
   Flag it during the next morning's read so the plan is aware of the conflict.
6. **Say what you wrote** — at the end of every answer, list the knowledge-base files updated.
7. **Start from memory** — before any decision, check the latest `journal\` entry and latest
   `lessons\` file; the brain answers with its full history, not just a fresh pull.
8. **Day close** — after 15:30 IST (or the next session), if the user gave results, write the day's
   journal entry. If they didn't, ask once for the result — don't invent it.
