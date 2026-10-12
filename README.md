# ai-harvester-cycles

Paper 4 of the AI-for-MOF/COF water-harvesting program: the data audit that decides whether a
cycle-level model transferring across materials can be built honestly on published data.

Start with `AUDIT.md`: the criteria fixed before any data were opened (section 1), every dataset
checked live (sections 2 and 3), the novelty check (section 4) and the go/no-go verdict
(section 5). `DATA_SOURCES.md` lists every downloaded file with its checksum. Scripts in
`audit/` run on the downloaded files with `python -I`; their outputs are in `results/`.
