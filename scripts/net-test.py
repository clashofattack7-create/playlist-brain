import urllib.request, socket, time, sys
out = []
def log(m): out.append(m)
t0 = time.time()
try:
    r = urllib.request.urlopen("https://example.com", timeout=10)
    log("example status: %s elapsed: %.2f" % (r.status, time.time()-t0))
except Exception as e:
    log("example error: %s %s elapsed: %.2f" % (type(e).__name__, e, time.time()-t0))
t0 = time.time()
try:
    req = urllib.request.Request("https://www.youtube.com/youtubei/v1/player", data=b"{}", method="POST", headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=15)
    log("yt post status: %s elapsed: %.2f" % (r.status, time.time()-t0))
except Exception as e:
    log("yt post error: %s %s elapsed: %.2f" % (type(e).__name__, e, time.time()-t0))
open(r"D:\dsh\DSH\playlist-brain\raw\net-test-out.txt", "w", encoding="utf-8").write("\n".join(out))
print("DONE")