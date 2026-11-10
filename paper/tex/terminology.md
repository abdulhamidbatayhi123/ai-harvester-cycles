# Terminology of the Paper 3A manuscript (each term defined once; use it only with the evidence named)

Pattern: Bio-Inspired Photovoltaics `manuscript/terminology.md`. `paper/tex/build_ms.py` gate G4 parses the
banned-phrase table below and fails on any match in `main.tex` or `si.tex` (comments stripped). Edit the table,
not the gate.

## Terms

| Term | Meaning in this paper | Evidence required before using it |
|---|---|---|
| potential model, P | the learned reduced spreading pressure psi(s, T) with hard shape constraints (softplus mixture, capacities > 0, Henry g = 1 and cooperative g >= 1.5 terms) and van't Hoff positions; the isotherm is d psi / d s | PREREG 4; src/p3a/models.py |
| hard constraint | holds for every parameter value by construction (monotone in p, finite Henry slope, defined heat) | the architecture, not the fit |
| penalty model (F-pen, V-pen, A-pen) | the same function class without the hard constraint, with monotonicity and Henry penalties in the loss | PREREG 4 |
| unconstrained twin (F-none, V-none, A-none) | the same function class, no constraint and no penalty | PREREG 4 |
| temperature structure F / V / A | free network in 1/T / van't Hoff position per term / temperature-invariant characteristic curve in A = RT ln(p_sat/p) | PREREG 4 |
| C1 | dual-site Sips with van't Hoff affinities, the classical comparator | PREREG 4 |
| E-high, E-low | train on all but the highest (lowest) temperature, predict it; the extrapolation tasks | PREREG 5.1 |
| I-mid | interpolation task, secondary | PREREG 5.1 |
| held-out error E | RMSE of the held-out isotherm divided by q_ref | PREREG 6.1 |
| error ratio R | 10^d with d the Hodges-Lehmann estimate of the paired difference of per-material mean log10 E | PREREG 7.2 |
| violation, violating fit | a fit whose isotherm on the dense grid falls more than 2 % of q_ref below its running maximum, or below -2 % of q_ref, inside the penalty domain | PREREG 6.2; study.VIOL_TOL |
| confirmatory | a verdict of the frozen rule (H1b-H1e, H3) | analyse.py output on the confirmatory runs |
| primary claim | H1b non-inferiority only (upper exact 95 % bound of R below 1.25) | PREREG 7.3 |
| descriptive | reported without a hypothesis (H1a, F-rel, P-K, MLP) | must be labelled wherever used |
| exploratory (post hoc) | computed after the confirmatory results were known | must be labelled wherever used |
| inconclusive | the exact test is not significant and the interval does not fit "equivalent"; never "no difference" | PREREG 8 |
| equivalent within 25 % | the frozen verdict word: exact 90 % interval inside 0.8-1.25 | PREREG 8 |

## Banned phrases (with replacements)

| Do not write | Write instead |
|---|---|
| the first to | state what was done; cite prior work |
| the first study | state what was done; cite prior work |
| for the first time | state what was done |
| first-ever | state what was done |
| novel | describe the finding |
| groundbreaking | describe the finding |
| paradigm | describe the finding |
| unprecedented | give the number |
| dramatically | give the number |
| drastically | give the number |
| remarkably | give the number |
| strikingly | give the number |
| significantly | give the effect size, or the test and p |
| proves | shows, in this design |
| demonstrates conclusively | shows, in this design |
| seamless | plain words |
| leverage | use |
| utilize | use |
| delve | examine |
| crucial | important, or say why |
| pivotal | important, or say why |
| state-of-the-art | name the method |
| it is worth noting | delete; state the point |
| interestingly | delete; state the point |
| notably | delete; state the point |
| universal | name the tested scope |
| robustly | say what was varied and what did not change |
| no difference | "inconclusive at this sample size" (PREREG 8) |
| physics-informed | say "with penalties" or "with hard constraints" |
| thermodynamically consistent | name the property that holds (monotone, finite Henry slope, defined heat) |
| outperforms | give R and its interval |
| white box | name the structure |
