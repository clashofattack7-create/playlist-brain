param([string]$Dir)
$ErrorActionPreference = "Continue"
$files = Get-ChildItem -Path $Dir -Filter *.json3 -ErrorAction SilentlyContinue
$n = 0; $skipped = 0; $failed = 0
foreach ($f in $files) {
  $txt = Join-Path $Dir ($f.BaseName + ".txt")
  if (Test-Path $txt) { $skipped++; continue }
  try {
    $pr = Get-Content -Raw $f.FullName -Encoding UTF8 | ConvertFrom-Json
    $sb = New-Object System.Text.StringBuilder
    if ($pr.events) {
      foreach ($e in $pr.events) {
        if ($null -ne $e.segs -and $null -ne $e.tStartMs) {
          $t = ($e.segs | ForEach-Object { if ($null -ne $_.utf8) { $_.utf8 } else { $_.text } }) -join ""
          $t = ($t -replace "\s+", " ").Trim()
          if ($t -ne "") {
            $ms = [long]$e.tStartMs
            $hh = [math]::Floor($ms / 3600000); $mm = [math]::Floor(($ms % 3600000) / 60000); $ss = [math]::Floor(($ms % 60000) / 1000)
            $ts = "{0:00}:{1:00}:{2:00}" -f $hh, $mm, $ss
            [void]$sb.AppendLine("[" + $ts + "] " + $t)
          }
        }
      }
    }
    if ($sb.Length -gt 0) { [System.IO.File]::WriteAllText($txt, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false))); $n++ }
    else { "EMPTY " + $f.BaseName; $failed++ }
  } catch { "FAIL " + $f.BaseName + " :: " + $_.Exception.Message; $failed++ }
}
"CONVERTED new=$n skipped=$skipped failed=$failed total=" + $files.Count