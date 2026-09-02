
import os, csv, json, datetime
RAW = r"D:\dsh\DSH\playlist-brain\raw"

print("=== 1) NSE ind_close_all_31082026.csv ===")
p = os.path.join(RAW, "ind_close_all_31082026.csv")
with open(p, encoding="utf-8-sig") as f:
    rd = csv.DictReader(f)
    cols = rd.fieldnames
    print("  cols:", cols)
    for r_ in rd:
        if r_["Index Name"] in ("Nifty 50", "Nifty Bank"):
            print("  ", {k: r_[k] for k in cols})

print()
print("=== 2) yahoo-nsei.json daily closes (last 10) ===")
j = json.load(open(os.path.join(RAW, "yahoo-nsei.json"), encoding="utf-8"))
res = j["chart"]["result"][0]
m = res["meta"]
print("  meta last=", m.get("regularMarketPrice"), "metaPrev=", m.get("chartPreviousClose"), "range=", m.get("range"))
ts = res.get("timestamp", []); q = res["indicators"]["quote"][0]
for i in range(max(0, len(ts) - 10), len(ts)):
    d = datetime.datetime.utcfromtimestamp(ts[i]).strftime("%Y-%m-%d")
    print("  ", d, "O=%s H=%s L=%s C=%s" % (q["open"][i], q["high"][i], q["low"][i], q["close"][i]))

print()
print("=== 3) yahoo-nsebank/bsesn last 6 ===")
for nm in ("yahoo-nsebank.json", "yahoo-bsesn.json"):
    j = json.load(open(os.path.join(RAW, nm), encoding="utf-8"))
    res = j["chart"]["result"][0]
    m = res["meta"]
    print(" ", nm, "last=", m.get("regularMarketPrice"), "metaPrev=", m.get("chartPreviousClose"))
    ts = res.get("timestamp", []); q = res["indicators"]["quote"][0]
    for i in range(max(0, len(ts) - 6), len(ts)):
        d = datetime.datetime.utcfromtimestamp(ts[i]).strftime("%Y-%m-%d")
        print("    ", d, "C=%s" % (q["close"][i]))

print()
print("=== 4) live-NIFTY.json (04:45) meta ===")
try:
    j = json.load(open(os.path.join(RAW, "live-NIFTY.json"), encoding="utf-8"))
    res = j["chart"]["result"][0]
    m = res["meta"]
    print("  ", {k: m.get(k) for k in ("regularMarketPrice", "chartPreviousClose", "regularMarketDayHigh", "regularMarketDayLow")})
except Exception as e:
    print("  ERR", e)

print()
print("=== 5) fo-31AUG2026.zip header ===")
with open(os.path.join(RAW, "fo-31AUG2026.zip"), "rb") as f:
    print("  ", f.read(80))

print()
print("=== 6) BSE bhavcopy expiry ===")
csvs = sorted([f for f in os.listdir(RAW) if f.startswith("bse-fo-") and f.endswith(".csv")])
print("  files:", csvs)
if csvs:
    with open(os.path.join(RAW, csvs[-1]), encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print("  cols:", list(rows[0].keys())[:10])
    for sym in ("SENSEX", "BANKEX"):
        exps = sorted({str(r_["XpryDt"]) for r_ in rows if r_["TckrSymb"] == sym and str(r_["StrkPric"]).strip() and str(r_["XpryDt"]).strip()})
        und = [r_["UndrlygPric"] for r_ in rows if r_["TckrSymb"] == sym and str(r_["StrkPric"]).strip()]
        print("  ", sym, "expiries:", exps[:10], " underlyings:", und[:3])
