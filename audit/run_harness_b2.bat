@echo off
rem usage: run_harness_b2.bat <part> <worlds>   (one of three parallel parts of the B2 harness v2)
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
.venv\Scripts\python.exe -I audit\harness_b2.py data_derived\bezrukov2023 results\harness_b2\part%1 %2 > results\harness_b2_part%1.log 2>&1
echo finished %date% %time% exit %errorlevel% > results\harness_b2_part%1.status
