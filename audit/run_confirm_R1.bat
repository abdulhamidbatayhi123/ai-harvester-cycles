.venv\Scripts\python.exe -E -s -m p4.run_study data_derived\bezrukov2023 results\confirm_R1 --kinds none --rule R1 >> results\confirm_R1.log 2>&1
.venv\Scripts\python.exe -E -s -m p4.decide results\confirm_R1\rows.jsonl results\prefreeze\checks2.json results\confirm_R1\decide.json >> results\confirm_R1.log 2>&1
echo finished %date% %time% exit %errorlevel% >> results\confirm_R1.status
