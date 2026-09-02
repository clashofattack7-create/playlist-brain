import csv, collections
rows = []
with open(r"D:\dsh\DSH\playlist-brain\raw\bse-fo-20260831.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["TckrSymb"] in ("SENSEX", "BANKEX") and r["StrkPric"].strip():
            rows.append(r)
by = collections.defaultdict(collections.defaultdict)
for r in rows:
    key = (r["TckrSymb"], r["XpryDt"])
    s = float(r["StrkPric"])
    ce = int(r["OpnIntrst"]) if r["OptnTp"] == "CE" else 0
    pe = int(r["OpnIntrst"]) if r["OptnTp"] == "PE" else 0
    d = by[key]
    d[s] = {"ce": d.get(s, {}).get("ce", 0) + ce, "pe": d.get(s, {}).get("pe", 0) + pe}
for (sym, exp) in sorted(by):
    d = by[(sym, exp)]
    tot_ce = sum(v["ce"] for v in d.values())
    tot_pe = sum(v["pe"] for v in d.values())
    pcr = tot_pe / tot_ce if tot_ce else 0
    print("=== " + sym + "  expiry " + exp + " ===")
    print("  total CE OI=%d  PE OI=%d  PCR=%.2f  strikes=%d" % (tot_ce, tot_pe, pcr, len(d)))
    top = sorted(d.items(), key=lambda kv: -(kv[1]["ce"] + kv[1]["pe"]))[:7]
    for s, v in top:
        print("  strike %8.0f  CE=%6d  PE=%6d  total=%6d" % (s, v["ce"], v["pe"], v["ce"] + v["pe"]))