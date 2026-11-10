# Introduction (draft, 2026-11-10; before the freeze, no confirmatory result)

Citation keys are those of docs/literature/T-P4-6_references.bib. Status C references (metadata
only) are cited only for their standard use and must be read before the text is final; they are
marked [C]. RESULT placeholders are filled after the confirmatory runs. No subheadings (house style).

Sorbents that take up and release water within minutes can be cycled many times a day, so their
rate, and not only their capacity, sets how much water a harvester or heat pump delivers. MOF-303
completes an adsorption–desorption cycle within minutes under a mild temperature swing, which is
what allows many harvesting cycles per day [Hanikel2019Rapid], and analyses of adsorption-based
harvesting place heat and mass transport next to the isotherm among the properties that set
device output [LaPotin2019Adsorption]. Yet sorbents are usually compared, and increasingly
screened by machine learning, on equilibrium properties: the humidity of the condensation step,
the capacity and the cycling stability [Furukawa2014Water; Harriman2025Optimizing;
Alkhatib2026Machine; Zheng2023Shaping]. Whether the rate of a new sorbent can be predicted from
the same equilibrium data is the question that decides whether such screening can rank sorbents
by what a cycle delivers.

The working models of sorption dynamics answer it with an assumption. They take the driving force
from the isotherm and lump everything else into a rate constant, in the linear-driving-force
tradition [Glueckauf1955Theory C; Sircar2000Why C] that adsorption-cooling and chiller models
have long used [Sakoda1984Fundamental C; Chua2004Transient C]. The approximation has known limits
[Raymond2011Intraparticle], and the measured rate depends on how the sorbent is held, as loose
grains, glued grains or coatings, powder or monolith [Solovyeva2023Water; Li2025Atmospheric], and
on loading within one framework [Hossain2019Kinetics]. Bezrukov et al. measured the water uptake
dynamics of seven MOFs and a silica gel by dynamic vapour sorption on milligram powder layers and
described them with one such model, in which the rate is proportional to the difference between
the humidity of the gas and the humidity in equilibrium with the current uptake, read from the
isotherm, with one rate constant for all materials [Bezrukov2023Regeneration]. If that holds, an
unseen sorbent's dynamics follow from its isotherm alone. The assumption was fitted to all
sorbents together; it has not been tested on a sorbent left out of the fit. Comparative studies
of the same frameworks measure dynamics material by material [Velte2023Adsorption;
AbuElMaaty2024Kinetics], and a recent study relates water-adsorption kinetics to MOF structure
properties [Xia2025Relationship C, READ BEFORE THE NOVELTY SENTENCE], but none asks whether an
isotherm-based model predicts a sorbent it has not seen.

Learning offers an alternative. Hybrid models that place a neural network inside a mechanistic
equation [Psichogios1992Hybrid; Thompson1994Modeling], now often written as universal
differential equations [Rackauckas2020Universal], have been applied to adsorption dynamics
[Nogueira2022Using; Subraveti2022Physics], and are expected to extrapolate better than black
boxes because the mechanistic part holds where data are lacking [Thompson1994Modeling]. Two
cautions apply to any claim that such a model transfers to new materials. Random splits
overestimate performance on materials unlike those in training, so a test must hold out whole
materials or families [Meredig2018Can; Roberts2017Cross], and leakage between training and test
data inflates results across machine-learning-based science [Kapoor2023Leakage]. And a flexible
model can appear to win for reasons that have nothing to do with the effect it is meant to
capture; testing a procedure on data simulated from a known truth, before it meets real data, is
how such failures are found [Cook2006Validation; Talts2018Validating]. With eight to ten
materials, the uncertainty of any hold-out score is large [Varoquaux2018Cross], which makes it
all the more important that the analysis is fixed before the data are seen
[Nosek2018Preregistration].

Here we test the isotherm-driven model on sorbents it has not seen, under a pre-registered
protocol. We first asked whether a learned grey-box correction, given only a held-out sorbent's
isotherms, predicts its uptake better than the published model. A learned model could enter that
test only after recovering a known correction in synthetic data generated on the real humidity
records and isotherms; the grey-box model did so on two of three held-out sorbents but not the
third in its last allowed round, so under a stopping rule fixed in advance it was not tested on
real data. We then test, with its own synthetic harness, whether the isotherm of a held-out
sorbent predicts its rate constant better than one value shared by the training sorbents, and we
measure how much of the published model's error a correct per-sorbent rate constant or a correct
end point would remove. RESULT: one sentence per outcome (H4a′ verdict and its wording from the
K2 worlds; H4b share; end-point split; family hold-out). We report the learned model's harness
record in full: leaving failed attempts out of the record biases what later models learn from
it [StriethKalthoff2022Machine].
