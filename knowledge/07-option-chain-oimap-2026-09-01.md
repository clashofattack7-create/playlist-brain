# 📊 OPTION CHAIN / OI MAP — pulled 01-Sep-2026 pre-open (last session Mon 31-Aug)
> Source: **official BSE derivatives bhavcopy** (NSE blocks this cloud IP — see note at bottom).

## SENSEX — weekly expiry **Thu 03-Sep-2026** (2 sessions away) · underlying 76,957.27
**Total CE OI: 11.70 M contracts · PE OI: 12.80 M · PCR = 1.09 (mildly bullish posture)**

| Strike | CE OI | PE OI | Monday OI change CE / PE | Read |
|---|---|---|---|---|
| **77,000** | 643,920 | **959,780** | +424,580 / +295,200 | ⚡ THE pivot. Giant PE wall (support) + huge CE attack (resistance fight) |
| **78,000** | **906,560** | 235,820 | +269,960 / −8,460 | 🔒 Call wall — resistance 1 |
| **77,500** | 645,140 | 287,980 | (+~300k CE area) | 🔒 resistance 2 |
| **76,800** | 171,120 | **564,880** | +138,880 / +411,620 | 🛡️ fresh PE defense — support 1 |
| **76,900** | 178,040 | 496,440 | +147,860 / +294,920 | 🛡️ support 1b |
| **76,700** | 62,880 | 391,540 | +51,680 / +257,320 | 🛡️ support 2 |
| **75,000** | 7,800 | 843,900 | — | 🛡️ deep support wall |
| **78,500** | 589,380 | 46,520 | +302,860 / +880 | 🔒 resistance 3 (fresh build) |
| **80,000** | 739,360 | 21,680 | — | 🔒 far ceiling |

### OI reading (course lens: "where do the orders/stops sit")
- Price 76,957 sits in a **battle band: 76,800–77,500**, pivot 77,000.
- **Below price the PUT walls are thicker** (76,700–76,900 fresh PE adds ~960k) → downside to 76,800 is defended; below 76,700 → 76,000-75,000 wall territory.
- **Above price the CALL walls are massive and freshly built** (77,500 645k + 78,000 906k + 78,500 589k) → rallies will meet sellers; 78,000 is the hard ceiling for this week.
- **Battle at 77,000:** CE added +424k vs PE +295k — aggressive sellers pressing the pivot while deep PE defends. Expect chop around 77,000 until one side breaks.
- 📌 Course link: OI walls = the liquidity where stop-loss hunting happens (Round Number 77,000 + OI wall coincide — classic trap zone at the round number).

## BANKEX (BSE bank index) — monthly 24-Sep · underlying 65,198.96
- Support: **63,000** (PE 3,240) · 64,900 (PE 1,410 fresh) · Resistance: **66,000** (CE 5,040) · 65,500+ (CE 1,410 fresh)
- PCR 1.01 — neutral; bank-index OI says **range 63,000–66,000, mild upward space to 66,000** → supports the Bank Nifty constructive-but-cautious read.

## What this changes in today's plan
- **SENSEX:** my earlier chart read said "below 77,000 = weak" — OI refines it: **76,800–77,200 is a defended support band; shorts into 76,900 are trading WITH a thick PE wall against them.** High-probability long zone = 76,850–76,950 retest IF it holds; stops below 76,700 (under support-2). Targets: 77,200 → 77,500 (where CE build starts). Do NOT chase above 77,500 (call walls); 78,000 = week ceiling.
- **Bank Nifty / Nifty:** no NSE OI available from this cloud → chart-level plan stands (BNF 57,500–58,025 buy zone; NIFTY 24,000 floor / 24,128 resistance). For exact NSE OI, run the scraper below on your own PC.

## ⚠️ Note on NSE data (NIFTY / BANKNIFTY OC)
NSE's site + archives are blocked from this cloud/datacenter IP (Akamai). BSE (SENSEX/BANKEX) works. **To get NIFTY & BANKNIFTY option chains: run the included script on YOUR computer:**
- `scripts/nse-oc-fetch.py` — standard-library Python: visits nseindia.com homepage (captures session cookie) then fetches NIFTY, BANKNIFTY, SENSEX chains and saves JSON. Run: `python nse-oc-fetch.py` on your PC, then paste/save the JSONs into `raw/` and I'll analyze them with the same OI map.
- Or screenshot/paste the NSE option-chain tables; I'll read them directly.
