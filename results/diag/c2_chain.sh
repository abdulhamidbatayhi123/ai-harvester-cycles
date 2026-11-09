cd "/c/Users/abdulhamid batayhi/Desktop/ai-harvester-cycles"
P=.venv/Scripts/python.exe
DIAG_WORLD=C2 $P -I audit/diag/l1_stageA_diag.py data_derived/bezrukov2023 results/diag/c2_base.json t63_srh3,exact MOF-303,ROS-039 > results/diag/c2_base.log 2>&1
DIAG_WORLD=C2 DIAG_MASK=3,6 $P -I audit/diag/l1_stageA_diag.py data_derived/bezrukov2023 results/diag/c2_m36.json t63_srh3 MOF-303,ROS-039 > results/diag/c2_m36.log 2>&1
DIAG_WORLD=C2 DIAG_MASK=0,3,6 $P -I audit/diag/l1_stageA_diag.py data_derived/bezrukov2023 results/diag/c2_m036.json t63_srh3 MOF-303,ROS-039 > results/diag/c2_m036.log 2>&1
echo CHAIN_DONE
