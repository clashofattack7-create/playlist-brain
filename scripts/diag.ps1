$ErrorActionPreference = "Continue"
$t1 = Get-Content -Raw "D:\dsh\DSH\playlist-brain\raw\watch2.html" -Encoding UTF8
"html len=" + $t1.Length
"captionTracks: " + ([regex]::Matches($t1, "captionTracks").Count)
"timedtext: " + ([regex]::Matches($t1, "timedtext").Count)
"playerResp: " + ([regex]::Matches($t1, "ytInitialPlayerResponse").Count)
$m = [regex]::Match($t1, '"status":"([A-Z_]+)"')
if ($m.Success) { "STATUS=" + $m.Groups[1].Value }
$m2 = [regex]::Match($t1, '"videoDetails":{"videoId":"[^"]*","title":"([^"]*)"')
if ($m2.Success) { "TITLE=" + $m2.Groups[1].Value }
$m3 = [regex]::Match($t1, '"playerErrorMessageRenderer":{.{0,300}')
if ($m3.Success) { "ERR=" + $m3.Value.Substring(0, [Math]::Min(200, $m3.Value.Length)) }
"token:" + $t1.Contains("ytcfg")
"bot:" + $t1.Contains("Sign in to confirm")