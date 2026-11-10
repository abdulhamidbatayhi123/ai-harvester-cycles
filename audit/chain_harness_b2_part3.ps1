# Starts part 3 of the B2 harness v2 when part 1 or part 2 has finished its second launch, so that at most two
# harness jobs share the memory-starved laptop. The status files are appended to, one line per launch.
Set-Location "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
function Lines($f) { if (Test-Path $f) { (Get-Content $f | Measure-Object -Line).Lines } else { 0 } }
while ((Lines results\harness_b2_part1.status) -lt 2 -and (Lines results\harness_b2_part2.status) -lt 2) { Start-Sleep 120 }
& cmd.exe /c 'audit\run_harness_b2.bat 3 "S4,C3"'
