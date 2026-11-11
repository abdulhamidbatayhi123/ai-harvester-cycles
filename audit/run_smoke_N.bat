.venv\Scripts\python.exe -E -s -m p4.run_study data_derived\bezrukov2023 results\smoke_N --synthetic N --fast --kinds none >> results\smoke_N.log 2>&1
.venv\Scripts\python.exe -E -s -m p4.decide results\smoke_N\rows.jsonl results\prefreeze\checks2.json results\smoke_N\decide.json >> results\smoke_N.log 2>&1
.venv\Scripts\python.exe -E -s -m p4.final_verdict results\smoke_N\decide.json results\smoke_N\decide.json results\harness_b2\harness_b2.json results\smoke_N\final_verdict.json >> results\smoke_N.log 2>&1
echo finished %date% %time% exit %errorlevel% >> results\smoke_N.status
