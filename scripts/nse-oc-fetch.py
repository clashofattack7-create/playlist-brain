"""NSE option-chain fetcher (for use on YOUR machine / residential IP).
NSE blocks cloud IPs; run this at home with normal internet.
Saves raw/NSE-NIFTY.json, raw/NSE-BANKNIFTY.json, raw/NSE-SENSEX.json
Usage:  python nse-oc-fetch.py
Personal research use only; respect NSE rate limits (~10 req/min)."""
import socket, urllib.request, urllib.error, http.cookiejar, time, os as _os
# force IPv4 if needed
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def get(url, extra=None, timeout=25):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if extra: h.update(extra)
    req = urllib.request.Request(url, headers=h)
    try:
        return urllib.request.urlopen(req, timeout=timeout).read()
    except urllib.error.HTTPError as e:
        return e.read()
out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "raw")
_os.makedirs(out, exist_ok=True)
print("step 1: session handshake with nseindia.com ...")
home = get("https://www.nseindia.com/")
print("  homepage bytes:", len(home), " cookies:", len(jar))
for sym in ["NIFTY", "BANKNIFTY", "SENSEX"]:
    data = get("https://www.nseindia.com/api/option-chain-indices?symbol=" + sym,
               {"Referer": "https://www.nseindia.com/option-chain", "Accept": "application/json, text/plain, */*"})
    txt = data.decode("utf-8", "replace")
    ok = txt.strip().startswith("{")
    path = _os.path.join(out, "NSE-" + sym + ".json")
    with open(path, "w", encoding="utf-8") as f: f.write(txt)
    print("%s -> %s (%d bytes%s)" % (sym, path, len(data), " OK" if ok else " FAILED - check network/IP"))
    time.sleep(1.5)
print("done. Now send me the saved JSON files and I will read the OI map.")