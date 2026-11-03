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
  uptake trajectories more accurately than the per-fold refitted isotherm-driven baseline B0,
  by more than the measured noise floor.
- **H4b.** Most of B0's error on a held-out sorbent comes from the assumption that the rate
  constant is the same for every material, not from the form of the model. Test: the oracle
  B0* (B0 with its rate constant fitted on the held-out sorbent itself) closes more than half of
  the gap between B0 and the noise floor.
- **H4c.** Holding out whole families degrades every model more than holding out single
  sorbents does. Reported descriptively; four families cannot support a significance test.

Each hypothesis has a falsifier in section 7.

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
- Each composite has two 27 °C isotherms. The later file is used; the other is used only in a
  sensitivity check.

### 3.3 Variables

- **Target.** Uptake w(t) in wt% = 100·(m − m_dry)/m_dry, with m_dry the sample's dry mass.
  The instrument's own "reference mass" (mass at the end of the first 0 % stage) is not used,
  because in the cycling runs that stage lasts minutes and the sample is not dry: in one Syloid
  cycling file the reference is 21.11 mg while the mass falls to 18.89 mg.
  - Step runs begin with an activation stage under gas preheated to 100 °C. m_dry is the median
    mass over the last minute of that stage.
  - Cycling runs have no drying stage. Bezrukov's own code back-calculates m_dry by assuming
    that the highest mass in the run equals the isotherm's uptake at 30 % RH. That makes the
    measured uptake depend on the isotherm, which is also the baseline's input, so it is not
    used. **Open, to be fixed before the freeze from the data alone:** whether each cycling
    sample can be tied to a drying stage of the same physical sample in an adjacent file (same
    pan, same session). Where it can, that dry mass is used. Where it cannot, the cycling run is
    scored only on quantities that do not need m_dry: mass swings per cycle, and their timing,
    in mg per mg of the run's minimum mass. That rule is stated here and not changed later.
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
- **Cycling run.** One whole cycling file, simulated open-loop from its first point, with no
  resetting to measured values at any later time.

## 4. Folds

- **Paired samples.** The step runs were measured two samples at a time on a two-pan
  instrument; the files come in pairs with the same timestamp. A pair shares its forcing, so it
  counts as one experiment in every bootstrap. The logged total gas flow is 400 sccm, against
  200 mL/min in the paper; plausibly 200 per pan, which is to be confirmed from the data before
  the freeze.
- **LOSO (leave one sorbent out).** Eight folds, one per Bezrukov sorbent. A composite is
  always held out together with its parent, so ROS-037 with the ROS-037 composite, and ROS-039
  with the ROS-039 composite.
- **LOFO (leave one family out).** Four folds:
  - aluminium carboxylate rods: MOF-303, MIL-160, CAU-10-H, Al-fumarate;
  - zinc triazolate fluorides: ROS-039, ROS-040, ROS-039 composite;
  - ROS-037 and its composite;
  - Syloid AL-1.

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
  - Variant B0-b: the same, but reading the desorption branch during release. Which of B0 and
    B0-b is used in each outer fold is chosen by the same inner leave-one-sorbent-out as the
    learned models' hyperparameters, so the baseline gets the same tuning as the competitors.
- **B1, the second baseline: linear driving force.**
  - Equation: dw/dt = k_LDF(T, m)·(w*(RH_flow) − w), with k_LDF = k‴(T)/m, fitted the same way.
- **B0\*, the oracle.** B0 with k″ fitted on the held-out sorbent's own data. It is not a
  competitor; it measures how much is lost by assuming a material-independent rate constant
  (H4b).
- **L1, grey box.**
  - Equation: dw/dt = k(T, m)·(RH_flow − RH_bed(w))·exp(g_θ(z)).
  - The correction is a positive factor, so the rate is still zero at equilibrium and the
    model cannot produce uptake against the driving force.
  - z holds: w normalised by the isotherm's uptake at 30 % RH; RH_flow; RH_bed; the local
    isotherm slope dw/dRH at w; the branch flag; T; and 1/m.
- **L2, black box: a neural ODE.**
  - Equation: dw/dt = f_θ(w, RH_flow, T, 1/m, e).
  - e is a fixed encoding of the isotherms: uptake at 11 RH values per branch and temperature.
  - No physics is imposed.

Implementation and training rules:

- L1 and L2 are small multilayer perceptrons, trained by simulating whole segments with an
  adaptive solver and minimising squared trajectory error.
- Each learned model is an ensemble of 5 seeds, and its prediction is the ensemble mean.
- Hyperparameters are chosen within each outer fold by inner leave-one-sorbent-out on the
  training sorbents only, from a grid fixed here: width {16, 32}, depth {2}, weight decay
  {1e-4, 1e-3}, learning rate {1e-3}.
- Early stopping uses the inner folds. The outer held-out sorbent is never used for any choice.

## 6. Metrics

- **Primary metric.** The normalised trajectory error of a step segment, E = RMS(w_pred −
  w_meas) / |Δw|, where Δw is the measured change over the segment. Per held-out sorbent, its
  score is the median E over its segments.
- **Noise floor F.**
  - Within a step-run file, the same step (same from- and to-RH) is repeated, from the second
    repeat onwards.
  - For each pair of consecutive repeats, the two trajectories are aligned on time since the
    step and compared with the same normalised RMS.
  - A sorbent's F is the median over its pairs.
  - F is computed before the freeze (section 9) and recorded in section 12.
- **Secondary metrics.**
  - The relative error in time-to-63 % per segment.
  - For the cycling runs, the relative error in steady-state productivity: the mean uptake
    swing per unit time over the last three cycles, the definition Bezrukov uses.
  - For L1 and L2, the number of segments on which the model moves uptake against the driving
    force or beyond the isotherm (physical violations), reported for every model.

## 7. Decision rules and falsifiers

**Beating the baseline in a fold.** A learned model "beats B0" on a held-out sorbent if both
of these hold:

- its median E is lower than B0's by more than that sorbent's F;
- the 95 % bootstrap interval of the paired difference, resampling that sorbent's segments,
  excludes zero.

**H4a.** H4a is decided on LOSO for each learned model separately (L1, L2):

- Supported if the model beats B0 on at least 7 of 8 LOSO folds. That is a one-sided sign
  test, p = 0.035.
- Falsified if it beats B0 on 4 or fewer.
- Five or six is reported as "not established".

A learned model that beats B0 on LOSO but not on at least 3 of the 4 LOFO folds is reported as
not transferring across families, whatever its LOSO result.

**H4b.** Supported if, for at least 6 of 8 sorbents, B0* reduces (E_B0 − F) by more than half.

**H4c.** Reported per model as LOFO-minus-LOSO median E per family, with intervals. No
threshold.

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
- A synthetic test of the harness (section 10).
- Timing runs of L1 and L2 on synthetic data to fix the compute budget.

Not allowed before the freeze: fitting L1 or L2 on real data, and any held-out evaluation.

## 10. Synthetic harness test (must pass before the freeze)

Synthetic trajectories are generated on the real forcing and real isotherms of P, from B0 with
a known k″ and a known material-dependent multiplicative correction. The harness passes if:

- B0 refitted on the synthetic data recovers k″ within 2 %;
- L1 recovers the injected correction on held-out synthetic sorbents with a median E below
  the injected correction's effect;
- on correction-free synthetic data, neither L1 nor L2 "beats" B0 by the section 7 rule. This
  is the false-positive check.

## 11. Compute

Everything runs on the author's laptop: CPU only, one training job at a time, launched as
background chains when the machine is free. The budget is fixed after the timing runs of
section 9 and written here before the freeze.

## 12. Freeze record

(empty until frozen: commit hash, date, noise floor values per sorbent, compute budget)
