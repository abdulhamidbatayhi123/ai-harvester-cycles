# ai-harvester-cycles

Code, pre-registration, harness records and every results file of the paper

**No detectable gain from predicting water-uptake rate constants from half-loading humidity: a pre-registered test**
(Abdulhamid Batayhi, Yildiz Technical University; manuscript in `paper/tex/`).

The paper tests, on the open dynamic-vapour-sorption archive of Bezrukov et al. (Zenodo
[10.5281/zenodo.6631711](https://doi.org/10.5281/zenodo.6631711), CC BY 4.0; seven MOFs and a silica gel), whether an
unseen sorbent's isotherm predicts the rate constant of the isotherm-driven uptake model better than one value shared
by the other sorbents. The protocol was frozen before any confirmatory fit (git tag `prereg-p4-freeze`, commit
bf0b2cf; hashes in `FREEZE_MANIFEST.json`). Result: falsified under both dry-mass rules (`results/final_verdict.json`).

## Where things are

| Path | Content |
|---|---|
| `PREREG_P4_draft.md` | the pre-registration, frozen at tag `prereg-p4-freeze`; section 13 lists every change before the freeze with its cause |
| `AUDIT.md`, `DATA_SOURCES.md` | the data audit that preceded the study, and every downloaded file with its checksum |
| `p4/` | the analysis package: data loading and dry-mass rules (`dataset.py`, `segments.py`), the physics models (`physics.py`), the learned models (`train.py`), the confirmatory runner (`run_study.py`), the decision rule (`decide.py`) and the final verdict (`final_verdict.py`), the figure style (`figstyle.py`) |
| `tests/` | unit tests of the decision rule, the verdict table and the data handling (`python -E -s -m pytest -q`) |
| `audit/` | harnesses (`synthetic_harness.py` for the learned models, `harness_b2.py` for H4a'), pre-freeze checks, the independent re-implementation of the decision rule, the summaries used by the manuscript, and the exploratory analyses (file names start with `exploratory_`) |
| `results/` | every output: harness rounds (`harness_round*/`, `harness_alfu/`, `harness_b2/`), pre-freeze checks (`prefreeze/`), the confirmatory runs (`confirm_R2/`, `confirm_R1/`, with logs), `final_verdict.json`, `confirm_summary.json`, secondary metrics and `exploratory/` |
| `figures/` | one script per figure; outputs in `figures/out/` with a provenance file each (script, style and input hashes; uncommitted inputs refused) |
| `paper/tex/` | `main.tex`, `si.tex`, the number bindings (`bindings.json`), generated tables (`make_tables.py`), generated references (`make_refs_master.py`) and the build with its gates (`build_ms.py`) |
| `docs/` | literature base with live verification records, journal notes, submission metadata |

## Reproduce

Python 3.12; exact package versions in `requirements-lock.txt` (`pip install -r requirements-lock.txt`; CPU only).

1. Data. Download `data.zip` from Zenodo 6631711 into `data_raw/bezrukov2023/` and check its md5 against
   `DATA_SOURCES.md`. Convert once: `python -I audit/extract_dvs.py data_raw/bezrukov2023/data.zip data_derived/bezrukov2023`.
   Raw and derived data are not redistributed here.
2. Tests: `python -E -s -m pytest -q`.
3. B2 harness (synthetic; about 15 h on a laptop in four parallel parts): `python -I audit/harness_b2.py
   data_derived/bezrukov2023 <out_dir> "<worlds>"`, then `--evaluate` and `audit/b2_harness_report.py`
   (commands in `PREREG_P4_draft.md` section 10b and `audit/run_harness_b2.bat`).
4. Confirmatory runs (about 4.5 h per dry-mass rule), exactly as in PREREG section 11:

       python -E -s -m p4.run_study data_derived/bezrukov2023 results/confirm_R2 --kinds none
       python -E -s -m p4.run_study data_derived/bezrukov2023 results/confirm_R1 --kinds none --rule R1
       python -E -s -m p4.decide results/confirm_R2/rows.jsonl results/prefreeze/checks2.json results/confirm_R2/decide.json
       python -E -s -m p4.decide results/confirm_R1/rows.jsonl results/prefreeze/checks2.json results/confirm_R1/decide.json
       python -E -s -m p4.final_verdict results/confirm_R2/decide.json results/confirm_R1/decide.json results/harness_b2/harness_b2.json results/final_verdict.json B2

   `run_study` appends one row per fold to `rows.jsonl` and skips folds already there, so an interrupted run resumes.
5. Summaries, secondary and exploratory analyses: `audit/summarise_confirm.py`, `audit/secondary_metrics.py`,
   `audit/exploratory_joint_oracle.py`, `audit/exploratory_rh50_vs_k.py` (usage line at the top of each).
6. Figures: the usage line at the top of each `figures/fig_*.py`. Manuscript: `python -I paper/tex/make_tables.py`, then
   `python -I paper/tex/build_ms.py` (needs the `tectonic` TeX engine; the gates check that every number in the text
   equals its source, that every reference and figure is current, and more; see the script's docstring).

## Notes for data reviewers

- In `decide.json`, the field `p_signflip` holds the exact one-sided Wilcoxon signed-rank p (computed by counting
  subset sums over all sign vectors; `p4/decide.py`, `signflip_p`); the name is historical.
- `r_fold` is the relative improvement of the PREREG section 7 rule (median cluster gain over the comparator's median
  cluster error, the smaller value over the materials of a fold); table medians in the manuscript are over segments.
- Learned-model code (`p4/train.py`) is kept because its harness record is reported; no learned model was fitted to
  the real data (H4a not tested).

## Licence

Code: MIT (`LICENSE`). The Bezrukov et al. data are CC BY 4.0 and stay at their source.
