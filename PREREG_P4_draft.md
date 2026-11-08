# Pre-registration (DRAFT, not frozen): Paper 4

**Working title.** Does learning beat the isotherm? A held-out-material test of water-sorption
cycle dynamics for ten sorbents.

**Status.** Draft written 2026-11-03 for the author's review. Nothing in it has been run on
real data except what section 9 lists as allowed before the freeze. When frozen, the commit
hash goes in section 12 and no confirmatory number exists before that commit.

---

## 1. Question

When a sorbent has never been seen in training, can a learned dynamic model predict how its
water uptake rises and falls over time better than the published isotherm-driven model?
Both models are driven by measured humidity and temperature, and both are told only the new
sorbent's water isotherms.

The data are milligram powder layers on a dynamic vapour sorption (DVS) balance: 8 sorbents
from Bezrukov et al. 2023 and 2 MOFs from Gao et al. 2026, all from one laboratory. All
claims stay at that scale. The words "harvester", "device" and "digital twin" are not used for
the results.

## 2. Hypotheses

- **H4a, primary.** A learned model, given only the held-out sorbent's isotherms, predicts its
  uptake trajectories more accurately than the best per-fold refitted isotherm-only physics
  model (B0, B0-b or B1, chosen on the validation sorbent; section 5), by more than the
  measured noise floor and by a practically relevant margin. L1 (grey box) is the primary
  learned model and L2 (black box) the secondary one; only L1 can support the headline claim.
- **H4b, descriptive.** How much of B0's error on a held-out sorbent comes from the assumption
  that the rate constant is the same for every material. Measured as the fraction of the gap
  between B0 and the noise floor that the oracle B0* closes (B0 with k″ fitted on the held-out
  sorbent itself, by the scored metric). It is not a confirmatory test: an in-sample version of
  both quantities was seen before the freeze (section 12), and it closed at most a third of the
  gap for every sorbent.
- **H4c, descriptive.** Holding out whole families degrades every model more than holding out
  single sorbents does. Only two of the four LOFO folds differ from a LOSO fold (section 4), so
  this is reported descriptively, without a significance test.

H4a has a decision rule and a falsifier in section 7; H4b and H4c are estimates with intervals
and no verdict.

## 3. Data

### 3.1 Sources (all verified and checksummed in `DATA_SOURCES.md`)

- Bezrukov et al. 2023, Zenodo 6631711, CC BY 4.0: the training and test pool.
- Gao et al. 2026, Nat. Commun. 17, 9494, Source Data, CC BY-NC-ND 4.0: external test only (section 3.4).

### 3.2 Inclusion: the primary set P

For each of the 8 sorbents and the 2 composites, P contains:

- all step-run files at 27 and 60 °C;
- all 0↔30 % cycling files at 27 °C;
- the isotherm files at both temperatures.

Excluded from P and reserved for secondary analyses (section 8):

- the particle-size fractions;
- the packing and pan variations, whose different pans change the bed area A;
- the carrier-gas flow variation;
- the two 100-cycle runs;
- the cellulose isotherm.

Isotherm choices fixed now:

- ROS-037 and Syloid have 27 °C-level isotherms whose set-point is 25 °C. They are used as the
  27 °C isotherms, as in the original paper, and flagged.
- MOF-303 has two 60 °C isotherms. The file named `..._50-100um_60C_isotherm...` is used; the
  other is used only in a sensitivity check.
- Each composite's 27 °C isotherm appears in the archive twice, in its main folder and in the
  `hm` folder. The two files have identical mass traces (checked 2026-11-08), so there is one
  isotherm, not two. The earlier draft's "later file, other one as a sensitivity check" was
  wrong and is withdrawn.
- These choices were fixed on 2026-11-03 from file names alone, before any model was fitted.
  For MOF-303 the 50–100 µm isotherm matches the 50–100 µm fraction of every step run in P.

**Exact duplicates.** The archive holds 8 files whose mass trace is identical to another file's
(`p4/data.py`, `duplicate_files`). One of them was inside P: the MOF-303 60 °C 5 mg step run,
exported under two file names. Every analysis keeps the copy in the sorbent's main folder and
drops the rest. The pre-freeze numbers in section 12 were recomputed after this fix.

**Files in P** are listed per sorbent and temperature in `results/prefreeze/checks2.json`. The
two ROS-037 27 °C files named `400flow-…flowRateVariation` are the 400 sccm runs of the flow
series; they use the standard flow and stay in P. The other flow levels stay excluded.

### 3.3 Variables

- **Target.** Uptake w(t) in wt% = 100·(m − m_dry)/m_dry, with m_dry the sample's dry mass.
  The instrument's own "reference mass" (mass at the end of the first 0 % stage) is not used,
  because in the cycling runs that stage lasts minutes and the sample is not dry: in one Syloid
  cycling file the reference is 21.11 mg while the mass falls to 18.89 mg.
  - Step runs and most isotherm runs begin with an activation stage under gas preheated to
    100 °C, followed by a 0 % RH plateau at the sorption temperature.
    - **Primary rule R2:** after the heated activation, the 0 % set-point continues with the
      preheater off for 70 to 229 minutes (median 90). m_dry is the median mass over the last
      minute of that stretch, measured under the same gas and temperature as the rest of the
      run. It applies to all 65 activated step runs and all 18 activated isotherm runs. The
      isotherm takes this reference as its first point, with uptake 0 at its measured RH.
    - **Sensitivity rule R1:** the last minute of the heated activation itself.
    - Why R2 (2026-11-08, data only, `results/prefreeze/dry_rules.json`): R1 and R2 differ by
      −3.5 % to +6.2 % of the dry mass. The activation mass reads high in most runs, which
      fits buoyancy and thermal effects of the hot gas. In MOF-303 and Syloid it reads low,
      which fits re-adsorption at the instrument's real "0 %" (0.1 to 1.2 % RH).
    - **Primary criterion, isotherm-free (review finding M8):** a dry mass should be taken where
      the mass has stopped changing. The mass drift over the last 10 minutes of each window
      (`results/prefreeze/checks2.md`) has a median magnitude of 0.023 %/h for R2 against
      0.106 %/h for R1 (80 runs each). At the end of R1 the sample is still losing mass in 32 of
      the 33 run groups with both windows (kind × sorbent × temperature).
      R2 is near zero except in MOF-303, where the mass is rising (step runs +1.6 %/h at 27 °C;
      isotherm runs +1.1 and +0.6 %/h), consistent with re-adsorption at the instrument's real
      "0 %"; Syloid step runs at 27 °C (+0.35 %/h); and the Syloid isotherm at 60 °C (−0.7 %/h).
    - Supporting check, which uses the isotherm and so was not the basis of the choice: how well
      equilibrated step end-points agree with the isotherm at the same measured RH. Median over
      the 18 sorbent–temperature groups: R2 0.50 wt%, R1 0.79 wt%. The rule was first
      chosen on this check (2026-11-08) and re-justified by the drift criterion the same day,
      after the review pointed out that agreement with the isotherm moves the target toward the
      baseline's own input (section 13).
    - R2 is worse on the supporting check for Al-fumarate at 60 °C and for MOF-303, so every
      confirmatory result is also computed under R1, and the H4a verdict must agree under both
      (section 7).
    - A third rule, R3 (the end of the first desorption step), was measured by mistake (section
      13): median 0.61 wt%. It is not used.
  - Exception, measured 2026-11-04: the two composites' 27 °C step runs were dried only at
    27 °C, for 26 to 64 minutes, and were still losing 0.3 to 0.9 % of their mass per hour
    when the 0 % stage ended. Their dry mass is not established, so these runs are excluded from
    P and used only in a sensitivity check. The isotherm runs dried without a heated stage (the
    MIL-160 and ROS-039 isotherms and Syloid at 25 °C) had stopped changing (drift at most
    0.17 % per hour) and are kept.
  - Cycling runs have no drying stage. Bezrukov's own code back-calculates m_dry by assuming
    that the highest mass in the run equals the isotherm's uptake at 30 % RH. That makes the
    measured uptake depend on the isotherm, which is also the baseline's input, so it is not
    used. An open-loop simulation needs w(0) and 1/m, and both need m_dry, so a cycling run
    without its own dry mass cannot be simulated fairly. **Rule (fixed now):** the cycling runs
    are excluded from every confirmatory comparison. They enter only the secondary analyses of
    section 8, and only where the same physical sample can be tied to a drying stage in an
    adjacent file (same pan, same session, no handling in between); that check is done from the
    file metadata alone before the freeze.
- **Forcing.**
  - Measured RH (not the set-point).
  - Measured sample temperature.
  - The sample's dry mass, which with a fixed pan sets the layer thickness.
- **Material description.** The held-out sorbent's adsorption and desorption isotherms at 27
  and 60 °C. Each isotherm is taken as the equilibrium uptake at the end of each RH plateau
  of its isotherm file, by a rule fixed in code before the freeze. Nothing else about the
  material is given: no name, no family label, no kinetics.
- **Grid.** Trajectories are linearly resampled to a uniform 6 s grid. The fastest
  time-to-63 % in P is 1.1 min, so this keeps at least 11 points inside every time constant.

### 3.4 Gao 2026 (bnn-1-Co, bnn-1-Ni): external test only

Gao's flow rate is not reported, and the Source Data step curves give set-point RH, not
measured RH. The two MOFs are therefore never used for training or tuning. All models are
trained on the full P, then evaluated on:

- the Fig. 3c/d step curves, driven by set-point RH and flagged;
- the 128-cycle 27 °C runs, which have logged RH.

These results are reported separately from H4a. If the authors confirm the protocol (flow and
pan identical to Bezrukov's), the bnn MOFs become a fifth family in H4c. That decision has to
be made and recorded before any model is evaluated on them.

### 3.5 Units of evaluation

- **Step segment.** One RH plateau of a step run, from the change of set-point to the next
  change.
- **Cycling run (secondary analyses only; section 3.3).** One whole cycling file, simulated
  open-loop from its first point, with no resetting to measured values at any later time.

## 4. Folds

- **Paired samples and inference clusters.** 31 groups of runs share a start timestamp (`results/prefreeze/summary.md`, after the duplicates were dropped): two
  samples measured together on a two-pan instrument, sharing their forcing. Measuring sessions
  are few: MOF-303 has one session at each temperature and Al-fumarate one at 60 °C
  (`results/prefreeze/checks2.md`). Sessions alone therefore cannot carry a per-sorbent test.
  The inference cluster is **one RH step (from-RH, to-RH) in one session**: both pans and all
  repeats of that step are averaged into one cluster value. Inference is thus over the
  humidity conditions measured for a sorbent, given the samples measured; the paper does not
  claim generalisation to new samples of the same sorbent beyond the pans in the archive.
- **Sessions that mix sorbents.** Three kinds of two-pan sessions hold two different sorbents:
  CAU-10-H with MIL-160 (2021-08-27), ROS-040 with Syloid (2021-08-28), and the two composites
  (six sessions, 2022-04-28 to 05-03). Pans that share a session share their measured forcing,
  but no uptake trace is shared, so this is no leakage of the target. Clusters are formed
  within one sorbent.
- **Gas flow (checked per plateau, 2026-11-08; `results/prefreeze/checks2.md`).** All 1,212
  step plateaus and all 1,612 cycling plateaus in P ran at a logged total flow of 400 sccm, and
  none lacks a value. The isotherm runs used 50 sccm, which does not matter at equilibrium. The
  paper states 200 mL/min, plausibly per pan; this matters only for pooling with Gao 2026.
- **LOSO (leave one sorbent out).** Eight folds, one per Bezrukov sorbent. A composite is
  always held out together with its parent, so ROS-037 with the ROS-037 composite, and ROS-039
  with the ROS-039 composite.
- **LOFO (leave one family out).** Four folds:
  - aluminium carboxylate rods: MOF-303, MIL-160, CAU-10-H, Al-fumarate;
  - zinc triazolate fluorides: ROS-039, ROS-040, ROS-039 composite;
  - ROS-037 and its composite;
  - Syloid AL-1.

  The last two hold out exactly the sorbents of the ROS-037 and Syloid LOSO folds, with the same
  training set and validation sorbent. They are not new tests, and only their seeds differ.
  The family rule (section 7) therefore rests on the two folds that hold out a whole family:
  the aluminium rods and the zinc triazolates.

In every fold, everything that is fitted is fitted on the training sorbents only:

- model parameters;
- the baseline rate constants;
- the normalisation statistics;
- the hyperparameter choice.

## 5. Models

- **B0, the baseline: Bezrukov's model as published** (his code read 2026-11-03).
  - Equation: dw/dt = k·(RH_flow − RH_bed(w)), with separate rate constants for uptake
    (RH_flow > RH_bed) and release (RH_flow < RH_bed).
  - RH_bed(w) is the inverse of the adsorption branch of the held-out sorbent's isotherm, in
    both directions, as in the published code. Interpolation is monotone.
  - k = k″/m, with k″ fitted by least squares on the training sorbents only. It is fitted
    separately for each temperature and direction, and pooled across materials: the
    "independent of the material" assumption, refitted per fold.
  - The published code can rescale the isotherm to match a kinetic run ("scale_isotherm"). That
    uses the held-out sorbent's own kinetics, so it is forbidden here for every model.
  - Variant B0-b: the same, but reading the desorption branch during release.
- **B1, the second baseline: linear driving force.**
  - Equation: dw/dt = k_LDF(T, m)·(w*(RH_flow) − w), with k_LDF = k‴(T)/m, fitted the same way.
- **The comparator for H4a** is whichever of B0, B0-b and B1 has the lowest median E on the
  fold's validation sorbent, the same choice the learned models get. A learned model that beat
  B0 but not B1 would not have beaten "the isotherm".
- **B2, reported comparator (not in the decision rule).** B0 with k″ made material-dependent
  in the simplest way an isotherm allows: log k″ = a + b·(RH₅₀/30 %), where RH₅₀ is the RH at
  which the adsorption branch reaches half its uptake at 30 % RH. a and b are fitted per
  temperature and direction on the training sorbents. If L1 beats the comparator but not B2,
  the paper says that a two-parameter isotherm descriptor does as well as learning.
- **B0\*, the oracle.** B0 with k″ fitted on the held-out sorbent's own data by minimising the
  scored metric (the median E over its segments; a log-grid search then a bounded refinement),
  not least squares. Least squares is not the scored metric, so in 7 of 36 in-sample strata a
  least-squares "oracle" scored worse than the pooled k″. It is not a competitor; it measures
  how much any choice of a single k″ could gain (H4b).
- **Initial state.** Every model starts a step segment from the measured uptake at its first
  grid point (the first sample after the set-point change), and runs open loop to the end of
  the segment with no later resetting.
- **L1, grey box.**
  - Equation: dw/dt = k(T, m)·(RH_flow − RH_bed(w))·exp(g_θ(z)).
  - The correction is a positive factor, so the rate is still zero at equilibrium and the
    model cannot produce uptake against the driving force.
  - z holds: w normalised by the isotherm's uptake at 30 % RH; RH_flow; RH_bed; the local
    isotherm slope dw/dRH at w; the branch flag; T; and 1/m.
- **L2, black box: a neural ODE.**
  - Equation: dw/dt = (S/m)·f_θ(z), with S = 10 a fixed unit scale. Since w = 100·(water
    mass)/m_dry, f_θ is the water mass flux into the sample; the factor 1/m is a unit identity,
    not a physical assumption.
  - z holds local isotherm features at the current state, the same information L1 receives:
    w/w₃₀; RH_flow; the equilibrium uptake on both branches at the current RH (/w₃₀); the bed RH
    on both branches at the current uptake; the adsorption-branch slope at w; T; and 1/m.
  - No physics is imposed: no sign constraint, no zero rate at equilibrium.
  - History of this design (section 10): a global 44-number isotherm encoding let the network
    memorise material identity (round 2), and an output scaled by w₃₀, a per-sorbent number the
    network never sees, made the rate scale of a new sorbent unknowable (round 3).

Implementation and training rules:

- L1 and L2 are small multilayer perceptrons, trained in two stages (changed after harness
  round 1, section 10):
  - stage A fits the rate law to the measured dw/dt, a centred difference over ±18 s, with each
    point's error divided by its segment's change;
  - stage B fine-tunes on open-loop rollouts over random 10-minute windows, started from the
    measured uptake.
  Validation on whole segments, open loop, picks the best state. Backpropagating through whole
  segments, the first design, took about 2.5 hours per 300 steps on this machine. It left L1
  unable to learn a correction that was present and L2 badly undertrained.
- Each learned model is an ensemble of 5 seeds, and its prediction is the ensemble mean.
- Hyperparameters are chosen within each outer fold on one validation sorbent taken from the
  training sorbents, from a grid fixed here: width {16, 32}, depth {2}, weight decay
  {1e-4, 1e-3}, learning rate {1e-3}. The comparator choice (B0, B0-b or B1) is made the same way.
- Stage A's centred difference over ±18 s spans about half of the fastest time-to-63 % (1.1
  min), so it smooths the onset of the fastest steps. Stage B trains on the trajectories
  themselves, so this affects only the starting point of training, not the scored quantity.
- **A model that fails the synthetic harness (section 10) is dropped from H4a**, and the paper
  says so.
  - The validation sorbent is Syloid AL-1, except in folds that hold Syloid out, where it is
    ROS-040. If ROS-040 is held out too, it is CAU-10-H.
  - The same validation sorbent serves for early stopping.
  - The outer held-out sorbent is never used for any choice.
  - Full inner leave-one-sorbent-out would be cleaner but costs about seven times more (section
    11). A single validation sorbent makes the choice noisier, not leaky.

## 6. Metrics

- **Primary metric.** The normalised trajectory error of a step segment, E = RMS(w_pred −
  w_meas) / |Δw|, where Δw is the measured change over the segment. Per held-out sorbent, its
  score is the median E over its segments.
- **Noise floor F.**
  - Within a step-run file, the same step (same from- and to-RH) is repeated, from the second
    repeat onwards.
  - For each pair of consecutive repeats, the two trajectories are aligned on time since the
    step and compared with the same normalised RMS.
  - Per sorbent and temperature, F is the median over its pairs. The F used in the decision rule
    is one number per sorbent: the segment-weighted mean of its two temperature values
    (`results/prefreeze/checks2.json`, `F_within_segment_weighted`). A fold that holds out
    several sorbents uses the largest.
  - F is computed before the freeze (section 9) and recorded in section 12.
  - **Between-pan and between-session agreement**, the same step compared across files of one
    sorbent, is reported beside F as a ceiling, not a floor: pans and sessions differ in sample
    mass, and the rate scales with 1/m, so their disagreement mixes noise with a real,
    modelled effect. It is 0.034 to 0.374 (section 12).
- **Segment inclusion.** A step segment is scored only if its measured change |Δw| is at least
  0.05 wt% (`p4/dataset.py`); E is undefined as |Δw| → 0. The rule is applied to the measured
  data before any model is run, so it is the same for every model.
- **Aggregation.** A sorbent's score pools all its segments at both temperatures and in both
  directions. Composite segments count towards the fold of their parent, with which they are
  held out. Temperature and direction strata are also reported separately.
- **Secondary metrics.**
  - The relative error in time-to-63 % per segment.
  - For the cycling runs, the relative error in steady-state productivity: the mean uptake
    swing per unit time over the last three cycles, the definition Bezrukov uses.
  - E truncated at five times the segment's measured time-to-63 %, so that long equilibrium
    tails of experimenter-chosen length do not dilute the error of the transient.
  - Physical violations: the fraction of held-out segments on which a model's uptake moves
    against the direction of the set-point step (falls after a rise in RH, or rises after a
    fall) by more than 0.05 wt% over any 1-minute window. The measured data's own rate is the
    floor (section 12). Tests against the isotherm-derived driving force or the isotherm itself
    were considered and rejected before any model was run, because the measured data fail them
    in 50 to 100 % of segments: measured equilibria differ from the isotherm. L1 cannot violate
    the isotherm by construction; L2 can do anything.

## 7. Decision rules and falsifiers

**Beating the comparator in a fold.** Per held-out sorbent, let d = E_comparator − E_model per
segment, averaged within each cluster (one RH step in one session; section 4). A learned model
"beats the comparator" in the fold if all three hold:

1. the median of the cluster values of d exceeds that sorbent's F (section 6);
2. the median of d is at least 10 % of the comparator's median E over the same clusters
   (practical significance);
3. a one-sided exact Wilcoxon signed-rank test of d over clusters gives p ≤ 0.025 (exact null
   distribution over all 2ⁿ sign vectors, average ranks for ties, computed by counting subset
   sums so that it is exact for any n).

This is one statistic throughout, the paired difference, and `p4/decide.py` implements exactly
this text. The signed-rank statistic replaces the median in the test because the median ties
heavily under sign flips (six equal gains give p = 0.34, not 1/64). The attainable minimum p
is 2⁻ⁿ for n clusters, so a sorbent with fewer than 6 clusters cannot be beaten; the cluster
counts are recorded in section 12 before the freeze.

The order of events matters for condition 2. The 10 % threshold was proposed on 2026-11-04,
after the noise floor (F medians 0.001 to 0.013) and the in-sample B0 reproduction were seen,
and before any learned model was fitted to real data. It exists because F alone would count
almost any improvement as real. It is the author's to confirm or change at the freeze.

**Physical admissibility.** A model whose violation rate on a held-out sorbent (section 6)
exceeds the measured data's own rate by more than 5 percentage points does not beat the
comparator in that fold, whatever its E.

**H4a**, decided on the 8 LOSO folds, separately for L1 (primary) and L2 (secondary):

- **Supported** if the model beats the comparator in at least 7 of 8 folds. This is a
  decision rule, not a p-value. The folds share most of their training sorbents, so a sign-test
  p would overstate the evidence.
- **Falsified** only if an interval excludes the declared effect: the 95 % bootstrap interval,
  over the 8 folds, of the mean relative improvement (median d divided by the comparator's
  median E) lies wholly below 10 %.
- **Not established** otherwise, including a moderate real effect that the 8 folds cannot
  resolve.
- The headline claim rests on L1. An L2 result is reported as secondary. If only L2 meets the
  rule, the paper says so and does not claim H4a.
- The verdict must be the same under the primary dry-mass rule R2 and the sensitivity rule R1.
  If it differs, H4a is reported as not robust to the dry-mass definition, and the weaker of
  the two verdicts is the result.

**Transfer across families.** A model that is supported on LOSO transfers across families if it
also beats the comparator on both non-trivial LOFO folds (aluminium rods; zinc triazolates).

**Complete verdict table** (per model; LOSO beats out of 8; non-trivial LOFO beats out of 2):

| LOSO beats | Interval below 10 % | LOFO beats | Verdict |
|---|---|---|---|
| 7 or 8 | (not used) | 2 | supported, transfers across families |
| 7 or 8 | (not used) | 0 or 1 | supported within families; does not transfer across families |
| 0 to 6 | yes | any | falsified |
| 0 to 6 | no | any | not established |

**H4b and H4c** are estimates with bootstrap intervals and carry no verdict (section 2).

**Negative results.** If L1 and L2 both fail H4a, the paper reports that, on these data, a
learned dynamic model adds nothing measurable to the isotherm. Section 8's analyses are then
used only to say where the residual error lives, not to rescue the claim.

## 8. Secondary and exploratory analyses (labelled as such in the paper)

- Generalisation to the excluded protocol variations, with every model trained on P only:
  carrier-gas flow, particle size, pan and packing, and the 100-cycle runs (error growth over
  long open-loop horizons).
- The Gao bnn external test (section 3.4).
- The device illustrations: Song 2023 (MOF-303, three Death Valley cycles, six per-test yields)
  and Almassad 2022 (MOF-801, nine cycles), using the sorbent model driven by the logged air
  conditions. These are clearly bounded illustrations, not validation. Device yields are
  condenser water and include transport the model does not contain.
- Temperature-swing cycles. There are no measured ones. Any predicted temperature-swing
  productivity is labelled as an extrapolation from two isothermal levels.

## 9. Allowed before the freeze

- Building and testing the data pipeline: extraction, resampling, segmentation, isotherm
  end-point rule.
- Computing the noise floor F (data only, no model).
- Measuring how far the end-points of the step runs fall from the isotherm at the same RH
  (data only). This shows how much error any isotherm-driven model inherits from a mismatch
  between runs, before any model is fitted.
- Reproducing Bezrukov's published fits, B0 fitted on all eight sorbents, as a check of the
  implementation against the paper. This is in-sample, involves no learned model, and is
  reported as a reproduction.
- Further data-only checks asked for by the review: per-plateau gas flow, cluster counts,
  between-file agreement, mass drift at the dry-mass windows, and the data's own rate of
  physical violations (`audit/prefreeze_checks2.py`, `audit/violation_floor.py`).
- A synthetic test of the harness (section 10), including the size calibration of the null
  world (`audit/null_calibration.py`) and the null study through the confirmatory code.
- Timing runs of L1 and L2 on synthetic data to fix the compute budget.

Not allowed before the freeze: fitting L1 or L2 on real data, and any held-out evaluation.

## 10. Synthetic harness test (must pass before the freeze)

Synthetic trajectories are generated on the real forcing and real isotherms of P from a known
truth, and the fold pipeline is run on them (`audit/synthetic_harness.py`). Three worlds:

- **N, no correction:** truth = B0 with the pooled k″ of the real data.
- **C, a learnable correction:** truth = B0 × exp(−0.7·w/w₃₀), a material-independent slow-down
  near saturation that a model given only the isotherm can learn. On the two held-out test
  sorbents it raises B0's median E from about 0.0005 (case N) to 0.036 and 0.041.
- **Null, realistic (review finding F2):** every sorbent deviates from B0 by its own rate
  factor exp(b_s + a_s·(w/w₃₀ − ½)), with b_s ~ N(0, 0.3²) and a_s ~ N(0, 0.6²) drawn
  independently of anything in the isotherm; AR(1) measurement noise (σ = 0.01 wt%, φ = 0.9).
  With these sizes B0's median E over the eight sorbents is 0.064 to 0.081 in three
  replicates, and 0.021 to 0.205 per sorbent (`results/null_calibration.json`, computed before the
  duplicate fix), inside the range B0 shows on the real data. A model given only the isotherm cannot predict these deviations, so any "beat" here is
  a false positive.

The harness passes if:

1. in world N, B0 refitted on the training sorbents recovers k″ within 2 %;
2. in world C, L1 beats B0 by the section 7 rule on both held-out sorbents and halves B0's
   median E (the injected effect; this number was set after round 2, which met it);
3. in world N, neither learned model beats B0 (a check that is weak by itself: noise-free data
   put E_B0 below every F, so condition 1 of the rule blocks a beat whatever the model does;
   in round 2, L1's median paired gain on the MOF-303 null fold was 24 % of E_B0 with its
   bootstrap interval above zero, so only F stopped a beat; on ROS-039 it was 6 %;
   `results/harness_round2/harness.json`);
4. **in the null world, run through the confirmatory runner and decision script themselves**
   (`p4.run_study --synthetic null`, `p4.decide`) on all 8 LOSO folds, with one configuration
   and one seed per fit, the per-fold false-positive rate of each learned model is estimated
   from all its null fold-fits. H4a can be declared only if that rate's one-sided 95 % upper
   bound implies P(≥ 7 of 8 beats) ≤ 5 % under independence (`audit/null_summary.py`). With
   16 fold-fits this allows at most about 2 null beats. The folds share training sorbents, so
   independence is optimistic; the beats per replicate are reported as well. The number of
   replicates is set by the compute available and stated; at least 2 (16 fold-fits per model).

**Round 1 (2026-11-04/05; `results/harness_round1/`)**, with whole-segment training. Seven of
the eight runs finished before it was stopped:

- no false positive for L1;
- L1 missed the injected correction (E 0.034 against B0's 0.036);
- L2 failed even on correction-free data (E 0.27 to 0.58);
- the decision rule compared a difference of medians with a bootstrap of paired medians. It
  now uses the paired difference throughout.

**Round 2 (2026-11-07/08; `results/harness_round2/`)**, two-stage training. Criteria 1 to 3
passed: k″ recovered within 0.2 %; L1 found the correction (E 0.036 → 0.015 on MOF-303, 0.041 →
0.019 on ROS-039); no beat in world N. L2 fitted the training sorbents (loss ≤ 0.009) but not an
unseen one (validation E 0.35 to 0.44): with a global 44-number isotherm encoding it memorised
material identity. L2 was rebuilt on local isotherm features.

**Round 3 (2026-11-08; `results/harness_round3/`), L2 only.** In world N the rebuilt L2 still
did not transfer: E 0.21 on MOF-303 and 0.19 on ROS-039, against B0's 0.0004 and 0.0006 (no
false positive, but no competitor either). Cause: its output was scaled by w₃₀, a per-sorbent
number the network never sees, so the rate scale of a new sorbent was unknowable. The output
is now a water mass flux (section 5). Round 3 was stopped during world C, since that run would
have measured the same flaw.

**Round 4**: ROUND4.

## 11. Compute

Measured in harness round 2 (`results/harness_round2/harness.json`, six or seven training
sorbents per fit, on the shared laptop): one L1 fit took 39 to 55 minutes (mean 45.5), one L2 fit
13 to 36 minutes (mean 19.9). Round 4 times replace the L2 figure when it finishes.

The protocol has 10 outer folds (8 LOSO and the 2 LOFO folds that differ from them; section 4).
Per model and fold: 4 configurations × 1 seed for tuning, then 5 seeds of the chosen one, so
9 fits. That gives 90 fits per model:

| Item | Fits | Hours (single job) |
|---|---|---|
| L1, primary rule R2 | 90 | about 68 |
| L2, primary rule R2 | 90 | about 30 |
| R1 sensitivity, reusing each fold's R2 configuration (5 seeds only) | 100 | about 54 |
| Null study, 2 replicates × 8 folds × 2 models, 1 configuration, 1 seed | 32 | about 18 |
| Physics baselines, B2 and oracle fits | — | under 3 |
| **Total** | 312 | **about 173** |

The R1 sensitivity run reuses the configuration chosen under R2 in each fold. It asks whether
the dry-mass definition changes the verdict, not whether tuning changes it.

**Pre-registered reduction order**, applied only if the full protocol cannot be run, decided
and recorded at the freeze (before any real-data fit exists) and never afterwards:

1. seeds per ensemble 5 → 3;
2. tuning grid 4 → 2 configurations (width 32; both weight decays);
3. the null study's second replicate dropped, with the false-positive bound computed from 8
   fold-fits per model and stated as such.

Full inner leave-one-sorbent-out would add roughly 300 h and is not planned. The jobs are
independent, so they can run as parallel CPU jobs elsewhere (for example the author's Kaggle
account) without changing any result. Every job writes a resumable row; a fit counts only if it
completed. The final run times are reported.

## 12. Freeze record

Not frozen. Pre-freeze measurements, recomputed on 2026-11-08 after the duplicate exports were
dropped (section 13). All are data-only or in-sample; none evaluates a learned model on real data.

- **Noise floor F** (within-file test-retest: median normalised RMS between repeats of the same
  step in the same file; `results/prefreeze/checks2.md`). F is a ratio and is the same under R1
  and R2 to the fourth decimal.

| Sorbent | 27 °C (pairs) | 60 °C (pairs) | F used in section 7 (segment-weighted) | clusters |
|---|---|---|---|---|
| ROS-037 | 0.0020 (16) | 0.0050 (28) | 0.0040 | 26 |
| ROS-039 | 0.0018 (16) | 0.0029 (13) | 0.0023 | 26 |
| ROS-040 | 0.0035 (16) | 0.0066 (21) | 0.0054 | 35 |
| MOF-303 | 0.0019 (8) | 0.0050 (14) | 0.0039 | 13 |
| MIL-160 | 0.0026 (16) | 0.0044 (21) | 0.0037 | 35 |
| CAU-10-H | 0.0009 (16) | 0.0028 (21) | 0.0021 | 35 |
| Al-fumarate | 0.0014 (12) | 0.0126 (14) | 0.0078 | 17 |
| Syloid | 0.0011 (16) | 0.0058 (28) | 0.0042 | 35 |
| ROS-037 composite | excluded | 0.0062 (42) | 0.0062 | 54 |
| ROS-039 composite | excluded | 0.0062 (42) | 0.0062 | 54 |

- **Inference clusters** (one RH step in one session, both temperatures;
  `results/prefreeze/cluster_counts.json`, identical under R1 and R2): 13 to 54 per sorbent, so
  every held-out sorbent can reach p ≤ 0.025 (minimum attainable p 2⁻¹³ for MOF-303).
- **F_between** (same step and repeat in another pan or another session): 0.066 to 0.216
  between pans and 0.034 to 0.374 between sessions. It is reported as a ceiling only.
- **Dry-mass rules** (section 3.3): end-of-window drift, median |drift| 0.023 %/h (R2) against
  0.106 %/h (R1) over 80 runs. Step end-points minus the isotherm at the same measured RH, median
  per sorbent–temperature group: −1.16 to +3.13 wt% under R2 (median of the absolute values
  0.50 wt%) and −1.80 to +2.78 wt% under R1 (0.79 wt%); worst single point 9.8 wt% under R1
  (Al-fumarate, 60 °C; `results/prefreeze/summary.md`). Every isotherm-driven model inherits this
  error.
- **In-sample reproduction of B0** (`results/prefreeze/reproduce_b0.json`, R2; per-material and
  pooled fits, no held-out evaluation):
  - At 27 °C the per-material k″ agree across the eight sorbents: coefficient of variation 0.07
    for uptake and 0.11 for release (sample SD; 0.07 and 0.10 with the population SD),
    reproducing Bezrukov's "independent of the material" there.
  - At 60 °C they do not: 0.42 and 0.30 (population SD 0.39 and 0.28). CAU-10-H uptake has
    k″ = 3.16 against 1.59 pooled.
  - Even with its own k″, B0's in-sample median E is 0.022 to 0.237 (0.018 to 0.236 when k″ is
    fitted by the scored metric). That is 3.5 to 67 times the noise floor, median 15 over the 32
    strata (sorbent × temperature × direction). The remaining error lies in the model's form.
  - Under R1 (`reproduce_b0_R1.json`): coefficients of variation 0.08, 0.10, 0.42, 0.29
    (population SD); E 0.018 to 0.206.
- **Physical-violation floor** (section 6; `results/prefreeze/violation_floor.json`): the share of
  measured segments in which uptake moves against the step direction for a minute is 0 for the
  three ROS sorbents, Syloid and both composites; 0.04 for MIL-160, 0.06 for CAU-10-H, 0.15 for
  Al-fumarate and 0.28 for MOF-303.
- **Null-world size** (section 10; `results/null_calibration.json`): B0's median E in the null
  world, over all eight sorbents, is 0.080, 0.064 and 0.081 for replicates 0 to 2, inside the
  range seen on the real data.
- Commit hash, date and compute budget: to be filled at the freeze.

## 13. Corrections to this draft

- 2026-11-08. The first implementation of rule R2 did not do what section 3.3 described.
  Plateaus are split only on RH set-point changes, so the activation and the 0 % stretch after it
  form one plateau, and the code picked the next unheated 0 % plateau instead: the end of the
  first desorption step. Its comparison ("R2 better in 12 of 18 groups") therefore described
  another rule, now named R3. Found because the isotherms of the data figure vanished when the
  isotherm builder was changed to start at the reference. Corrected R2 is implemented in
  `p4/segments.py`; the comparison was rerun for R1, R2 and R3. The first-run numbers stay
  quoted here; the rule choice (R2) is unchanged, now with the correct numbers.
- 2026-11-08. **Exact duplicate exports.** Eight files in the archive repeat another file's mass
  trace exactly. One was inside P: the MOF-303 60 °C 5 mg step run, exported under two names, so
  its segments were counted twice in every pre-freeze number. Each composite's "two" 27 °C
  isotherms are one file in two folders, so the planned sensitivity check between them was void.
  Found while checking the file lists the review asked for. Duplicates are now dropped in one
  place (`p4/data.py`, `duplicate_files`), and every pre-freeze number in section 12 was
  recomputed (`audit/rerun_prefreeze.sh`).
- 2026-11-08. **Dry-mass rationale.** R2 was first chosen by how well step end-points agree with
  the isotherm. The review (finding M8) pointed out that this moves the target toward the
  baseline's own input. R2 is now justified by an isotherm-free criterion, the mass drift at the
  end of each window (section 3.3), which gives the same choice. The end-point check stays as
  supporting evidence.
- 2026-11-08. **L2 output scale.** Round 3 of the harness showed that L2's output, scaled by w₃₀,
  depended on a number the network never sees. The output is now a water mass flux (section 5).
- 2026-11-08. **Decision statistics** (review findings F1, M1, M3–M7). The paired difference is the
  only statistic. Per-fold inference uses session × step clusters and an exact signed-rank test,
  in place of a bootstrap over sessions, which are as few as one per temperature. Falsification
  needs an interval. L1 is primary. The comparator is the best of B0, B0-b and B1. The oracle is
  fitted by the scored metric. H4b and H4c are descriptive, and the family rule uses the two
  non-trivial LOFO folds. A realistic null world is added to the harness.
- 2026-11-08. **Cluster key and exact test.** A code check against section 4 found that the
  cluster key in `p4/run_study.py` (`seg_ids`) still held the plateau number, so every repeat of a
  step was its own cluster, against the text. Fixed, with a unit test. Clusters are now 13 to 54
  per sorbent (section 12), not 36 to 144. The signed-rank test now uses its exact null
  distribution for any number of clusters; before, it switched to Monte Carlo above 16. Neither
  change touched any real-data result: no learned model had been evaluated on real data.
