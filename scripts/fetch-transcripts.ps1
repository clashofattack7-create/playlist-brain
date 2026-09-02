param([string]$ListTsv, [string]$OutDir, [int]$Max = 0)
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
$rows = @(Get-Content -Raw $ListTsv -Encoding UTF8 | ForEach-Object { $_ -split "`r?`n" } | Where-Object { $_ -match "\S" })
$ok = 0; $noCap = 0; $fail = 0; $done = 0
foreach ($row in $rows) {
  if ($Max -gt 0 -and $done -ge $Max) { break }
  $f = $row -split "`t"
  if ($f.Count -lt 2) { continue }
  $vid = $f[1]
  $dest = Join-Path $OutDir ($vid + ".txt")
  if (Test-Path $dest) { $ok++; $done++; continue }
  $tmpHtml = Join-Path $env:TEMP ("w-" + [guid]::NewGuid().ToString("N") + ".html")
  $cookie = Join-Path $env:TEMP ("ck-" + [guid]::NewGuid().ToString("N") + ".txt")
  $url = "https://www.youtube.com/watch?v=" + $vid
  & curl.exe -4 -s -L --max-time 45 -A $ua -c $cookie -o $tmpHtml $url 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $tmpHtml)) { "FAIL curl $vid"; Remove-Item $tmpHtml,$cookie -ErrorAction SilentlyContinue; $fail++; $done++; continue }
  $html = Get-Content -Raw $tmpHtml -Encoding UTF8
  Remove-Item $tmpHtml,$cookie -ErrorAction SilentlyContinue
  $m = [regex]::Match($html, '"captionTracks":(\[.*?\])', [System.Text.RegularExpressions.RegexOptions]::Singleline)
  if (-not $m.Success) { "NO CAP $vid :: " + $f[2]; $noCap++; $done++; continue }
  $tracks = $m.Groups[1].Value | ConvertFrom-Json
  $t = $tracks | Where-Object { $_.languageCode -eq "en" } | Select-Object -First 1
  if ($null -eq $t) { $t = $tracks | Where-Object { $_.kind -ne "asr" } | Select-Object -First 1 }
  if ($null -eq $t) { $t = $tracks[0] }
  $base = ([string]$t.baseUrl) -replace "\\u0026", "&"
  $base = $base -replace "&fmt=[a-z0-9]+", ""
  if ($base -match "\?") { $url2 = $base + "&fmt=json3" } else { $url2 = $base + "?fmt=json3" }
  $tmpJ = Join-Path $env:TEMP ("j-" + [guid]::NewGuid().ToString("N") + ".json")
  & curl.exe -4 -s -L --max-time 60 -A $ua -o $tmpJ $url2 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $tmpJ)) { "FAIL transcript $vid"; Remove-Item $tmpJ -ErrorAction SilentlyContinue; $fail++; $done++; continue }
  $pr = Get-Content -Raw $tmpJ -Encoding UTF8 | ConvertFrom-Json
  Remove-Item $tmpJ -ErrorAction SilentlyContinue
  $sb = New-Object System.Text.StringBuilder
  if ($pr.events) {
    foreach ($e in $pr.events) {
      if ($null -ne $e.segs -and $null -ne $e.tStartMs) {
        $txt = ($e.segs | ForEach-Object { $_.text }) -join ""
        $txt = ($txt -replace "\s+", " ").Trim()
        if ($txt -ne "") {
          $ms = [long]$e.tStartMs
          $mm = [math]::Floor($ms / 60000); $ss = [math]::Floor(($ms % 60000) / 1000)
          $ts = "{0:00}:{1:00}" -f $mm, $ss
          [void]$sb.AppendLine("[" + $ts + "] " + $txt)
        }
      }
    }
  }
  if ($sb.Length -gt 0) {
    [System.IO.File]::WriteAllText($dest, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))
    $ok++
    "OK $vid len=" + $sb.Length
  } else {
    "EMPTY $vid"; $noCap++
  }
  $done++
  Start-Sleep -Milliseconds 300
}
"DONE ok=$ok nocap=$noCap fail=$fail processed=$done"