# ai-harvester-cycles

Code, pre-registration, harness records and every results file of the paper

**No detectable gain from predicting water-uptake rate constants from half-loading humidity: a pre-registered test**
(Abdulhamid Batayhi, Yildiz Technical University; manuscript in `paper/tex/`).

The paper tests, on the open dynamic vapor sorption archive of Bezrukov et al. (Zenodo
[10.5281/zenodo.6631711](https://doi.org/10.5281/zenodo.6631711), CC BY 4.0; seven MOFs and a silica gel), whether an
unseen sorbent's isotherm predicts the rate constant of the isotherm-driven uptake model better than one value shared
by the other sorbents. The protocol was frozen before any confirmatory fit (git tag `prereg-p4-freeze`, commit
84d8e8c; hashes in `FREEZE_MANIFEST.json`; the history was filtered once before publication, see below). Result:
falsified under both dry-mass rules (`results/final_verdict.json`).

Archived at Zenodo: version 1.0.2, [10.5281/zenodo.24260908](https://doi.org/10.5281/zenodo.24260908) (all versions:
[10.5281/zenodo.24148228](https://doi.org/10.5281/zenodo.24148228)). To cite the code and results, see `CITATION.cff`.

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

Python 3.12; exact package versions in `requirements-lock.txt` (`pip install -r requirements-lock.txt --extra-index-url https://download.pytorch.org/whl/cpu`; the CPU build of
torch is pinned as `+cpu`, which only the PyTorch index provides).

1. Data. Download `data.zip` from Zenodo 6631711 into `data_raw/bezrukov2023/` and check its md5 against
   `DATA_SOURCES.md`. Convert once: `python -I audit/extract_dvs.py data_raw/bezrukov2023/data.zip data_derived/bezrukov2023`.
   Raw and derived data are not redistributed here.
2. Tests: `python -E -s -m pytest -q`.
3. B2 harness (synthetic; about 15 h on a laptop in four parallel parts): `python -I audit/harness_b2.py
   data_derived/bezrukov2023 results/harness_b2/part1 "N,K,K2a,K2b"` (part2 "S0,K2c,S1,S2", part3 "S3,S4,C3",
   part4 "S5"), then `python -I audit/harness_b2.py --evaluate results/harness_b2/harness_b2.json
   results/harness_b2/part1/harness_b2.json ... results/harness_b2/part4/harness_b2.json` and
   `python -I audit/b2_harness_report.py results/harness_b2/harness_b2.json results/harness_b2/report.json`.
4. Confirmatory runs (about 4.5 h per dry-mass rule), exactly as in PREREG section 11:

       python -E -s -m p4.run_study data_derived/bezrukov2023 results/confirm_R2 --kinds none
       python -E -s -m p4.run_study data_derived/bezrukov2023 results/confirm_R1 --kinds none --rule R1
       python -E -s -m p4.decide results/confirm_R2/rows.jsonl results/prefreeze/checks2.json results/confirm_R2/decide.json
       python -E -s -m p4.decide results/confirm_R1/rows.jsonl results/prefreeze/checks2.json results/confirm_R1/decide.json
       python -E -s -m p4.final_verdict results/confirm_R2/decide.json results/confirm_R1/decide.json results/harness_b2/harness_b2.json results/final_verdict.json B2

   `run_study` appends one row per fold to `rows.jsonl` and skips folds already there, so an interrupted run resumes.
5. Secondary and exploratory analyses, then the summary: `audit/secondary_metrics.py` (R2, R1),
   `audit/exploratory_joint_oracle.py` (R2, R1), `audit/exploratory_rh50_vs_k.py`, and, from the last internal review,
   `audit/exploratory_oracle_r.py` (the oracle's r by the decision rule), `audit/exploratory_rh50_vs_k_R1.py` (the
   rank correlation under R1, with RH50 recomputed under R1) and `audit/exploratory_k_spread.py`; then
   `audit/summarise_confirm.py` last, because it collects their outputs (usage line at the top of each).
Pre-freeze inputs (run before the freeze; their outputs were committed before the freeze and are unchanged since,
   see tag `prereg-p4-freeze`; `checks2.json` and `rh50.json` are also hashed in `FREEZE_MANIFEST.json`):
   `audit/prefreeze_checks.py` and `audit/prefreeze_checks2.py` (noise floors, clusters, drift; `checks2.json` holds the
   floors F the decision rule uses), `audit/reproduce_b0.py` (in-sample reproduction of B0, R2 and R1),
   `audit/h4b_insample.py` and `audit/extrapolation_flags.py`; `audit/rh50_table.py` recomputes every value of
   `results/rh50.json` and checks it against the frozen file; usage line at the top of each.
6. Figures: the usage line at the top of each `figures/fig_*.py`; each data-figure script (all but the schematic
   `fig_workflow.py`) also writes the plotted numbers to `figures/out/<figure>.data.csv`, and
   `python -I paper/tex/package_aiche.py` packs them as `figure_data.zip` for the Supporting Information. Figures 2 and 3
   also read `data_derived/` (not redistributed; its combined hash is in `FREEZE_MANIFEST.json`), which their provenance
   files do not list. Manuscript: `python -I paper/tex/make_tables.py`, then `python -I paper/tex/build_ms.py` (needs the
   `tectonic` TeX engine; set `TECTONIC` to its executable). The gates check every number written in digits against
   its source (a results file or the frozen protocol), that every reference and figure is current, and more; see the
   script's docstring.

## Notes for data reviewers

- In `decide.json`, the field `p_signflip` holds the exact one-sided Wilcoxon signed-rank p (computed by counting
  subset sums over all sign vectors; `p4/decide.py`, `signflip_p`); the name is historical.
- `r_fold` is the relative improvement of the PREREG section 7 rule (median cluster gain over the comparator's median
  cluster error, the smaller value over the materials of a fold); table medians in the manuscript are over segments.
- Learned-model code (`p4/train.py`) is kept because its harness record is reported; no learned model was fitted to
  the real data (H4a not tested).

## History of this repository

The project was kept in a local git repository from the first data audit (October 2026) to submission. Before it was
made public (2026-11-12), three private documents (an unsent letter and two documents meant for the journal only)
were removed from the whole history; nothing else changed. This changed the hash of every commit after the first three: `COMMIT_MAP.tsv` maps old
to new, and the commit hashes quoted inside `PREREG_P4_draft.md` are the old ones. The frozen protocol is
byte-identical before and after (its SHA-256 is in `FREEZE_MANIFEST.json`). The freeze is recorded only in this
history; it was not deposited with a third-party registry before the confirmatory runs.

To check the hashes in `FREEZE_MANIFEST.json`, hash text files with line endings converted to LF: the manifest
hashes are LF-normalized, and the Zenodo archive (built on Windows) stores most text files with CRLF line endings,
so hashing them as downloaded gives a false mismatch. `python -I audit/verify_freeze.py` does this check, reads the
manifest's p4 keys (written with Windows separators) as `p4/<name>`, and recomputes the combined hash of
`data_derived/` (recipe in its docstring). Every listed file matches the tagged commit except `p4/figstyle.py`, the
figure style, which was changed after the freeze (figure appearance and the export of figure data only; disclosed in
the manuscript, Section 2.10).

## License

Code: MIT (`LICENSE`). The Bezrukov et al. data are CC BY 4.0 and stay at their source.
