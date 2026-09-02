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
  $r0 = Send-Cmd 'Runtime.evaluate' @{ expression = "(() => { const b = Array.from(document.querySelectorAll('button')).find(x=>/^login$/i.test((x.innerText||'').replace(/\\s+/g,' ').trim()) && x.offsetParent!==null); if (!b) return 'none'; const r = b.getBoundingClientRect(); return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2}); })()"; returnByValue = $true }
  $coords = $null
  if ($r0.result -and $r0.result.result -and $r0.result.result.value) { $coords = $r0.result.result.value | ConvertFrom-Json }
  if ($null -eq $coords) { Write-Output 'no login button found'; return }
  Write-Output ('button at: ' + $coords.x + ',' + $coords.y)
  [void](Send-Cmd 'Input.dispatchMouseEvent' @{ type = 'mouseMoved'; x = $coords.x; y = $coords.y })
  Start-Sleep -Milliseconds 250
  [void](Send-Cmd 'Input.dispatchMouseEvent' @{ type = 'mousePressed'; x = $coords.x; y = $coords.y; button = 'left'; clickCount = 1 })
  Start-Sleep -Milliseconds 150
  [void](Send-Cmd 'Input.dispatchMouseEvent' @{ type = 'mouseReleased'; x = $coords.x; y = $coords.y; button = 'left'; clickCount = 1 })
  Start-Sleep -Seconds 12
  $r2 = Send-Cmd 'Runtime.evaluate' @{ expression = "(async () => { await new Promise(r=>setTimeout(r,500)); return JSON.stringify({url: location.href, txt:(document.body.innerText||'').replace(/\\s+/g,' ').slice(0,300), errs:(Array.from(document.querySelectorAll('div,span,p,label')).map(e=>(e.innerText||'').replace(/\\s+/g,' ').trim()).filter(t=>/wrong|invalid|incorrect|failed|mismatch/i.test(t)&&t.length<100).slice(0,3)), visBtns: Array.from(document.querySelectorAll('button')).filter(b=>b.offsetParent!==null).map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean).filter(t=>/login|web|trader|continue|try|otp/i.test(t)).slice(0,6)}); })()"; awaitPromise = $true; returnByValue = $true }
  if ($r2.result -and $r2.result.result) { Write-Output ('state: ' + $r2.result.result.value) }
} catch {
  Write-Output ('MOUSE-ERR: ' + $_.Exception.Message)
} finally {
  try { $ws.Dispose() } catch {}
}