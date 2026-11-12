# Terminology of the Paper 4 manuscript (each term defined once; use it only with the evidence named)

Pattern: Paper 3A `paper/tex/terminology.md` (from Bio-Inspired Photovoltaics). `paper/tex/build_ms.py` gate G4
parses the banned-phrase table below and fails on any match in `main.tex` or `si.tex` (comments stripped). Edit the
table, not the gate. Section numbers refer to PREREG_P4_draft.md (the frozen pre-registration after the freeze).

## Terms

| Term | Meaning in this paper | Evidence required before using it |
|---|---|---|
| isotherm-driven model, B0 | Bezrukov's model as published: dw/dt = (k″/m)(RH_flow − RH_bed(w)), RH_bed read from the measured isotherm, one k″ per temperature and direction shared by the training sorbents; variant B0-b uses the desorption branch for release | PREREG 5; p4/physics.py |
| B1 | linear driving force: dw/dt = (k‴/m)(w*(RH_flow) − w); a comparator candidate | PREREG 5 |
| B2 | B0 with log k″ = a + b·(RH50/30 − x̄) per temperature and direction, fitted on the training sorbents; the isotherm-predicted rate constant | PREREG 2 (H4a′), 5 |
| oracle k″ (B0*) | B0 with the held-out sorbent's own fitted k″; an upper bound, never a prediction | PREREG 8 |
| end-point oracle | B0 with the held-out sorbent's measured end point ε̂ in place of the isotherm's; descriptive | PREREG 8 |
| L1 (gray box), L2 (black box) | learned models; L1 = B0 times exp(2 tanh g_θ), a bounded positive correction (zero rate at equilibrium kept); L2 = neural ODE given the same local isotherm features, no physics imposed | PREREG 5 |
| harness | synthetic trajectories generated from a known truth on the real humidity records and isotherms; a model must pass it before it meets real data | PREREG 10 (L1), 10b (B2) |
| world (N, K, K2a–c, S0–S5, C3) | one synthetic truth of the harness: no effect, known effect, realistic-power effect, structure-free null, form error | PREREG 10b |
| held-out error E | RMS(w_pred − w_meas)/\|Δw\| of a step segment; a sorbent's score is the median over its segments | PREREG 6 |
| noise floor F | median normalised RMS between consecutive repeats of the same step in one file; one segment-weighted value per sorbent | PREREG 6; results/prefreeze/checks2.json |
| practical margin r | median d divided by the comparator's median cluster E; at least 10 % for a beat | PREREG 7 |
| beat | all four conditions of PREREG 7 on every held-out material of the fold, and physically admissible | p4/decide.py output |
| LOSO, LOFO | leave one sorbent out (8 folds; a composite goes with its parent), leave one family out | PREREG 4 |
| supported / falsified / not established / not tested | the verdict words of the PREREG 7 table, only from p4/final_verdict.py; never paraphrased | p4/final_verdict.py output on the confirmatory runs |
| confirmatory | a verdict of the frozen rule (H4a′) | final_verdict output |
| descriptive | reported without a decision rule (H4b, H4c, harness record) | must be labelled wherever used |
| exploratory (post hoc) | computed after the confirmatory results were known | must be labelled wherever used |
| dry-mass rule R2 (primary), R1 (sensitivity) | the two pre-registered definitions of the dry mass; a verdict stands only if both give it | PREREG 3.3, 7 |

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
| universal law | name the tested scope |
| robustly | say what was varied and what did not change |
| no difference | "not established at this noise and error level" (PREREG 7) |
| physics-informed | say "gray box" and name the structure |
| outperforms | give r, the fold count and the verdict word |
| white box | name the structure |
| failed to learn | "was not tested on real data: it did not pass the harness" (PREREG 10) |
| L1 was falsified | "not tested" (PREREG 10 stopping rule) |
| intrinsic kinetics | "effective rate constant of this model on these powder layers" |
| diffusion coefficient | "effective rate constant k″" (no transport mechanism was identified) |
| normalised | normalized (AIChE J., American spelling) |
| modelling | modeling (American spelling) |
| vapour | vapor (American spelling) |
| behaviour | behavior (American spelling) |
| grey | gray (American spelling) |
| colour | color (American spelling) |
| analyse | analyze (American spelling) |
| licence | license (American spelling) |
| aluminium | aluminum (American spelling) |
