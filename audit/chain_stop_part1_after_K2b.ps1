# World S5 was moved from part 1 to part 4 (2026-11-11, to use the memory freed by part 3). Part 1 is stopped
# once its K2b world has all 8 folds, so S5 is not computed twice. Stops only the part-1 harness processes.
Set-Location "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
while ($true) {
  try { $d = Get-Content results\harness_b2\part1\harness_b2.json -Raw | ConvertFrom-Json
        if ($d.worlds.K2b -and (($d.worlds.K2b.folds.PSObject.Properties | Measure-Object).Count -ge 8)) { break } } catch {}
  Start-Sleep 120
}
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*harness_b2.py*part1*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
"part1 stopped after K2b $(Get-Date -Format s)" | Out-File -Append results\harness_b2_part1.status
