# T-P4-6 reference base: Introduction and Discussion (Paper 4)

Built 2026-11-10. Every DOI below was resolved live through the Crossref REST API (`api.crossref.org/works/<DOI>`) or, for arXiv items, the DataCite API; the citation text is generated from those records, not typed by hand. Raw records: `T-P4-6_verification.json`.

**Verification status**

- **A**: metadata verified on Crossref/DataCite and the abstract read on a live source (Crossref record, Semantic Scholar, Europe PMC, DOAJ or DataCite). The "what it shows" sentence paraphrases that abstract.
- **B**: metadata verified; only a short summary was readable (one-sentence graphical abstract, Semantic Scholar TLDR, a search-engine copy of the abstract, or the abstract of the preprint version of the same work). The sentence stays within that summary.
- **C**: metadata verified; no abstract was reachable (publisher pages return 403 to automated tools; Crossref, Semantic Scholar and Europe PMC hold none). The sentence is limited to what the title states plus the paper's standard use. **Read the paper before citing any specific claim from it.**

OpenAlex could not be used (its free daily budget was exhausted, and getting a key needs an e-mail address, which the rules forbid). Claude in Chrome was not connected, so publisher pages could not be opened in a browser.

"Primary" items (the 45 recommended for the paper) come first in each group. "Reserve" items are verified too and can stand in for a primary item.

## G1. Water-sorption kinetics in MOFs and desiccants; rate-limiting steps; the study materials

### Primary

- **[Bezrukov2023Regeneration]** Bezrukov, A. A.; O’Hearn, D. J.; Gascón-Pérez, V.; Darwish, S.; Kumar, A.; Sanda, S.; Kumar, N.; Francis, K.; et al. Metal-organic frameworks as regeneration optimized sorbents for atmospheric water harvesting. *Cell Reports Physical Science* **2023**, 4, 101252. https://doi.org/10.1016/j.xcrp.2023.101252
  - What it shows: Reports DVS uptake kinetics of seven MOFs and the desiccant Syloid under AWH-type swings and concludes they are limited by diffusion to the sorbent bed surface; cellulose composites keep powder kinetics, reported to give up to 7.3 L/kg/day under a 27 C/30 % RH to 60 C/5.4 % RH temperature swing.
  - Supports our sentence about: the data source and the baseline isotherm-driven model with one shared k'' (Methods, Introduction).
  - Status: **B**. Sources: Crossref metadata; abstract via CORE record (core.ac.uk/works/150442324, search snippet; cell.com returned 403); content cross-checked against the project AUDIT.md notes. Metadata URL: https://api.crossref.org/works/10.1016/j.xcrp.2023.101252

- **[Gao2026Molecular]** Gao, M.; Bezrukov, A. A.; Eaby, A. C.; Deng, C.; Liu, L.; Song, B.; Nikkhah, S. J.; Vandichel, M.; et al. Molecular-level insight into water adsorption and projected atmospheric water harvesting performance in a hydrolytically stable MOF. *Nature Communications* **2026**, 17, 9494. https://doi.org/10.1038/s41467-026-76301-0
  - What it shows: Reports bnn-1-Co and bnn-1-Ni rod-building-block MOFs with low-RH uptake thresholds, hydrolytic stability, measured DVS isotherms/kinetics and projected (not measured) AWH productivity.
  - Supports our sentence about: the two additional held-out MOFs from the same laboratory and that their headline productivities are projections.
  - Status: **A**. Sources: Crossref metadata; abstract via Semantic Scholar; full text read earlier via Europe PMC PMC13542148 (AUDIT.md 2.5). Metadata URL: https://api.crossref.org/works/10.1038/s41467-026-76301-0

- **[Hanikel2019Rapid]** Hanikel, N.; Prévot, M. S.; Fathieh, F.; Kapustin, E. A.; Lyu, H.; Wang, H.; Diercks, N. J.; Glover, T. G.; et al. Rapid Cycling and Exceptional Yield in a Metal-Organic Framework Water Harvester. *ACS Central Science* **2019**, 5, 1699-1706. https://doi.org/10.1021/acscentsci.9b00745
  - What it shows: Shows MOF-303 completes an adsorption-desorption cycle within minutes under a mild temperature swing, enabling many water-harvesting cycles per day.
  - Supports our sentence about: cycle rate (kinetics), not only capacity, sets harvester productivity (Introduction motivation).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1021/acscentsci.9b00745

- **[AbuElMaaty2024Kinetics]** Abu EL-Maaty, A. E.; Abdalla, M. A.; Essalhi, M.; Abdelnaby, M. M.; Mahmoud, M. M.; Habib, M. A.; Antar, M.; Ben-Mansour, R. Kinetics of Water Adsorption in Metal-Organic Framework(MOF-303) for Adsorption Cooling Application. *Energy Conversion and Management: X* **2024**, 24, 100694. https://doi.org/10.1016/j.ecmx.2024.100694
  - What it shows: Measures water isotherms and LDF kinetics of MOF-303 under vacuum (adsorption-cooling) conditions; diffusion kinetics about 8x faster than silica gel at 25 C (about 7x at 10-30 % RH).
  - Supports our sentence about: MOF-303 kinetics have been characterised with LDF fits in single-material studies, under conditions different from DVS powder layers.
  - Status: **A**. Sources: Crossref metadata; abstract via DOAJ API. Metadata URL: https://api.crossref.org/works/10.1016/j.ecmx.2024.100694

- **[Cadiau2015Design]** Cadiau, A.; Lee, J. S.; Damasceno Borges, D.; Fabry, P.; Devic, T.; Wharmby, M. T.; Martineau, C.; Foucher, D.; et al. Design of Hydrophilic Metal Organic Framework Water Adsorbents for Heat Reallocation. *Advanced Materials* **2015**, 27, 4775-4780. https://doi.org/10.1002/adma.201502418
  - What it shows: Introduces MIL-160(Al), a hydrothermally stable Al-MOF with a bio-derived furandicarboxylate linker that outperforms SAPO-34 for heat reallocation in some conditions.
  - Supports our sentence about: the origin and application context of MIL-160 (Materials).
  - Status: **A**. Sources: Crossref metadata; abstract via Europe PMC. Metadata URL: https://api.crossref.org/works/10.1002/adma.201502418

- **[Lenzen2018Scalable]** Lenzen, D.; Bendix, P.; Reinsch, H.; Fröhlich, D.; Kummer, H.; Möllers, M.; Hügenell, P. P. C.; Gläser, R.; et al. Scalable Green Synthesis and Full‐Scale Test of the Metal–Organic Framework CAU‐10‐H for Use in Adsorption‐Driven Chillers. *Advanced Materials* **2017**, 30, 1705869. https://doi.org/10.1002/adma.201705869
  - What it shows: Reports scalable green synthesis of CAU-10-H and a full-scale test in an adsorption-driven chiller using water.
  - Supports our sentence about: the origin and application context of CAU-10-H (Materials).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/adma.201705869

- **[Velte2023Adsorption]** Velte, A.; Laurenz, E.; Rustam, L.; P.C. Hügenell, P.; Henninger, M.; Seiler, J.; Füldner, G. Adsorption dynamics and hydrothermal stability of MOFs aluminium fumarate, MIL-160 (Al), and CAU-10-H, and zeotype TiAPSO for heat transformation applications. *Applied Thermal Engineering* **2023**, 227, 120336. https://doi.org/10.1016/j.applthermaleng.2023.120336
  - What it shows: Measures sorption dynamics of coated Al-fumarate, MIL-160(Al), CAU-10-H and TiAPSO before and after about 70,000 hydrothermal cycles and argues stability must be judged on dynamics as well as uptake.
  - Supports our sentence about: multi-sorbent comparisons of water-sorption dynamics exist for three of our MOFs, but as material comparisons, not predictive held-out tests (Introduction/novelty).
  - Status: **B**. Sources: Crossref metadata; abstract of the SSRN preprint of the same work (10.2139/ssrn.4230996, Crossref). Metadata URL: https://api.crossref.org/works/10.1016/j.applthermaleng.2023.120336

- **[Hossain2019Kinetics]** Hossain, M. I.; Glover, T. G. Kinetics of Water Adsorption in UiO-66 MOF. *Industrial & Engineering Chemistry Research* **2019**, 58, 10550-10558. https://doi.org/10.1021/acs.iecr.9b00976
  - What it shows: Uses concentration-swing frequency response to show water uptake in UiO-66 is micropore-diffusion controlled with a loading-dependent rate (minimum near 4 mol/kg).
  - Supports our sentence about: rate constants depend on loading/RH even within one MOF, so a single k'' per material is itself an approximation (Discussion).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1021/acs.iecr.9b00976

- **[Aristov2012Optimization]** Aristov, Y. I.; Glaznev, I. S.; Girnik, I. S. Optimization of adsorption dynamics in adsorptive chillers: Loose grains configuration. *Energy* **2012**, 46, 484-492. https://doi.org/10.1016/j.energy.2012.08.001
  - What it shows: Title-level: studies how to optimise water adsorption dynamics for loose-grain adsorber configurations in adsorptive chillers (Aristov group).
  - Supports our sentence about: adsorbent layer/grain configuration controls observed uptake rates (Discussion on bed-depth effects). Read before citing specifics.
  - Status: **C**. Sources: Crossref metadata only (ScienceDirect 403; no abstract in Crossref/S2/Europe PMC). Metadata URL: https://api.crossref.org/works/10.1016/j.energy.2012.08.001

- **[Solovyeva2023Water]** Solovyeva, M.; Gordeeva, L. Water Adsorption Dynamics on Metal–Organic Framework MOF-801: Comparative Study of Loose and Glued Grains, and Coatings. *Nanomaterials* **2023**, 13, 2442. https://doi.org/10.3390/nano13172442
  - What it shows: Compares water adsorption dynamics of MOF-801 as loose grains, glued grains and thin coatings: heat transfer between support and bed controls the initial rate, mass transfer later; binders can speed up or slow down uptake.
  - Supports our sentence about: measured MOF uptake rates depend on sample configuration, not only on the material (Discussion).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.3390/nano13172442

- **[Li2025Atmospheric]** Li, J.; Wang, G.; Fan, H.; Li, Z.; Tso, C. Y.; Zhou, Y. Atmospheric Water Sorption Kinetics in Powder and Monolithic Metal–Organic Frameworks. *Advanced Materials Interfaces* **2025**, 12, 2400628. https://doi.org/10.1002/admi.202400628
  - What it shows: Compares atmospheric water-sorption kinetics of powder and monolithic MOF-801: the mesoporous monolith takes up more water above 90 % RH but less at 10-90 % RH, which MD simulations attribute to capillary-condensed water films.
  - Supports our sentence about: the same framework behaves differently in different physical forms, so uptake behaviour is not a pure material property (Discussion).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/admi.202400628

### Reserve

- **[Girnik2016Dynamics]** Girnik, I. S.; Aristov, Y. I. Dynamics of water vapour adsorption by a monolayer of loose AQSOA™-FAM-Z02 grains: Indication of inseparably coupled heat and mass transfer. *Energy* **2016**, 114, 767-773. https://doi.org/10.1016/j.energy.2016.08.056
  - What it shows: Title-level: water vapour adsorption dynamics on a monolayer of loose AQSOA-FAM-Z02 grains, indicating inseparably coupled heat and mass transfer.
  - Supports our sentence about: heat and mass transfer can be coupled in thin-layer uptake experiments (Discussion of rate-limiting steps). Read before citing.
  - Status: **C**. Sources: Crossref metadata only (no abstract available to automated tools). Metadata URL: https://api.crossref.org/works/10.1016/j.energy.2016.08.056

- **[Teo2017Experimental]** Teo, H. W. B.; Chakraborty, A.; Kitagawa, Y.; Kayal, S. Experimental study of isotherms and kinetics for adsorption of water on Aluminium Fumarate. *International Journal of Heat and Mass Transfer* **2017**, 114, 621-627. https://doi.org/10.1016/j.ijheatmasstransfer.2017.06.086
  - What it shows: Title-level: experimental isotherms and kinetics of water adsorption on aluminium fumarate.
  - Supports our sentence about: Al-fumarate water kinetics have been measured before (Materials). Read before citing values.
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.ijheatmasstransfer.2017.06.086

- **[Kummer2017Functional]** Kummer, H.; Jeremias, F.; Warlo, A.; Füldner, G.; Fröhlich, D.; Janiak, C.; Gläser, R.; Henninger, S. K. A Functional Full-Scale Heat Exchanger Coated with Aluminum Fumarate Metal–Organic Framework for Adsorption Heat Transformation. *Industrial & Engineering Chemistry Research* **2017**, 56, 8393-8398. https://doi.org/10.1021/acs.iecr.7b00106
  - What it shows: Title-level: a full-scale heat exchanger coated with aluminium fumarate MOF for adsorption heat transformation.
  - Supports our sentence about: Al-fumarate application context (Materials).
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1021/acs.iecr.7b00106

- **[Tannert2019Robust]** Tannert, N.; Jansen, C.; Nießing, S.; Janiak, C. Robust synthesis routes and porosity of the Al-based metal–organic frameworks Al-fumarate, CAU-10-H and MIL-160. *Dalton Transactions* **2019**, 48, 2967-2976. https://doi.org/10.1039/c8dt04688c
  - What it shows: Confirms reproducible synthesis routes and porosity of Al-fumarate, CAU-10-H and MIL-160.
  - Supports our sentence about: the three Al-MOFs are reproducible materials (Materials).
  - Status: **B**. Sources: Crossref (one-sentence graphical abstract). Metadata URL: https://api.crossref.org/works/10.1039/c8dt04688c

- **[Dawoud2003Experimental]** Dawoud, B.; Aristov, Y. Experimental study on the kinetics of water vapor sorption on selective water sorbents, silica gel and alumina under typical operating conditions of sorption heat pumps. *International Journal of Heat and Mass Transfer* **2003**, 46, 273-281. https://doi.org/10.1016/s0017-9310(02)00288-0
  - What it shows: Title-level: experimental kinetics of water vapour sorption on selective water sorbents, silica gel and alumina under typical adsorption heat pump conditions.
  - Supports our sentence about: classic measured water-sorption kinetics on desiccants (Introduction). Read before citing.
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/s0017-9310(02)00288-0

- **[Glaznev2009Kinetics]** Glaznev, I.; Ovoshchnikov, D.; Aristov, Y. Kinetics of water adsorption/desorption under isobaric stages of adsorption heat transformers: The effect of isobar shape. *International Journal of Heat and Mass Transfer* **2009**, 52, 1774-1777. https://doi.org/10.1016/j.ijheatmasstransfer.2008.09.031
  - What it shows: Title-level: kinetics of water adsorption/desorption under isobaric stages of adsorption heat transformers and the effect of isobar shape.
  - Supports our sentence about: the shape of the equilibrium curve affects uptake kinetics (novelty (b), Discussion of RH50). Read before citing.
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.ijheatmasstransfer.2008.09.031

- **[Bozbiyik2016Stepped]** Bozbiyik, B.; Van Assche, T.; Lannoeye, J.; De Vos, D. E.; Baron, G. V.; Denayer, J. F. M. Stepped water isotherm and breakthrough curves on aluminium fumarate metal–organic framework: experimental and modelling study. *Adsorption* **2016**, 23, 185-192. https://doi.org/10.1007/s10450-016-9847-0
  - What it shows: Title-level: stepped water isotherm and breakthrough curves on aluminium fumarate, experiment and modelling.
  - Supports our sentence about: Al-fumarate stepped isotherm and dynamic modelling (Materials).
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1007/s10450-016-9847-0

## G2. Isotherm-driven / LDF models; chiller and AWH models with isotherm + one rate constant

### Primary

- **[Glueckauf1955Theory]** Glueckauf, E. Theory of chromatography. Part 10.—Formulæ for diffusion into spheres and their application to chromatography. *Trans. Faraday Soc.* **1955**, 51, 1540-1551. https://doi.org/10.1039/TF9555101540
  - What it shows: Title-level: formulae for diffusion into spheres and their application to chromatography; the standard origin citation of the linear driving force approximation.
  - Supports our sentence about: the LDF form of our rate law (Introduction/Methods). Check the paper before quoting the 15D/R^2 factor.
  - Status: **C**. Sources: Crossref metadata only (RSC page not read). Metadata URL: https://api.crossref.org/works/10.1039/TF9555101540

- **[Sircar2000Why]** Sircar, S.; Hufton, J. Why Does the Linear Driving Force Model for Adsorption Kinetics Work? *Adsorption* **2000**, 6, 137-147. https://doi.org/10.1023/A:1008965317983
  - What it shows: Title-level: explains why the LDF model for adsorption kinetics works (standard review of LDF validity).
  - Supports our sentence about: LDF models are widely used and often adequate for process design (Introduction).
  - Status: **C**. Sources: Crossref metadata only (Springer redirect to login). Metadata URL: https://api.crossref.org/works/10.1023/A:1008965317983

- **[Sakoda1984Fundamental]** SAKODA, A.; SUZUKI, M. Fundamental study on solar powered adsorption cooling system. *JOURNAL OF CHEMICAL ENGINEERING OF JAPAN* **1984**, 17, 52-57. https://doi.org/10.1252/jcej.17.52
  - What it shows: Title-level: fundamental study of a solar-powered adsorption cooling system; widely cited source of an LDF-type water uptake model for silica gel.
  - Supports our sentence about: adsorption-cooling models have long used isotherm plus one LDF rate constant (Introduction). Read before citing.
  - Status: **C**. Sources: Crossref metadata only (J-STAGE page has no abstract). Metadata URL: https://api.crossref.org/works/10.1252/jcej.17.52

- **[Raymond2011Intraparticle]** Raymond, A.; Garimella, S. Intraparticle Mass Transfer in Adsorption Heat Pumps: Limitations of the Linear Driving Force Approximation. *Journal of Heat Transfer* **2011**, 133, 042001. https://doi.org/10.1115/1.4001310
  - What it shows: Compares LDF and Fickian-diffusion predictions for cylindrical and spherical adsorbents in adsorption heat pumps and evaluates the conditions under which LDF agrees with diffusion.
  - Supports our sentence about: the single-rate-constant LDF form is an approximation with known limits (Discussion).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1115/1.4001310

- **[Chua2004Transient]** Chua, H.; Ng, K.; Wang, W.; Yap, C.; Wang, X. Transient modeling of a two-bed silica gel–water adsorption chiller. *International Journal of Heat and Mass Transfer* **2004**, 47, 659-669. https://doi.org/10.1016/j.ijheatmasstransfer.2003.08.010
  - What it shows: Title-level: transient modelling of a two-bed silica gel-water adsorption chiller (lumped model with isotherm and rate equation).
  - Supports our sentence about: system models of chillers assume isotherm + LDF kinetics (Introduction). Read before citing.
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.ijheatmasstransfer.2003.08.010

- **[LaPotin2019Adsorption]** LaPotin, A.; Kim, H.; Rao, S. R.; Wang, E. N. Adsorption-Based Atmospheric Water Harvesting: Impact of Material and Component Properties on System-Level Performance. *Accounts of Chemical Research* **2019**, 52, 1588-1597. https://doi.org/10.1021/acs.accounts.9b00062
  - What it shows: Reviews adsorption-based AWH and how material and component properties (isotherm, kinetics, heat and mass transport) set system-level performance.
  - Supports our sentence about: kinetics and transport, not only isotherms, govern harvester output (Introduction).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1021/acs.accounts.9b00062

### Reserve

- **[ElSharkawy2011Linear]** El-Sharkawy, I. I. On the linear driving force approximation for adsorption cooling applications. *International Journal of Refrigeration* **2011**, 34, 667-673. https://doi.org/10.1016/j.ijrefrig.2010.12.006
  - What it shows: Title-level: examines the linear driving force approximation for adsorption cooling applications.
  - Supports our sentence about: LDF validity in adsorption cooling (G2). Read before citing.
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.ijrefrig.2010.12.006

- **[Harriman2025Optimizing]** Harriman, C.; Ke, Q.; Vlugt, T. J. H.; Howarth, A. J.; Simon, C. M. Optimizing Mixtures of Metal–Organic Frameworks for Robust and Bespoke Passive Atmospheric Water Harvesting. *ACS Engineering Au* **2025**, 5, 707-725. https://doi.org/10.1021/acsengineeringau.5c00051
  - What it shows: Optimises mixtures of MOFs for passive AWH using isotherm-based water-delivery calculations across capture/release conditions.
  - Supports our sentence about: isotherm-driven (equilibrium) screening is the dominant design approach, leaving kinetics untested (Introduction).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1021/acsengineeringau.5c00051

- **[Wilkins2020Dynamic]** Wilkins, N. S.; Rajendran, A.; Farooq, S. Dynamic column breakthrough experiments for measurement of adsorption equilibrium and kinetics. *Adsorption* **2020**, 27, 397-422. https://doi.org/10.1007/s10450-020-00269-6
  - What it shows: Title-level: review of dynamic column breakthrough experiments for measuring adsorption equilibrium and kinetics.
  - Supports our sentence about: kinetic parameters are usually extracted by fitting dynamic experiments (Methods context).
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1007/s10450-020-00269-6

- **[Lehmann2019Modelling]** Lehmann, C.; Kolditz, O.; Nagel, T. Modelling sorption equilibria and kinetics in numerical simulations of dynamic sorption experiments in packed beds of salt/zeolite composites for thermochemical energy storage. *International Journal of Heat and Mass Transfer* **2019**, 128, 1102-1113. https://doi.org/10.1016/j.ijheatmasstransfer.2018.09.042
  - What it shows: Models sorption equilibria and kinetics in simulations of dynamic sorption experiments in packed beds of salt/zeolite composites.
  - Supports our sentence about: dynamic sorption experiments are routinely modelled with equilibrium + kinetic closures (Introduction).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1016/j.ijheatmasstransfer.2018.09.042

## G3. MOF atmospheric water harvesting and data-driven screening

### Primary

- **[Kim2017Water]** Kim, H.; Yang, S.; Rao, S. R.; Narayanan, S.; Kapustin, E. A.; Furukawa, H.; Umans, A. S.; Yaghi, O. M.; et al. Water harvesting from air with metal-organic frameworks powered by natural sunlight. *Science* **2017**, 356, 430-434. https://doi.org/10.1126/science.aam8743
  - What it shows: Demonstrates MOF-801 water harvesting from air at low RH powered by natural sunlight.
  - Supports our sentence about: the founding MOF AWH demonstration (Introduction).
  - Status: **A**. Sources: Crossref (editor summary in record). Metadata URL: https://api.crossref.org/works/10.1126/science.aam8743

- **[Fathieh2018Practical]** Fathieh, F.; Kalmutzki, M. J.; Kapustin, E. A.; Waller, P. J.; Yang, J.; Yaghi, O. M. Practical water production from desert air. *Science Advances* **2018**, 4, eaat3198. https://doi.org/10.1126/sciadv.aat3198
  - What it shows: Reports a next-generation MOF (MOF-303 class) device and material for water production from desert air.
  - Supports our sentence about: field AWH with Al-MOFs (Introduction).
  - Status: **B**. Sources: Crossref (one-sentence summary). Metadata URL: https://api.crossref.org/works/10.1126/sciadv.aat3198

- **[Hanikel2020MOF]** Hanikel, N.; Prévot, M. S.; Yaghi, O. M. MOF water harvesters. *Nature Nanotechnology* **2020**, 15, 348-355. https://doi.org/10.1038/s41565-020-0673-x
  - What it shows: Reviews MOFs for atmospheric water harvesting and the design of MOF water harvesters.
  - Supports our sentence about: general AWH background and open problems (Introduction).
  - Status: **A**. Sources: Crossref metadata; abstract via Europe PMC. Metadata URL: https://api.crossref.org/works/10.1038/s41565-020-0673-x

- **[Hanikel2021Evolution]** Hanikel, N.; Pei, X.; Chheda, S.; Lyu, H.; Jeong, W.; Sauer, J.; Gagliardi, L.; Yaghi, O. M. Evolution of water structures in metal-organic frameworks for improved atmospheric water harvesting. *Science* **2021**, 374, 454-459. https://doi.org/10.1126/science.abj0890
  - What it shows: Locates water molecules in MOF-303 at increasing loadings by single-crystal XRD and uses the filling sequence to design improved variants.
  - Supports our sentence about: isotherm step position is tunable by design, which motivates using isotherm descriptors (RH50) as predictors (Introduction).
  - Status: **A**. Sources: Crossref (editor summary in record). Metadata URL: https://api.crossref.org/works/10.1126/science.abj0890

- **[Furukawa2014Water]** Furukawa, H.; Gándara, F.; Zhang, Y.; Jiang, J.; Queen, W. L.; Hudson, M. R.; Yaghi, O. M. Water Adsorption in Porous Metal–Organic Frameworks and Related Materials. *Journal of the American Chemical Society* **2014**, 136, 4369-4381. https://doi.org/10.1021/ja500330a
  - What it shows: Compares water adsorption in 23 porous materials (20 MOFs) and proposes criteria: condensation pressure, capacity, cyclability/stability.
  - Supports our sentence about: standard criteria are equilibrium-based; kinetics is not among them (Introduction).
  - Status: **A**. Sources: Crossref metadata; abstract via Europe PMC. Metadata URL: https://api.crossref.org/works/10.1021/ja500330a

- **[Zhang2023Metal]** Zhang, Z.; Tang, H.; Wang, M.; Lyu, B.; Jiang, Z.; Jiang, J. Metal–Organic Frameworks for Water Harvesting: Machine Learning-Based Prediction and Rapid Screening. *ACS Sustainable Chemistry & Engineering* **2023**, 11, 8148-8160. https://doi.org/10.1021/acssuschemeng.3c01233
  - What it shows: Title-level: machine-learning-based prediction and rapid screening of MOFs for water harvesting.
  - Supports our sentence about: ML screening for AWH predicts equilibrium properties (Introduction). Read before citing which target was predicted.
  - Status: **C**. Sources: Crossref metadata only (ACS page not read). Metadata URL: https://api.crossref.org/works/10.1021/acssuschemeng.3c01233

- **[Zheng2023Shaping]** Zheng, Z.; Alawadhi, A. H.; Chheda, S.; Neumann, S. E.; Rampal, N.; Liu, S.; Nguyen, H. L.; Lin, Y.; et al. Shaping the Water-Harvesting Behavior of Metal–Organic Frameworks Aided by Fine-Tuned GPT Models. *Journal of the American Chemical Society* **2023**, 145, 28284-28295. https://doi.org/10.1021/jacs.3c12086
  - What it shows: Uses a fine-tuned GPT model to propose MOF-303 linker variants and expands the water-harvesting MOF design space.
  - Supports our sentence about: data-driven design for AWH targets isotherm behaviour (Introduction).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1021/jacs.3c12086

- **[Alkhatib2026Machine]** Alkhatib, N.; Abed Alrhman, S.; Kirmizialtin, S. Machine learning highlights chemistry as the key factor in metal–organic frameworks for atmospheric water harvesting. *Molecular Systems Design & Engineering* **2026**, 11, 50-61. https://doi.org/10.1039/D5ME00101C
  - What it shows: GCMC simulations of diverse MOFs plus ML identify chemical features governing water uptake and AWH performance.
  - Supports our sentence about: ML work on AWH MOFs targets simulated uptake, not measured kinetics (Introduction).
  - Status: **B**. Sources: Crossref (graphical-abstract sentence). Metadata URL: https://api.crossref.org/works/10.1039/D5ME00101C

### Reserve

- **[Kalmutzki2018Metal]** Kalmutzki, M. J.; Diercks, C. S.; Yaghi, O. M. Metal–Organic Frameworks for Water Harvesting from Air. *Advanced Materials* **2018**, 30, 1704304. https://doi.org/10.1002/adma.201704304
  - What it shows: Reviews MOFs for adsorption-based water harvesting from air and the need to tailor working capacity and step position.
  - Supports our sentence about: AWH background (Introduction).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/adma.201704304

- **[Xu2020Metal]** Xu, W.; Yaghi, O. M. Metal–Organic Frameworks for Water Harvesting from Air, Anywhere, Anytime. *ACS Central Science* **2020**, 6, 1348-1354. https://doi.org/10.1021/acscentsci.0c00678
  - What it shows: Outlook arguing MOF water harvesting can be deployed in arid and humid regions.
  - Supports our sentence about: AWH motivation (Introduction).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1021/acscentsci.0c00678

- **[Kim2018Adsorption]** Kim, H.; Rao, S. R.; Kapustin, E. A.; Zhao, L.; Yang, S.; Yaghi, O. M.; Wang, E. N. Adsorption-based atmospheric water harvesting device for arid climates. *Nature Communications* **2018**, 9, 1191. https://doi.org/10.1038/s41467-018-03162-7
  - What it shows: Reports an adsorption-based AWH device for arid climates (MOF-801) tested outdoors.
  - Supports our sentence about: AWH device context (Introduction).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1038/s41467-018-03162-7

- **[Rafat2025Assessment]** Rafat, M.; Chandrasekaran, G.; Shrivastava, S.; Farsad, A.; Ananpattarachai, J.; Qiu, A.; Sinha, S.; Westerhoff, P.; et al. Assessment of Beaded, Powdered and Coated Desiccants for Atmospheric Water Harvesting in Arid Environments. *Environments* **2025**, 12, 110. https://doi.org/10.3390/environments12040110
  - What it shows: Assesses zeolite, activated alumina and silica gel as beads, powders or coatings for AWH in arid regions.
  - Supports our sentence about: sorbent form matters for AWH (Discussion).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.3390/environments12040110

- **[Jablonka2020Big]** Jablonka, K. M.; Ongari, D.; Moosavi, S. M.; Smit, B. Big-Data Science in Porous Materials: Materials Genomics and Machine Learning. *Chemical Reviews* **2020**, 120, 8066-8129. https://doi.org/10.1021/acs.chemrev.0c00004
  - What it shows: Reviews big-data and ML methods for porous materials including MOFs.
  - Supports our sentence about: background on ML for MOFs (Introduction).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1021/acs.chemrev.0c00004

## G4. Hybrid / grey-box / physics-informed ML, UDEs, neural ODEs; transfer to unseen materials

### Primary

- **[Psichogios1992Hybrid]** Psichogios, D. C.; Ungar, L. H. A hybrid neural network‐first principles approach to process modeling. *AIChE Journal* **1992**, 38, 1499-1511. https://doi.org/10.1002/aic.690381003
  - What it shows: Hybrid neural network-first principles model of a fed-batch bioreactor; the network estimates unmeasured parameters inside a mechanistic model and extrapolates better than black-box networks.
  - Supports our sentence about: our grey-box design (neural factor on a mechanistic rate) follows the classic hybrid-modelling idea (Introduction).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/aic.690381003

- **[Thompson1994Modeling]** Thompson, M. L.; Kramer, M. A. Modeling chemical processes using prior knowledge and neural networks. *AIChE Journal* **1994**, 40, 1328-1340. https://doi.org/10.1002/aic.690400806
  - What it shows: Combines prior process knowledge and neural networks; the simple model controls extrapolation where training data are lacking.
  - Supports our sentence about: grey-box models are expected to transfer better than black boxes, which is what our harness tested (Introduction).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/aic.690400806

- **[Rackauckas2020Universal]** Rackauckas, C.; Ma, Y.; Martensen, J.; Warner, C.; Zubov, K.; Supekar, R.; Skinner, D.; Ramadhan, A.; et al. Universal Differential Equations for Scientific Machine Learning. *arXiv* **2020**. https://doi.org/10.48550/arXiv.2001.04385
  - What it shows: Introduces universal differential equations (mechanistic ODEs with embedded neural networks) and the SciML ecosystem.
  - Supports our sentence about: the UDE framing of the learned correction (Introduction/Methods).
  - Status: **A**. Sources: https://api.datacite.org/dois/ (abstract in record). Metadata URL: https://api.datacite.org/dois/10.48550/arXiv.2001.04385

- **[Chen2018Neural]** Chen, R. T. Q.; Rubanova, Y.; Bettencourt, J.; Duvenaud, D. Neural Ordinary Differential Equations. *arXiv* **2018**. https://doi.org/10.48550/arXiv.1806.07366
  - What it shows: Introduces neural ODEs, parameterising a hidden-state derivative with a neural network solved by an ODE solver.
  - Supports our sentence about: neural-ODE background (Introduction).
  - Status: **A**. Sources: https://api.datacite.org/dois/ (abstract in record). Metadata URL: https://api.datacite.org/dois/10.48550/arXiv.1806.07366

- **[Karniadakis2021Physics]** Karniadakis, G. E.; Kevrekidis, I. G.; Lu, L.; Perdikaris, P.; Wang, S.; Yang, L. Physics-informed machine learning. *Nature Reviews Physics* **2021**, 3, 422-440. https://doi.org/10.1038/s42254-021-00314-5
  - What it shows: Reviews physics-informed machine learning, its capabilities and limitations.
  - Supports our sentence about: physics-informed ML background (Introduction).
  - Status: **B**. Sources: Crossref metadata; S2 TLDR. Metadata URL: https://api.crossref.org/works/10.1038/s42254-021-00314-5

- **[Nogueira2022Using]** B. R. Nogueira, I.; V. Santana, V.; Ribeiro, A. M.; Rodrigues, A. E. Using scientific machine learning to develop universal differential equation for multicomponent adsorption separation systems. *The Canadian Journal of Chemical Engineering* **2022**, 100, 2279-2290. https://doi.org/10.1002/cjce.24495
  - What it shows: Proposes a universal ODE for multicomponent fixed-bed adsorption separation in which a neural network complements the mechanistic sink/source (equilibrium) term, identified from a small amount of experimental data.
  - Supports our sentence about: UDEs have been applied to adsorption dynamics, identified on data from one fixed-bed system rather than tested on unseen materials (Introduction/novelty).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/cjce.24495

- **[Subraveti2022Physics]** Subraveti, S. G.; Li, Z.; Prasad, V.; Rajendran, A. Physics-Based Neural Networks for Simulation and Synthesis of Cyclic Adsorption Processes. *Industrial & Engineering Chemistry Research* **2022**, 61, 4095-4113. https://doi.org/10.1021/acs.iecr.1c04731
  - What it shows: PANACHE: physics-constrained neural networks that emulate cyclic adsorption processes (PSA steps) without isotherm inputs.
  - Supports our sentence about: physics-based ML surrogates exist for adsorption process dynamics (Introduction).
  - Status: **B**. Sources: Crossref metadata; abstract of the ChemRxiv version (10.26434/chemrxiv-2021-lm2sl-v2). Metadata URL: https://api.crossref.org/works/10.1021/acs.iecr.1c04731

- **[Meredig2018Can]** Meredig, B.; Antono, E.; Church, C.; Hutchinson, M.; Ling, J.; Paradiso, S.; Blaiszik, B.; Foster, I.; et al. Can machine learning identify the next high-temperature superconductor? Examining extrapolation performance for materials discovery. *Molecular Systems Design & Engineering* **2018**, 3, 819-825. https://doi.org/10.1039/C8ME00012C
  - What it shows: Shows conventional ML metrics overestimate performance for materials discovery and proposes extrapolation-oriented (leave-cluster-out) evaluation.
  - Supports our sentence about: held-out-material (extrapolative) evaluation gives a more honest estimate than random splits (Methods/Discussion).
  - Status: **B**. Sources: Crossref (one-sentence abstract). Metadata URL: https://api.crossref.org/works/10.1039/C8ME00012C

### Reserve

- **[Raissi2019Physics]** Raissi, M.; Perdikaris, P.; Karniadakis, G. Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. *Journal of Computational Physics* **2019**, 378, 686-707. https://doi.org/10.1016/j.jcp.2018.10.045
  - What it shows: Introduces physics-informed neural networks for forward and inverse PDE problems.
  - Supports our sentence about: PINN background (Introduction).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1016/j.jcp.2018.10.045

- **[vonStosch2014Hybrid]** von Stosch, M.; Oliveira, R.; Peres, J.; Feyo de Azevedo, S. Hybrid semi-parametric modeling in process systems engineering: Past, present and future. *Computers & Chemical Engineering* **2014**, 60, 86-101. https://doi.org/10.1016/j.compchemeng.2013.08.008
  - What it shows: Reviews hybrid semi-parametric modelling in process systems engineering; notes hybrid models do not automatically give better results.
  - Supports our sentence about: hybrid models need validation (Discussion).
  - Status: **B**. Sources: Crossref metadata; S2 TLDR. Metadata URL: https://api.crossref.org/works/10.1016/j.compchemeng.2013.08.008

- **[Bradley2022Perspectives]** Bradley, W.; Kim, J.; Kilwein, Z.; Blakely, L.; Eydenberg, M.; Jalvin, J.; Laird, C.; Boukouvala, F. Perspectives on the integration between first-principles and data-driven modeling. *Computers & Chemical Engineering* **2022**, 166, 107898. https://doi.org/10.1016/j.compchemeng.2022.107898
  - What it shows: Title-level: perspectives on integrating first-principles and data-driven modelling.
  - Supports our sentence about: hybrid modelling background (Introduction).
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.compchemeng.2022.107898

- **[Santana2023Efficient]** Santana, V. V.; Costa, E.; Rebello, C. M.; Ribeiro, A. M.; Rackauckas, C.; Nogueira, I. B. Efficient hybrid modeling and sorption model discovery for non-linear advection-diffusion-sorption systems: A systematic scientific machine learning approach. *Chemical Engineering Science* **2023**, 282, 119223. https://doi.org/10.1016/j.ces.2023.119223
  - What it shows: Title-level: hybrid modelling and sorption model discovery for advection-diffusion-sorption systems by scientific ML.
  - Supports our sentence about: SciML for sorption dynamics (Introduction). Read before citing.
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.ces.2023.119223

- **[Xiong2020Evaluating]** Xiong, Z.; Cui, Y.; Liu, Z.; Zhao, Y.; Hu, M.; Hu, J. Evaluating explorative prediction power of machine learning algorithms for materials discovery using k-fold forward cross-validation. *Computational Materials Science* **2020**, 171, 109203. https://doi.org/10.1016/j.commatsci.2019.109203
  - What it shows: Proposes k-fold forward cross-validation and shows standard CV overestimates explorative prediction for materials discovery.
  - Supports our sentence about: random CV is optimistic for unseen materials (Methods).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1016/j.commatsci.2019.109203

## G5. Synthetic ground truth, held-out-group validation, dependent training sets

### Primary

- **[Dietterich1998Approximate]** Dietterich, T. G. Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms. *Neural Computation* **1998**, 10, 1895-1923. https://doi.org/10.1162/089976698300017197
  - What it shows: Compares five tests for comparing learning algorithms and shows tests based on repeated random train/test splits have inflated type I error.
  - Supports our sentence about: naive tests on overlapping training sets are anti-conservative (Methods: statistics of paired comparisons).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1162/089976698300017197

- **[Nadeau2003Inference]** Nadeau, C.; Bengio, Y. Inference for the Generalization Error. *Machine Learning* **2003**, 52, 239-281. https://doi.org/10.1023/A:1024068626366
  - What it shows: Title-level: inference for the generalization error; the standard source of the corrected resampled variance for overlapping training sets.
  - Supports our sentence about: our variance correction for dependent folds (Methods). Check the formula in the paper.
  - Status: **C**. Sources: Crossref metadata only (Springer login redirect; no abstract in S2). Metadata URL: https://api.crossref.org/works/10.1023/A:1024068626366

- **[Roberts2017Cross]** Roberts, D. R.; Bahn, V.; Ciuti, S.; Boyce, M. S.; Elith, J.; Guillera‐Arroita, G.; Hauenstein, S.; Lahoz‐Monfort, J. J.; et al. Cross‐validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* **2017**, 40, 913-929. https://doi.org/10.1111/ecog.02881
  - What it shows: Shows random CV underestimates predictive error for structured (temporal, spatial, hierarchical, phylogenetic) data and recommends blocked CV.
  - Supports our sentence about: family-level / leave-one-group-out hold-out (Methods).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1111/ecog.02881

- **[Varoquaux2018Cross]** Varoquaux, G. Cross-validation failure: Small sample sizes lead to large error bars. *NeuroImage* **2018**, 180, 68-77. https://doi.org/10.1016/j.neuroimage.2017.06.061
  - What it shows: Shows that small samples give large CV error bars and that fold-to-fold standard errors underestimate them.
  - Supports our sentence about: with 8-10 sorbents the uncertainty of any hold-out score is large (Discussion/Limitations).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1016/j.neuroimage.2017.06.061

- **[VarmaSimon2006Bias]** Varma, S.; Simon, R. Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics* **2006**, 7, 91. https://doi.org/10.1186/1471-2105-7-91
  - What it shows: Shows that the CV error of a classifier tuned by CV is a biased estimate of its true error; nested CV is needed.
  - Supports our sentence about: tuning must be kept inside the hold-out loop (Methods).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1186/1471-2105-7-91

- **[Talts2018Validating]** Talts, S.; Betancourt, M.; Simpson, D.; Vehtari, A.; Gelman, A. Validating Bayesian Inference Algorithms with Simulation-Based Calibration. *arXiv* **2018**. https://doi.org/10.48550/arXiv.1804.06788
  - What it shows: Introduces simulation-based calibration: validating an inference procedure on data simulated from known parameters.
  - Supports our sentence about: testing a learned model first on synthetic ground truth (our harness) is an established validation step (Methods).
  - Status: **A**. Sources: https://api.datacite.org/dois/ (abstract in record). Metadata URL: https://api.datacite.org/dois/10.48550/arXiv.1804.06788

- **[Cook2006Validation]** Cook, S. R.; Gelman, A.; Rubin, D. B. Validation of Software for Bayesian Models Using Posterior Quantiles. *Journal of Computational and Graphical Statistics* **2006**, 15, 675-692. https://doi.org/10.1198/106186006X136976
  - What it shows: Validates Bayesian software by simulating data from known parameters and checking posterior quantiles; finds errors when they exist.
  - Supports our sentence about: known-truth simulation tests catch implementation errors before real data (Methods).
  - Status: **B**. Sources: Crossref metadata; S2 TLDR. Metadata URL: https://api.crossref.org/works/10.1198/106186006X136976

### Reserve

- **[Modrak2025Simulation]** Modrák, M.; Moon, A. H.; Kim, S.; Bürkner, P.; Huurre, N.; Faltejsková, K.; Gelman, A.; Vehtari, A. Simulation-Based Calibration Checking for Bayesian Computation: The Choice of Test Quantities Shapes Sensitivity. *Bayesian Analysis* **2025**, 20, 461-488. https://doi.org/10.1214/23-BA1404
  - What it shows: Shows SBC sensitivity depends on the chosen test quantities and adds data-dependent quantities to detect more failure classes.
  - Supports our sentence about: the choice of harness checks decides what a synthetic test can detect (Discussion).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1214/23-BA1404

- **[Brunton2016Discovering]** Brunton, S. L.; Proctor, J. L.; Kutz, J. N. Discovering governing equations from data by sparse identification of nonlinear dynamical systems. *Proceedings of the National Academy of Sciences* **2016**, 113, 3932-3937. https://doi.org/10.1073/pnas.1517384113
  - What it shows: SINDy: discovers governing equations from data by sparse regression, demonstrated by recovering known systems.
  - Supports our sentence about: equation-learning methods are routinely validated by recovering known dynamics (Methods).
  - Status: **A**. Sources: Crossref (significance statement in record). Metadata URL: https://api.crossref.org/works/10.1073/pnas.1517384113

- **[Gelman2020Bayesian]** Gelman, A.; Vehtari, A.; Simpson, D.; Margossian, C. C.; Carpenter, B.; Yao, Y.; Kennedy, L.; Gabry, J.; et al. Bayesian Workflow. *arXiv* **2020**. https://doi.org/10.48550/arXiv.2011.01808
  - What it shows: Describes a Bayesian workflow including fake-data simulation and model checking.
  - Supports our sentence about: fake-data checks before real data (Methods).
  - Status: **A**. Sources: https://api.datacite.org/dois/ (abstract in record). Metadata URL: https://api.datacite.org/dois/10.48550/arXiv.2011.01808

## G6. Preregistration, negative results, reproducibility of ML in chemistry

### Primary

- **[Nosek2018Preregistration]** Nosek, B. A.; Ebersole, C. R.; DeHaven, A. C.; Mellor, D. T. The preregistration revolution. *Proceedings of the National Academy of Sciences* **2018**, 115, 2600-2606. https://doi.org/10.1073/pnas.1708274114
  - What it shows: Argues for preregistration to separate prediction (confirmatory) from postdiction (exploratory) research.
  - Supports our sentence about: why our hypotheses, harness and stopping rule were frozen in advance (Introduction/Methods).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1073/pnas.1708274114

- **[Kapoor2023Leakage]** Kapoor, S.; Narayanan, A. Leakage and the reproducibility crisis in machine-learning-based science. *Patterns* **2023**, 4, 100804. https://doi.org/10.1016/j.patter.2023.100804
  - What it shows: Surveys leakage in ML-based science (17 fields, 294 papers) and proposes a taxonomy and model info sheets.
  - Supports our sentence about: leakage between training and test materials inflates reported performance (Methods/Discussion).
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1016/j.patter.2023.100804

- **[Artrith2021Best]** Artrith, N.; Butler, K. T.; Coudert, F.; Han, S.; Isayev, O.; Jain, A.; Walsh, A. Best practices in machine learning for chemistry. *Nature Chemistry* **2021**, 13, 505-508. https://doi.org/10.1038/s41557-021-00716-z
  - What it shows: Recommends guidelines for reliable, reproducible ML models in chemistry and for ML reports.
  - Supports our sentence about: we follow best-practice reporting for ML in chemistry (Methods/Data availability).
  - Status: **B**. Sources: Crossref metadata; S2 TLDR. Metadata URL: https://api.crossref.org/works/10.1038/s41557-021-00716-z

- **[Raccuglia2016Machine]** Raccuglia, P.; Elbert, K. C.; Adler, P. D. F.; Falk, C.; Wenny, M. B.; Mollo, A.; Zeller, M.; Friedler, S. A.; et al. Machine-learning-assisted materials discovery using failed experiments. *Nature* **2016**, 533, 73-76. https://doi.org/10.1038/nature17439
  - What it shows: Trains models on failed (unsuccessful) synthesis experiments to predict reaction outcomes for templated vanadium selenites.
  - Supports our sentence about: negative results carry information and should be reported (Discussion).
  - Status: **A**. Sources: Crossref metadata; abstract via Europe PMC. Metadata URL: https://api.crossref.org/works/10.1038/nature17439

- **[StriethKalthoff2022Machine]** Strieth‐Kalthoff, F.; Sandfort, F.; Kühnemund, M.; Schäfer, F. R.; Kuchen, H.; Glorius, F. Machine Learning for Chemical Reactivity: The Importance of Failed Experiments. *Angewandte Chemie International Edition* **2022**, 61, e202204647. https://doi.org/10.1002/anie.202204647
  - What it shows: Shows that human biases in experiment selection and result reporting, including omission of failed experiments, degrade ML reactivity models.
  - Supports our sentence about: reporting the failed grey-box test helps the field (Discussion).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1002/anie.202204647

### Reserve

- **[Munafo2017Manifesto]** Munafò, M. R.; Nosek, B. A.; Bishop, D. V. M.; Button, K. S.; Chambers, C. D.; Percie du Sert, N.; Simonsohn, U.; Wagenmakers, E.; et al. A manifesto for reproducible science. *Nature Human Behaviour* **2017**, 1, 0021. https://doi.org/10.1038/s41562-016-0021
  - What it shows: Manifesto proposing measures (methods, reporting, reproducibility, incentives) to improve reproducible science.
  - Supports our sentence about: preregistration and open reporting (Introduction).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1038/s41562-016-0021

- **[Chambers2013Registered]** Chambers, C. D. Registered Reports: A new publishing initiative at Cortex. *Cortex* **2013**, 49, 609-610. https://doi.org/10.1016/j.cortex.2012.12.016
  - What it shows: Title-level: editorial launching the Registered Reports format at Cortex.
  - Supports our sentence about: registered/preregistered designs (Introduction).
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1016/j.cortex.2012.12.016

- **[Wang2020Machine]** Wang, A. Y.; Murdock, R. J.; Kauwe, S. K.; Oliynyk, A. O.; Gurlo, A.; Brgoch, J.; Persson, K. A.; Sparks, T. D. Machine Learning for Materials Scientists: An Introductory Guide toward Best Practices. *Chemistry of Materials* **2020**, 32, 4954-4965. https://doi.org/10.1021/acs.chemmater.0c01907
  - What it shows: Title-level: introductory guide to best practices in ML for materials scientists.
  - Supports our sentence about: best practices (Methods).
  - Status: **C**. Sources: Crossref metadata only. Metadata URL: https://api.crossref.org/works/10.1021/acs.chemmater.0c01907

- **[Jablonka2022Making]** Jablonka, K. M.; Patiny, L.; Smit, B. Making the collective knowledge of chemistry open and machine actionable. *Nature Chemistry* **2022**, 14, 365-376. https://doi.org/10.1038/s41557-022-00910-7
  - What it shows: Argues for an open, machine-actionable data platform in chemistry so data (incl. non-headline results) are reusable.
  - Supports our sentence about: open release of code and data (Data availability).
  - Status: **A**. Sources: Crossref (abstract in record). Metadata URL: https://api.crossref.org/works/10.1038/s41557-022-00910-7

## Novelty-check items (verified; discussed in T-P4-6_novelty.md)

- **[Xia2025Relationship]** Xia, X.; Li, K.; Chen, G.; Li, S. Relationship between water adsorption kinetics and structure property of metal-organic frameworks for adsorption cooling. *Colloids and Surfaces A: Physicochemical and Engineering Aspects* **2025**, 720, 137168. https://doi.org/10.1016/j.colsurfa.2025.137168
  - What it shows: Title-level: relationship between water adsorption kinetics and structure properties of MOFs for adsorption cooling (Li group). Closest prior work to novelty (b); must be read before citing.
  - Supports our sentence about: novelty (b).
  - Status: **C**. Sources: Crossref metadata only (no abstract in Crossref/S2; ScienceDirect 403; web search found no abstract). Metadata URL: https://api.crossref.org/works/10.1016/j.colsurfa.2025.137168

- **[Nikolenko2026Modality]** Nikolenko, S. I. Modality Graphs Predict Cross-Modal Reconstructability But Not Fusion Gain: A Preregistered Study in Machine Fault Diagnosis. *IEEE Access* **2026**, 14, 158836-158853. https://doi.org/10.1109/access.2026.3741122
  - What it shows: A preregistered ML study on four public machine-fault rigs testing whether dependence-based modality graphs predict fusion gain (title: they predict reconstructability but not fusion gain).
  - Supports our sentence about: novelty (c): preregistered ML studies with negative findings exist outside materials science.
  - Status: **A**. Sources: Semantic Scholar Graph API (abstract/TLDR). Metadata URL: https://api.crossref.org/works/10.1109/access.2026.3741122

## Crossref metadata quirks (fix by hand in the manuscript)

- Velte2023Adsorption: Crossref splits one author as family "P.C. Hügenell", given "Philipp"; the person is Philipp P. C. Hügenell.
- Nogueira2022Using: Crossref gives families "B. R. Nogueira" and "V. Santana"; the authors are Idelfonso B. R. Nogueira and Vinicius V. Santana.
- Sakoda1984Fundamental: Crossref gives the authors and journal in capitals (SAKODA, SUZUKI; JOURNAL OF CHEMICAL ENGINEERING OF JAPAN) and a trailing full stop in the title.
- Xiong2020Evaluating: the title contains MathML for "k" in Crossref; rendered here as "k-fold".
- Bezrukov2023Regeneration: Crossref encodes the apostrophe in O-Hearn (O’Hearn) as a typographic quote; use a plain apostrophe in LaTeX.

## Dropped or not used

- Velte et al. SSRN preprint (10.2139/ssrn.4230996) and Subraveti et al. ChemRxiv versions: used only to read abstracts; cite the journal versions.
- Li & Xia SSRN preprint "Correlation of structure property and water adsorption kinetics of MOFs for adsorption cooling" (10.2139/ssrn.4270233, 2022): superseded by the journal paper Xia et al. 2025 (10.1016/j.colsurfa.2025.137168); not cited separately.
- Rackauckas et al., Research Square version (10.21203/rs.3.rs-55125/v1): the arXiv record (10.48550/arXiv.2001.04385) is cited instead.
- Bengio & Grandvalet 2004 (no unbiased estimator of the K-fold CV variance, JMLR) and Ruthven's textbook: not added, because no DOI could be verified through Crossref/DataCite.
- No DOI in the candidate list failed to resolve.

## Counts

| Group | Primary | Reserve |
|---|---|---|
| G1 | 11 | 7 |
| G2 | 6 | 4 |
| G3 | 8 | 5 |
| G4 | 8 | 5 |
| G5 | 7 | 3 |
| G6 | 5 | 4 |
| N | 0 | 2 |
| total | 45 | 30 |

Status counts (all 75 entries): A = 44, B = 11, C = 20
