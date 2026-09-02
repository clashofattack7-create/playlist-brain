# 🧠 Playlist Brain — Your Personal Knowledge Assistant

## What this is
A knowledge base built **ONLY from your two YouTube playlists**. Nothing from outside — every answer this brain gives comes from inside these playlists.

| Playlist | Channel | Videos | Class time |
|---|---|---|---|
| **SL Hunting Course** | Plus Gaming 3 | 83 | ~97h 41m |
| **Chart Reading Live Classes** | CHART HUB | 40 | ~47h 57m |
| **Total** | | **123** | **~145h 38m** |

## How to use it (in chat with me)
Just ask, for example:

- `Playlist Brain: what is stop-loss hunting?`
- `Playlist Brain: how does the course say to mark round numbers?`
- `Playlist Brain: what does Class 15 of Chart Hub teach about losing money?`

## 🎯 TRADING DECISIONS (Nifty / Bank Nifty / Sensex)
Every trading morning, send me:
1. Today's open / gap of the 3 indexes (or just say "pull live data")
2. Yesterday's closes
3. Expiry day? Any news?

I answer with a **locked plan**: Bias → Levels → Entry → Stop-Loss → Target → Invalidation, plus the class citations behind every line. Rules live in `knowledge/03-trading-decision-framework.md`.

⚠️ The brain decides *according to the course* — it does not guarantee profits. Capital protection first; final click is yours.

**Rule of the brain:** I will answer ONLY from these playlists — the videos, the classes, the transcripts. If the answer is not in the playlists, I will say so instead of guessing.

## What's inside
- `BRAIN.md` — master index: curriculum, every video, links, durations
- `knowledge/` — deep knowledge documents per playlist (topics, concepts, class-by-class notes)
- `transcripts/` — full text of every class (with timestamps) — the raw memory of the brain
- `raw/` — downloaded page data and video metadata
- `scripts/` — the tools that build this brain

## Status
Transcripts are downloaded in the background and knowledge documents are built on top of them. Coverage is tracked in `BRAIN.md`.

## 📤 SENDING FILES TO THE BRAIN (in chat)
- **Images (option-chain / chart screenshots):** drag & drop onto the chat page (drop overlay appears) → thumbnails rail → Send. Accepted: PNG / JPEG / WebP / GIF.
- **Text / JSON / CSV / anything else:** type `@` in the composer → pick the file from the workspace menu (e.g. `@playlist-brain/inbox/oc-NIFTY.json`), or drop it into `playlist-brain/inbox/` and reference it.
- The Brain then reads the file/image and merges it (OI map, chart read, etc.) into today's plan.
- If drag & drop ever doesn't respond: Settings → Plugins → make sure the Attachment presentation plugin is enabled.
