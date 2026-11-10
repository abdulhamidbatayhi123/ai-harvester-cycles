# Starts part 3 of the B2 harness v2 (S3,S4,S5,C3) when part 1 or part 2 has finished, so that at
# most two harness jobs share the memory-starved laptop.
Set-Location "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
while (-not ((Test-Path results\harness_b2_part1.status) -or (Test-Path results\harness_b2_part2.status))) { Start-Sleep 120 }
& cmd.exe /c "audit\run_harness_b2.bat 3 S3,S4,S5,C3"
