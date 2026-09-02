
import socket, urllib.request, urllib.error, json, os, datetime
RAW = r"D:\dsh\DSH\playlist-brain\raw"
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
def ist(ts):
    return datetime.datetime.utcfromtimestamp(ts + 19800).strftime("%H:%M")

PDC = {"NIFTY": 24080.40, "BANKNIFTY": 58024.95, "SENSEX": 76957.27}
print("PULL TIME:", datetime.datetime.now().strftime("%H:%M:%S"))
for key, sym in [("NIFTY", "NSEI"), ("BANKNIFTY", "NSEBANK"), ("SENSEX", "BSESN")]:
    j = json.loads(get("https://query1.finance.yahoo.com/v8/finance/chart/^" + sym + "?interval=5m&range=1d&includePrePost=false"))
    res = j["chart"]["result"][0]
    m = res["meta"]
    ts = res["timestamp"]; q = res["indicators"]["quote"][0]
    o, h, l, c = q["open"], q["high"], q["low"], q["close"]
    n = len(ts)
    # 15-min aggregation
    rows = []
    cur = None
    for i in range(n):
        if o[i] is None: continue
        slot = datetime.datetime.utcfromtimestamp(ts[i] + 19800).hour * 4 + datetime.datetime.utcfromtimestamp(ts[i] + 19800).minute // 15
        if cur is None or slot != cur[0]:
            if cur: rows.append(cur)
            cur = [slot, o[i], h[i], l[i], c[i]]
        else:
            cur[2] = max(cur[2], h[i]); cur[3] = min(cur[3], l[i]); cur[4] = c[i]
    if cur: rows.append(cur)
    sess_open = rows[0][1] if rows else None
    day_h = max(r[2] for r in rows); day_l = min(r[3] for r in rows)
    last = m["regularMarketPrice"]; lastbar = ist(ts[-1])
    print()
    print("### %s  last=%s (Y! lastbar %s)  sessO=%s  H=%s  L=%s  vsPDC=%+.2f (%.2f%%)" % (
        key, round(last,2), lastbar, round(sess_open,2) if sess_open else "-", round(day_h,2), round(day_l,2),
        last - PDC[key], (last - PDC[key]) / PDC[key] * 100))
    print("  15m rows (recent):")
    for r_ in rows[8:]:
        hh = r_[0] // 4; mm = (r_[0] % 4) * 15
        print("    %02d:%02d  O=%8.2f H=%8.2f L=%8.2f C=%8.2f" % (hh, mm, r_[1], r_[2], r_[3], r_[4]))
    # last 6 5m bars
    print("  last 6 5m:")
    for i in range(n - 6, n):
        if o[i] is None: continue
        print("    %s O=%8.2f H=%8.2f L=%8.2f C=%8.2f" % (ist(ts[i]), round(o[i],2), round(h[i],2), round(l[i],2), round(c[i],2)))
