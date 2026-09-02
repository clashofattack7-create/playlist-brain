import csv, collections
rows = []
with open(r"D:\dsh\DSH\playlist-brain\raw\bse-fo-20260831.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["TckrSymb"] in ("SENSEX", "BANKEX") and r["StrkPric"].strip():
            rows.append(r)
for sym in ("SENSEX", "BANKEX"):
    exp = "2026-09-03" if sym == "SENSEX" else "2026-09-24"
    d = collections.defaultdict(lambda: {"ce": 0, "pe": 0, "ceChg": 0, "peChg": 0})
    und = None
    for r in rows:
        if r["TckrSymb"] == sym and r["XpryDt"] == exp:
            s = float(r["StrkPric"]); und = r["UndrlygPric"]
            oi = int(r["OpnIntrst"] or 0); chg = int(r["ChngInOpnIntrst"] or 0)
            if r["OptnTp"] == "CE":
                d[s]["ce"] += oi; d[s]["ceChg"] += chg
            else:
                d[s]["pe"] += oi; d[s]["peChg"] += chg
    print("=== %s %s  underlying=%s ===" % (sym, exp, und))
    print("TOP OI CHANGE (additions = fresh positioning):")
    top = sorted(d.items(), key=lambda kv: -abs(kv[1]["ceChg"] + kv[1]["peChg"]))[:9]
    for s, v in top:
        print("  %8.0f  CEchg=%7d  PEchg=%7d   | CE=%6d  PE=%6d" % (s, v["ceChg"], v["peChg"], v["ce"], v["pe"]))