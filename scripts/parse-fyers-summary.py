# -*- coding: utf-8 -*-
"""parse-fyers-summary.py — print a compact OI/expiry summary from a saved FYERS chain JSON.

Usage:  python scripts/parse-fyers-summary.py raw/fyers-chain-nifty-2026-09-02.json
Notes: FYERS options-chain-v3 gives a flat `optionsChain` list: one row per CE/PE contract
       with keys: symbol / option_type ("CE"|"PE") / strike_price / oi / prev_oi / ltp / greeks.
"""
import json, sys

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8-sig") as f:
        txt = f.read()
    i = txt.find("{")
    if i > 0:
        txt = txt[i:]
    d = json.loads(txt)
    data = d.get("data", d)

    print("== channel fields ==")
    for k in ("callOi", "putOi"):
        if k in data:
            print("  %s = %s" % (k, format(data[k], ",")))
    exps = data.get("expiryData") or []
    print("  expiryData:", [(e.get("date"), e.get("expiry_flag")) for e in exps][:8])

    rows = data.get("optionsChain") or []
    und = None
    contracts = []
    for r in rows:
        if r.get("option_type") == "":
            und = r
            continue
        try:
            contracts.append({
                "strike": float(r["strike_price"]),
                "type": r["option_type"],
                "oi": int(r.get("oi") or 0),
                "prev_oi": int(r.get("prev_oi") or 0),
                "ltp": float(r.get("ltp") or 0),
            })
        except Exception:
            pass

    if und:
        print("== underlying ==")
        print("  %s ltp=%s fp=%s fpch=%s/%s%%" % (und.get("symbol"), und.get("ltp"), und.get("fp"),
                                                  und.get("fpch"), und.get("fpchp")))

    if not contracts:
        print("  !! no contracts parsed")
        return

    by = {}
    for c in contracts:
        s = c["strike"]
        b = by.setdefault(s, {"ce": 0, "pe": 0})
        if c["type"].upper() == "CE":
            b["ce"] += c["oi"]
        else:
            b["pe"] += c["oi"]

    tot_ce = sum(b["ce"] for b in by.values())
    tot_pe = sum(b["pe"] for b in by.values())
    print("== window totals (strikes=%d) ==" % len(by))
    print("  CE=%s  PE=%s  PCR=%.2f" % (format(tot_ce, ","), format(tot_pe, ","), tot_pe / tot_ce if tot_ce else 0))

    top_ce = sorted(by.items(), key=lambda kv: -kv[1]["ce"])[:8]
    top_pe = sorted(by.items(), key=lambda kv: -kv[1]["pe"])[:8]
    print("TOP CE:", ", ".join("%s(%.2fM)" % (format(s, ",.0f"), v["ce"] / 1e6) for s, v in top_ce))
    print("TOP PE:", ", ".join("%s(%.2fM)" % (format(s, ",.0f"), v["pe"] / 1e6) for s, v in top_pe))

    # OI change (vs prev_oi) summed per strike — who ADDED yesterday
    chg = {}
    for c in contracts:
        s = c["strike"]
        b = chg.setdefault(s, {"ce": 0, "pe": 0})
        diff = c["oi"] - c["prev_oi"]
        if c["type"].upper() == "CE":
            b["ce"] += diff
        else:
            b["pe"] += diff
    top_add_ce = sorted(chg.items(), key=lambda kv: -kv[1]["ce"])[:5]
    top_add_pe = sorted(chg.items(), key=lambda kv: kv[1]["pe"])[:5]
    print("CE ADDED MOST:", ", ".join("%s(%.2fM)" % (format(s, ",.0f"), v["ce"] / 1e6) for s, v in top_add_ce))
    print("PE ADDED MOST:", ", ".join("%s(%.2fM)" % (format(s, ",.0f"), -v["pe"] / 1e6) for s, v in top_add_pe))

if __name__ == "__main__":
    main()
