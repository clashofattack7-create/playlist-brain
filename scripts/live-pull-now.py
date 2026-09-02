# -*- coding: utf-8 -*-
"""live-pull-now.py — fresh intraday pull (Yahoo) + expiry determination."""
import socket, urllib.request, urllib.error, json, csv, zipfile, io, datetime, os, urllib.parse

_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")

print("=" * 66)
print("LIVE PULL -", datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S IST"))
print("=" * 66)

SYMS = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "SENSEX": "^BSESN"}

# --- 1) intraday today (5m) + meta ---
for name, sym in SYMS.items():
    try:
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(sym) +
               "?interval=5m&range=1d&includePrePost=true")
        txt = get(url)
        data = json.loads(txt)["chart"]["result"][0]
        meta = data["meta"]
        ts = data["timestamp"]
        q = data["indicators"]["quote"][0]
        rows = []
        for i in range(len(ts)):
            c = q["close"][i]
            if c is None: continue
            rows.append((ts[i], q["open"][i], q["high"][i], q["low"][i], c, q["volume"][i]))
        print("\n---", name, "(live via Yahoo, ~15-min delay) ---")
        print("regTZ:", meta.get("exchangeTimezoneName"), "| last close bar:", meta.get("chartPreviousClose"))
        print("prevClose:", meta.get("previousClose"), "| current:", meta.get("regularMarketPrice"),
              "| latest ts:", datetime.datetime.fromtimestamp(ts[-1]).strftime("%H:%M"))
        print("first bar:", datetime.datetime.fromtimestamp(rows[0][0]).strftime("%H:%M"),
              "open", round(rows[0][1], 2))
        hi = max(r[2] for r in rows); lo = min(r[3] for r in rows)
        print("day H:", round(hi, 2), "day L:", round(lo, 2))
        for r in rows:
            t = datetime.datetime.fromtimestamp(r[0]).strftime("%H:%M")
            if t in ("09:15","09:20","09:30","09:45","10:00","10:15","10:30","11:00","11:15","11:30","11:45","12:00","12:30","13:00","13:15","13:30","13:45","14:00","14:05") or i == len(rows)-1:
                print(f"  {t} O{r[1]:.1f} H{r[2]:.1f} L{r[3]:.1f} C{r[4]:.1f}")
        with open(os.path.join(RAW, "live3-" + name + ".json"), "w", encoding="utf-8") as f:
            json.dump({"symbol": sym, "meta": meta, "rows": [{"t": datetime.datetime.fromtimestamp(r[0]).strftime("%H:%M"), "o": r[1], "h": r[2], "l": r[3], "c": r[4], "v": r[5]} for r in rows]}, f)
    except Exception as e:
        print(name, "ERROR:", e)

# --- 2) expiry: NSE FO bhavcopy zip (fo-31AUG2026.zip) ---
print("\n--- NSE FO bhavcopy 31-Aug: weekly expiry dates ---")
try:
    with zipfile.ZipFile(os.path.join(RAW, "fo-31AUG2026.zip")) as z:
        for nm in z.namelist():
            if nm.endswith(".csv"):
                data = z.read(nm).decode("utf-8", "replace").replace("\r", "")
                rd = csv.DictReader(io.StringIO(data))
                cols = rd.fieldnames
                exp_col = [c for c in cols if "EXPIRY" in c.upper()][0] if cols else None
                sym_col = [c for c in cols if "SYMBOL" in c.upper()][0] if cols else None
                inst_col = [c for c in cols if "INSTRUMENT" in c.upper()][0] if cols else None
                print("file:", nm, "| cols:", [c for c in cols if "EXPIRY" in c.upper() or c == "SYMBOL"])
                seen = {}
                for r in rd:
                    sym = r.get(sym_col or "", "")
                    if sym in ("NIFTY", "BANKNIFTY", "NIFTYBANK"):
                        exp = r.get(exp_col or "", "")
                        seen.setdefault(sym, set()).add(exp)
                for s, es in seen.items():
                    print(s, "expiries:", sorted(es))
                break
except Exception as e:
    print("zip ERROR:", e)

# --- 3) BSE FO bhavcopy csv (31-Aug): weekly expiry ---
print("\n--- BSE FO bhavcopy 31-Aug: expiry rows ---")
try:
    with open(os.path.join(RAW, "bse-fo-20260831.csv"), encoding="utf-8", errors="replace") as f:
        rd = csv.DictReader(f)
        cols = rd.fieldnames
        print("cols:", cols)
        exps = {}
        for r in rd:
            e = r.get("Expiry Date") or r.get("EXPIRY DATE") or ""
            inst = r.get("Instrument") or r.get("INSTRUMENT") or ""
            exps.setdefault(e, 0)
            exps[e] += 1
        for e, c in sorted(exps.items()):
            print(" ", e, "->", c, "rows")
except Exception as e:
    print("csv ERROR:", e)
