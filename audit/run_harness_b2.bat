@echo off
rem usage: run_harness_b2.bat <part> "<world,world,...>"   (one of three parallel parts of the B2 harness v2)
rem The world list MUST be quoted: cmd splits unquoted arguments at commas (2026-11-10: each part ran only
rem its first world). %~2 strips the quotes.
cd /d "C:\Users\abdulhamid batayhi\Desktop\ai-harvester-cycles"
.venv\Scripts\python.exe -I audit\harness_b2.py data_derived\bezrukov2023 results\harness_b2\part%1 "%~2" >> results\harness_b2_part%1.log 2>&1
echo finished %date% %time% exit %errorlevel% worlds %~2 >> results\harness_b2_part%1.status
