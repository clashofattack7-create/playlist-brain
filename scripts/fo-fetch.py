# -*- coding: utf-8 -*-
import socket, urllib.request, urllib.error, http.cookiejar, json, zipfile, io, csv, datetime
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def get(url, referer=None, timeout=30):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": "*/*"}
    if referer: h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        d = r.read()
        return d, r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.read(), e.code, dict(e.headers)

# A) warm up nseindia.com for cookies
try:
    d, s, hh = get("https://www.nseindia.com/")
    print("nseindia.com warmup:", s, len(d) if isinstance(d, (bytes, str)) else d)
except Exception as e:
    print("warmup err:", e)

url = "https://nsearchives.nseindia.com/content/fo/fo_31AUG2026.zip"
d, s, hh = get(url, referer="https://www.nseindia.com/")
print("fo zip fetch:", s, "len", len(d) if isinstance(d, (bytes,)) else len(d.encode()), "ctype", hh.get("Content-Type"))
if isinstance(d, bytes) and d[:2] == b"PK":
    with open("raw\\foE_31AUG2026.zip", "wb") as f: f.write(d)
    print("SAVED raw\\foE_31AUG2026.zip")
    z = zipfile.ZipFile(io.BytesIO(d))
    nm = z.namelist()[0]
    data = z.read(nm).decode("utf-8", "replace").replace("\r", "")
    rd = csv.DictReader(io.StringIO(data))
    print("cols:", rd.fieldnames)
    rows = list(rd)
    print("total rows:", len(rows))
    nifty = [r for r in rows if r.get("SYMBOL") in ("NIFTY",) and r.get("INSTRUMENT", "").startswith("OPT")]
    exps = {}
    for r in nifty:
        exps.setdefault(r.get("EXPIRY_DT", "?"), 0)
        exps[r.get("EXPIRY_DT", "?")] += 1
    print("NIFTY option expiry dates (count rows):")
    for e, c in sorted(exps.items()): print("  ", e, "->", c)
    bnf = [r for r in rows if r.get("SYMBOL") in ("BANKNIFTY", "NIFTYBANK") and r.get("INSTRUMENT", "").startswith("OPT")]
    exps2 = {}
    for r in bnf: exps2.setdefault(r.get("EXPIRY_DT", "?"), 0); exps2[r.get("EXPIRY_DT", "?")] += 1
    print("BANKNIFTY option expiry dates:")
    for e, c in sorted(exps2.items()): print("  ", e, "->", c)
else:
    print("first bytes:", d[:120] if isinstance(d, bytes) else str(d)[:120])
