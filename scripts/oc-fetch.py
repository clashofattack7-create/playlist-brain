import socket, urllib.request, urllib.error, http.cookiejar, json, time, sys, re, os
# force IPv4 (environment has broken IPv6 routing)
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
try:
    home = get("https://www.nseindia.com/")
    log_home = len(home)
except Exception as e:
    log_home = "ERR %s" % e
path = "D:/dsh/DSH/playlist-brain/raw"
ok = 0
for sym in ["NIFTY", "BANKNIFTY", "SENSEX"]:
    data = get("https://www.nseindia.com/api/option-chain-indices?symbol=" + sym,
               {"Referer": "https://www.nseindia.com/option-chain", "Accept": "application/json, text/plain, */*"})
    txt = data.decode("utf-8", "replace")
    with open(os.path.join(path, "oc-%s.json" % sym), "w", encoding="utf-8") as f:
        f.write(txt)
    print("%s: %d bytes, starts: %s" % (sym, len(data), txt[:60].replace("\n", " ")))
    if txt.strip().startswith("{"): ok += 1
    time.sleep(1.2)
print("home bytes:", log_home)
print("json_ok:", ok, "of 3")