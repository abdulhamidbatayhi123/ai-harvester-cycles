# Methods (draft, 2026-11-10; written from PREREG_P4_draft.md before the freeze)

Every number carries its source in a comment `[src: ...]`; the LaTeX port binds each one with
`\V{key}{value}` (paper/tex/build_ms.py, gate G1). Nothing here reports a confirmatory result.
Placeholders: FREEZE (commit hash), VENUE (journal format).

## Pre-registration and order of events

The protocol was written before any model was fitted to held-out real data and frozen at commit
FREEZE; every change before the freeze is listed with its cause in the protocol's corrections
section [src: PREREG §13]. The order of events matters for how the results may be read, so we
state it here. The original primary hypothesis (H4a) asked whether a learned model, given only an
unseen sorbent's isotherms, predicts its uptake trajectories better than the published
isotherm-driven model. A learned model could enter that test only after passing a synthetic
ground-truth harness. The grey-box model L1 failed the harness in its last allowed round, under a
stopping rule written before that round's judged result existed [src: PREREG §10, round 7;
results/harness_round7/harness.json; results/harness_alfu/harness.json], so H4a is reported as
not tested and no learned model was fitted to the real data. The confirmatory hypothesis H4a′ was
then added, before any fit of its model to held-out real data; that model's form had been fixed
two days earlier as a reported comparator [src: PREREG §2; commit 127ab6d, 2026-11-08]. H4a′ has
its own harness, which had to pass before the freeze [src: PREREG §10b].

## Data

We used the dynamic vapour sorption (DVS) archive of Bezrukov et al. [ref], deposited under CC BY
4.0 [src: DATA_SOURCES.md; Zenodo 6631711]. It holds step runs, cycling runs and isotherms of
eight sorbents: MOF-303, MIL-160, CAU-10-H and Al-fumarate (aluminium carboxylate rods), ROS-039
and ROS-040 (zinc triazolate fluorides), ROS-037 (a copper framework) and the silica gel Syloid
AL-1, plus composites of ROS-037 and ROS-039. The primary set contains all step runs at 27 and
60 °C, all 0↔30 % RH cycling runs at 27 °C and the isotherms at both temperatures; particle-size,
packing, pan and flow variations, the 100-cycle runs and the cellulose isotherm are reserved for
secondary analyses [src: PREREG §3.2]. Eight files duplicate another file's mass trace exactly;
the copy in the sorbent's main folder is kept [src: PREREG §3.2; p4/data.py duplicate_files].
Two MOFs of Gao et al. [ref] serve only as an external test, because their flow rate is not
reported and their step curves give set-point rather than measured humidity [src: PREREG §3.4].

Uptake is w = 100 (m − m_dry)/m_dry in wt%. The instrument's reference mass is not used, because
the sample is not yet dry when it is recorded [src: PREREG §3.3]. The primary dry mass (rule R2)
is the median mass over the last minute of the unheated 0 % RH stretch that follows the heated
activation (70 to 229 min, median 90) [src: PREREG §3.3]; it was chosen because the mass has
stopped changing there: the median drift over the last 10 min is 0.023 % h⁻¹, against
0.106 % h⁻¹ at the end of the heated activation (rule R1, 80 runs each) [src:
results/prefreeze/checks2.md]. Every confirmatory result is computed under both rules, and a
verdict stands only if both give it. The composites' 27 °C step runs, dried only at 27 °C and
still losing 0.3 to 0.9 % of their mass per hour, and all cycling runs, which have no drying
stage, are excluded from the confirmatory comparisons [src: PREREG §3.3]. Models are driven by
the measured humidity and sample temperature and the sample's dry mass, and are told nothing
about the held-out sorbent except its adsorption and desorption isotherms at both temperatures.
Trajectories are resampled to a 6 s grid, which keeps at least 11 points within the fastest
time to 63 % of the step (1.1 min) [src: PREREG §3.3].

## Units, folds and clusters

The unit of evaluation is a step segment, one humidity plateau of a step run, simulated open
loop from the measured uptake at its first grid point [src: PREREG §3.5, §5]. Eight
leave-one-sorbent-out (LOSO) folds hold out each Bezrukov sorbent, a composite always together
with its parent [src: PREREG §4]. Two leave-one-family-out folds hold out the aluminium rods and
the zinc triazolates; the other two family folds coincide with LOSO folds. Everything fitted is
fitted on the training sorbents only.

Two pans measured together share their forcing, and each sorbent was measured in few sessions
(one session at each temperature for MOF-303) [src: PREREG §4; results/prefreeze/checks2.md].
The inference cluster is therefore one humidity step (from-RH, to-RH) in one session, averaging
both pans and all repeats [src: PREREG §4]; a sorbent has 13 to 54 clusters [src:
results/prefreeze/cluster_counts.json]. A per-fold result is a consistency check over humidity
conditions for the samples measured; the claim about unseen sorbents rests on the count over
folds.

## Models

B0 is Bezrukov's model [ref]: dw/dt = (k″/m)(RH_flow − RH_bed(w)), with RH_bed(w) the inverse of
the held-out sorbent's adsorption isotherm and one k″ for uptake and one for release at each
temperature, shared by all training sorbents. B0-b reads the desorption branch during release,
and B1 is a linear-driving-force model, dw/dt = (k‴/m)(w*(RH_flow) − w) [src: PREREG §5]. All
physics models are fitted by the scored metric (the median normalised error over segments, below)
rather than by least squares, so that no model gains merely from being fitted to the metric it is
scored on [src: PREREG §5, review finding N5].

B2, the model of H4a′, is B0 with an isotherm-predicted rate constant: log k″ = a + b(x − x̄),
with x = RH₅₀/30 %, RH₅₀ the humidity at which the adsorption branch reaches half its uptake at
30 % RH, and x̄ the mean of x over the training sorbents; a and b are fitted for each temperature
and direction [src: PREREG §5; p4/physics.py fit_b2]. RH₅₀ spans 7.4 % to 24.3 % RH at 27 °C and
10.5 % to 28.7 % at 60 °C [src: results/rh50.json]. B2 is built on the fold's B0 variant, so that
it differs from the pooled model in k″ alone. The oracle B0* is B0 with k″ fitted on the held-out
sorbent's own data; it is not a competitor but measures what any single per-sorbent k″ could gain
[src: PREREG §5].

The learned grey-box model L1 multiplied B0's rate by a bounded positive factor,
exp(2 tanh g_θ(z)), from a small network of local isotherm features and the driving force [src:
PREREG §5]. It is described in full with its harness record in the Supplementary Information.

## Metric and noise floor

The error of a segment is E = RMS(w_pred − w_meas)/|Δw|, with Δw the measured change over the
segment [src: PREREG §6]. The noise floor F of a sorbent is the median error between consecutive
repeats of the same step within one file, aligned on time since the step, as a segment-weighted
mean over its two temperatures; F is 0.0021 to 0.0078 [src: results/prefreeze/checks2.json
F_within_segment_weighted].

## Decision rule

For each held-out material, d = E_B0 − E_B2 per segment and D = d·|Δw| are averaged within
clusters. B2 beats B0 on a material if (1) the median cluster d exceeds that material's F; (2) the
relative improvement r, the median d over B0's median cluster E, is at least 10 %; (3) a one-sided
exact Wilcoxon signed-rank test of D over clusters gives p ≤ 0.025; and (4) B2's median cluster E
is below B0's [src: PREREG §7]. A fold is beaten if every held-out material is beaten and B2 adds
physical violations (uptake moving against the step by more than 0.05 wt% within a minute, where
neither data nor B0 do) on at most 5 % of segments [src: PREREG §6, §7]. H4a′ is supported if at
least 7 of the 8 LOSO folds are beaten, falsified if at most one fold has r ≥ 10 % (the seventh
order statistic of r is then a one-sided 96.5 % upper bound on its median below 10 %), and not
established otherwise; the verdict must agree under R1 and R2, and the B2 harness must have
passed, or H4a′ is not tested [src: PREREG §7, §10b; p4/decide.py, p4/final_verdict.py]. The
10 % margin was proposed after the noise floor and an in-sample reproduction of B0 were seen and
before any learned model was fitted to real data [src: PREREG §7].

## Synthetic harnesses

Both harnesses generate trajectories on the real forcing, isotherms and dry masses from a known
truth, add autocorrelated noise (σ = 0.01 wt%, φ = 0.9), and run the confirmatory pipeline [src:
PREREG §10, §10b]. For L1, the harness required recovery of k″ in a world without correction, a
beat and a halving of B0's error in a correction world not used during development, and no false
positive; it ran in seven rounds, with the judging world replaced whenever a world had been used
for diagnosis, and stopped by rule after round 7 [src: PREREG §10]. For B2, version 2 of the
harness [src: audit/harness_b2.py, commit 78accf6] has a world without effect, a plumbing world
whose truth lies in B2's class, three realistic-power worlds with the effect at the measured
size of the across-sorbent spread of k″ plus end-point offsets, six structure-free null worlds
with sorbent-level rate and end-point deviations independent of the isotherm, and a form-error
world; its pass criteria and the role of each world are in PREREG §10b.

## Descriptive analyses

H4b reports, per held-out sorbent, the fraction of the gap between B0 and F that the oracle B0*
closes; an in-sample version was seen before the freeze [src: PREREG §2]. An end-point oracle
re-scores B0 with its branches scaled by the held-out sorbent's own equilibrium offsets
(estimated from equilibrated segments ending above 0.2 w₃₀), separating the part of B0's error a
correct end point removes from the part a correct k″ removes [src: PREREG §8; p4/run_study.py
endpoint_eps]. H4c compares LOSO and family-level errors without a test [src: PREREG §2].

## Software and data availability

Code, pre-registration, harness records and every results file: VENUE-specific repository and
Zenodo deposit (to be created). Python, NumPy, SciPy, PyTorch (versions in requirements file).
