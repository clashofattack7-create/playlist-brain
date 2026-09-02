# 📊 OPTION CHAIN / OI MAP — pulled 02-Sep-2026 01:49 IST (data as of 01-Sep close)
> Source: **Fyers official Trading API (options-chain-v3)** — real-time broker feed, via
> `option-chain-live` (token cached in `D:\dsh\DSH\option-chain-live\.fyers_credentials.json`).
> NSE blocks this PC directly (Akamai) — Fyers is now the NSE OC path. ✅ validated 02-Sep.

## ✅ Expiry verification (this is the data, not assumptions)
- **Fyers rejects 09-02-2026 for NIFTY (code 1)** → **today (Wed 02-Sep) is NOT an expiry**.
- NIFTY weekly expiry = **Tuesday**: next = **Tue 08-Sep-2026** (W) · then 15-Sep, 22-Sep (W) · monthly **29-Sep-2026** (M, last Tuesday).
- BANKNIFTY: **weekly contracts are GONE — monthly only** (29-Sep, 27-Oct, 23-Nov, 29-Dec…) → BNF expiry = **Tue 29-Sep-2026**.
- BSE (from bhavcopy 31-Aug): SENSEX weekly = **Thu 03-Sep-2026 (TOMORROW)** · BANKEX monthly = 24-Sep.
- ⚠️ The free `expiries` source (niftytrader) lists "09-02 / 09-03 / 09-04" — **stale/unreliable** (it also lists the already-expired 09-01). Trust Fyers.

## NIFTY — weekly chain, expiry Tue 08-Sep-2026 · spot 24,055.80 (01-Sep close)
**PCR 0.65 (call-heavy · 96.98M CE vs 63.19M PE OI) · max pain = 24,300**

| Strike | CE OI (wall) | PE OI (wall) | Read |
|---|---|---|---|
| **24,200** | **7,401,095** | 3,434,535 | 🔒 biggest CE wall — resistance 1 |
| **24,500** | **7,239,700** | 993,070 | 🔒 resistance 2 (fresh) |
| 24,100 | 6,453,915 | 3,499,990 | 🔒 resistance 1b |
| 24,300 | 5,062,655 | 1,483,105 | 🔒 (max pain zone) |
| 24,600 | 5,432,050 | 272,870 | 🔒 |
| 25,000 / 25,500 | 5,499,325 / 7,331,805 | 204,555 / 117,130 | 🔒 far ceiling cluster |
| **24,000** | 5,773,885 | **5,352,945** | ⚡ THE pivot — biggest PE wall + huge CE fight |
| **23,500** | 173,160 | **6,194,825** | 🛡️ biggest PE wall — support 1 |
| 23,600 | 169,975 | 4,844,840 | 🛡️ support 1b |
| 23,000 | 71,760 | 4,913,610 | 🛡️ support 2 |
| 23,900 / 23,800 | 1,367,470 / 566,410 | 3,349,060 / 3,025,360 | 🛡️ support 3 |

**OI reading (course lens: OI walls = the liquidity where stop-hunting happens):**
- Battle band **23,500–24,500**; the round 24,000 is the pivot (5.35M PE vs 5.77M CE — evenly contested).
- Below: thick PE defense 23,500–24,000 → downside defended; below 23,500 → 23,000 wall.
- Above: **massive CE walls 24,200/24,500 (7.2–7.4M)** → this week's upside meets real sellers there; max pain 24,300 pulls price up toward that zone.

## BANKNIFTY — monthly chain, expiry Tue 29-Sep-2026 · spot 57,409.60 (01-Sep close) · fut 57,566.20
**PCR 1.05 (10.08M PE vs 9.64M CE) · max pain ~57,500–57,600**

| Strike | CE OI (wall) | PE OI (wall) | Read |
|---|---|---|---|
| **58,000** | **1,360,110** | 974,010 | 🔒 THE call wall of the whole chain — hard ceiling |
| 59,000 | 830,040 | 293,970 | 🔒 resistance 2 |
| 60,000 | 901,800 | 348,570 | 🔒 far ceiling |
| 57,400 | 189,330 | 327,600 | 🛡️ PE defends at spot level |
| 57,600 | 227,280 | 146,190 | ⚡ max pain — CE/PE meet |
| **57,000** | 278,970 | **838,170** | 🛡️ biggest PE wall — support 1 |
| 56,000 | 63,720 | 702,930 | 🛡️ support 2 |
| 55,000 | 63,840 | 704,370 | 🛡️ deep support |

**OI reading:** BNF sits in the **57,000–58,000 auction band** with max pain *above* spot (57,500–57,600) → OI gravity is mildly up; **58,000 CE wall = the week's ceiling**; 57,000 PE wall = floor. Futures premium +157 (futures buyers paying up).

## SENSEX — weekly expiry Thu 03-Sep-2026 (**TOMORROW**) · from BSE bhavcopy 31-Aug · spot 76,957.27→76,944.28
**PCR 1.09 (12.80M PE vs 11.70M CE)**
- Pivot **77,000**: CE 643,920 (aggressively added +424,580 Mon) vs **PE 959,780** (+295,200) — big PE wall.
- Supports: 76,900 (PE 496,440) · 76,800 (PE 564,880) · 76,700 (PE 391,540) · 75,000 (PE 843,900).
- Resistances: 77,500 (CE 645,140) · 78,000 (CE 906,560) · 78,500 (CE 589,380).
- **Read:** expiry-eve tomorrow — price 76,944 sits just under the 77,000 pivot; PE walls below mean the 76,800–77,000 zone is defended; CE walls above (77,500+) cap rallies. Expect **chop/pin around 77,000** into tomorrow's expiry; 78,000 = week ceiling.

## How to re-pull (save for next time)
```powershell
# NIFTY weekly (Tue 08-Sep) chain — full 61-strike, IV + Greeks
python -m option_chain_live fyers-chain "NSE:NIFTY50-INDEX" --strike-count 30 --json
# BANKNIFTY monthly (29-Sep) chain
python -m option_chain_live fyers-chain "NSE:BANKNIFTY-INDEX" --strike-count 30 --json
# token: D:\dsh\DSH\option-chain-live\.fyers_credentials.json  (refresh: fyers-refresh --pin XXXX)
```
- Pre-open pulls return **last session's close** OI (market closed) — still the right input for the pre-open plan.
- NSE weekly expiry = **Tuesday** (NIFTY only — BNF weekly discontinued); monthly = **last Tuesday** (29-Sep).
- BSE weekly = **Thursday** (SENSEX, 03-Sep); BSE monthly = last Thursday (24-Sep BANKEX).
