
import socket, urllib.request, re
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")

for url in [
  "https://www.cnbctv18.com/market/stock-market-live-updates-sensex-nifty-50-expiry-today-cas-nifty-bank-auto-sun-pharma-epl-happiest-minds-share-price-liveblog-19980939.htm/amp",
  "https://www.moneycontrol.com/news/business/markets/technical-view-nifty-reverses-fridays-gains-with-24-000-critical-for-further-direction-cas-lifts-bank-nifty-above-58-000-but-sustainability-remains-key-14019010.html",
]:
    try:
        html = get(url)
        txt = re.sub(r"<[^>]+>", " ", html)
        txt = re.sub(r"\s+", " ", txt)
        print("=== ", url[:80], " len=", len(html))
        # find expiry mentions
        for m in re.finditer(r".{160}(?:expiry|Expiy|weekly|Tuesday|Thursday).{160}", txt):
            s = m.group(0)
            print("  ...", s[:400])
        print()
    except Exception as e:
        print("ERR", url[:60], repr(e)[:150])
