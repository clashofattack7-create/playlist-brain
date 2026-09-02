param([string]$Data, [string]$OutPrefix)
$ErrorActionPreference = "Stop"
$d = (Get-Content -Raw $Data) | ConvertFrom-Json
$contents = $d.contents.twoColumnBrowseResultsRenderer.tabs[0].tabRenderer.content.sectionListRenderer.contents[0].itemSectionRenderer.contents
$items = New-Object System.Collections.ArrayList
$pos = 0
foreach ($c in $contents) {
  $lv = $c.lockupViewModel
  if ($null -eq $lv) { continue }
  $pos++
  $title = ""
  try { $title = $lv.metadata.lockupMetadataViewModel.title.content } catch {}
  $parts = @()
  try {
    $rows = $lv.metadata.lockupMetadataViewModel.metadata.contentMetadataViewModel.metadataRows
    $parts = @(foreach ($row in $rows) { foreach ($p in $row.metadataParts) { [string]$p.text.content } })
  } catch {}
  $dur = ""
  try {
    $dur = $lv.contentImage.thumbnailViewModel.overlays[0].thumbnailBottomOverlayViewModel.badges[0].thumbnailBadgeViewModel.text
  } catch {}
  $item = [PSCustomObject]@{ pos = $pos; videoId = [string]$lv.contentId; title = $title; channel = [string]$parts[0]; stat1 = [string]$parts[1]; stat2 = [string]$parts[2]; duration = $dur }
  [void]$items.Add($item)
}
$items | ConvertTo-Json -Depth 4 | Set-Content -Path "$OutPrefix.json" -Encoding UTF8
$lines = $items | ForEach-Object { "$($_.pos)`t$($_.videoId)`t$($_.title)`t$($_.channel)`t$($_.stat1)`t$($_.stat2)`t$($_.duration)" }
$lines | Set-Content -Path "$OutPrefix.tsv" -Encoding UTF8
"TOTAL: " + $items.Count
"channels: " + (($items | Group-Object channel | ForEach-Object { "$($_.Name) ($($_.Count))" }) -join "; ")