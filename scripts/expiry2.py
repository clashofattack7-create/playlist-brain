
import socket, urllib.request, urllib.error, os, io, zipfile, csv, datetime
RAW = r"D:\dsh\DSH\playlist-brain\raw"
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout).read()

variants = [
    "https://nsearchives.nseindia.com/archives/fo/fo_31082026.zip",
    "https://nsearchives.nseindia.com/content/fo/fo_31AUG2026.zip",
    "https://nsearchives.nseindia.com/content/fo/fo_31082026.csv",
    "https://nsearchives.nseindia.com/content/fo/fo_20260831.zip",
    "https://nsearchives.nseindia.com/content/fo/fo_01SEP2026.zip",
    "https://nsearchives.nseindia.com/content/fo/Equity_Derivatives_31Aug2026.zip",
]
for u in variants:
    try:
        d = get(u)
        print("OK", u.split("/")[-1], len(d), "magic", d[:4])
        if d[:4] == b"PK\x03\x04":
            z = zipfile.ZipFile(io.BytesIO(d))
            nm = z.namelist()[0]
            txt = z.read(nm).decode("utf-8", "replace")
            rd = csv.DictReader(io.StringIO(txt))
            exps = {}
            for r_ in rd:
                s = str(r_.get("SYMBOL", ""))
                if s in ("NIFTY", "BANKNIFTY") and str(r_.get("OPTION_TYP", "")).strip() in ("CE", "PE"):
                    exps.setdefault(s, set()).add(str(r_.get("EXPIRY_DT", "")).strip())
            for k, v in exps.items():
                print("   ", k, "expiries:", sorted(v)[:12])
        break
    except Exception as e:
        print("ERR", u.split("/")[-1], repr(e)[:120])
