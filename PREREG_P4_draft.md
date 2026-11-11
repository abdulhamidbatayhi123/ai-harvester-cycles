# Pre-registration (DRAFT, not frozen): Paper 4

**Working title.** Does the isotherm predict an unseen sorbent's rate constant? A pre-registered
held-out-sorbent test of isotherm-driven water-uptake dynamics for ten sorbents. (Until
2026-11-10: "Does learning beat the isotherm?"; changed when the learned model failed the
synthetic harness, section 10. A title asking whether the rate constant is material-independent
was considered and dropped the same day: section 12 already shows in sample that it is not at
60 °C, and a B2 verdict cannot answer that question; red-team M5.)

**Status.** Draft written 2026-11-03 for the author's review. Nothing in it has been run on
real data except what section 9 lists as allowed before the freeze. When frozen, the commit
hash goes in section 12 and no confirmatory number exists before that commit.

---

## 1. Question

When a sorbent has never been seen in training, can a learned dynamic model predict how its
water uptake rises and falls over time better than the published isotherm-driven model?
Both models are driven by measured humidity and temperature, and both are told only the new
sorbent's water isotherms. (Before the freeze this question became untestable: no learned model
passed the synthetic harness; section 10.)

Since 2026-11-10 the confirmatory question is narrower: does the isotherm of an unseen sorbent
predict the effective rate constant k″ of Bezrukov's equation better than one value shared by all
training sorbents (H4a′)? And, descriptively, how much of the published model's error would a
correct per-sorbent k″, or a correct end point, remove (H4b, section 8)?

The data are milligram powder layers on a dynamic vapour sorption (DVS) balance: 8 sorbents
from Bezrukov et al. 2023 and 2 MOFs from Gao et al. 2026, all from one laboratory. All
claims stay at that scale. The words "harvester", "device" and "digital twin" are not used for
the results.

## 2. Hypotheses

- **H4a, primary.** A learned model, given only the held-out sorbent's isotherms, predicts its
  uptake trajectories more accurately than the best per-fold refitted isotherm-only physics
  model (B0, B0-b or B1, chosen on the training sorbents; section 5), by more than the
  measured noise floor and by a practically relevant margin. L1 (grey box) was the primary
  learned model and L2 (black box) the secondary one; only L1 could have supported the original
  headline claim.
  L2 failed the synthetic harness and is dropped from H4a under the rule in section 5 (section
  10, round 4); its harness results are reported. **Outcome before the freeze (2026-11-10):** L1
  failed criterion 2 of the harness in its last allowed round (section 10, round 7), so under the
  stopping rule H4a is reported as "not tested: no learned model passed the synthetic harness",
  and no learned model is fitted to the real data for a verdict.
- **H4a′, the confirmatory hypothesis from 2026-11-10.** The isotherm of a held-out sorbent
  predicts the effective k″ of Bezrukov's equation better than one value shared by the training
  sorbents: B2 (log k″ = a + b·(RH₅₀/30 − mean), per temperature and direction, section 5) beats
  the pooled B0 of the same form (the fold's B0 variant, so that only k″ differs) by the section 7
  rule, on the same folds, with the same 7-of-8 count, the same R1/R2 agreement and the same
  falsifier. Its own synthetic harness (section 10b) takes the place of criterion 4; if that
  harness fails, H4a′ is "not tested", as H4a was.
  - *What a verdict means.* B2 is B0 with an isotherm-dependent effective k″. A rate law shared by
    all materials but not of B0's form also makes the best effective k″ depend on the isotherm,
    because sorbents of different shape spend their time at different bed RH. So a B2 win shows
    that the isotherm predicts the effective k″ of this equation, not that the true rate
    constant depends on the material; world C3 of section 10b measures the size of that confound.
    A falsification says that the simplest isotherm descriptor does not improve on one shared
    effective k″ at this noise and error level; the realistic-power worlds K2 of section 10b set
    how strongly that can be worded.
  - *When and why it was added, and what was known.* After L1 failed the harness (round 7) and
    before any fit of B2 to held-out real data. B2's functional form had been fixed on 2026-11-08
    as a reported comparator (repository commit 127ab6d), before L1 failed. Before H4a′ was
    written, the following bore on it: (1) each sorbent's in-sample k″ (section 12), in which
    CAU-10-H at 60 °C has both the largest uptake k″ (3.16 against 1.59 pooled) and, computed the same
    day as H4a′ (`results/rh50.json`, first committed with this text), the largest RH₅₀ (28.7 %);
    no correlation over the sorbents was computed; (2) H4b's in-sample ceilings: a sorbent's own
    k″ closes 10 % to 42 % of the gap between B0 and F (Syloid 0.10, Al-fumarate 0.11, MOF-303
    0.13), so a B2 beat with r ≥ 10 % on 7 of 8 folds needs B2 to capture most of the reachable
    gain almost everywhere, and "supported" was foreseeably hard to reach; (3) in the archived
    synthetic null replicate `results/null_rep0_preD`, B2's median E was below B0's in 3 of 5
    folds by small margins. The paper reports H4a as the original primary hypothesis, "not
    tested", in its abstract, and H4a′ with this timeline.
  - *Reported with the verdict (descriptive).* Per held-out sorbent, the share of the oracle's gain
    that B2 achieves out of sample, (E_B0 − E_B2)/(E_B0 − E_B0\*) (`share_of_oracle_gain` in
    `p4.decide`). A held-out group is flagged as an extrapolation if its RH₅₀ at that temperature
    lies outside [min, max] of RH₅₀ over every group B2 is fitted on (validation sorbent and
    composites of non-held parents included); `audit/extrapolation_flags.py` gives Al-fumarate at
    27 °C, CAU-10-H at 60 °C, and ROS-039 at both temperatures (7.41 against a training minimum of
    8.15 at 27 °C; 10.47 against 10.50 at 60 °C; `results/extrapolation_flags.json`). An earlier
    draft listed only the first two.
- **H4b, descriptive.** How much of B0's error on a held-out sorbent comes from the assumption
  that the rate constant is the same for every material. Measured as the fraction of the gap
  between B0 and the noise floor that the oracle B0* closes (B0 with k″ fitted on the held-out
  sorbent itself, by the scored metric). It is not a confirmatory test: an in-sample version of
  both quantities was seen before the freeze (section 12): under R2, with k″ fitted by the
  scored metric, a sorbent's own k″ closed 10 % to 42 % of the gap per sorbent (segment-weighted
  over its four strata; up to 84 % in single strata; `results/prefreeze/h4b_insample.json`). An
  earlier draft said "at most a third"; that figure predated the duplicate fix and used a
  least-squares oracle.
- **H4c, descriptive.** Holding out whole families degrades every model more than holding out
  single sorbents does. Only two of the four LOFO folds differ from a LOSO fold (section 4), so
  this is reported descriptively, without a significance test.

H4a′ has a decision rule and a falsifier in section 7 (H4a's machinery, applied to B2); H4b and
H4c are descriptive point estimates, reported per sorbent, with no interval and no verdict
(section 7).

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
      confirmatory result is also computed under R1, and the H4a′ verdict (H4a's until
      2026-11-10) must agree under both (section 7).
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
measured RH. The two MOFs are therefore never used for training or tuning. All physics models
(no learned model is fitted; section 10) are fitted on the full P, then evaluated on:

- the Fig. 3c/d step curves, driven by set-point RH and flagged;
- the 128-cycle 27 °C runs, which have logged RH.

These results are reported separately from H4a′. If the authors confirm the protocol (flow and
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
- **What a per-fold beat means (review findings C3, C4).** Clusters from one session share that
  sample's systematic errors (its dry mass, its end-point offset, its mass); MOF-303's clusters
  come from two sessions. A per-fold beat is therefore a consistency screen over humidity
  conditions, not a material-level test; the error control at the material level is the
  7-of-8 rule over held-out sorbents (section 7). Averaging the two pans hides the effect of
  sample mass, so d is also reported per pan as a diagnostic.
- **Parents and composites (review finding C2).** A composite is held out with its parent, but
  the two are judged separately and both must pass (section 7): composite clusters are about two
  thirds of those folds, and the composites respond several times faster than their parents.
- **Sessions that mix sorbents.** Three kinds of two-pan sessions hold two different sorbents:
  CAU-10-H with MIL-160 (2021-08-27), ROS-040 with Syloid (2021-08-28), and the two composites
  (six sessions, 2022-04-28 to 05-03). Pans that share a session share their measured forcing,
  but no uptake trace is shared, so this is no leakage of the target. Clusters are formed
  within one sorbent.
- **Gas flow (checked per plateau, 2026-11-08; `results/prefreeze/checks2.md`).** All 1,188
  step plateaus and all 1,492 cycling plateaus in P (after the duplicates were dropped) ran at a
  logged total flow of 400 sccm, and
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
  - k = k″/m, with k″ fitted on the training sorbents only, by the scored metric (the median E
    over segments, as for the oracle below). It is fitted separately for each temperature and
    direction, and pooled across materials: the "independent of the material" assumption,
    refitted per fold.
  - Why the scored metric and not least squares (review finding N5): the learned models are
    validated and early-stopped on median E, and L1 = B0·exp(g) can learn a constant g, which is
    just a refit of k″ to that metric. Fitting the comparators by least squares would hand the
    learned models that refit as a "win". The same holds for B2, whose constant term a is such a
    refit. In sample, the metric fit alone lowers B0's E from
    0.022–0.237 to 0.018–0.236 (section 12). Every physics model (B0, B0-b, B1, B2, B0\*) is fitted
    the same way.
  - The published code can rescale the isotherm to match a kinetic run ("scale_isotherm"). That
    uses the held-out sorbent's own kinetics, so it is forbidden here for every model.
  - Variant B0-b: the same, but reading the desorption branch during release.
  - **The fold's B0 variant** is B0-b if B0-b has the lower comparator-choice score on the
    training sorbents (the median over them of their per-sorbent median E, as for the comparator
    below), and B0 otherwise, whichever candidate is chosen as comparator (`p4.run_study`,
    `use_des`). It is the model that H4a′ contrasts B2 with, the model B2 is built on, and the
    model of the oracle B0\* and the end-point oracle.
- **B1, the second baseline: linear driving force.**
  - Equation: dw/dt = k_LDF(T, m)·(w*(RH_flow) − w), with k_LDF = k‴(T)/m, fitted the same way.
- **The comparator for H4a** (and, for the wording of H4a′, section 7) is whichever of B0, B0-b and B1 does best across the fold's
  training sorbents (review finding O2): each candidate is fitted on all training sorbents, and
  the one with the lowest median, over those sorbents, of its per-sorbent median E is chosen.
  The three have the same four parameters (one k″ per temperature and direction), so an
  in-sample comparison does not favour a more flexible one, and six or seven sorbents make it far
  less noisy than the single validation sorbent of the earlier draft. Inner leave-one-sorbent-out
  was costed: on this machine it would add about 17 to 28 hours of physics fits to every run (main
  and R1; the null replicates are no longer run), and it was rejected for that reason. The choice
  uses no outer held-out data. A learned model that beat B0 but not B1 would not have beaten "the
  isotherm"; for B2 the same contrast decides only the wording (section 7).
- **B2, the model tested by H4a′ (section 2; until 2026-11-10 a reported comparator).** B0 with k″ made material-dependent
  in the simplest way an isotherm allows: log k″ = a + b·(RH₅₀/30 %), where RH₅₀ is the RH at
  which the adsorption branch reaches half its uptake at 30 % RH. The full form is
  log k″ = a + b·(RH₅₀/30 − mean), the mean of RH₅₀/30 over the training groups, so that a and b
  are not correlated through an uncentred descriptor. a and b are fitted per temperature and
  direction on the training sorbents by the scored metric, Nelder–Mead from the pooled fit with an
  explicit starting simplex whose step in b is 0.5 (`p4.physics.fit_b2`; SciPy's default step for
  a zero entry, 0.00025, could leave b at 0; red-team M10). B2 is built on the fold's B0 variant:
  in a fold whose B0 variant is B0-b, B2 uses the desorption branch during release. B2 has eight
  parameters per fold against B0's four and is judged out of sample only, where the extra
  parameters add variance and make a beat harder. Its predictions are flagged for physical violations like any
  model (`viol_B2`). RH₅₀ per sorbent and temperature (`results/rh50.json`) spans 7.4 % to 24.3 %
  RH at 27 °C and 10.5 % to 28.7 % at 60 °C.
- **B0\*, the oracle.** B0 with k″ fitted on the held-out sorbent's own data by minimising the
  scored metric (the median E over its segments; a log-grid search then a bounded refinement),
  not least squares. Least squares is not the scored metric, so in 7 of 36 in-sample strata a
  least-squares "oracle" scored worse than the pooled k″. It is not a competitor; it measures
  how much any choice of a single k″ could gain (H4b).
- **Initial state.** Every model starts a step segment from the measured uptake at its first
  grid point (the first sample after the set-point change), and runs open loop to the end of
  the segment with no later resetting.
- **L1, grey box.**
  - Equation: dw/dt = k(T, m)·(RH_flow − RH_bed(w))·exp(2 tanh g_θ(z)).
  - The correction is a positive factor between e⁻² and e², so the rate is still zero at
    equilibrium and the model cannot produce uptake against the driving force.
  - z holds: w normalised by the isotherm's uptake at 30 % RH; RH_flow; RH_bed; the local
    isotherm slope dw/dRH at w; the branch flag; T; 1/m; and the driving force
    d = RH_flow − RH_bed itself. d was added after harness round 6 (section 10): without it the
    network had to form d as a difference of two inputs and could not do so precisely enough.
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
  - stage A fits the rate law to the measured dw/dt, a centred difference over ±18 s. Each rate is
    paired with the RH averaged over the same window, not the instantaneous RH, whose jitter
    would be an error in an input variable. Each point's error is weighted by its segment's
    t63/|Δw|: a rate error times the segment's time scale is the trajectory error it causes, in
    units of E, so slow and fast segments count alike. (Both rules were found in harness rounds
    4 and 5, section 10.)
  - stage B fine-tunes on open-loop rollouts over random 10-minute windows, started from the
    measured uptake.
  Validation on whole segments, open loop, picks the best state. Backpropagating through whole
  segments, the first design, took about 2.5 hours per 300 steps on this machine. It left L1
  unable to learn a correction that was present and L2 badly undertrained.
- Each learned model is an ensemble of 5 seeds, and its prediction is the ensemble mean.
- Hyperparameters are chosen within each outer fold on one validation sorbent taken from the
  training sorbents, from a grid fixed here: width {16, 32}, depth {2}, weight decay
  {1e-4, 1e-3}, learning rate {1e-3}. (The comparator is chosen on all training sorbents
  instead; see above.)
- Stage A's centred difference over ±18 s spans about half of the fastest time-to-63 % (1.1
  min), so it smooths the onset of the fastest steps. Stage B trains on the trajectories
  themselves, so this affects only the starting point of training, not the scored quantity.
- **A model that fails the synthetic harness (section 10) is dropped from H4a**, and the paper
  says so. A failed model may be redesigned before the freeze only if it is then judged on a
  world not used during the redesign. L1 failed rounds 4 to 6 and was revised each time; round 7
  was its last chance (section 10, stopping rule), and it failed.
  - The validation sorbent is Syloid AL-1, except in folds that hold Syloid out, where it is
    ROS-040. If ROS-040 is held out too, it is CAU-10-H.
  - The same validation sorbent serves for early stopping.
  - The outer held-out sorbent is never used for any choice.
  - Full inner leave-one-sorbent-out for the learned models would be cleaner but costs about
    seven times more (section 11). A single validation sorbent makes the choice noisier, not
    leaky.
  - Syloid is the only non-MOF (review finding O2). Tuning on it can only pick configurations
    that transfer worse to MOFs, which works against a positive H4a. It also weakens a
    "falsified" verdict, so the paper states that the learned models were tuned on a silica gel
    and does not claim that no tuning on MOFs could help. A second, MOF validation sorbent was
    considered and rejected: it would cut the training set from six sorbents to five.

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
    (`results/prefreeze/checks2.json`, `F_within_segment_weighted`). In a fold that holds out a
    parent and its composite, each material is judged against its own F (section 7); the
    largest of the two is used only for the pooled figures that are reported beside them.
  - F is computed before the freeze (section 9) and recorded in section 12.
  - **Between-pan and between-session agreement**, the same step compared across files of one
    sorbent, is reported beside F as a ceiling, not a floor: pans and sessions differ in sample
    mass, and the rate scales with 1/m, so their disagreement mixes noise with a real,
    modelled effect. It is 0.034 to 0.374 (section 12).
- **Segment inclusion.** A step segment is scored only if its measured mass change is at least
  0.05 mg and has the sign of the set-point change (`p4/segments.py`, `is_scored`), the rule of
  AUDIT.md section 2.3. Every step segment in P changes by 4.0 to 40.6 wt% (`results/prefreeze/checks2.md`),
  far above it, so in P the rule excludes nothing; it matters for the secondary analyses. E is undefined as
  |Δw| → 0 and is dominated by noise for tiny steps. The rule is applied to the measured data
  before any model is run, so it is the same for every model, and the noise floor F uses the
  same segments. (An earlier draft used |Δw| ≥ 0.05 wt%, ten times looser than the audit rule;
  review finding C1, section 13.)
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

**Beating the comparator in a fold.** For each held-out material (a parent and its composite
separately; section 4), let d = E_comparator − E_model per segment, and let D = d·|Δw|, the
difference in unnormalised RMS error (wt%). Both are averaged within each cluster (one RH step in
one session). A segment whose model E is not finite (a diverged prediction) counts as an
infinite loss for the model, never as a missing value; a segment whose comparator E is not
finite is left out. A learned model beats the comparator on a material if all four hold:

1. the median of the cluster values of d exceeds that material's own F (section 6);
2. r, the median of d divided by the comparator's median cluster E over the same clusters, is
   at least 10 % (practical significance). The same r, computed once, is used for "falsified"
   below;
3. a one-sided exact Wilcoxon signed-rank test of D over clusters gives p ≤ 0.025 (exact null
   distribution over all 2ⁿ sign vectors, average ranks for ties, computed by counting subset
   sums so that it is exact for any n; clusters with D exactly 0 are dropped, the Wilcoxon
   convention);
4. the model's median cluster E is below the comparator's median cluster E.

It beats the comparator in the fold if it does so on every held-out material of the fold (both
the parent and the composite in the ROS-037 and ROS-039 folds; a held material with no scored
segment fails), and is physically admissible (below). `p4/decide.py` implements exactly this text.

Why two quantities (review finding C1): conditions 1 and 2 are about the size of the gain
relative to the error and to the noise, for which the dimensionless d is the natural scale. The
test ranks D instead, because d divides by |Δw|, so the smallest steps would have the largest
|d| and would dominate the ranks; D weights each cluster by how much water it moved. The
signed-rank statistic is used rather than the median because the median ties heavily under sign
flips (six equal gains give p = 0.34, not 1/64). The attainable minimum p is 2⁻ⁿ for n
clusters, so a material with fewer than 6 clusters cannot be beaten; the counts are in section 12.

Why condition 4 (added 2026-11-09, before any real-data fit): conditions 1 to 3 are paired.
Harness round 6 (section 10) showed that they can favour a model that is much better on the hard
steps and several times worse on the easy ones. In world C2, on held-out ROS-039, L1 improved 19
of 26 clusters (median d +0.012, p = 0.009), but its median E was 0.034 against B0's 0.013,
because it was up to twelve times worse on every 0→30 % adsorption step
(`results/diag/c2_clusters/harness.json`). Such a model has not beaten the comparator, so
condition 4 asks that its typical error be lower too. It can only make a beat harder.

The order of events matters for condition 2. The 10 % threshold was proposed on 2026-11-04,
after the noise floor (F medians 0.001 to 0.013) and the in-sample B0 reproduction were seen,
and before any learned model was fitted to real data. It exists because F alone would count
almost any improvement as real. It is the author's to confirm or change at the freeze.

**Physical admissibility (review finding O3).** A segment counts as a violation against a
learned model (or B2, under H4a′) only if the model violates (section 6) and neither the measured data nor the
comparator does on that segment: an isotherm-driven model can move against the step where the
measured start lies off the isotherm, and L1 shares B0's driving force. If such excess
violations exceed 5 % of a fold's segments, the model does not beat the comparator in that fold,
whatever its E.

**H4a**, decided on the 8 LOSO folds for L1 (L2 was dropped; section 10, round 4). Let r be a
fold's relative improvement, the median d over its clusters divided by the comparator's median E.
In a fold that holds out a parent with its composite, r is the smaller of the two materials'
values, consistent with "both must pass"; the pooled value is reported (review T-P4-4 F-6).
Otherwise a gain on the composite alone, which has twice the parent's clusters, could move a
fold to r ≥ 10 % and turn "falsified" into "not established".

- **Supported** if the model beats the comparator in at least 7 of 8 folds. This is a decision
  rule, not a p-value; the folds share most of their training sorbents, so a sign-test p would
  overstate the evidence. It also requires the null study to pass (section 10, criterion 4).
- **Falsified** if at most one of the 8 folds has r ≥ 10 % (review finding O1). The 7th order
  statistic of r is then below 10 %, and it is a one-sided 96.5 % upper bound on the median of
  r over folds whatever their dependence on the training sets: P(at least 7 of 8 below the
  median) = 1 − 9/256. A bootstrap over 8 dependent folds, the earlier rule, undercovers.
- **Not established** otherwise, including a moderate real effect that the 8 folds cannot
  resolve.
- The verdict must be the same under the primary dry-mass rule R2 and the sensitivity rule R1.
  If it differs, H4a is reported as not robust to the dry-mass definition, and the result is
  "not established": neither "supported" nor "falsified" stands unless both rules give it.
  `p4/final_verdict.py` combines the R2 and R1 outputs of `p4.decide` with criterion 4 of the
  null study into the verdict of the table below (tested over every combination of its inputs). R2 is not drift-free for MOF-303 and Syloid (section 3.3), so
  if R1 and R2 disagree on those folds in particular, the paper says so (review finding O4).

**Robustness to the comparator choice (review T-P4-4 F-7).** The comparator is chosen on the
training sorbents (section 5), which keeps the held-out test valid but does not guarantee that
it is the strongest candidate on the held-out sorbent. `p4.decide` therefore also applies the
rule against each of the three candidates (B0, the other B0 variant, B1) and against the one
with the lowest held-out median E (median over the fold's held-out segments) in each fold. If L1 is supported against the chosen
comparator but beats the held-out-best candidate in fewer than 7 of 8 folds, the paper says
"supported against the comparator chosen on the training sorbents only" and does not say that
L1 beats the isotherm-driven models. This decides only the wording of the claim, not the
verdict.

**Transfer across families.** A model that is supported on LOSO transfers across families if it
also beats the comparator on both non-trivial LOFO folds (aluminium rods; zinc triazolates).

**Complete verdict table** (per model; LOSO beats out of 8; folds with r ≥ 10 %; non-trivial
LOFO beats out of 2):

| LOSO beats | Folds with r ≥ 10 % | LOFO beats | Verdict |
|---|---|---|---|
| 7 or 8 (null study passed; for H4a′ the B2 harness) | (not used) | 2 | supported, transfers across families |
| 7 or 8 (null study passed; for H4a′ the B2 harness) | (not used) | 0 or 1 | supported within families; does not transfer across families |
| 7 or 8 (null study failed) | (not used) | any | not established; the paper reports the null study's failure |
| any (H4a′ only: B2 harness failed) | any | any | not tested |
| 0 to 6 | 0 or 1 | any | falsified |
| 0 to 6 | 2 or more | any | not established |

**H4a′ (from 2026-11-10)** is decided exactly as H4a above, with B2 in place of the learned
model and the pooled B0 of the fold's variant (row field `E["B0"]`) in place of the chosen
comparator, so that the contrast changes k″ and nothing else (red-team B2): the same four
conditions per material, admissibility from B2's own violation flags, the same 7-of-8 count,
falsifier, R1/R2 agreement and LOFO transfer. `p4.decide` scores B2 from each fold's physics row
(kind "B2"), and `p4/final_verdict.py` combines R2, R1 and the B2 harness:
- if the B2 harness (section 10b) did not pass all three of its criteria, H4a′ is "not tested",
  whatever R1 and R2 give;
- otherwise the verdict table above applies, with the B2 harness in the place of the null study.
Wording: if supported, the claim is "beats the shared-k″ model of the same form", strengthened to
"and every shared-k″ candidate" only if B2 also beats the held-out-best of B0, B0-b and B1 in at
least 7 of 8 folds. If falsified, and B2 was not "supported" in all three realistic-power worlds
K2a–c of section 10b, the paper words it as "no isotherm-predicted rate constant was detectable at
this noise and error level", and states in how many of the three worlds an effect of the measured
size was missed.

**H4b and H4c** are descriptive point estimates and carry no verdict (section 2). An earlier draft
promised bootstrap intervals without a resampling unit or code; they were dropped before the
freeze rather than defined after it. H4b: per LOSO fold, the fraction of the gap between B0 and
F that B0\* closes (`p4.decide`, field `H4b`). H4c: for each sorbent of the two non-trivial LOFO
folds, the median E of B0 and of B2 in its LOFO fold against the same in its LOSO fold, from the
physics rows (reported as a table, no test).

**Negative results.** L1 is not tested on real data (section 10, round 7). The paper says that no
learned model passed the synthetic harness, and makes no statement that learning cannot help on
these data. If B2 is falsified under H4a′, the paper says that the simplest isotherm descriptor
does not improve on one shared effective k″ here, worded as above. In either case section 8's
analyses are used only to say where the residual error lives, not to rescue a claim.

## 8. Secondary and exploratory analyses (labelled as such in the paper)

- Generalisation to the excluded protocol variations, with every model trained on P only:
  carrier-gas flow, particle size, pan and packing, and the 100-cycle runs (error growth over
  long open-loop horizons).
- The Gao bnn external test (section 3.4).
- **End point or rate? (added 2026-11-10, cs T-P4-5 R5a; descriptive, an oracle like B0\*).** In
  each fold, B0 (the fold's variant, pooled k″ of the training sorbents, no refit) is re-scored
  with its branches scaled by the held-out sorbent's own end-point offsets, per temperature and
  direction. The adsorption branch is scaled by (1 + ε̂_ads), with ε̂_ads the median of
  w_end/w_ads(RH_end) − 1 over the sorbent's equilibrated uptake segments; in a fold whose variant
  is B0-b, the desorption branch is scaled by (1 + ε̂_des), the same over its release segments
  against the desorption branch (uptake and release are kept apart so that hysteresis is not read
  as a scale error). A segment counts if it moved at least 0.5 wt%, the slope of its last tenth
  extrapolated over the segment is below 2 % of its move, and the branch value at its end RH
  (median RH of that tenth) is at least 0.2·w₃₀. A group with a missing offset is scored NaN and
  reported as missing (`p4.run_study.endpoint_eps`, `endpoint_oracle_E`; row fields `eps_hat`
  and `E["B0_endpoint_oracle"]`). Reported per held-out sorbent: B0's median E, the end-point
  oracle's, and the k″ oracle B0\*'s, so B0's error is split into a part a correct end point
  removes and a part a correct rate constant removes. On a synthetic null world with known
  offsets the estimator recovers every ε within 0.001 (`results/endpoint_eps_check_S0.txt`).
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
- The synthetic harness for H4a′ (section 10b), and isotherm features such as RH₅₀ (inputs, not
  outcomes; `results/rh50.json`).
- Timing runs of L1 and L2 on synthetic data to fix the compute budget.

Not allowed before the freeze: fitting L1 or L2 on real data; fitting B2 on real data in or out of
sample; computing the relation between RH₅₀ and any real k″; and any held-out evaluation.

## 10. Synthetic harness test for H4a (failed in round 7; see the stopping rule)

The freeze now needs section 10b to pass, not this section. This section is the record of the
learned models' harness, kept in full.

Synthetic trajectories are generated on the real forcing and real isotherms of P from a known
truth, and the fold pipeline is run on them (`audit/synthetic_harness.py`). Three worlds:

- **N, no correction:** truth = B0 with the pooled k″ of the real data.
- **C, a learnable correction:** truth = B0 × exp(−0.7·w/w₃₀), a material-independent slow-down
  near saturation that a model given only the isotherm can learn. On the two held-out test
  sorbents it raises B0's median E from about 0.0005 (case N) to 0.036 and 0.041.
- **Null, realistic (review findings F2, N3, N4).** Every sorbent–temperature group deviates
  from B0 in two ways drawn independently of anything in its isotherm, so a model given only the
  isotherm cannot predict them, and any "beat" here is a false positive:
  - a rate factor exp(b + a·(x − ½) − σ_b²/2 − σ_a²·(x − ½)²/2), x = w/w₃₀, with b ~ N(0, σ_b(T)²)
    per group and a ~ N(0, σ_a²) per sorbent, σ_a = 0.6. The last two terms make the expected
    factor exactly 1 at every w, so the null world holds no average shape that a model could
    learn and transfer (N4). σ_b(T) is the measured spread of log k″ across the eight sorbents
    (`results/prefreeze/reproduce_b0.json`): 0.089 at 27 °C and 0.300 at 60 °C;
  - an equilibrium offset: the truth equilibrates on the isotherm scaled by (1 + ε), with ε
    resampled from the 18 measured relative end-point offsets (median step end-point minus
    isotherm, divided by w₃₀, per sorbent–temperature group; −0.04 to +0.45). This gives the
    null world the material-specific equilibrium error of the real data (N3), which L2 could
    otherwise exploit or be penalised for unrealistically;
  - AR(1) measurement noise, σ = 0.01 wt%, φ = 0.9.
  - Two corrections from review T-P4-4: each sorbent's draws come from its own random stream,
    keyed by the replicate and the sorbent's name, so a sorbent gets the same world in the
    calibration (8 sorbents) as in the study (10, with the composites) (F-8). A relative offset
    drawn from a low-capacity group could put a high-capacity sorbent 17 wt% off its isotherm,
    against a largest observed group median of 3.13 wt% (Al-fumarate at 60 °C,
    `results/prefreeze/dry_rules.json`); |ε·w₃₀| is therefore capped at that value, and the
    realised absolute offsets are stored with each replicate's draws (F-9).
  With these sizes (`results/null_calibration.json`, computed by the same code for the real and
  the synthetic data, pooled least-squares k″ refitted on each): B0's median E over the eight
  sorbents is 0.057, 0.070 and 0.045 in replicates 0 to 2, against 0.067 on the real data, and
  0.032 to 0.125 per sorbent, against 0.055 to 0.093. The null world's within-file noise floor
  F, per sorbent–temperature group, is 0.0014 to 0.0140, against 0.0009 to 0.0126 on the real
  data, and lies within a factor of about two of the real value in each group. So the noise
  model (σ = 0.01 wt%, φ = 0.9) reproduces the measured F, and the decision rule is tested
  where it will run on real data.

The harness passes if:

1. in world N, B0 refitted on the training sorbents recovers k″ within 2 %;
2. in a correction world not used to develop L1, L1 beats B0 by the section 7 rule on every
   held-out sorbent and halves B0's median E there (the injected effect). The halving was set
   after round 2, which met it, so round 2 does not count for it (review finding O6). The judging
   world moved from C (rounds 2 to 5) to C2 (round 6) to C3 (round 7) as each earlier one was
   spent on diagnosis; round 7 is the last (stopping rule below), and C3 is judged on MOF-303,
   ROS-039 and Al-fumarate;
3. in world N, neither learned model beats B0 (a check that is weak by itself: noise-free data
   put E_B0 below every F, so condition 1 of the rule blocks a beat whatever the model does;
   in round 2, L1's median paired gain on the MOF-303 null fold was 24 % of E_B0 with its
   bootstrap interval above zero, so only F stopped a beat; on ROS-039 it was 6 %;
   `results/harness_round2/harness.json`);
4. **the null study** (review findings N1, N2), run through the confirmatory runner and decision
   script themselves (`p4.run_study --synthetic null`, `p4.decide`) on all 8 LOSO folds, and
   summarised by `audit/null_summary.py`. Let r be a fold's relative improvement (section 7).

   *What a null beat is.* All clusters of a held-out sorbent share its random rate draws (b, a).
   With six training sorbents, some isotherm feature always correlates with their draws by chance,
   and on a held-out sorbent the shift a learner takes from that has the right sign about half
   the time; the within-fold test, with clusters as units, then gives p near 0. A per-fold beat
   means "better on this sorbent" (section 4). The claim about new sorbents rests on the 7-of-8
   count, so criterion 4 bounds the per-fold null beat rate rather than demanding no beats:
   P(at least 7 of 8 | per-fold rate q), independent folds, is 0.0013 at q = 0.3, 0.0085 at 0.4,
   0.025 at 0.473 and 0.05 at 0.529. (The diagnostic that found this is in round 7's notes below.)

   For each learned model, over all its null fold-fits:
   - (a) the one-sided 95 % Clopper–Pearson upper bound on the per-fold beat rate is at most
     0.40, so that even at the bound P(at least 7 of 8) ≤ 0.0085 for independent folds, leaving
     room for positive dependence between folds that share training sorbents. With 24 fold-fits
     (3 replicates) this allows at most 5 beats (bound 0.389; 6 beats give 0.435);
   - (b) no replicate has 5 or more of its 8 folds beaten, a direct check on the dependence that
     (a) does not model: a spurious correction learned from the shared training sorbents would
     make the folds of one replicate beat together;
   - (c) the mean of r over the null folds is below 2.5 %, a quarter of the 10 % practical margin.
     The earlier "mean below 0" would fail half the time for an exactly neutral model (review
     T-P4-4 F-5); a transferable spurious correction shows as r of about 10 % or more.
   The earlier conditions, at most 2 beats per replicate and a 90th percentile of r below 10 %,
   were replaced on 2026-11-09, before any null replicate with the final L1 existed: no learner
   that deviates from B0 at all can meet them when sorbent effects of the measured size exist,
   while the 7-of-8 claim is protected at any per-fold rate below about 0.47. The 90th
   percentile of r is still reported.

   Two procedures:
   - **Before the freeze**: 3 null worlds of the same design (24 fold-fits per model) with a reduced
     procedure, one configuration and one seed per fit. This tests the decision machinery and
     the models in a realistic null; it had to pass for the draft to be frozen (moot since round
     7: the L1 null study is not run).
   - **With the confirmatory runs** (not run: L1 is not tested, see the round 7 outcome below): one further null world (replicate 3; the pre-freeze worlds
     are replicates 0 to 2) with the full confirmatory procedure for L1 (4 configurations tuned on the validation sorbent, then 5 seeds; 72 fits).
     Selection on a validation sorbent and ensembling change how often a spurious correction
     survives, in an unknown direction, so the reduced replicates alone would test a different
     procedure. L1 can be declared "supported" only if this replicate also meets (b), and if (a) and (c)
     still hold with its 8 fold-fits added.

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

**Round 4 (2026-11-09; `results/harness_round4/`), L1 and L2, with the revised rule and the
metric-fitted comparator.** Criteria 1 and 3 passed: k″ recovered; no beat in world N. Criterion
2 failed. Fitted by the scored metric, B0 absorbs part of the injected slow-down (its E in world C
is 0.026 on MOF-303, against 0.036 under least squares in round 2). L1 reached only 0.020 there
(p = 0.53) and 0.031 against 0.031 on ROS-039. Round 2 had passed mainly because its comparator
was weaker. L2 failed world N outright: E 0.22 to 0.30 against B0's 0.0003 to 0.0005.

Diagnostics on world C, held-out MOF-303, stage A only (`audit/diag/`, `results/diag/`):
- **L1 can represent the correction.** Fitted to the exact truth rates, it reaches E 0.007, and
  0.003 with weights relative to B0's rate.
- **The bias came from the stage-A target.** Each finite-difference rate averages over ±18 s,
  but it was paired with the instantaneous measured RH. That RH jitter is an error in an input
  variable, and it is largest relative to the driving force near equilibrium, where the
  correction acts. Pairing the rate with the RH averaged over the same window gives E 0.008.
  Wider difference windows (±36 s to ±150 s), relative weights on noisy rates and longer
  training did not help (E 0.023 to 0.059).
- Stage A now uses the window-averaged RH (`p4/train.py`, `smoothed_rh`). Stage B and
  validation are unchanged.
- **L2 cannot hold equilibrium.** Fitted to the exact world-N rates, L2 still reaches only E
  0.19 on held-out sorbents. Its rate at equilibrium is 0.03 to 0.06 wt%/min where the truth is
  zero, and over equilibrium tails of an hour or more that drifts by several wt%. Explicit
  driving-force inputs do not help (0.17 to 0.18). Subtracting the network's own output on the isotherm,
  which imposes only the equilibrium, gives 0.06 to 0.07: still about 200 times B0.
- Under the rule in section 5, **L2 is dropped from H4a**. Three L2 designs failed world N. The
  paper reports this as a result: an unconstrained flux network trained on six sorbents does not
  hold the equilibrium precisely enough for open-loop prediction over long plateaus. H4a rests on
  L1 alone, which section 2 already made the only model that can carry the headline claim.

**Round 5 (2026-11-09; `results/harness_round5/`), L1 with the window-averaged RH.** Criteria 1
and 3 passed again. Criterion 2 failed. On MOF-303, L1 cut E from B0's 0.026 to 0.0065, but over
13 clusters the gain was not consistent enough (p = 0.11). On ROS-039 it was worse than B0
(0.035 against 0.031). Per-cluster diagnostics on ROS-039 (`results/diag/diag_l1_clusters.log`,
`diag_l1_t63.log`) showed why. Stage A summed raw rate errors, so the fast steps, whose rates are
largest, set the fit, and the slow steps, where the correction acts longest, hardly counted.
Weighting each point's rate error by t63/|Δw| of its segment puts every segment on the scale of
the scored relative error. With that weight, the stage-A fit on ROS-039 reaches E 0.014 against
B0's 0.030 (p = 1.5 × 10⁻⁸). Without it, the fit reaches 0.042. Stage A now uses this weight
(`p4/train.py`, `segment_t63`).

World C had now been used to develop two fixes, so it can no longer judge them. **Round 6** keeps
world C as a reported run and judges criterion 2 on a fresh world C2, fixed before the run: the
true rate is B0's times exp(0.8 tanh(d/15)), where d = RH − RH_bed(w) is B0's own driving force in
% RH. It speeds adsorption and slows desorption by up to a factor e^0.8 ≈ 2.2, saturating at large
|d|: a different form from world C, which slows uptake as loading rises. Criterion
2 needs a beat on both held-out sorbents AND E_model ≤ 0.5·E_B0.

**Round 6 (2026-11-09; `results/harness_round6/`), L1 in worlds N, C and C2.** Criteria 1 and 3
passed, and world C (reported only) now passed too: E 0.0054 against B0's 0.026 on MOF-303, and
0.014 against 0.031 on ROS-039. **Criterion 2 failed on C2.** On MOF-303, L1 more than halved
B0's E (0.011 against 0.025), but over 13 clusters the gain was not consistent enough
(p = 0.040). On ROS-039 the rule of the time declared a beat (19 of 26 clusters improved, median
d +0.012, p = 0.009), yet L1's median E was 0.034 against B0's 0.013. That result led to
condition 4 of section 7.

Diagnostics on world C2 (`audit/diag/`, `results/diag/c2_*`), which spent C2 as a judge:
- **The pipeline is sound.** The true C2 rate law, run through L1's own evaluation path,
  reproduces the synthetic data to the noise level (median E 0.0003 to 0.0005;
  `oracle_c2.py`).
- **Noise and weighting were not the cause.** Fitted to the exact true rates, with any of four
  weightings, L1 still lost to B0 on ROS-039 (E 0.019 to 0.037, against 0.019). Zeroing the
  inputs that could carry sorbent identity did not help either. In the exact-rate fit, L1 was
  accurate away from equilibrium, but within 5 % RH of it, where C2's factor changes fastest,
  its log-factor was about ±0.25 where ±0.6 to 0.7 was needed, even on the training sorbents
  (`factor_c2.py`).
- **L1 could not represent the correction precisely enough.** B0 fitted by the scored metric is
  already close to the C2 truth (E 0.013 to 0.025), so halving its error needs a factor accurate
  to a few per cent. Even fitted directly to the needed log-factor (possible only in a synthetic
  world), L1 plateaued at a mean squared error of 0.004, and open loop it still lost to B0
  (E 0.032 against 0.025 on MOF-303, 0.027 against 0.013 on ROS-039; `factor_fit_c2.py`).
- **The driving force as an input fixes it.** With d = RH − RH_bed given explicitly, the same
  direct fit reached a log-factor mean squared error of 0.0001 and E 0.001 on both held-out
  sorbents. Trained on the noisy rates by the normal stage A, L1 then beat B0 in C2 (E 0.0037
  against 0.023 on MOF-303, and 0.0092 against 0.019 on ROS-039) and in C (0.0056 against
  0.027, and 0.010 against 0.030). Section 5 now lists d among L1's inputs.

**Round 7** runs the full procedure in worlds N, C, C2 and C3. World C3 was defined and committed
before any run on it (repository commit a7d163e): the true rate is B0's times
exp(−0.6 tanh(4(RH_bed/100 − 0.25))), faster where the bed sits low on its isotherm and slower
high up. Criterion 2 is judged on C3 alone; C and C2 are reported.

**Stopping rule and an untouched fold (review T-P4-4 F-2, F-3), written on 2026-11-09 while round
7 was in world C, before any C3 result existed.**
- L1 is not redesigned again. If it fails criterion 2 on C3, no learned model has passed the
  harness. The paper then reports H4a as "not tested: no learned model passed the synthetic
  harness", with every round of this section, and no confirmatory LOSO verdict is claimed for L1.
  "Fix, then judge on a fresh world" cannot repeat without limit, or the harness stops being a test.
- C3 is judged on three held-out sorbents, not two. MOF-303 and ROS-039 were held out in the
  stage-A diagnostics of rounds 4 to 6, so a fit to their forcing, isotherm shape or step mix could
  carry over to any world. Al-fumarate was never held out in any diagnostic. A run with the same
  code and seed holds it out in worlds N and C3 (`HARNESS_HELD=Al-fumarate HARNESS_CASES=N,C3`), and
  criterion 2 needs a beat and E_model ≤ 0.5·E_B0 on all three. Criterion 3 (no beat in world N)
  covers Al-fumarate too.
- B0's E in world N and in each correction world is reported per held-out sorbent, so the size of
  the injected effect that the metric-fitted B0 cannot absorb is on record.

**Round 7 result (2026-11-10; `results/harness_round7/harness.json` and `harness.log`).** Median E
per held-out sorbent, L1 against B0 refitted on the training sorbents:

| World | MOF-303: L1 / B0 (ratio) | ROS-039: L1 / B0 (ratio) | Section 7 rule |
|---|---|---|---|
| N | 0.00032 / 0.00032 (1.00) | 0.00053 / 0.00049 (1.07) | no beat on either (p 0.97, 0.98) |
| C (reported) | 0.0067 / 0.026 (0.26) | 0.0091 / 0.031 (0.29) | beat on both |
| C2 (reported) | 0.0028 / 0.025 (0.11) | 0.0076 / 0.013 (0.57) | beat on both |
| C3 (judged) | 0.0070 / 0.0128 (0.55) | 0.013 / 0.036 (0.36) | beat on ROS-039 only |

- Criterion 1 passed: in world N, k″ was recovered within 0.13 % in every stratum (largest error
  0.12 %, ROS-039 fold).
- Criterion 3 passed on MOF-303 and ROS-039.
- **Criterion 2 failed.** On MOF-303 in C3, L1 lowered the median E from 0.0128 to 0.0070, but
  the median cluster gain, 0.0022, was below F = 0.003; the signed-rank p, 0.034, was above
  0.025; and the ratio, 0.55, missed the required halving. On ROS-039 in C3 it passed every
  condition (gain 0.020, p = 1.5 × 10⁻⁸, ratio 0.36). C3's effect on MOF-303 was the smallest
  of any correction-world case (B0's E 0.0128, against 0.025 to 0.036 elsewhere), so the
  margin over F was narrowest exactly where the world was new. (In C2, ROS-039's ratio of 0.57
  would also have missed the halving.)

**Outcome, under the stopping rule written before any C3 result:** L1 is not redesigned and no
learned model passed the harness. H4a is reported as "not tested: no learned model passed the
synthetic harness", with every round of this section. The Al-fumarate run (worlds N and C3, same
code and seed) was specified in advance and is reported below; it cannot change the outcome,
since criterion 2 needs all three sorbents. What follows from sections 5, 7 and 11 as written:

- no confirmatory L1 fits, and no null study: criterion 4 exists to make a positive H4a
  credible, and with no learned model in H4a there is nothing for it to protect. The null worlds
  already run stay in the record as harness evidence;
- the confirmatory runs are the physics models (B0, B0-b, B1, B2 and the oracle B0*) on the 10
  outer folds under R2 and R1, for H4b and H4c, plus the section 8 analyses;
- the paper's negative result is about the method, not the data: a grey-box learner given only
  isotherms could not reliably recover a known, injected, isotherm-dependent rate correction of
  this size at the noise floor of these measurements. No statement is made that learning cannot
  help on the real data.

**The untouched fold, Al-fumarate** (`results/harness_alfu/harness.json`, same code and seed,
finished 2026-11-10 07:48). World N: no beat (L1 0.00035 against B0 0.00034, p = 0.88; k″
recovered within 0.15 %), so criterion 3 holds on all three sorbents. World C3: a beat, with
median E 0.028 against 0.067 (ratio 0.42, gain 0.031, p = 7.6 × 10⁻⁶). L1 thus met criterion 2
on two of the three judged sorbents and failed it on MOF-303, the one with the smallest injected
effect. The outcome above stands.

## 10b. Synthetic harness for H4a′ (B2), must pass before the freeze

Added on 2026-11-10 with H4a′. Version 1 of the script (repository da52584) was revised after an
independent red-team review the same day; its only run was stopped before any result was read
and its output is archived unread (`results/harness_b2_aborted_unread/`). Version 2
(`audit/harness_b2.py`, repository 78accf6, committed before its first run) is the one that
counts. It uses the real forcing, isotherms and dry masses of the primary set and the two
composites, the truth integrated by the B0 integrator unless stated, and AR(1) noise
(σ = 0.01 wt%, φ = 0.9). Each world runs the 8 LOSO folds; per fold, B0 and B2 are fitted on the
training sorbents by the scored metric and the section 7 rule is applied with each material's
real F (`results/prefreeze/checks2.json`) and the admissibility check.

- **N**: the truth is B0 with the pooled k″ of the real data.
- **K** (plumbing): log k″ of each sorbent is shifted by 1.5·(RH₅₀/30 − mean), the means over the
  8 primary sorbents at each temperature (across-sorbent SD of log k″ 0.27 at 27 °C, 0.33 at
  60 °C; no end-point offsets). The truth lies inside B2's class, so this checks the machinery,
  not power.
- **K2a, K2b, K2c** (realistic power; reported, and they set the wording of a real "falsified",
  section 7): the same form with the slope at each temperature chosen so that the across-sorbent
  SD of the shift equals the real in-sample SD of log k″ (0.089 at 27 °C, slope 0.50; 0.300 at
  60 °C, slope 1.38), plus end-point offsets drawn as in the S worlds. This is the largest effect
  of the measured size that the isotherm could carry, with end-point error on top.
- **S0 to S5, structure-free null worlds** (cs T-P4-5 R1 without its shape term): log k″ of each
  sorbent and temperature is shifted by b ~ N(0, σ_b(T)²), σ_b = 0.089 and 0.300, independent of
  the isotherm, one b for both directions; the equilibrium is the isotherm scaled by (1 + ε), with
  |ε| resampled from the 18 measured group offsets, a random sign, and |ε·w₃₀| ≤ 3.128 wt% (the
  observed offsets reach −1.16 wt% on the negative side, so the symmetric cap is generous there).
  Nothing any model sees predicts these draws and no component is shared by all sorbents, so any
  beat is a false positive of a null without model-form error.
- **C3** (form error; reported only): world C3 of the L1 harness (section 10), a rate law shared by
  every material but not of B0's form. A B2 beat there would come from the isotherm shape changing
  B0's best effective k″, the confound of section 2.

Draws: b and ε come from `default_rng([2000 + j, crc32("sorbent|T")])` for null world j, the K2
offsets from `[3000 + j, ...]`; noise from `default_rng(seed + 10)` with seeds N 1, K 1, K2a–c
21–23, S0–S5 0–5 (S1 shares its noise seed with N and K; the truths differ). Composites get their
own draws and their own RH₅₀.

It passes if (1) no fold is beaten in N; (2) at least 7 of 8 folds are beaten in K and the median
over folds and strata of |b_fit/1.5 − 1| is at most 0.25; (3) over the 48 null fold-fits of
S0–S5, the one-sided 95 % Clopper–Pearson upper bound on the per-fold beat rate is at most 0.40,
no world has 5 or more of its 8 folds beaten, and the median of r is below 2.5 %. The 0.40 bound
keeps P(at least 7 of 8 | H0) ≤ 0.05 for a within-world fold correlation ρ ≤ 0.12, a model
assumption taken from cs T-P4-5's stylised simulation (ρ 0.03 to 0.12 without a shared
component; the simulation and its output are archived in `audit/cs_T-P4-5/`); the within-world
correlation of beats over the six worlds is reported. The
median of r replaces the mean, which one catastrophic fold can pull down. Criterion 3 tests a null
without model-form error; world C3 reports the form-error case. If the harness fails, H4a′ is
"not tested" (section 7), and no further hypothesis is added. The K2 and C3 results are reported
whatever happens.

**Result (2026-11-11; `results/harness_b2/harness_b2.json` from the four part files, summary in
`results/harness_b2/report.json`, written by `audit/b2_harness_report.py`). The harness passed all
three criteria.**

| World | Folds beaten (of 8) | Median r | Median E, B0 | Median E, B2 | Median fitted b (27 °C ads, des; 60 °C ads, des) |
|---|---|---|---|---|---|
| N | 0 | −0.002 | 0.0005 | 0.0005 | 0.000, 0.000, 0.001, 0.000 |
| K | 8 | 0.993 | 0.072 | 0.0006 | 1.500, 1.500, 1.501, 1.502 |
| K2a | 7 | 0.602 | 0.060 | 0.014 | 0.560, 0.178, 1.372, 1.324 |
| K2b | 7 | 0.425 | 0.055 | 0.016 | 0.446, 0.541, 1.400, 1.305 |
| K2c | 5 | 0.327 | 0.083 | 0.017 | 0.510, 0.504, 1.178, 1.228 |
| S0 | 0 | −0.064 | 0.054 | 0.050 | −0.072, −0.108, 0.117, 0.161 |
| S1 | 0 | −0.041 | 0.044 | 0.050 | −0.251, −0.057, −0.146, 0.061 |
| S2 | 2 | 0.024 | 0.043 | 0.042 | 0.180, 0.062, −0.269, −0.117 |
| S3 | 0 | −0.020 | 0.043 | 0.051 | −0.128, −0.020, −0.007, 0.901 |
| S4 | 0 | −0.014 | 0.042 | 0.050 | 0.241, 0.143, −0.057, −0.209 |
| S5 | 1 | −0.019 | 0.039 | 0.045 | 0.273, 0.346, 0.371, 0.441 |
| C3 (form error) | 6 | 0.523 | 0.031 | 0.011 | −0.541, −0.628, −0.650, −0.638 |

(Median E: median over the 8 folds of each fold's median E over its held-out segments. True slopes: K 1.5 everywhere; K2 0.50 at
27 °C and 1.38 at 60 °C.)

- Criterion 1: no fold beaten in N.
- Criterion 2: 8 of 8 folds beaten in K; median |b_fit/1.5 − 1| = 0.0005.
- Criterion 3: 3 of the 48 null fold-fits beaten (S2: CAU-10-H and Syloid; S5: MIL-160);
  one-sided 95 % Clopper–Pearson upper bound 0.154 (limit 0.40); at most 2 of 8 in any world
  (limit 5); median r over the null folds −0.027 (limit 0.025; 90th percentile 0.091). The
  within-world correlation of null beats (moment estimator over the six worlds) is 0.064, inside
  the ρ ≤ 0.12 that the 0.40 bound assumes.
- No B2 fit in any world had excess physical violations above 0.007 of a fold's segments.

What follows, from sections 2 and 7 as already written (nothing is changed by this result):
- H4a′ is testable; its verdict will be decided by section 7.
- **Realistic power.** B2 was "supported" in K2a and K2b (7 of 8 each) and "not established" in
  K2c (5 of 8). An effect of the measured size is therefore found in two of three realistic
  worlds, not all three, so if H4a′ is falsified on the real data the paper must use the weaker
  wording of section 7, "no isotherm-predicted rate constant was detectable at this noise and
  error level", and state that an effect of the measured size was missed in one of three
  realistic-power worlds.
- **Form error (C3).** A rate law shared by every material but not of B0's form made B2 beat B0 in
  6 of 8 folds, with median r 0.52 and a negative fitted slope at both temperatures. This is the
  confound named in section 2 and it is large: a "supported" verdict on the real data shows only
  that the isotherm predicts the effective k″ of Bezrukov's equation, which a shared form error
  alone can produce, and the paper must say so beside the verdict. The fitted slopes on the real
  data are reported with it (row field `B2_ab`).
- **Limitation of the harness.** Every harness fit used the plain B0 variant (adsorption branch in
  both directions); B2 built on B0-b was not exercised. In the archived null replicate
  `results/null_rep0_preD` all six folds it ran chose B0 (B0-b's training score higher in each),
  so the untested path may not be used; the variant
  of each real fold is reported with the verdict.

## 11. Compute

**Since 2026-11-10 (L1 not tested, section 10; H4a′ added, section 2) the confirmatory runs are
physics only:** `p4.run_study ... --kinds none` under R2 and under R1 (`--rule R1`), 10 outer folds
each (8 LOSO and the 2 LOFO folds that differ from them; section 4), fitting B0, B0-b and B1,
choosing the comparator, and fitting B2 and the oracle B0* by the scored metric. One physics fold
took about 64 minutes in the end-to-end dry run (`results/dryrun_null.log`) and 29 to 43 minutes
in the six folds of the archived null replicate (`results/null_rep0_preD/rows.jsonl`, field `s`),
on the shared laptop: 5 to 11 hours per rule, at most about 22 hours in all. Nothing is reduced.

The confirmatory commands, in this order (Python 3.12 venv of the repository, `requirements-lock.txt`):

    python -E -s -m p4.run_study data_derived/bezrukov2023 results/confirm_R2 --kinds none
    python -E -s -m p4.run_study data_derived/bezrukov2023 results/confirm_R1 --kinds none --rule R1
    python -E -s -m p4.decide results/confirm_R2/rows.jsonl results/prefreeze/checks2.json results/confirm_R2/decide.json
    python -E -s -m p4.decide results/confirm_R1/rows.jsonl results/prefreeze/checks2.json results/confirm_R1/decide.json
    python -E -s -m p4.final_verdict results/confirm_R2/decide.json results/confirm_R1/decide.json results/harness_b2/harness_b2.json results/final_verdict.json B2

Before the freeze the same chain was run end to end on a synthetic world (section 9).

The plan below was the one for the learned models and is kept for the record.

Measured in harness round 2 (`results/harness_round2/harness.json`, six or seven training
sorbents per fit, on the shared laptop): one L1 fit took 39 to 55 minutes (mean 45.5).

The protocol had 10 outer folds. Per fold: 4 configurations × 1 seed for tuning, then 5 seeds of
the chosen one, so 9 fits. That gave 90 L1 fits (L2 was dropped; section 10):

| Item | Fits | Hours (single job) |
|---|---|---|
| L1, primary rule R2 | 90 | about 68 |
| R1 sensitivity, reusing each fold's R2 configuration (5 seeds only) | 50 | about 38 |
| Null study before the freeze, 2 replicates × 8 folds, 1 configuration, 1 seed (3 replicates, 24 fits, in the last plan) | 16 | about 12 |
| Null study with the confirmatory runs, 1 replicate × 8 folds, full procedure (4 + 5 fits) | 72 | about 55 |
| Physics in every run (10 folds for R2 and R1, 8 per null replicate; about 64 min per fold) | — | about 47 |
| **Total** | 228 | **about 220** |

The R1 sensitivity run reuses the configuration chosen under R2 in each fold. It asks whether
the dry-mass definition changes the verdict, not whether tuning changes it.

**Pre-registered reduction order (learned models; no longer applies)**, applied only if the full protocol cannot be run, decided
and recorded at the freeze (before any real-data fit exists) and never afterwards:

1. R1 sensitivity seeds 5 → 3;
2. seeds per ensemble 5 → 3 (all other runs, including the full-procedure null replicate);
3. tuning grid 4 → 2 configurations (width 32; both weight decays).

The null study is not on this list (review finding N1): it is what makes a positive H4a
credible, so it is never reduced.

Full inner leave-one-sorbent-out would add roughly 300 h for the learned models and about
17 to 28 h per run for the physics comparators (seven inner folds, each refitting the three
candidates on six sorbents: 6 × the 17 to 28 minutes the three candidate fits took per fold in null
replicate 0, `results/null_rep0/rows.jsonl` field `s_parts`, × 10 folds); neither is planned (section 5). The jobs are
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
    fitted by the scored metric). That is 3.5 to 67 times the noise floor, median 16 over the 32
    strata (sorbent × temperature × direction). The remaining error lies in the model's form or in its isotherm input (step end-points miss the isotherm by group medians of −1.16 to +3.13 wt% under R2).
  - Under R1 (`reproduce_b0_R1.json`): coefficients of variation 0.08, 0.10, 0.42, 0.29
    (population SD); E 0.018 to 0.206.
  - The pooled k″ fitted by the scored metric, as the comparator now is (section 5), is close to
    the least-squares value at 27 °C (0.320 against 0.323 for uptake, 0.252 against 0.257 for
    release) but clearly lower at 60 °C (1.25 against 1.59, and 0.86 against 1.03), consistent with
    the median discounting the worst-fitted segments that dominate a squared error. With it, B0's in-sample
    median E per stratum is 0.030 to 0.237, against 0.028 to 0.256 with the least-squares k″.
- **Physical-violation floor** (section 6; `results/prefreeze/violation_floor.json`): the share of
  measured segments in which uptake moves against the step direction for a minute is 0 for the
  three ROS sorbents, Syloid and both composites; 0.04 for MIL-160, 0.06 for CAU-10-H, 0.15 for
  Al-fumarate and 0.28 for MOF-303.
- **Null-world size** (section 10; `results/null_calibration.json`, recomputed for the revised
  null world of 2026-11-08, before the per-sorbent draws and offset cap of 2026-11-09; not
  recomputed after them, because the L1 null study is not run): B0's median E over the eight sorbents is 0.057, 0.070 and 0.045 for replicates
  0 to 2, against 0.067 on the real data; the null world's F per group is 0.0014 to 0.0140,
  against the real 0.0009 to 0.0126.
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
- 2026-11-09. **Second review (Claude Science T-P4-3) answered.**
  - Comparators and B2 are fitted by the scored metric, like the oracle (N5). The comparator is
    chosen on all training sorbents, not on Syloid (O2); inner leave-one-sorbent-out, which the
    review proposed, was costed and rejected (section 5).
  - Scored segments follow the audit rule, |Δm| ≥ 0.05 mg with the step's sign, not |Δw| ≥
    0.05 wt% (C1). In P this excludes no segment: all move 4.0 to 40.6 wt%, so F and the cluster
    counts are unchanged. The test ranks the unnormalised difference D, so that within a fold
    the larger steps (up to about five times larger) carry more weight than under d (C1). A parent and
    its composite must each pass (C2).
  - Falsification uses the 7th order statistic of r over the 8 folds, not a bootstrap (O1).
    Violations count against a learned model only beyond both the data and the comparator (O3).
  - Null world: the expected rate factor is exactly 1 at every w (N4); the rate spread is per
    temperature (N4); material-specific equilibrium offsets are resampled from the data (N3).
    Criterion 4 no longer leans on independent folds (N1). One null replicate runs with the
    full confirmatory procedure for L1 and gates "supported" (N2). The null study is off the
    reduction order (N1).
  - The harness now applies the section 7 rule of `p4/decide.py` itself (clusters, D test,
    every material), not the old segment-level bootstrap in `p4/train.py`.
  - The metric fit searches a narrower, moving log grid (±0.5 decade, 11 points, shifted if the
    best point is at an edge) instead of a fixed ±2-decade grid of 41 points. Batching all
    materials into one integration was tried; it gave identical results but was not faster
    on this machine, and it was dropped.
  - All pre-freeze numbers were recomputed after the inclusion change (section 12).
- 2026-11-09 (review T-P4-4 and the null-world diagnostics; none of this used real data).
  - World C2 and round 5 and 6 text added to section 10 (F-1, F-4). L1 gained the driving force
    d as an input after round 6 (section 5). Condition 4 of the section 7 rule added after round 6
    showed a paired-median "beat" with a worse typical error.
  - World C3 committed before any run on it (repository commit a7d163e). A stopping rule for the
    harness: round 7 is L1's last; and C3 is also judged on Al-fumarate, a sorbent no diagnostic
    held out (F-2, F-3). Both written while round 7 was in world C, before any C3 result.
  - r in a parent + composite fold is the smaller per-material value (F-6). The rule is also
    applied against every comparator candidate and against the held-out-best one, which sets
    the wording of a positive claim (F-7).
  - Criterion 4 rewritten around the per-fold null beat rate: Clopper–Pearson 95 % bound ≤ 0.40,
    no replicate with 5 or more of 8 beats, mean r below 2.5 %; 3 null worlds before the freeze
    (F-5 and the sorbent-level-luck diagnostic). A null replicate with the old L1 (before the d
    input) is archived in `results/null_rep0_preD/` and does not count.
  - Null draws are keyed per sorbent, and |ε·w₃₀| is capped at 3.13 wt% (F-8, F-9). The null
    calibration numbers in section 10 were computed before this change and were to be recomputed
    with it before the freeze; after round 7 they were not, because the L1 null study is not run
    (section 12).
- 2026-11-10 (independent re-implementation of the decision rule from this text alone,
  `audit/independent_decide.py`, compared with `p4/decide.py` on the archived null replicate and
  240 random cases; `results/independent_decide_check*.json`). Five places in the text were
  unclear and are now explicit: each material is judged against its own F (section 6 said the
  largest); clusters with D = 0 are dropped; a diverged prediction counts as an infinite loss; the
  held-out-best candidate is chosen by the median over segments; disagreeing R1 and R2 verdicts
  give "not established". The confirmatory full-procedure null world is replicate 3. Code fixes:
  a held material with no scored segment now fails (it was skipped); a non-finite model E now
  counts as a loss (it was dropped, which favoured a diverging model); r is computed once and
  used for both condition 2 and "falsified" (the two could disagree at exactly 10 % by rounding);
  the cluster gain is the mean of segment differences. `p4/final_verdict.py` added. No result
  depended on these: no real-data fit exists, and the archived null replicate agrees in every fold.
- 2026-11-10 (round 7 result). L1 failed criterion 2 in world C3 on MOF-303 (section 10). Under
  the stopping rule written on 2026-11-09, before any C3 result, H4a becomes "not tested", the
  confirmatory L1 fits and the null study are not run, and the confirmatory runs are the physics
  models for H4b and H4c. The Al-fumarate run continues because it was specified in advance; it
  cannot change the outcome.
- 2026-11-10 (after round 7; written before any real-data fit). H4a′ added (section 2): B2 judged
  by H4a's rule, with its own synthetic harness (section 10b; script and criteria committed in
  da52584 before the first run; that was version 1, replaced the same day by version 2, 78accf6,
  the one that counts) in place of criterion 4. Reason and what was on record are in
  section 2. Title changed. Compute is physics only (section 11). The end-point oracle added to
  section 8. cs T-P4-5's null recommendations (structure-free worlds, 0.40 bound with a stated
  fold-correlation assumption, median r) are used in section 10b; the L1 null study is not run.
- 2026-11-10 (independent red-team of H4a′, a fresh read-only reviewer while cs is out of usage;
  22 findings, 4 blocking; all addressed before any B2 harness result was read). B2 is judged
  against the pooled B0 of the same variant, and built on that variant (B2); a failed B2 harness
  gives "not tested" in text and code (B3); section 10 no longer gates the freeze, section 10b
  does (B4); harness version 2 adds realistic-power worlds K2a–c that set the wording of a
  falsification (B1), six null worlds (M9), the real per-sorbent F and admissibility (M11, m15),
  and the form-error world C3 (M5, M8); fit_b2 centred with an explicit simplex (M10); end-point
  oracle per direction, missing offsets reported (M13, m14); title, section 1, the H4a′ wording
  ("effective k″"), the disclosure (form fixed on 2026-11-08, CAU-10-H visible, null-replicate B2
  behaviour, RH₅₀ computed the same day) and the descriptive share of the oracle gain (M5–M7);
  negative-results paragraph (M12); stale statements (m19). The version 1 harness run was
  stopped and archived unread.
- 2026-11-11 (B2 harness result, section 10b). Version 2 passed all three criteria. It was run in
  four parts because of memory (a cmd quoting bug first made each part stop after its first
  world; relaunched with the same code and seeds; world S5 moved to a fourth part and the first
  part stopped after K2b, so no world was computed twice). Consequences, from the rules already
  in sections 2 and 7: H4a′ is testable; a falsification takes the weaker wording, since K2c was
  "not established"; a support must be reported with C3's form-error result (6 of 8 folds).
  Nothing in the rule or the wording rules was changed after the result.
- 2026-11-11 (independent read-only pre-freeze consistency review, text against code; after the
  B2 harness result, before any real-data B2 fit). Code: B2's admissibility was counted against
  the chosen comparator's violation flags, not the pooled B0 of the fold's variant that section 7
  and the harness use; fixed (`viol_B0`, with a test). `p4.final_verdict` defaulted to kind L1,
  which `--kinds none` does not produce; it now defaults to B2 and writes the wording rules of
  sections 7 and 10b. Text: the fold's B0 variant defined (section 5); the extrapolation flag
  given a rule, which adds ROS-039 at both temperatures (section 2); section 8 made to match the
  end-point code (per direction, equilibration rule); bootstrap intervals for H4b and H4c, never
  defined, dropped (section 7); exact confirmatory commands and a synthetic end-to-end run
  (section 11); the harness's B0-b limitation (section 10b); stale statements corrected. The
  decision rule, its thresholds and the wording rules are unchanged.
