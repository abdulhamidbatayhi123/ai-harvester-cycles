# AIChE Journal compliance table (Paper 4)

Rules read live on 2026-11-11/12 (section 1a of ~/.claude/PAPER_WORKFLOW_LESSONS.md). Re-check every row right before
submission. Sources:
[G] author guidelines, https://aiche.onlinelibrary.wiley.com/hub/journal/15475905/homepage/forauthors.html (read 2026-11-11)
[P] Manuscript Content - Pointers for Authors (PDF linked from [G]; read 2026-11-12)
[U] AIChE Journal SI units (PDF linked from [G]; downloaded 2026-11-12)
[D] Wiley data sharing policy, https://authors.wiley.com/author-resources/Journal-Authors/open-access/data-sharing-citation/data-sharing-policy.html (read 2026-11-12)
[A] Wiley publishing ethics, AI section, https://authors.wiley.com/ethics-guidelines/index.html (read 2026-11-12)
[B] Editorial board, https://aiche.onlinelibrary.wiley.com/hub/journal/15475905/homepage/editorialboard.html (read 2026-11-12)
[E] Editorial "New data sharing requirements for AIChE Journal authors" (Sholl 2023, doi:10.1002/aic.18017): free to read
    but the reader did not render in the automated browser; UNREAD, PDF requested from the author.

| Rule | Source | What the package does | Status |
|---|---|---|---|
| Fits a topical area; Separations excludes "purely modeling exercises ... with no attempt to compare to experimental data or to benchmark" | [P] | Separations: Materials, Devices and Processes; every test is on measured DVS data and benchmarks against the published model | PASS |
| Rigor, novelty, innovation | [G] | rigor: frozen protocol, harnesses, two dry-mass rules; novelty framed as a validated negative answer to a screening question (cover letter) | PASS (risk noted) |
| Title fewer than 120 letters and spaces | [G] | 112 characters | PASS |
| Abstract at most 150 words, states objective and conclusions | [G] | 147 words (build gate fails above 147) | PASS |
| Topical heading and five key words | [G] | after the abstract | PASS |
| 12 pt, double spaced, 1 inch margins; below 35 pages with figures inline | [G] | main.tex layout; 24 pages (build gate measures the PDF) | PASS |
| SI units for dimensional quantities | [G],[U] | min, mg and degrees C are accepted for use with SI; wt% and % RH dimensionless | PASS (check [U] list at submission) |
| Notation section only if symbols are not all defined in the text | [G] | every symbol defined where introduced (Methods, Eq. 1-2) | PASS |
| Plain Language Summary, at most 250 characters | [G] | 204 characters, docs/submission/aiche_metadata.md | PASS |
| Graphical abstract fitting 50 mm x 60 mm, legible | [G] | figures/out/fig_toc.* (50 x 60 mm, fonts >= 6 pt) | PASS |
| References numbered in citation order, AMA style, all authors | [G] | make_refs_master.py STYLE = "ama"; build checks order of first citation | PASS |
| Appendices in Supplementary Material | [G] | SI Notes 1-4 | PASS |
| Figures TIFF or EPS; color free | [G] | figures are vector PDF + 600 dpi PNG | FIX at packaging: export TIFF/EPS |
| LaTeX: no directory structure for external files; PDF of the manuscript for review | [G] | main.tex uses ../../figures/out/ paths | FIX at packaging: flat folder, \includegraphics without paths |
| Cover letter: short statement, readership, originality | [G] | docs/submission/ (private/cover_letter_aichej.md, kept out of git) | PASS |
| 4-6 suggested reviewers, >= 2 with AIChE J papers in 10 years, justified, no colleagues | [G],[B] | private/suggested_reviewers.md: 3 with AIChE J papers, none on the board | PASS |
| CRediT roles for authors | [G] | Author Contributions section | PASS |
| Data Availability Statement with link and persistent identifier; scripts archived | [D] | GitHub + Zenodo 10.5281/zenodo.24148229 (reserved) | PASS |
| Shared data cited in the reference list | [D] | own archive cited (Batayhi2026Archive; built from the Zenodo draft metadata, to be re-fetched from DataCite after publication) | PASS |
| AI disclosure: tool, purpose, whether it influenced key arguments or conclusions, how outputs were verified | [A] | author's wording plus model names and a verification sentence (author's choice 2026-11-12), in the Acknowledgments as in recent AIChE J papers | PASS |
| Data-sharing editorial requirements | [E] | not yet read | USER: please save the editorial as PDF |
| American spelling (US journal) | style | converted; British forms in the banned list (build gate G4) | PASS |
| Structure and style of recent AIChE J papers of this type (8 open-access 2023-2026 papers read: 10.1002/aic.18779, 70045, 18600, 18627, 70604, 18573, 70404, 18074) | 1a.3 | numbered sections; Methods before Results; Results, Discussion, Conclusions; no Notation section; back matter Author Contributions, Acknowledgments (AI note), Conflict of Interest, Data Availability, Supporting Information; abstract about 150 words; negative results stated directly | PASS |
| Optional "under review" preprint at submission (Authorea) | [G] | author chose YES (2026-11-12): opt in on the submission form | PASS (at submission) |
