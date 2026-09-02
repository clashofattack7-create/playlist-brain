# cdp-helper.ps1 — send a series of CDP commands to a target and print responses
# Usage: powershell -File cdp-helper.ps1 -WsUrl 'ws://127.0.0.1:9222/devtools/page/XXXX' -CommandsJson '<json array>'
param(
  [Parameter(Mandatory=$true)][string]$WsUrl,
  [string]$CommandsJson = "",
  [string]$CommandsFile = "",
  [int]$WaitMs = 9000
)
$ErrorActionPreference = 'Stop'
$ws = New-Object System.Net.WebSockets.ClientWebSocket
try {
  $ws.ConnectAsync([Uri]$WsUrl, [Threading.CancellationToken]::None).Wait()
  $cmdsText = if ($CommandsFile -ne "" -and (Test-Path $CommandsFile)) { Get-Content -Raw $CommandsFile } else { $CommandsJson }
  $cmds = $cmdsText | ConvertFrom-Json
  $nextId = 1
  $buf = New-Object byte[] 4194304
  foreach ($c in $cmds) {
    $payload = @{ id = $nextId; method = $c.method; params = $c.params } | ConvertTo-Json -Depth 8 -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($payload)
    $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
    $deadline = [DateTime]::Now.AddSeconds(40)
    $resp = $null
    while ([DateTime]::Now -lt $deadline) {
      if ($ws.State -ne [System.Net.WebSockets.WebSocketState]::Open) { Write-Output "WS_CLOSED"; break }
      $seg = [ArraySegment[byte]]::new($buf)
      $sb = New-Object System.Text.StringBuilder
      do {
        $recv = $ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result
        if ($recv.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { Write-Output "WS_CLOSE_RECV"; break }
        [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $recv.Count))
      } while (-not $recv.EndOfMessage)
      $txt = $sb.ToString()
      $obj = $txt | ConvertFrom-Json -ErrorAction SilentlyContinue
      if ($obj -and $obj.id -eq $nextId) { $resp = $obj; break }
      # else: event — swallow
    }
    if ($resp) {
      if ($resp.result -and $resp.result.result -and $resp.result.result.value -isnot [string]) {
        Write-Output ("--- CMD {0} {1} (json result) ---" -f $nextId, $c.method)
        Write-Output ($resp.result.result.value | ConvertTo-Json -Depth 6)
      } else {
        Write-Output ("--- CMD {0} {1} ---" -f $nextId, $c.method)
        if ($resp.result) { Write-Output ($resp.result | ConvertTo-Json -Depth 6 -Compress) }
        if ($resp.error) { Write-Output ("ERROR: " + ($resp.error | ConvertTo-Json -Compress)) }
      }
    } else {
      Write-Output ("--- CMD {0} {1} TIMEOUT ---" -f $nextId, $c.method)
    }
    $nextId++
  }
} catch {
  Write-Output ("CDP-ERR: " + $_.Exception.Message)
} finally {
  try { $ws.Dispose() } catch {}
}
