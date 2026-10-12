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

(filled in below as each source is read)
