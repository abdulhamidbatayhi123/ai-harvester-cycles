# T-P4-6 novelty check and competitor check

Search date: **2026-11-10**. Every DOI below was resolved on Crossref that day (raw records are in
`T-P4-6_verification.json`). Status letters (A/B/C) are defined in `T-P4-6_references.md`.

## How the search was done, and its limits

- **Crossref** `works?query.bibliographic=` (no e-mail in any request). Queries run:
  "water sorption kinetics metal-organic framework dynamic vapor sorption"; "MOF-303 water adsorption
  kinetics"; "MIL-160 water adsorption dynamics adsorption heat transformation"; "aluminium fumarate
  water adsorption dynamics"; "effect of sample mass dynamic vapour sorption kinetics"; "large
  temperature jump water adsorption dynamics loose grains layer"; "water vapor sorption kinetics rate
  constant correlation isotherm multiple metal-organic frameworks comparison"; "comparison water
  adsorption kinetics several MOFs mass transfer coefficient isotherm shape step position"; "predict
  kinetics from isotherm water adsorption MOFs desiccants transferable model"; "machine learning
  prediction water adsorption kinetics metal-organic frameworks"; "leave-one-material-out validation
  adsorption model metal-organic frameworks"; "preregistered machine learning materials study";
  "pre-registration computational study machine learning stopping rule"; "synthetic data validation
  hybrid model neural network identifiability parameter recovery dynamical system"; "water sorption
  kinetics metal-organic frameworks benchmark multiple sorbents heat and mass transfer limited powder
  layer"; plus title searches for each competitor record and an author search (`query.author=Ferrer
  Pareja`, from 2026-01-01).
- **Web search** (general engine) for the competitor and for the closest kinetics-structure paper.
- **Zenodo REST API** for the competitor records and all records with creator "Ferrer Pareja".
- **Not available:** OpenAlex (free daily budget exhausted; a key needs an e-mail address, which the
  rules forbid), Google Scholar (no automated access), and publisher pages (ScienceDirect, Cell,
  Springer returned 403 or a login redirect; Claude in Chrome was not connected). The novelty claims
  below therefore rest on Crossref plus web search. **Recommendation:** queue a Claude Science
  re-check with OpenAlex and Google Scholar before submission (cc-to-cs message, scope = the three
  questions below).

## (a) Held-out-material test of water-sorption kinetics models across several sorbents

**Finding: none found.** No paper found tests a water-uptake kinetics model by predicting a sorbent
that was left out of the fit.

Closest prior work:

1. **Bezrukov et al. 2023**, *Cell Rep. Phys. Sci.* 4, 101252, doi:10.1016/j.xcrp.2023.101252
   (status B). Measures AWH uptake kinetics of seven MOFs and Syloid and describes them with one
   isotherm-driven rate law that has a single rate constant for all materials; concludes the uptake is
   limited by diffusion to the sorbent bed surface. *Difference:* the shared constant is fitted to
   all materials together. Nobody tests whether it, or a descriptor-based value, predicts a sorbent
   that was left out, which is our confirmatory test.
2. **Velte et al. 2023**, *Appl. Therm. Eng.* 227, 120336, doi:10.1016/j.applthermaleng.2023.120336
   (status B, via the SSRN preprint abstract). Measures sorption dynamics of Al-fumarate, MIL-160(Al),
   CAU-10-H and TiAPSO coatings before and after hydrothermal cycling. *Difference:* a descriptive
   comparison across materials. No model is fitted on some materials and tested on others.
3. **Ferrer Pareja et al., Zenodo 10.5281/zenodo.23222539** (dataset, 2026-10-07; not peer
   reviewed). Per its description, it validates equilibrium and LDF kinetics against field-measured
   capacities from Song et al. 2023 (Death Valley) for MOF-303 and MOF-801. *Difference:* it
   validates against field-measured capacities, not time-resolved DVS uptake,
   and has no held-out-sorbent design (see the competitor section).

Related multi-material kinetics work, all descriptive, with no hold-out: Solovyeva & Gordeeva 2023
(doi:10.3390/nano13172442, MOF-801 configurations), Li et al. 2025 (doi:10.1002/admi.202400628, MOF-801
powder vs monolith), Abu EL-Maaty et al. 2024 (doi:10.1016/j.ecmx.2024.100694, MOF-303 vs silica gel).

## (b) Do isotherm features predict sorption rate constants across MOFs?

**Finding: no direct test found.** We found no study that uses an isotherm descriptor (such as the
step position or RH50) to predict a rate constant for an unseen MOF. One paper may come close and has
to be read before submission.

Closest prior work:

1. **Xia, Li, Chen, Li 2025**, *Colloids Surf. A* 720, 137168, doi:10.1016/j.colsurfa.2025.137168
   (status **C**, so the abstract was not readable; the SSRN preprint 10.2139/ssrn.4270233 by Li & Xia,
   2022, has no abstract either). Title: "Relationship between water adsorption kinetics and structure
   property of metal-organic frameworks for adsorption cooling". It probably correlates kinetics
   with *structural* properties (pore size, surface area) across MOFs, but that is a guess from
   the title. *Possible difference:* structural descriptors, adsorption-cooling (vacuum) conditions,
   and most likely in-sample correlation, not a pre-registered held-out prediction from an
   *isotherm* descriptor. **Action: read the full text and check this before we claim novelty.**
2. **Glaznev, Ovoshchnikov, Aristov 2009**, *Int. J. Heat Mass Transf.* 52, 1774-1777,
   doi:10.1016/j.ijheatmasstransfer.2008.09.031 (status C). Title: kinetics of water
   adsorption/desorption under isobaric stages, "the effect of isobar shape". Links equilibrium-curve
   shape to uptake kinetics, apparently for one or a few sorbents and as a mechanism study. *Difference:*
   it does not predict across materials.
3. **Hossain & Glover 2019**, *Ind. Eng. Chem. Res.* 58, 10550-10558, doi:10.1021/acs.iecr.9b00976
   (status A). The water uptake rate in UiO-66 depends on loading, with a minimum near 4 mol/kg.
   *Difference:* this is a link between loading and rate within one MOF, not between materials.

## (c) Pre-registered ML-for-materials study with a synthetic harness and a stopping rule

**Finding: none found in materials science or chemistry.**

Closest prior work:

1. **Nikolenko 2026**, *IEEE Access* 14, 158836-158853, doi:10.1109/access.2026.3741122 (status A).
   A pre-registered ML study on four public machine-fault-diagnosis rigs that reports a partly negative
   result: modality graphs predict reconstructability but not fusion gain. *Difference:* it is not
   materials science, and we could not see a synthetic ground-truth gate or a stopping rule in the
   abstract.
2. **Ferrer Pareja et al., Zenodo 23222539** says its "preregistered quality criteria and modeling
   decisions [were] fixed before results were computed". *Difference:* the record is a dataset and
   does not link to any registration. It has no synthetic ground-truth harness and no stopping rule
   for a learned model.
3. **Methodological precedents, not materials:** simulation-based calibration (Talts et al. 2018,
   doi:10.48550/arXiv.1804.06788; Modrák et al. 2025, doi:10.1214/23-BA1404) and Cook, Gelman & Rubin
   2006 (doi:10.1198/106186006X136976) test an inference method on data simulated with known truth
   before real data. Our harness applies the same idea to a grey-box kinetics model and uses it as a
   pre-registered gate with a fixed number of rounds.

## Competitor check: Ferrer Pareja et al. (Universidad de Las Palmas de Gran Canaria)

Authors on all three records: Miguel Ferrer Pareja, Carlos Sánchez Morales, Federico León Zerpa,
Alejandro Ramos Martín (all ULPGC).

| Zenodo record | Published | Content (from the record description) |
|---|---|---|
| 10.5281/zenodo.23222539 | 2026-10-07 | "From measured isotherms to field performance: a traceable MOF water-sorption library and kinetic model validation": Dubinin-Astakhov fits to 62 NIST ISODB materials; MOF-303/MOF-801 isotherm fits; equilibrium and LDF-kinetics validation against Song et al. 2023 field capacities; "preregistered" criteria |
| 10.5281/zenodo.23226307 | 2026-10-08 | Multi-objective (NSGA-III) optimisation of passive solar MOF AWH; screens 12,020 CoRE MOF 2019 structures down to 185; validates a "point-equilibrium kinetic closure" against three measured field cycles (Song et al. 2023); **includes the final manuscript LaTeX source** |
| 10.5281/zenodo.23286170 | 2026-10-10 | Linear-regression surrogate trained on n = 99 measured water-sorption data, GA search, and virtual screening of 1,780 CoRE MOF structures |

Status on 2026-11-10:

- Each record has one version, with no newer version under its concept ID and no
  `related_identifiers`, so no record links to a paper or preprint.
- A Zenodo search by creator "Ferrer Pareja" (20 records) found no other MOF or water-sorption record
  after 2026-10-10. The later records are on thermoelectric/fractional-order control, a statistics
  book companion, and a Peltier dew-point controller.
- A Crossref author search ("Ferrer Pareja", from 2026-01-01; this covers journal articles and
  posted content such as ChemRxiv, SSRN and Research Square) found only thermoelectric/control papers
  (e.g. Appl. Therm. Eng. 10.1016/j.applthermaleng.2026.133836; Fractal Fract. 10.3390/fractalfract10100695;
  J. Chem. Educ. 10.1021/acs.jchemed.5c01810) and nothing on MOFs. Crossref searches on the three
  record titles found nothing.
- A web search for "Ferrer Pareja" with MOF water harvesting found nothing.
- **Conclusion: as of 2026-11-10, no preprint or journal paper from this group on MOF water
  harvesting was found.** At least one manuscript exists, because its LaTeX is in record 23226307.
  The overlap with our paper is thematic: measured validation of harvester kinetics models. Their
  validation is against field yields (Song et al. 2023) and equilibrium screening. It is not a
  held-out-sorbent test on DVS uptake curves. Re-check monthly (Zenodo concept IDs 23222538,
  23226306, 23286169; Crossref author query) and before submission.

## Bottom line for the paper's novelty statement

As far as Crossref and web search show on 2026-11-10, these parts are new:
(i) a pre-registered held-out-sorbent test of an isotherm-driven DVS uptake model;
(ii) a confirmatory test of whether an isotherm descriptor (RH50) predicts an unseen sorbent's
effective rate constant better than one shared value;
(iii) a synthetic ground-truth gate with a stopping rule applied to a grey-box (UDE-type) kinetics
model, with the failed gate reported.
Before (ii) is claimed in print, Xia et al. 2025 must be read in full, and the OpenAlex/Scholar
re-check should be done.
