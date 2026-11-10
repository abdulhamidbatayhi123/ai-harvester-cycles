@echo off
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
.venv\Scripts\python.exe -I audit\harness_b2.py data_derived\bezrukov2023 results\harness_b2 > results\harness_b2.log 2>&1
echo finished %date% %time% exit %errorlevel% > results\harness_b2.status
