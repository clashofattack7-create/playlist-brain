param([string]$Dir)
$ErrorActionPreference = "Continue"
$enStop = "the,a,an,and,or,but,if,then,else,when,while,for,to,of,in,on,at,by,with,from,is,are,was,were,be,been,being,am,do,does,did,have,has,had,this,that,these,those,it,its,we,you,they,he,she,i,my,me,your,our,their,them,him,her,us,so,as,like,just,very,also,can,could,would,should,may,might,must,shall,will,not,no,yes,ok,okay,now,here,there,all,some,any,one,two,three,four,five,what,which,who,whom,whose,how,why,where,when,than,too,more,most,only,even,about,into,over,under,again,up,down,out,off,get,got,going,go,come,came,see,saw,look,take,took,make,made,think,know,say,said,tell,told,way,thing,things,time,day,days,right,left,good,bad,big,small,first,last,next,back,people,person,market,price,chart,point,points,level,levels,means,mean,toh,haan,hai,hi,market,price,chart,level,levels"
$hiStop = (Get-Content (Join-Path $PSScriptRoot "stopwords-hi.txt") -Encoding UTF8) -join ","
$stop = New-Object "System.Collections.Generic.HashSet[string]"
($enStop -split ",") | ForEach-Object { [void]$stop.Add($_.Trim()) }
($hiStop -split ",") | ForEach-Object { [void]$stop.Add($_.Trim()) }
$files = Get-ChildItem -Path $Dir -Filter *.txt -ErrorAction SilentlyContinue
$rows = New-Object System.Collections.ArrayList
foreach ($f in $files) {
  $txt = Get-Content -Raw $f.FullName -Encoding UTF8
  $words = [regex]::Matches($txt.ToLower(), "[a-z0-9]+|[\u0900-\u097F]+") | ForEach-Object { $_.Value }
  $freq = @{}
  foreach ($w in $words) {
    if ($w.Length -lt 3) { continue }
    if ($stop.Contains($w)) { continue }
    if ($freq.ContainsKey($w)) { $freq[$w]++ } else { $freq[$w] = 1 }
  }
  $top = ($freq.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 25 | ForEach-Object { $_.Key + ":" + $_.Value }) -join "|"
  $lines = ($txt -split "`n").Count
  $dur = ""
  $m = [regex]::Match($txt, "\[(\d{2}):(\d{2}):(\d{2})\]")
  if ($m.Success) { $dur = [string]([int]$m.Groups[1].Value*3600 + [int]$m.Groups[2].Value*60 + [int]$m.Groups[3].Value) }
  [void]$rows.Add(($f.BaseName -replace "\.(en|hi)$","") + "`t" + $f.BaseName + "`t" + $words.Count + "`t" + $lines + "`t" + $dur + "`t" + $top)
}
$rows | Set-Content -Path (Join-Path $Dir "keywords.tsv") -Encoding UTF8
"ANALYZED files=" + $files.Count