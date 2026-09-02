$ErrorActionPreference = "Continue"
$py = "C:\Python314\python.exe"
$common = @("-m","yt_dlp","--impersonate","chrome","--js-runtimes","node","--remote-components","ejs:github","--skip-download","--write-auto-subs","--write-subs","--sub-format","json3","--sub-langs","en,hi","--ignore-errors","--no-warnings","--sleep-requests","0.5","--sleep-subtitles","1.5","--retries","3")
"START P1 " + (Get-Date -Format "HH:mm:ss")
$args1 = $common + @("-o","D:\dsh\DSH\playlist-brain\transcripts\p1\%(id)s","https://www.youtube.com/playlist?list=PLBX2XimSX5_Y")
$p1 = Start-Process -FilePath $py -ArgumentList $args1 -PassThru -WindowStyle Hidden -RedirectStandardOutput "D:\dsh\DSH\playlist-brain\raw\dl-p1-out.log" -RedirectStandardError "D:\dsh\DSH\playlist-brain\raw\dl-p1-err.log"
$p1.WaitForExit()
"P1_EXIT=" + $p1.ExitCode + " at " + (Get-Date -Format "HH:mm:ss")
"START P2 " + (Get-Date -Format "HH:mm:ss")
$args2 = $common + @("-o","D:\dsh\DSH\playlist-brain\transcripts\p2\%(id)s","https://www.youtube.com/playlist?list=PLPUSajfOG-ew")
$p2 = Start-Process -FilePath $py -ArgumentList $args2 -PassThru -WindowStyle Hidden -RedirectStandardOutput "D:\dsh\DSH\playlist-brain\raw\dl-p2-out.log" -RedirectStandardError "D:\dsh\DSH\playlist-brain\raw\dl-p2-err.log"
$p2.WaitForExit()
"P2_EXIT=" + $p2.ExitCode + " at " + (Get-Date -Format "HH:mm:ss")
"ALL DONE"