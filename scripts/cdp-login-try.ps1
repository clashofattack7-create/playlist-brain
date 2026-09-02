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
    $deadline = [DateTime]::Now.AddSeconds(40)
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
  function Get-ButtonRect {
    $r = Send-Cmd 'Runtime.evaluate' @{ expression = "(() => { const b = Array.from(document.querySelectorAll('button')).find(x=>/^login$/i.test((x.innerText||'').replace(/",'s+/g,"',' ').trim()) && x.offsetParent!==null); if (!b) return 'none'; const r = b.getBoundingClientRect(); return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2}); })()"; returnByValue = $true }
    if ($r.result -and $r.result.result -and $r.result.result.value -and $r.result.result.value -ne 'none') {
      return ($r.result.result.value | ConvertFrom-Json)
    }
    return $null
  }
  $c = Get-ButtonRect
  if ($null -eq $c) { Write-Output 'login button not found'; return }
  Write-Output ('login btn at: ' + [math]::Round($c.x,1) + ',' + [math]::Round($c.y,1))
  [void](Send-Cmd 'Input.dispatchMouseEvent' @{ type = 'mouseMoved'; x = $c.x; y = $c.y })
  Start-Sleep -Milliseconds 200
  [void](Send-Cmd 'Input.dispatchMouseEvent' @{ type = 'mousePressed'; x = $c.x; y = $c.y; button = 'left'; clickCount = 1 })
  Start-Sleep -Milliseconds 120
  [void](Send-Cmd 'Input.dispatchMouseEvent' @{ type = 'mouseReleased'; x = $c.x; y = $c.y; button = 'left'; clickCount = 1 })
  Start-Sleep -Seconds 10
  $chk = Send-Cmd 'Runtime.evaluate' @{ expression = "location.href"; returnByValue = $true }
  $url1 = ''
  if ($chk.result -and $chk.result.result) { $url1 = $chk.result.result.value }
  Write-Output ('after mouse click: ' + $url1)
  if ($url1 -like '*login*') {
    [void](Send-Cmd 'Runtime.evaluate' @{ expression = "(() => { const v = Array.from(document.querySelectorAll('input[type=number]')).filter(x => x.offsetParent !== null && ['first','second','third','fourth'].includes(x.id)); if (v[0]) v[0].focus(); return 'ok'; })()"; returnByValue = $true })
    Start-Sleep -Milliseconds 300
    [void](Send-Cmd 'Input.dispatchKeyEvent' @{ type = 'keyDown'; key = 'Enter'; code = 'Enter'; windowsVirtualKeyCode = 13; nativeVirtualKeyCode = 13 })
    [void](Send-Cmd 'Input.dispatchKeyEvent' @{ type = 'keyUp'; key = 'Enter'; code = 'Enter'; windowsVirtualKeyCode = 13; nativeVirtualKeyCode = 13 })
    Start-Sleep -Seconds 10
    $chk2 = Send-Cmd 'Runtime.evaluate' @{ expression = "location.href"; returnByValue = $true }
    $url2 = ''
    if ($chk2.result -and $chk2.result.result) { $url2 = $chk2.result.result.value }
    Write-Output ('after Enter: ' + $url2)
  }
  $fin = Send-Cmd 'Runtime.evaluate' @{ expression = "JSON.stringify({url: location.href, txt:(document.body.innerText||'').replace(/",'s+/g,'" ',' ').slice(0,220)})"; returnByValue = $true }
  if ($fin.result -and $fin.result.result) { Write-Output ('state: ' + $fin.result.result.value) }
} catch {
  Write-Output ('ERR: ' + $_.Exception.Message)
} finally {
  try { $ws.Dispose() } catch {}
}