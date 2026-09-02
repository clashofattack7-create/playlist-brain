# cdp-capture.ps1 - navigate a CDP browser target and capture network responses matching a pattern
# Usage: powershell -File cdp-capture.ps1 -WsUrl 'ws://...' -Url 'https://www.niftytrader.in/' -Pattern 'option|chain|nifty' -OutDir 'D:\dsh\DSH\playlist-brain\raw\captures' -WaitMs 15000
param(
  [Parameter(Mandatory=$true)][string]$WsUrl,
  [Parameter(Mandatory=$true)][string]$Url,
  [string]$Pattern = 'option|chain|nifty|banknifty|oi|quote',
  [string]$OutDir = '',
  [int]$WaitMs = 15000
)
$ErrorActionPreference = 'Stop'
if ($OutDir -eq '') { $OutDir = Join-Path $env:TEMP ('cdp-capture-' + [DateTime]::Now.ToString('HHmmss')) }
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$ws = New-Object System.Net.WebSockets.ClientWebSocket
try {
  $ws.ConnectAsync([Uri]$WsUrl, [Threading.CancellationToken]::None).Wait()
  $buf = New-Object byte[] 8388608
  $interesting = @()

  function Send-Cmd([int]$id, [string]$method, $params) {
    $payload = @{ id = $id; method = $method; params = $params } | ConvertTo-Json -Depth 10 -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($payload)
    $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  }
  function Recv-Message {
    $sb = New-Object System.Text.StringBuilder
    do {
      $seg = [ArraySegment[byte]]::new($buf)
      $recv = $ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result
      if ($recv.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { return $null }
      [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $recv.Count))
    } while (-not $recv.EndOfMessage)
    return $sb.ToString()
  }
  function Wait-For([int]$id, [int]$timeoutSec = 30) {
    $deadline = [DateTime]::Now.AddSeconds($timeoutSec)
    while ([DateTime]::Now -lt $deadline) {
      $txt = Recv-Message
      if ($null -eq $txt) { return $null }
      $obj = $txt | ConvertFrom-Json -ErrorAction SilentlyContinue
      if ($null -eq $obj) { continue }
      if ($obj.method -eq 'Network.responseReceived') {
        $u = $obj.params.response.url
        if ($u -match $Pattern -and $obj.params.response.status -eq 200) {
          $interesting += [PSCustomObject]@{ req = $obj.params.requestId; url = $u; mime = $obj.params.response.mimeType }
          Write-Output ('[resp] ' + $u.Substring(0, [Math]::Min(160, $u.Length)))
        }
      }
      if ($obj.id -eq $id) { return $obj }
    }
    return $null
  }

  Send-Cmd 1 'Network.enable' @{} | Out-Null
  [void](Wait-For 1 10)
  Send-Cmd 2 'Page.enable' @{} | Out-Null
  [void](Wait-For 2 10)

  Write-Output ('--- navigating: ' + $Url)
  Send-Cmd 3 'Page.navigate' @{ url = $Url } | Out-Null
  [void](Wait-For 3 20)

  $deadline = [DateTime]::Now.AddMilliseconds($WaitMs)
  while ([DateTime]::Now -lt $deadline) {
    $txt = Recv-Message
    if ($null -eq $txt) { break }
    $obj = $txt | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($null -eq $obj) { continue }
    if ($obj.method -eq 'Network.responseReceived') {
      $u = $obj.params.response.url
      if ($u -match $Pattern -and $obj.params.response.status -eq 200) {
        $interesting += [PSCustomObject]@{ req = $obj.params.requestId; url = $u; mime = $obj.params.response.mimeType }
        Write-Output ('[resp] ' + $u.Substring(0, [Math]::Min(160, $u.Length)))
      }
    }
  }

  Write-Output ('--- capturing ' + $interesting.Count + ' responses ---')
  $idx = 0
  foreach ($it in $interesting) {
    $idx++
    $mimeOk = $it.mime -match 'json|text|javascript'
    $urlOk = $it.url -match '\\.json'
    if (-not ($mimeOk -or $urlOk)) { continue }
    Send-Cmd (100 + $idx) 'Network.getResponseBody' @{ requestId = $it.req } | Out-Null
    $resp = Wait-For (100 + $idx) 20
    if ($resp -and $resp.result -and $resp.result.body) {
      $nameOrig = $it.url -replace 'https?://[^/]+/', '' -replace '[^A-Za-z0-9._-]', '_'
      if ($nameOrig.Length -gt 80) { $nameOrig = $nameOrig.Substring(0, 80) }
      $name = ('cap-{0:D2}-{1}' -f $idx, $nameOrig)
      $path = Join-Path $OutDir $name
      [System.IO.File]::WriteAllText($path, $resp.result.body, [System.Text.Encoding]::UTF8)
      Write-Output ('[saved] ' + $name + '  (' + $resp.result.body.Length + ' bytes)')
    }
  }
  Write-Output ('--- done. outputs in: ' + $OutDir)
} catch {
  Write-Output ('CAPTURE-ERR: ' + $_.Exception.Message)
} finally {
  try { $ws.Dispose() } catch {}
}