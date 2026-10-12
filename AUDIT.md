# Paper 4 data audit

Question: can a cycle-level model of MOF water harvesting (uptake and release over time,
driven by temperature and humidity, giving productivity) be trained on some materials and
tested honestly on materials it has never seen, using only published measured data?

Every fact below carries its source and the date it was read live. A yield or curve that
comes from a model is labelled as such and is never used as ground truth.

## 1. Criteria, fixed before any data file was opened (2026-10-12)

A dataset, or a set of datasets that can be pooled, is judged against these.

- **C1 Materials.** At least 5 distinct sorbents measured under one shared protocol. With
  fewer, leave-one-material-out leaves too few training materials and too few test cases to
  say anything about transfer. Eight or more is the level at which a held-out error can be
  reported with a spread rather than as a handful of anecdotes.
- **C2 Drivers logged.** The temperature and humidity the sorbent actually saw are recorded
  on the same clock as the uptake, not only the setpoints. A dynamic model is only as good
  as the forcing it is given.
- **C3 Resolution.** The sampling interval is at most one tenth of the uptake (or release)
  time constant estimated from the same record, and each record contains at least one full
  uptake and one full release.
- **C4 Repeats.** At least two cycles per material under the same conditions, so that a
  test-retest noise floor can be measured. A model error is only meaningful next to it.
- **C5 A material descriptor that is not the answer.** Each material has a measured water
  isotherm (in the same dataset or another open one), so that a held-out material can be
  described to the model without showing it that material's kinetics.
- **C6 Measured.** The time series is a measurement, not a simulation or a projection.
- **C7 Licence.** Reuse and publication of derived data are permitted.
- **C8 Scale.** Whether the data are device-level (a bed of grams to kilograms, with a
  condenser, field or chamber weather) or sorbent-level (milligrams in a dynamic vapour
  sorption balance, DVS). A claim about devices needs device data on at least two materials.

Outcomes:

- **GO (device).** C1 to C7 met by device-level data. The paper can claim transfer of
  harvester cycle dynamics across materials.
- **GO (sorbent level).** C1 to C7 met only by DVS-scale data. The paper may claim transfer
  of sorbent cycle dynamics across materials; device records serve only as an external check
  of how far the sorbent-level model carries to a real harvester, and the title and abstract
  must say "sorbent" or equivalent, not "harvester" or "device".
- **NO-GO.** Neither. The report then names the smallest paper that can be written honestly.

The single-material device records (Song 2023, MOF-303; Almassad 2022, MOF-801) cannot by
themselves test transfer across materials, whatever their quality. At most they are external
validation targets.

## 2. Live verification of candidate datasets

### 2.1 Almassad et al. 2022, Nat. Commun. 13, 4873 (MOF-801 adaptive device)

Read 2026-10-12. Article full text via Europe PMC (PMC9391386, fullTextXML API). Source Data
file downloaded from Springer
(`41467_2022_32642_MOESM3_ESM.xlsx`, 20,892,056 bytes, HTTP 200). Licence: the article is
CC BY 4.0 and the data statement says "Source data are provided with this paper".

What the file holds (read sheet by sheet with `audit/xlsx_sheet.py` and `audit/almassad_detail.py`):

- Figure 3A/3B: dew point (from logged RH and temperature) against minutes during adsorption
  and desorption trials at seven humidity levels (14 to 45 % RH), 1-minute steps, about 200 to
  300 minutes each.
- Figure 4A: air RH inside the adaptive and the timer-driven device side by side, 860 minutes,
  1-minute steps. Figure 4B: eleven cycle-time differences against ambient RH.
- Figure 5A: a 24 h stress test at 20 % RH, 1-minute RH trace, plus water collected for nine
  cycles (39 to 44; the sheet gives no unit, and the article reports per-cycle production in mL, so mL per cycle is likely but unconfirmed).
- Figure 5C and 5D: one week (10,081 rows) and about 37 days (45,311 rows) of air temperature
  and RH at 1-minute steps, field operation in Jordan, February to March 2022.
- Figure S28 + S30: the same long log with derived dew point.
- Figure S22: one water isotherm of MOF-801 (56 points, cm³/g against P/P0). Other sheets are
  PXRD and TGA.

What it does not hold: any record of the sorbent's water content over time. The sensors
measure air (in front of the heater, top and bottom of the sorption compartment, condenser);
the 400 g of MOF-801 is never weighed during a cycle. Water collected is given only per
cycle and only for nine cycles of one test.

Judgement against section 1: measured (C6), licensed (C7), 1-minute resolution adequate for
cycles of 20 to 90 minutes (C3), many cycles (C4), but one material (C1 fails), and the
sorbent state is unobserved. It is a usable external check on a model's predicted cycle
timing (when the bed saturates, when desorption ends) for MOF-801 in a real device, if the
model can be driven by the logged air conditions. It cannot test transfer across materials.

### 2.2 Song et al. 2023, Nature Water 1, 626 (MOF-303 passive device)

Zenodo record 7990951 read through the API 2026-10-12: CC-BY-4.0, published 2023-07-01, one
version, one file `Data-Song et al. Nat. Water.opju`, 2,315,847 bytes, md5
f37d2ad1ec09c9686eca80b19e893e82. Downloaded; the md5 matches. The article page on nature.com
(read 2026-10-12) lists only a PDF supplement and three videos, no Source Data spreadsheet, so
this Origin project is the only machine-readable release.

The file is an Origin Unicode project (header `CPYUA 4.3598`). No open-source reader decodes
it: the current SciDAVis liborigin (fetched from GitHub 2026-10-12 and compiled here)
recognises the header but fails on the body ("Wrong delimiter" at byte 22), and a scan for
stored float64 arrays found none, so the numbers are encoded. Origin is not installed on this
machine. The text that is readable names the worksheets and axes: `Time (h)`, `Time (min)`,
`RH_amb`, `RH_case`, `RH_Con`, `Temperature`, `Solar irradiance (W/m²)`, `H2O uptake (g/g)`,
`MOF-303 / day`, books `CapacityRH` (A to G) and `BerkeleyJun2`, and figure exports for
Fig. 3c. The `H2O uptake (g/g)` axis turned out to be the isotherm, not a time series (section 2.4).

From the article (read in full on 2026-09-25 for the program's literature journal, entry S07;
not re-read today because nature.com is paywalled): one cycle per day, adsorption at night and
solar desorption by day; 114 to 210 g of water per kg of MOF per day in Death Valley, 285 in
Berkeley; ambient 21.9 to 60.7 °C and 9.4 to 36 % RH.

Judgement: measured, licensed, one material, one cycle per day, so only a handful of cycles per site (the exact count is not verified until the numbers are extracted).
Like Almassad, an external check at most. Extracting the numbers myself would need Origin or
the free Origin Viewer; that turned out to be unnecessary, because another group has already
exported and deposited them (section 2.4).

### 2.3 Bezrukov et al. 2023, Cell Rep. Phys. Sci. 4, 101252 (seven MOFs and a silica gel, DVS)

Zenodo record 6631711 read through the API 2026-10-12: CC-BY-4.0, published 2023-01-23, one
version, one file `data.zip`, 606,719,336 bytes, md5 b5c12ec0c6bde5102075bc59429d9dae.
Downloaded (the first attempt stalled at 485 MB and was resumed); the md5 matches. The archive
holds 257 files, 3.48 GB uncompressed: 174 instrument exports (.xls/.xlsx), 71 binary .dat
twins of them, and 12 small CSVs of hypothetical isotherms used in the paper's model study. The
analysis code (github.com/AndreyBezrukov/Water_Sorption_Kinetics, last push 2023-01-12) has no
licence file, so it can be read and its ideas reused but not redistributed.

Every export was read in place (`audit/inventory_dvs.py` → `results/bezrukov_inventory.jsonl`;
all 174 parsed, none failed). Each is the raw instrument log, not a figure: time, sample mass,
target and measured RH, target and measured temperature, saved every 1.2 to 2 s, with the
method name, sample name and initial mass in the header.

What is there, by sorbent (27 and 60 °C; "steps" are RH step runs, typically three repeats of
0→30→0 % and three of 0→60→0 %, plus at 60 °C the 5.4 and 10.7 % levels that stand in for the
desorption side of a temperature swing; "cycling" is the 0↔30 % partial-loading cycling at 27 °C
used to validate the productivity maps):

| Sorbent | Isotherms (set temperature) | Step runs 27 °C | Step runs 60 °C | Cycling 27 °C |
|---|---|---|---|---|
| ROS-037 | 25 °C, 60 °C | 4 files, 5 to 14 mg, 41 h | 4 files, 5 to 16 mg, 46 h | 5 files, 19 mg, 34 h |
| ROS-039 | 27 °C, 60 °C | 4 files, 4 to 19 mg, 97 h | 2 files, 8 to 12 mg, 30 h | 10 files, 15 mg, 52 h |
| ROS-040 | 27 °C, 60 °C | 4 files, 5 to 16 mg, 53 h | 3 files, 5 to 16 mg, 45 h | 7 files, 18 mg, 33 h |
| MOF-303 | 27 °C, 60 °C, 60 °C | 2 files, 11 to 18 mg, 65 h | 3 files, 5 to 8 mg, 51 h | 9 files, 12 to 20 mg, 79 h |
| MIL-160 | 27 °C, 60 °C | 4 files, 4 to 14 mg, 110 h | 3 files, 8 to 14 mg, 60 h | 10 files, 11 to 15 mg, 72 h |
| CAU-10 | 27 °C, 60 °C | 4 files, 4 to 20 mg, 82 h | 3 files, 16 to 23 mg, 66 h | none |
| Al-fumarate | 27 °C, 60 °C | 3 files, 4 to 12 mg, 65 h | 2 files, 5 to 7 mg, 35 h | none |
| Syloid | 25 °C, 60 °C | 4 files, 5 to 19 mg, 69 h | 4 files, 5 to 17 mg, 63 h | 6 files, 21 mg, 26 h |
| ROS-037_composite | 27 °C, 27 °C, 60 °C | 4 files, 4 to 10 mg, 9 h | 6 files, 4 to 9 mg, 68 h | 4 files, 11 mg, 13 h |
| ROS-039_composite | 27 °C, 27 °C, 60 °C | 5 files, 4 to 8 mg, 31 h | 6 files, 3 to 9 mg, 68 h | 4 files, 9 mg, 14 h |

(Generated by `audit/table_bezrukov.py` from the inventory; hours are total logged time.)

Also present: particle-size fractions (CAU-10-H, MIL-160, MOF-303, Syloid), packing and pan
variations (ROS-037), carrier-gas flow variation labelled 100, 200 and 400 in the file names (ROS-037, two masses),
two 100-cycle runs (the ROS-037 and ROS-039 composites, 0↔60 %, 5 min each way, 27 °C, about 28 h
each) and one cellulose isotherm.

Time constants and repeatability (`audit/step_response.py` → `results/bezrukov_steps.jsonl`,
3,588 steps). For each step the time to 63 % of the mass change (t63) and the number of samples
inside it:

- Counting a step only if its mass change has the sign of the RH change and is at least
  0.05 mg (56 of 3,588 steps fail this and are noise-sized), and summarising the step runs
  (`audit/summarise_steps.py`): uptake t63 medians are 6 to 32 minutes at 27 °C for the eight
  sorbents (3 to 4 for the composites) and 3 to 14 minutes at 60 °C (1.7 for the composites);
  release at 27 °C is slower, with medians of 19 to 78 minutes (MOF-303 the slowest). In the
  5-minute cycling files, t63 is cut short by the plateau and is 3 to 10 minutes.
- The fewest samples inside any t63 are 33 (a composite at 60 °C), and 56 or more for every
  step run at 27 °C. C3 asks for 10: met everywhere, with a wide margin.
- In the step runs, repeated cycles of the same step in the same file change mass by amounts
  that agree to 0.01 to 0.16 % (median coefficient of variation over repeats 2 and 3). The
  equilibrium end-points are therefore extremely reproducible. In the 5-minute cycling files the
  spread is 1 to 9 %, because the early cycles drift towards the periodic steady state; that is
  dynamics, not noise. A noise floor for whole trajectories (not just end-points) still has to be
  computed before a model error can be judged; the data allow it.
- Measured RH is logged next to the set-point. It reaches the new set-point within tens of
  seconds, small against most t63 values but not against the fastest 60 °C steps, so any model
  has to be driven by the measured RH, not the set-point.

Judgement against section 1:

- C1 met: 8 sorbents (7 MOFs, 1 silica) under one protocol, 10 counting the two composites.
- C2 met: measured RH and sample temperature are logged on the same clock as the mass.
- C3 met (above). C4 met: three repeats per step and condition, several sample masses, and many
  cycling files per sorbent.
- C5 met: isotherms at both temperatures, measured in the same laboratory on the same batches.
- C6 met for everything in the archive. The paper's temperature-swing productivities are
  computed, not measured, and nothing in the archive swings temperature within a run.
- C7 met: CC-BY-4.0.
- C8: sorbent level only, 4 to 20 mg of powder on a balance pan.

### 2.4 Song 2023, the numbers after all: Ferrer Pareja et al., Zenodo 23222539 (2026-10-07)

Found by the dataset search and read through the Zenodo API on 2026-10-13. A group at the
Universidad de Las Palmas de Gran Canaria (Ferrer Pareja, Sánchez Morales, León Zerpa, Ramos
Martín) exported the 16 worksheets of Song's Origin project and deposited cleaned CSVs (data
redistributed under the original CC-BY; their code MIT). Downloaded (`data.zip`, 520 KB) and
read. What Song's release actually contains, per their files and their own numeric cross-checks
against Table 1 of the article:

- Three Death Valley cycles (about 1,400 minutes each, roughly 15 s sampling): ambient, MOF top,
  MOF bottom, case and condenser temperatures; ambient, case and condenser RH; solar irradiance
  (complete for two cycles only).
- Six per-test yields (laboratory n = 3, two Berkeley days, three Death Valley days), 114 to
  286 g per kg MOF per day. These are condenser-collected water, not weighings of the sorbent;
  the depositors say so themselves.
- The MOF-303 isotherm at 25 °C (powder and pellet), authors' data. A laboratory test with
  measured temperatures, and the authors' simulation of it, labelled as simulation.

So the "H2O uptake (g/g)" axis in the Origin file is the isotherm, not a time series. Song's
release gives forcing at good resolution and six integrated yields; it never observes the
sorbent's water content during a cycle.

### 2.5 Gao, Bezrukov, …, Zaworotko 2026, Nat. Commun. 17, 9494 (two more MOFs, same laboratory)

doi:10.1038/s41467-026-76301-0, published 7 August 2026. Full text read through Europe PMC
(PMC13542148) on 2026-10-13; Source Data files 1 to 5 downloaded from Springer (0.53, 19.9, 18.2
MB and two small files); SI PDF (59 pages) searched.

- Materials: bnn-1-Co and bnn-1-Ni.
- Measured: isotherms at 27 and 60 °C in 2 % RH steps (Fig. 3a, b); uptake against time at 27 and
  60 °C for 30 and 60 % RH adsorption and 0 % desorption, about 9 mg samples, 2 s steps (Fig. 3c,
  d); 128 cycles at 27 °C, 60 % to 0 % RH, about 875,000 rows each with cycle fraction, uptake and
  RH (Fig. 3g, h; DVS Intrinsic).
- Projected, not measured: the productivity heat maps (Fig. 3e, f) and the headline 4.4 to 4.5 kg
  per kg per day, which the paper calls "projected ... under simulated temperature swing".
- Protocol: the SI describes the same programme as Bezrukov 2023 (three 0 to 30 % swings, three
  0 to 60 % swings at 27 °C; at 60 °C also 5.4 and 10.7 % RH desorption levels) on an SMS
  Adventure DVS, and the heat maps use "methodology adapted from Bezrukov et al.". The carrier
  gas flow rate, which sets Bezrukov's rate constant, is not stated anywhere I could find.
- Gaps: the Fig. 3c/d sheets give time and uptake only; RH is the stated set-point, not a logged
  value. The full six- and twelve-cycle runs shown in SI Figs. 32 to 35 are not in the Source Data.
- Licence: CC BY-NC-ND 4.0 (article licence element in the XML; Crossref agrees). Using the data
  for analysis and publishing results is allowed; redistributing an adapted version of the data
  is not. Any benchmark package would have to point to the original files rather than ship
  cleaned copies.

Judgement: two more MOFs measured in the same laboratory under the same programme, with
isotherms at both temperatures. Poolable with Bezrukov in principle; the flow rate is the one
protocol variable to confirm (from the authors, or from the instrument header if a raw export
is ever obtained). Its kinetics would serve best as held-out test materials.

## 3. Newer datasets, 2024 to 2026

Search run 2026-10-12/13 over Zenodo, Figshare, Dryad, Mendeley Data, OSF, Materials Cloud,
GitHub, Europe PMC and the data statements of 2024 to 2026 MOF water-harvesting articles, with
group-by-group checks (Yaghi, E. Wang, R. Wang, Prasher, Zaworotko, Cordova, Yu, P. Wang, Kaskel,
Dincă). Items marked "verified" were opened by me; the others rest on the search agent's
report and are labelled as such.

- **Gao et al. 2026** (above, verified). The only new multi-MOF dataset, and it extends Bezrukov.
- **Kang et al. 2024, Nat. Commun. 15, 9793**, doi:10.1038/s41467-024-53853-7 (verified: Source Data
  15.2 MB downloaded, all 51 sheets listed). HKUST-1 and HKUST-1 loaded with fluorophenyl
  oligomers (F0, F1, F3 at several loadings); Mg-MOF-74 in isotherms only. Mass against time at 10
  to 30 % RH, multi-day cycling with RH logged, outdoor device logs (ambient and adsorbent
  temperature, RH, sun) and per-cycle water collected. Several kinetic panels carry a
  "Simulated" column next to the measured ones. Licence CC BY-NC-ND 4.0 (Crossref), not CC BY
  as the search agent first reported. One parent framework with additives is not material
  diversity in the sense of C1; useful at most as an out-of-distribution check, and a
  different laboratory and protocol.
- **Zhang et al. 2024, Nat. Commun. 15** (agent report): Zn-TCPP nanosheets in a hydrogel
  membrane, coarse uptake against time (15 to 130 points per series). Not a MOF bed.
- **MOF-303 battery-heat-sharing harvester, Nat. Commun. 2026** (agent report): measured
  temperatures, simulated mass transfer, CC BY-NC-ND. No uptake or RH series.
- **Lassitter et al. 2024, Chem. Eng. Sci. 285, 119430** (seen inside the Ferrer Pareja
  deposit): MOF-303 linear-driving-force coefficients against RH at 25 and 40 °C, as SI tables.
  One material, coefficients rather than time series.
- **Alawadhi, Rampal, Ahn, Yaghi, ChemRxiv 2026** (doi:10.26434/chemrxiv.15006110/v2): an
  autonomous passive harvester with a furan-based Al-MOF in Arabian desert conditions, field
  logs described in the abstract. Data statement not readable (Cloudflare). The most promising
  device lead; one material.
- Checked and excluded (agent report, spot-checked): Oppenheim & Dincă 2025 (isotherms only),
  Shao et al. 2026 SJTU device (data on request), several hydrogel, salt and zeolite devices
  (no MOF), simulation deposits on Zenodo and Figshare, and literature-isotherm repositories.
- No newer version of Zenodo 6631711 or 7990951 exists (checked 2026-10-12).

Conclusion of the search: no 2024 to 2026 release measures device cycles for more than one MOF.
Multi-material, time-resolved, measured data exist only at the sorbent level, and only from the
Zaworotko laboratory (8 sorbents in 2023, 2 MOFs in 2026).

## 4. Novelty, re-checked 2026-10-12 and 13

Read live through Crossref, OpenAlex, Semantic Scholar, the arXiv API, Crossref's preprint
index, OSTI and repository PDFs. ScienceDirect refused every request (HTTP 403 to scripts, an
error page in the built-in browser), and Claude in Chrome was not connected tonight, so two
items below rest on abstracts only.

- **Bezrukov et al. 2023** (full text, University of Limerick repository PDF; the quoted
  passages were checked against the extracted text on 2026-10-13). Not machine
  learning. One ODE, dw/dt = k(RH_gas - RH_surface), with the bed-surface RH taken from the
  material's own isotherm and a rate constant k that the authors find to be "independent of
  the specific material" and proportional to bed cross-section over sample mass; k is
  determined separately at 27 and 60 °C. A new sorbent therefore needs only its isotherm. This is already a
  transferable, isotherm-driven cycle model, and it is the baseline any learned model must
  beat on a held-out material. What in it is measured and what is computed:
  humidity-swing cycling at 27 °C between 0 and 30 % RH was measured and matched for six
  sorbents; the productivity heat maps are computed; the temperature-swing (27 to 60 °C)
  results are computed from separate isothermal runs, because the instrument cannot swing
  temperature quickly ("not possible due to the relatively large thermal inertia"); and the
  headline 7.3 L/kg/day for the cellulose composites is, in the paper's own words, a
  "projection of optimal performance", not a measurement.
- **Kim, Rubiera Landa, Ravutla, Realff, Boukouvala 2022** (full text, OSTI accepted
  manuscript). CO2 vacuum swing adsorption, not water. Simulated data from a full PDE model for
  75 adsorbents; neural networks map two isotherm principal components plus process settings to
  steady-state performance (test R² 0.93 to 0.98) on a random 80/20 split of adsorbents. It
  establishes that isotherm features let a static performance map carry to unseen adsorbents;
  it is not dynamic, not water, not measured.
- **Han & Chakraborty 2025** (abstract and highlights only). A review of machine learning for
  adsorption heat transformation, including water harvesting: screening and regression with
  random forests, XGBoost and neural networks. No dynamic, cross-material model is described.
  To be re-read in full through Chrome before any novelty sentence is written.
- **Hong, Park, Chung, Heo, Kim 2026, Appl. Therm. Eng.**
  (doi:10.1016/j.applthermaleng.2026.132018; abstract only). A physics-based digital twin of one
  MOF-coated desiccant dehumidifier, for fault detection. One system, one material, no learning
  across materials. It takes the phrase "digital twin of a MOF desiccant system". To be re-read
  in full through Chrome.
- **Amin (Higher Colleges of Technology, UAE)**: the funded "AI-enabled digital twin" of a
  solar MOF harvester (Dubai RDI grant page, read 2026-10-12) has, so far, published an
  experimental MIL-100(Fe) prototype (Alhamadi et al., Results in Engineering 2026,
  doi:10.1016/j.rineng.2026.111854) and a book chapter; no AI or twin model yet. This group is
  the most likely competitor for the phrase.
- **Other learned models found**: tabular regression of water output over time for one
  desiccant harvester (Ghiasvand & Soltani, Water Resour. Manage. 2025/26); an MLP that carries
  sorption-reactor dynamics to unseen fin geometries on CFD data (Energies 2026, 19, 1619);
  static uptake regressors for MOF screening (AquaMOF, 2025 preprint). None is a dynamic model
  tested on held-out materials.
- **Searches with nothing found**: neural ODE, physics-informed or surrogate models of water
  sorption dynamics on held-out MOFs (arXiv API, Crossref preprints, web search); the 41 papers
  citing Bezrukov (Semantic Scholar), screened by title.

What is taken: the idea that the isotherm carries a cycle model across materials (Bezrukov),
isotherm features as a transferable descriptor (Kim 2022, static, CO2), and the words "digital
twin" (Hong 2026; Amin's grant). Also active, and close in spirit: the Las Palmas group
(Ferrer Pareja et al., three Zenodo deposits 7 to 10 October 2026 with manuscripts) validates
equilibrium and linear-driving-force models of MOF harvesters against Song's three measured
Death Valley cycles, runs multi-objective design over CoRE MOF, and trains a linear surrogate on
99 measured literature points. Physics models and static regression, not a learned dynamic
model across materials; but they work on exactly this question of measured validation and
must be cited and watched. What still appears open: a learned dynamic model of uptake and
release, trained on measured time series of several MOFs, tested strictly on held-out MOFs,
and compared head to head with Bezrukov's isotherm-only model on the same held-out MOFs. Either
outcome is publishable only if the comparison is fair; "learning adds nothing beyond the
isotherm" is a real possibility and would itself be the result.

## 5. Go/no-go

### 5.1 Verdict: GO at the sorbent level, NO-GO at the device level

Scored against the criteria fixed in section 1 before any data were opened:

| | Bezrukov 2023 (+ Gao 2026) | Almassad 2022 | Song 2023 | Kang 2024 |
|---|---|---|---|---|
| C1 ≥ 5 sorbents, one protocol | yes: 8 (+2) | no: 1 | no: 1 | no: 1 parent framework |
| C2 forcing logged with the response | yes (Gao kinetics: set-points only) | air only, sorbent unobserved | air only, sorbent unobserved | yes |
| C3 ≥ 10 samples per t63 | yes, ≥ 33 | 1 min, adequate | ~15 s, adequate | adequate |
| C4 repeats | yes | yes | 3 field cycles | yes |
| C5 isotherm per material | yes, two temperatures | one isotherm | 25 °C only | yes |
| C6 measured | yes (temperature-swing maps are computed) | yes | yes | some panels simulated |
| C7 licence | CC BY (Gao: CC BY-NC-ND) | CC BY | CC BY | CC BY-NC-ND |
| C8 scale | sorbent, 3 to 23 mg | device, 400 g | device | sorbent and device |

Device level: no published dataset, old or new, records device cycles for more than one MOF,
and neither open device record observes the sorbent's water content. A model that transfers
across materials at the harvester level cannot be trained or tested on real data today. That
version of Paper 4 is not done.

Sorbent level: the Bezrukov archive alone meets C1 to C7, and Gao 2026 adds two MOFs measured in
the same laboratory under the same programme. A dynamic model of water uptake and release,
driven by measured RH and temperature, can be trained on some sorbents and tested on sorbents
it has never seen. The tests use measured time series, with the isotherm as the only
description of the new material.

### 5.2 What the data allow, and what they do not

They allow:

- Leave-one-sorbent-out prediction of whole uptake and release trajectories from the held-out
  sorbent's isotherms alone, for RH steps at 27 and 60 °C and for 5-minute partial-loading
  cycling at 27 °C.
- Transfer across bed loading (3 to 23 mg, which sets layer thickness), and for some sorbents
  across particle size, carrier-gas flow and packing, all of which the archive varies.
- A noise floor at the level of whole trajectories, from the repeated steps, against which any
  error is judged.
- Cycle productivity computed from predicted trajectories and compared with the productivity
  measured in the cycling files (six sorbents and two composites).

They do not allow:

- Any test of temperature-swing dynamics. Nothing in the archive changes temperature within a
  run, and Bezrukov's and Gao's temperature-swing productivities are computed from isothermal
  runs. A model may take temperature as an input across the two isothermal levels. But any claim
  about temperature-swing cycles would be an extrapolation, and must be labelled as one or not
  made.
- Any claim about devices. Song (MOF-303) and Almassad (MOF-801) can serve as external
  illustrations: drive the sorbent model with their logged air conditions, then compare its
  predicted per-cycle yield with the measured one (six numbers for Song, nine for Almassad).
  Those yields are condenser water, so they include heat and vapour transport that the sorbent
  model does not contain. This shows how far a sorbent model is from a device; it does not
  validate one.

### 5.3 How independent the materials are, which limits any transfer claim

The ten sorbents are not ten independent draws.

- ROS-037, ROS-039 and ROS-040 are one family from one group.
- MOF-303, MIL-160, CAU-10-H and Al-fumarate are all aluminium carboxylate rod MOFs.
- The two composites contain ROS-037 and ROS-039.
- bnn-1-Co and bnn-1-Ni are isostructural.
- Syloid is the only non-MOF.

Plain leave-one-sorbent-out therefore overstates transfer. The test has to be reported at two
levels:

- leave one sorbent out, always holding out a composite together with its parent;
- leave one family out, with about five families.

Five held-out families is a small sample, so results are reported per family with their spread,
not as one average.

### 5.4 The baseline, which decides whether there is a paper at all

Bezrukov's model already transfers. It uses dw/dt = k(RH_flow − RH_bed), takes RH_bed from the
material's isotherm, and uses a rate constant k that the authors report as independent of the
material. It is the first comparator, and it must be refitted fairly: in each fold, k is
estimated without the held-out sorbent, because the published k was fitted on all eight.

A learned model is worth reporting only against this baseline on identical folds. In this
experiment, a thin powder layer whose rate is limited by diffusion to the bed surface, the
physics leaves a learned model little room. "Learning adds nothing beyond the isotherm" is a
likely outcome. A learned model could plausibly add something only where the simple model is
weakest:

- two-step isotherms;
- hysteresis;
- the slow release tails at 27 °C (median t63 of 19 to 78 minutes);
- the dependence on mass, particle size and flow.

### 5.5 The minimum honest paper

A falsification paper in the program's own mould:

> Does learning beat the isotherm? A held-out-material test of water-sorption cycle dynamics for
> ten sorbents.

- **Data.** Bezrukov 2023 (CC BY) is the training and test pool; Gao 2026 adds two extra test
  MOFs. Gao's licence (CC BY-NC-ND) allows analysis but not redistribution of adapted data, so
  the released code reads the original files rather than shipping cleaned copies.
- **Pre-registered before anything is fitted:**
  - the folds: by sorbent and by family;
  - the metrics: trajectory error relative to the measured noise floor, error in t63, and error in cycle productivity against the cycling files;
  - the baseline: Bezrukov's model, refitted per fold;
  - the learned models: a neural ODE driven by measured RH and temperature, with the isotherm as an input layer, plus simpler grey-box corrections to the baseline;
  - the falsifier: the learned model must beat the refitted baseline on held-out families by more than the noise floor, or the paper says that it does not.
- **Scope words.** "Sorbent", "thin powder layer", "humidity-swing cycling", "two
  temperatures". Never "harvester", "device" or "digital twin".
- **Device records.** Only as an external, clearly bounded illustration.

This paper fits the program. It reuses Paper 1's held-out-material discipline, its outcome
could fall either way, and either outcome answers something the field does not yet know:
whether the isotherm alone is enough to predict cycle dynamics on new sorbents. The Las Palmas
group (section 4) is closest in spirit, working with physics models on one device, so speed
matters.

If even this sorbent-level comparison is judged too thin for a top venue, the fallback is a
short data and benchmark paper. It would:

- state which measured multi-material water-sorption dynamics exist;
- document that device-level transfer cannot be tested on any published data;
- specify the measurement campaign that would make it testable: device cycles for at least five
  MOFs, with the bed weighed in place.

That paper needs no model.

### 5.6 Before any model is built

1. Ask the Zaworotko group, through the author, for the carrier-gas flow rate and pan type used
   in Gao 2026, and whether the full six- and twelve-cycle runs exist as raw exports. The answer
   decides whether the two bnn MOFs can be pooled or only used as an out-of-protocol test.
2. Read Han & Chakraborty 2025 and Hong et al. 2026 in full through Chrome. Tonight only their
   abstracts were available. Neither looks like the same claim, but no novelty sentence is
   written until both are read.
3. Compute the trajectory-level noise floor from the repeated steps. It sets the smallest
   difference in error the paper can claim.
4. Freeze the pre-registration in this repository before anything is fitted.
5. Optional: if its data are open, use the Alawadhi et al. 2026 ChemRxiv field record (one
   Al-MOF) as a further external device illustration.

All computation in this audit was single-threaded file parsing under 200 MB of memory, and
nothing competed with Paper 2's grid.
