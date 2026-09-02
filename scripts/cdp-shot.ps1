param(
  [Parameter(Mandatory=$true)][string]$WsUrl,
  [Parameter(Mandatory=$true)][string]$OutFile
)
$ErrorActionPreference = 'Stop'
$ws = New-Object System.Net.WebSockets.ClientWebSocket
try {
  $ws.ConnectAsync([Uri]$WsUrl, [Threading.CancellationToken]::None).Wait()
  $payload = '{"id":1,"method":"Page.captureScreenshot","params":{"format":"png"}}'
  $bytes = [Text.Encoding]::UTF8.GetBytes($payload)
  $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  $buf = New-Object byte[] 20971520
  $sb = New-Object System.Text.StringBuilder
  do {
    $seg = [ArraySegment[byte]]::new($buf)
    $recv = $ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result
    if ($recv.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { break }
    [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $recv.Count))
  } while (-not $recv.EndOfMessage)
  $obj = $sb.ToString() | ConvertFrom-Json
  if ($obj.result -and $obj.result.data) {
    $b64 = $obj.result.data
    [System.IO.File]::WriteAllBytes($OutFile, [Convert]::FromBase64String($b64))
    Write-Output ('saved: ' + $OutFile + ' (' + $b64.Length + ' b64 chars)')
  } else { Write-Output ('NO IMAGE: ' + $sb.ToString().Substring(0, [Math]::Min(200, $sb.ToString().Length))) }
} catch { Write-Output ('SHOT-ERR: ' + $_.Exception.Message) } finally {
  try { $ws.Dispose() } catch {}
}