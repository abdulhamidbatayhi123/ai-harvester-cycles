# Waits for harness round 7, archives it, then runs the Al-fumarate C3 fold (PREREG section 10,
# stopping rule; committed in 150eb2f before any C3 result existed).
Set-Location "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
while (-not (Select-String -Path results\harness.log -Pattern "PASS criteria|Traceback" -Quiet)) { Start-Sleep 120 }
if (Select-String -Path results\harness.log -Pattern "Traceback" -Quiet) { "round 7 crashed" | Out-File results\chain_alfu.status; exit 1 }
New-Item -ItemType Directory -Force results\harness_round7 | Out-Null
Copy-Item results\harness\* results\harness_round7\ -Recurse -Force
Copy-Item results\harness.log results\harness_round7\harness.log -Force
"round 7 archived $(Get-Date -Format s); Al-fumarate run started" | Out-File results\chain_alfu.status
$env:HARNESS_HELD = "Al-fumarate"
$env:HARNESS_CASES = "N,C3"
& .venv\Scripts\python.exe -I audit\synthetic_harness.py data_derived\bezrukov2023 results\harness_alfu L1 *> results\harness_alfu.log
"Al-fumarate run finished $(Get-Date -Format s), exit $LASTEXITCODE" | Out-File results\chain_alfu.status -Append
