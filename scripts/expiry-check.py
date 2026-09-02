
import socket, urllib.request, urllib.error, json, os, datetime, zipfile, io, csv
RAW = r"D:\dsh\DSH\playlist-brain\raw"
_orig = socket.getaddrinfo
def _patched(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig(host, port, family, type, proto, flags)
    return [r for r in res if r[0] != socket.AF_INET6]
socket.getaddrinfo = _patched
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read()

# 1) try nsearchives FO bhavcopy (the host that worked for ind_close)
url = "https://nsearchives.nseindia.com/content/fo/fo_31082026.zip"
try:
    data = get(url)
    print("fo_31082026.zip via nsearchives:", len(data), "bytes, magic:", data[:4])
    if data[:4] == b"PK\x03\x04":
        open(os.path.join(RAW, "fo-31AUG2026-ns.zip"), "wb").write(data)
        z = zipfile.ZipFile(io.BytesIO(data))
        csvname = z.namelist()[0]
        txt = z.read(csvname).decode("utf-8", "replace")
        rd = csv.DictReader(io.StringIO(txt))
        print("  csv:", csvname, "cols:", list(rd.fieldnames)[:8])
        exps = {}
        for r_ in rd:
            s = str(r_.get("SYMBOL", ""))
            if s in ("NIFTY", "BANKNIFTY") and str(r_.get("OPTION_TYP", "")).strip() in ("CE", "PE"):
                exps.setdefault(s, set()).add(str(r_.get("EXPIRY_DT", "")).strip())
        for k, v in exps.items():
            print("  ", k, "expiries:", sorted(v)[:12])
    else:
        txt = data.decode("utf-8", "replace")
        print("  BLOCKED (html):", txt[:200].replace("\n", " "))
except Exception as e:
    print("ERR", repr(e))
