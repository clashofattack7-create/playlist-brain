# -*- coding: utf-8 -*-
import socket, urllib.request, urllib.error, json, datetime, time, urllib.parse
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
print("PULLED", datetime.datetime.now().strftime("%H:%M:%S"))
for attempt in range(3):
    try:
        data = json.loads(get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEBANK?interval=5m&range=1d&includePrePost=true"))["chart"]["result"][0]
        ts = data["timestamp"]; q = data["indicators"]["quote"][0]
        rows = [(datetime.datetime.fromtimestamp(ts[i]).strftime("%H:%M"), q["open"][i], q["high"][i], q["low"][i], q["close"][i]) for i in range(len(ts)) if q["close"][i] is not None]
        print("BANKNIFTY: last=%.1f at %s  dayH=%.1f  dayL=%.1f  open=%.1f" % (rows[-1][4], rows[-1][0], max(r[2] for r in rows), min(r[3] for r in rows), rows[0][1]))
        for r in rows[-4:]:
            print("   ", r[0], "O%.1f H%.1f L%.1f C%.1f" % (r[1], r[2], r[3], r[4]))
        break
    except Exception as e:
        print("retry", attempt, e); time.sleep(3)
