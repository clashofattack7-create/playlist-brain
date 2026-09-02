"""pull-market.py — the Playlist Brain's market-data pipeline (one command).

Pulls, in order:
  1. NSE OFFICIAL index closes   -> nsearchives.nseindia.com (WORKS from this PC, full list of NSE indices)
  2. Yahoo Finance quotes        -> 3 indices daily history (WORKS; ~15 min delayed)
  3. BSE derivatives bhavcopy    -> SENSEX/BANKEX option OI (uses last saved file; browser flow if missing)
  4. NSE option chain            -> BEST EFFORT only (Akamai-blocks this PC; report + alternatives)

Usage:  python scripts/pull-market.py          (run from playlist-brain/)
Output: raw/ files + printed MARKET STATE summary.
"""
import socket, urllib.request, urllib.error, http.cookiejar, json, time, os, csv, collections, datetime

# --- env ---
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
os.makedirs(RAW, exist_ok=True)

# --- IPv4 patch (this env has broken IPv6 routing) ---
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def get(url, extra=None, timeout=25):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if extra: h.update(extra)
    req = urllib.request.Request(url, headers=h)
    try:
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8", "replace")

def last_trading_days(n=6):
    out, d = [], datetime.date.today() - datetime.timedelta(days=1)
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d -= datetime.timedelta(days=1)
    return out

INDEX_NAMES = {"Nifty 50": "NIFTY", "Nifty Bank": "BANKNIFTY", "Nifty 500": "NIFTY500"}
YAHOO = {"NIFTY": "NSEI", "BANKNIFTY": "NSEBANK", "SENSEX": "BSESN"}

def main():
    print("=" * 62)
    print("PLAYLIST BRAIN MARKET PULL  -", datetime.datetime.now().strftime("%d-%b-%Y %H:%M"))
    print("=" * 62)

    state = {}
    days = last_trading_days()

    # ---------- 1) NSE official index closes ----------
    print("\n[1] NSE OFFICIAL INDEX CLOSES (nsearchives) ...")
    csvfile = None
    for d in days:
        ds = d.strftime("%d%m%Y")
        url = "https://nsearchives.nseindia.com/content/indices/ind_close_all_" + ds + ".csv"
        txt = get(url)
        if txt.strip().startswith("Index Name"):
            csvfile = os.path.join(RAW, "ind_close_all_" + ds + ".csv")
            with open(csvfile, "w", encoding="utf-8") as f:
                f.write(txt)
            rows = {}
            for r in csv.DictReader(txt.splitlines()):
                nm = r["Index Name"]
                if nm in INDEX_NAMES:
                    rows[INDEX_NAMES[nm]] = r
            for k in ("NIFTY", "BANKNIFTY"):
                if k in rows:
                    rr = rows[k]
                    print("  " + k + ": O=" + rr["Open Index Value"] + " H=" + rr["High Index Value"] +
                          " L=" + rr["Low Index Value"] + " C=" + rr["Closing Index Value"] +
                          " chg=" + rr["Change(%)"] + "% vol=" + rr["Volume"] + "  (" + d.strftime("%d-%b") + ")")
                    state[k] = {"date": d.isoformat(),
                                 "open": float(rr["Open Index Value"]), "high": float(rr["High Index Value"]),
                                 "low": float(rr["Low Index Value"]), "close": float(rr["Closing Index Value"]),
                                 "chg": float(rr["Change(%)"] or 0)}
            break
    if not csvfile:
        print("  !! no NSE index file found (check dates / host)")
    else:
        print("  saved: " + os.path.relpath(csvfile, HERE))

    # ---------- 2) Yahoo quotes ----------
    print("\n[2] YAHOO PRICES (3 indices) ...")
    for key, sym in YAHOO.items():
        url = "https://query1.finance.yahoo.com/v8/finance/chart/^" + sym + "?interval=1d&range=1mo"
        try:
            j = json.loads(get(url))
            m = j["chart"]["result"][0]["meta"]
            path = os.path.join(RAW, "yahoo-" + sym.lower() + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(j, f)
            print("  " + key + ": close=" + str(m["regularMarketPrice"]) + " chg%=" + str(m["regularMarketChangePercent"]))
            if key not in state:
                state[key] = {"date": "last", "close": m["regularMarketPrice"],
                              "high": m["regularMarketDayHigh"], "low": m["regularMarketDayLow"],
                              "chg": m["regularMarketChangePercent"]}
        except Exception as e:
            print("  " + key + ": ERR " + repr(e))

    # ---------- 3) BSE derivatives bhavcopy ----------
    print("\n[3] BSE DERIVATIVES BHAVCOPY (SENSEX/BANKEX OI) ...")
    files = sorted([f for f in os.listdir(RAW) if f.startswith("bse-fo-") and f.endswith(".csv")])
    if files:
        p = os.path.join(RAW, files[-1])
        print("  using existing: " + files[-1])
        rows = []
        with open(p, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r.get("TckrSymb") in ("SENSEX", "BANKEX") and r.get("StrkPric", "").strip():
                    rows.append(r)
        for sym in ("SENSEX", "BANKEX"):
            sub = [r for r in rows if r["TckrSymb"] == sym]
            if not sub:
                continue
            exps = sorted({r["XpryDt"] for r in sub})
            exp = exps[0] if exps else None
            d = collections.defaultdict(lambda: {"ce": 0, "pe": 0})
            und = None
            for r in sub:
                if r["XpryDt"] != exp:
                    continue
                und = r.get("UndrlygPric")
                s = float(r["StrkPric"]); oi = int(r.get("OpnIntrst") or 0)
                d[s]["ce" if r["OptnTp"] == "CE" else "pe"] += oi
            tot_ce = sum(v["ce"] for v in d.values()); tot_pe = sum(v["pe"] for v in d.values())
            pcr = tot_pe / tot_ce if tot_ce else 0
            print("  " + sym + " exp " + str(exp) + " und=" + str(und) + ": CE=" + format(tot_ce, ",") +
                  " PE=" + format(tot_pe, ",") + " PCR=" + format(pcr, ".2f"))
            top = sorted(d.items(), key=lambda kv: -(kv[1]["ce"] + kv[1]["pe"]))[:5]
            print("     walls: " + ", ".join(format(s, ",.0f") + "(CE" + format(v["ce"], ",") + "/PE" + format(v["pe"], ",") + ")" for s, v in top))
    else:
        print("  !! no BSE file yet - needs one browser/session fetch (or upload)")

    # ---------- 4) NSE option chain ----------
    print("\n[4] NSE OPTION CHAIN ...")
    try:
        home = get("https://www.nseindia.com/")
        print("  homepage: " + str(len(home)) + " bytes, cookies: " + str(len(jar)))
        ok = 0
        for sym in ("NIFTY", "BANKNIFTY"):
            data = get("https://www.nseindia.com/api/option-chain-indices?symbol=" + sym,
                       {"Referer": "https://www.nseindia.com/option-chain",
                        "Accept": "application/json, text/plain, */*"})
            p = os.path.join(RAW, "oc-" + sym + ".json")
            with open(p, "w", encoding="utf-8") as f:
                f.write(data)
            good = data.strip().startswith("{")
            print("  " + sym + ": " + ("OK" if good else "BLOCKED") + " (" + str(len(data)) + " bytes)")
            ok += good
            time.sleep(1.2)
        if ok == 0:
            print("  -> NSE blocks this PC (Akamai). Use one of:")
            print("     a) upload/screenshot the chain (drag-drop or @playlist-brain/inbox/)")
            print("     b) Fyers access token (validated flow ready)")
            print("     c) run scripts/nse-oc-fetch.py from a NON-blocked network")
    except Exception as e:
        print("  ERR " + repr(e))

    # ---------- summary ----------
    print("\n" + "=" * 62)
    print("MARKET STATE (last session)")
    for k in ("NIFTY", "BANKNIFTY", "SENSEX"):
        s = state.get(k, {})
        if s:
            print("  " + k.ljust(10) + " close=" + str(s["close"]).ljust(12) +
                  " range=" + str(s.get("low", "-")) + " - " + str(s.get("high", "-")) + "  chg=" + str(s.get("chg", "-")) + "%")
    print("=" * 62)
    print("done.")

if __name__ == "__main__":
    main()
