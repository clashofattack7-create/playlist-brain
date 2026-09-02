param(
  [Parameter(Mandatory=$true)][string]$WsUrl
)
$ErrorActionPreference = 'Stop'
$ws = New-Object System.Net.WebSockets.ClientWebSocket
try {
  $ws.ConnectAsync([Uri]$WsUrl, [Threading.CancellationToken]::None).Wait()
  $buf = New-Object byte[] 8388608
  $script:nextId = 0
  function Send-Cmd([string]$method, $params) {
    $script:nextId++
    $payload = @{ id = $script:nextId; method = $method; params = $params } | ConvertTo-Json -Depth 8 -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($payload)
    $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
    $deadline = [DateTime]::Now.AddSeconds(35)
    while ([DateTime]::Now -lt $deadline) {
      $sb = New-Object System.Text.StringBuilder
      do {
        $seg = [ArraySegment[byte]]::new($buf)
        $recv = $ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result
        if ($recv.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { return $null }
        [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $recv.Count))
      } while (-not $recv.EndOfMessage)
      $obj = $sb.ToString() | ConvertFrom-Json -ErrorAction SilentlyContinue
      if ($obj -and $obj.id -eq $script:nextId) { return $obj }
    }
    return $null
  }
  $pairs = @( @('first','8'), @('second','7'), @('third','5'), @('fourth','1') )
  foreach ($pair in $pairs) {
    $id = $pair[0]; $d = $pair[1]
    [void](Send-Cmd 'Runtime.evaluate' @{ expression = ("(() => { const el = document.getElementById('" + $id + "'); if (el) { el.value=''; el.focus(); } return 'ok'; })()"); returnByValue = $true })
    Start-Sleep -Milliseconds 350
    [void](Send-Cmd 'Input.insertText' @{ text = $d })
    Start-Sleep -Milliseconds 450
  }
  $r1 = Send-Cmd 'Runtime.evaluate' @{ expression = "JSON.stringify(Array.from(document.querySelectorAll('input[type=number]')).filter(i=>i.offsetParent!==null && /^(first|second|third|fourth)$/.test(i.id||'')).map(i=>i.value))"; returnByValue = $true }
  if ($r1.result -and $r1.result.result) { Write-Output ('boxVals: ' + $r1.result.result.value) }
  Start-Sleep -Milliseconds 800
  $r2 = Send-Cmd 'Runtime.evaluate' @{ expression = "(async () => { const b = Array.from(document.querySelectorAll('button')).find(b=>/^login$/i.test((b.innerText||'').replace(/\\s+/g,' ').trim()) && b.offsetParent!==null); if (b) b.click(); await new Promise(r=>setTimeout(r,12000)); return JSON.stringify({url: location.href, txt:(document.body.innerText||'').replace(/\\s+/g,' ').slice(0,300), errs:(Array.from(document.querySelectorAll('div,span,p,label')).map(e=>(e.innerText||'').replace(/\\s+/g,' ').trim()).filter(t=>/wrong|invalid|incorrect|failed|mismatch/i.test(t)&&t.length<100).slice(0,3)), visBtns: Array.from(document.querySelectorAll('button')).filter(b=>b.offsetParent!==null).map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean).filter(t=>/login|web|trader|continue|try/i.test(t)).slice(0,6)}); })()"; awaitPromise = $true; returnByValue = $true }
  if ($r2.result -and $r2.result.result) { Write-Output ('state: ' + $r2.result.result.value) }
  elseif ($r2.result) { Write-Output ('state: ' + ($r2.result | ConvertTo-Json -Compress)) }
} catch {
  Write-Output ('KEYS-ERR: ' + $_.Exception.Message)
} finally {
  try { $ws.Dispose() } catch {}
}