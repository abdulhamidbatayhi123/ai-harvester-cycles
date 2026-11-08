#!/bin/sh
# Rerun every pre-freeze measurement after a data-pipeline change, one job at a time.
set -e
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
D=data_derived/bezrukov2023
O=results/prefreeze
$PY -I audit/prefreeze_checks.py $D $O > $O/prefreeze_checks.log 2>&1
$PY -I audit/compare_dry_rules.py $D $O/dry_rules.json > $O/dry_rules.log 2>&1
$PY -I audit/prefreeze_checks2.py $D $O > $O/checks2.log 2>&1
$PY -I audit/reproduce_b0.py $D $O R2 > $O/reproduce_b0.log 2>&1
$PY -I audit/reproduce_b0.py $D $O R1 > $O/reproduce_b0_R1.log 2>&1
$PY -I audit/h4b_insample.py $O/reproduce_b0.json $O/checks2.json $O/h4b_insample.json > $O/h4b_insample.log 2>&1
$PY -I audit/violation_floor.py $D $O/violation_floor.json > $O/violation_floor.log 2>&1
echo done
