# Pre-freeze checks, round 2 (data only)

Answers the Claude Science review of 2026-11-08 (M2, M5, M8, M10, m1, m2, m10). Dry-mass rule R2.
Made by audit/prefreeze_checks2.py; full numbers in checks2.json.

## M10: total gas flow per plateau in P (sccm)

Kinetic plateaus only: step runs after the dry reference, all plateaus of the 27 °C cycling runs.
Plateau = run of constant set-point on the raw time base.

- cycling|[400.0]: 1492
- step|[400.0]: 1188

Plateaus not at 400 sccm or without a flow value: 0


## M5, C1: clusters per sorbent and temperature (step runs in P; scored segments: |Δm| ≥ 0.05 mg with the sign of the RH step)

| group | step files | two-pan sessions | inference clusters | up segments | down segments | |Δw| wt% min / 10 % / median / 90 % / max |
|---|---|---|---|---|---|---|
| Al-fumarate|27C | 3 | 2 | 8 | 18 | 18 | 31.81 / 31.88 / 36.17 / 39.56 / 39.57 |
| Al-fumarate|60C | 2 | 1 | 9 | 24 | 24 | 19.50 / 20.35 / 29.26 / 37.29 / 37.51 |
| CAU-10|27C | 4 | 2 | 8 | 24 | 24 | 23.69 / 23.80 / 26.38 / 30.15 / 30.17 |
| CAU-10|60C | 3 | 3 | 27 | 36 | 36 | 22.71 / 22.79 / 23.98 / 25.43 / 25.62 |
| MIL-160|27C | 4 | 2 | 8 | 24 | 24 | 12.12 / 32.94 / 34.95 / 39.73 / 40.60 |
| MIL-160|60C | 3 | 3 | 27 | 36 | 36 | 13.51 / 14.03 / 30.02 / 35.18 / 35.64 |
| MOF-303|27C | 2 | 1 | 4 | 12 | 12 | 32.61 / 32.64 / 34.94 / 35.93 / 36.81 |
| MOF-303|60C | 2 | 1 | 9 | 24 | 24 | 29.19 / 29.54 / 35.82 / 38.69 / 38.97 |
| ROS-037|27C | 4 | 2 | 8 | 24 | 24 | 8.44 / 8.47 / 8.88 / 9.35 / 9.36 |
| ROS-037|60C | 4 | 2 | 18 | 48 | 48 | 8.90 / 8.98 / 9.16 / 9.56 / 9.77 |
| ROS-037_composite|60C | 6 | 6 | 54 | 72 | 72 | 5.63 / 5.88 / 6.57 / 7.73 / 8.02 |
| ROS-039|27C | 4 | 2 | 8 | 24 | 24 | 21.25 / 21.28 / 22.12 / 22.93 / 22.95 |
| ROS-039|60C | 2 | 2 | 18 | 24 | 23 | 4.59 / 4.69 / 21.03 / 22.53 / 22.61 |
| ROS-039_composite|60C | 6 | 6 | 54 | 72 | 72 | 3.98 / 4.75 / 14.25 / 16.59 / 18.24 |
| ROS-040|27C | 4 | 2 | 8 | 24 | 24 | 13.66 / 13.75 / 14.85 / 15.94 / 15.96 |
| ROS-040|60C | 3 | 3 | 27 | 36 | 36 | 12.46 / 12.77 / 13.65 / 15.39 / 15.80 |
| Syloid|27C | 4 | 2 | 8 | 24 | 24 | 12.22 / 12.64 / 19.94 / 26.84 / 26.93 |
| Syloid|60C | 4 | 3 | 27 | 48 | 48 | 10.72 / 11.37 / 17.99 / 27.36 / 29.60 |

m10: two-pan sessions (shared start stamp) that combine different sorbents: 2021-08-27 20-08-03: CAU-10, MIL-160; 2022-04-28 17-09-42: ROS-037_composite, ROS-039_composite; 2022-04-29 10-06-14: ROS-037_composite, ROS-039_composite; 2022-04-30 16-40-18: ROS-037_composite, ROS-039_composite; 2022-05-02 10-36-27: ROS-037_composite, ROS-039_composite; 2022-05-03 10-56-06: ROS-037_composite, ROS-039_composite; 2022-05-03 22-56-16: ROS-037_composite, ROS-039_composite; 2021-08-28 16-11-45: ROS-040, Syloid

## M2: test-retest floor within a file against between files

Same step and same repeat number (from the second repeat on), responses compared as changes
from their own start (as for the within-file F). 'pan' = the other pan of the same session;
'session' = a different session.

| group | F within (n) | F between pans (n) | F between sessions (n) |
|---|---|---|---|
| Al-fumarate|27C | 0.0014 (12) | 0.1253 (8) | 0.3135 (16) |
| Al-fumarate|60C | 0.0126 (14) | 0.0754 (15) | n/a (0) |
| CAU-10|27C | 0.0009 (16) | 0.1991 (16) | 0.3740 (32) |
| CAU-10|60C | 0.0028 (21) | n/a (0) | 0.0974 (45) |
| MIL-160|27C | 0.0026 (16) | 0.2157 (16) | 0.2021 (32) |
| MIL-160|60C | 0.0044 (21) | n/a (0) | 0.0857 (45) |
| MOF-303|27C | 0.0019 (8) | 0.1644 (8) | n/a (0) |
| MOF-303|60C | 0.0050 (14) | 0.0775 (15) | n/a (0) |
| ROS-037|27C | 0.0020 (16) | 0.1023 (16) | 0.1553 (32) |
| ROS-037|60C | 0.0050 (28) | 0.0660 (30) | 0.0885 (60) |
| ROS-037_composite|60C | 0.0062 (42) | n/a (0) | 0.0343 (225) |
| ROS-039|27C | 0.0018 (16) | 0.1501 (16) | 0.3059 (32) |
| ROS-039|60C | 0.0029 (13) | n/a (0) | 0.0810 (14) |
| ROS-039_composite|60C | 0.0062 (42) | n/a (0) | 0.0965 (225) |
| ROS-040|27C | 0.0035 (16) | 0.0995 (16) | 0.1715 (32) |
| ROS-040|60C | 0.0066 (21) | n/a (0) | 0.1638 (45) |
| Syloid|27C | 0.0011 (16) | 0.1747 (16) | 0.1514 (32) |
| Syloid|60C | 0.0058 (28) | 0.1260 (15) | 0.0743 (75) |

Segment-weighted within-file F per sorbent (both temperatures): ROS-037 0.0040; ROS-039 0.0023; ROS-040 0.0054; MOF-303 0.0039; MIL-160 0.0037; CAU-10 0.0021; Al-fumarate 0.0078; Syloid 0.0042; ROS-037_composite 0.0062; ROS-039_composite 0.0062

## M8: mass drift at the end of the dry-mass windows (isotherm-free)

Slope of a linear fit over the last 10 min of each window, in % of m_dry per hour (negative = still
losing mass); temperature = median sample temperature over the last minute.

| kind | group | runs | R1 drift | R2 drift (runs) | R1 temp °C | R2 temp °C |
|---|---|---|---|---|---|---|
| isotherm | Al-fumarate 27C | 1 | -0.13 | 0.05 (1) | 27.60 | 27.20 |
| isotherm | Al-fumarate 60C | 1 | -0.06 | 0.13 (1) | 61.10 | 61.10 |
| isotherm | CAU-10 27C | 1 | -0.12 | 0.04 (1) | 27.40 | 27.40 |
| isotherm | CAU-10 60C | 1 | -0.11 | -0.01 (1) | 61.10 | 61.10 |
| isotherm | MIL-160 27C | 1 | n/a | n/a (0) | n/a | n/a |
| isotherm | MIL-160 60C | 1 | n/a | n/a (0) | n/a | n/a |
| isotherm | MOF-303 27C | 1 | -0.09 | 1.13 (1) | 27.40 | 27.40 |
| isotherm | MOF-303 60C | 2 | -0.08 | 0.57 (2) | 61.05 | 61.05 |
| isotherm | ROS-037 27C | 1 | -0.03 | -0.00 (1) | 25.10 | 25.20 |
| isotherm | ROS-037 60C | 1 | -0.01 | -0.00 (1) | 61.00 | 61.00 |
| isotherm | ROS-037_composite 27C | 1 | -0.16 | 0.05 (1) | 27.70 | 27.40 |
| isotherm | ROS-037_composite 60C | 1 | -0.10 | 0.01 (1) | 60.70 | 60.70 |
| isotherm | ROS-039 27C | 1 | n/a | n/a (0) | n/a | n/a |
| isotherm | ROS-039 60C | 1 | n/a | n/a (0) | n/a | n/a |
| isotherm | ROS-039_composite 27C | 1 | -0.11 | 0.05 (1) | 27.80 | 27.30 |
| isotherm | ROS-039_composite 60C | 1 | -0.07 | 0.01 (1) | 60.70 | 60.70 |
| isotherm | ROS-040 27C | 1 | -0.11 | 0.06 (1) | 27.40 | 27.40 |
| isotherm | ROS-040 60C | 1 | -0.06 | 0.00 (1) | 61.10 | 61.10 |
| isotherm | Syloid 27C | 1 | n/a | n/a (0) | n/a | n/a |
| isotherm | Syloid 60C | 1 | -0.08 | -0.69 (1) | 61.00 | 61.00 |
| step | Al-fumarate 27C | 3 | -0.35 | 0.08 (3) | 27.40 | 27.40 |
| step | Al-fumarate 60C | 2 | -0.39 | 0.01 (2) | 60.90 | 60.90 |
| step | CAU-10 27C | 4 | -0.15 | 0.04 (4) | 27.45 | 27.50 |
| step | CAU-10 60C | 3 | -0.10 | 0.00 (3) | 61.00 | 61.00 |
| step | MIL-160 27C | 4 | -0.07 | 0.18 (4) | 27.45 | 27.45 |
| step | MIL-160 60C | 3 | -0.17 | 0.02 (3) | 60.90 | 60.90 |
| step | MOF-303 27C | 2 | -0.06 | 1.59 (2) | 27.40 | 27.40 |
| step | MOF-303 60C | 2 | -0.27 | 0.12 (2) | 60.90 | 61.00 |
| step | ROS-037 27C | 4 | -0.22 | 0.01 (4) | 27.40 | 27.40 |
| step | ROS-037 60C | 4 | -0.04 | 0.00 (4) | 60.85 | 60.90 |
| step | ROS-037_composite 60C | 6 | -0.01 | 0.01 (6) | 60.70 | 60.70 |
| step | ROS-039 27C | 4 | -0.33 | 0.02 (4) | 27.48 | 27.45 |
| step | ROS-039 60C | 2 | -0.07 | 0.00 (2) | 60.95 | 61.00 |
| step | ROS-039_composite 60C | 6 | 0.06 | 0.00 (6) | 60.70 | 60.70 |
| step | ROS-040 27C | 4 | -0.10 | 0.03 (4) | 27.45 | 27.45 |
| step | ROS-040 60C | 3 | -0.26 | 0.01 (3) | 60.80 | 60.90 |
| step | Syloid 27C | 4 | -0.32 | 0.35 (4) | 27.40 | 27.45 |
| step | Syloid 60C | 4 | -0.17 | 0.01 (4) | 60.90 | 60.90 |

All runs: median |drift| R1 0.106 %/h (n 80, max 3.012); R2 0.023 %/h (n 80, max 1.845).

## m1: B0 with its own k'' against the noise floor (R2)

E_own / F over the 32 strata of the 8 sorbents: min 3.5 (Al-fumarate|60C|des), median 15.8, max 66.7 (CAU-10|60C|ads).

## m2: k'' across the 8 sorbents (R2)

| stratum | mean | range | CV (population SD) | CV (sample SD) |
|---|---|---|---|---|
| 27C|ads | 0.314 | 0.298 to 0.349 | 0.066 | 0.070 |
| 27C|des | 0.256 | 0.215 to 0.291 | 0.099 | 0.105 |
| 60C|ads | 1.596 | 1.144 to 3.157 | 0.387 | 0.413 |
| 60C|des | 0.974 | 0.719 to 1.505 | 0.283 | 0.302 |
