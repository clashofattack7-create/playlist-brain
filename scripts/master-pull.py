
"""master-pull.py — live intraday fetch + expiry determination for the Playlist Brain."""
import socket, urllib.request, urllib.error, json, time, os, datetime, zipfile, csv, io

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")

_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")

def fetch_chart(sym, interval, range_):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^" + sym + "?interval=" + interval + "&range=" + range_ + "&includePrePost=false"
    return json.loads(get(url))

def ist(ts):
    return datetime.datetime.utcfromtimestamp(ts + 19800).strftime("%H:%M")

print("=" * 70)
print("LIVE PULL", datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S"), "IST (system clock)")
print("=" * 70)

for key, sym in [("NIFTY", "NSEI"), ("BANKNIFTY", "NSEBANK"), ("SENSEX", "BSESN")]:
    try:
        j = fetch_chart(sym, "5m", "1d")
        res = j["chart"]["result"][0]
        m = res["meta"]
        ts = res["timestamp"]; q = res["indicators"]["quote"][0]
        o, h, l, c, v = q["open"], q["high"], q["low"], q["close"], q["volume"]
        # save
        path = os.path.join(RAW, "live2-" + key + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(j, f)
        # 15-min aggregation from 5m bars
        rows = []
        cur = None
        for i in range(len(ts)):
            if o[i] is None or c[i] is None:
                continue
            t = ts[i]
            minute = datetime.datetime.utcfromtimestamp(t + 19800).minute
            slot = minute // 15
            if cur is None or slot != cur[0]:
                if cur:
                    rows.append(cur)
                cur = [slot, o[i], h[i], l[i], c[i], v[i] or 0]
            else:
                cur[2] = max(cur[2], h[i]); cur[3] = min(cur[3], l[i]); cur[4] = c[i]; cur[5] += v[i] or 0
        if cur:
            rows.append(cur)
        print()
        print("### " + key + " (^" + sym + ")")
        print("  prevClose=%s  last=%s  chg%%=%.2f  dayHigh=%s  dayLow=%s  lastBar=%s" % (
            round(m.get("chartPreviousClose", 0), 2), round(m["regularMarketPrice"], 2),
            m["regularMarketChangePercent"], round(m["regularMarketDayHigh"], 2),
            round(m["regularMarketDayLow"], 2), ist(ts[-1]) if ts else "-"))
        for r_ in rows:
            tstr = ist(ts[rows.index(r_)] if False else 0)  # placeholder
        for row in rows:
            # reconstruct time from first ts of slot: approximate by slot
            print("   %s  O=%8.2f H=%8.2f L=%8.2f C=%8.2f  v=%s" % ("xx", row[1], row[2], row[3], row[4], format(row[5], ",")))
        # print full 5m tail (last 20 bars) with real times
        print("  -- last 20 5m bars --")
        n = len(ts)
        for i in range(max(0, n - 20), n):
            if o[i] is None:
                continue
            print("   %s O=%8.2f H=%8.2f L=%8.2f C=%8.2f v=%s" % (ist(ts[i]), round(o[i],2), round(h[i],2), round(l[i],2), round(c[i],2), format(v[i] or 0, ",")))
    except Exception as e:
        print(key, "ERR", repr(e))

# ---- expiry from NSE FO bhavcopy zip (latest) ----
print()
print("=== EXPIRY CHECK ===")
zips = sorted([f for f in os.listdir(RAW) if f.startswith("fo-") and f.endswith(".zip")])
print("FO zips found:", zips)
if zips:
    zp = os.path.join(RAW, zips[-1])
    with zipfile.ZipFile(zp) as z:
        names = z.namelist()
        txt = None
        for nm in names:
            if nm.endswith(".csv"):
                txt = z.read(nm).decode("utf-8", "replace")
                break
        if txt:
            rd = csv.DictReader(io.StringIO(txt))
            for target in ("NIFTY", "BANKNIFTY"):
                exps = set()
                for r_ in rd:
                    if r_.get("SYMBOL") == target and r_.get("OPTION_TYP") in ("CE", "PE") and r_.get("EXPIRY_DT", "").strip():
                        exps.add(r_["EXPIRY_DT"])
                    if len(exps) > 30:
                        break
                print("  " + target + " expiries in " + zips[-1] + ": " + ", ".join(sorted(exps)[:12]))
                rd = csv.DictReader(io.StringIO(txt))

# ---- BSE bhavcopy expiry ----
csvs = sorted([f for f in os.listdir(RAW) if f.startswith("bse-fo-") and f.endswith(".csv")])
if csvs:
    p = os.path.join(RAW, csvs[-1])
    with open(p, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        rows = list(rd)
    for sym in ("SENSEX", "BANKEX"):
        exps = sorted({r_["XpryDt"] for r_ in rows if r_["TckrSymb"] == sym and r_["StrkPric"].strip() and r_.get("XpryDt", "").strip()})
        print("  " + sym + " expiries in " + csvs[-1] + ": " + ", ".join(exps[:10]))
print("done.")
