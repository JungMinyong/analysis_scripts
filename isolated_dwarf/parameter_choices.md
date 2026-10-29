# Parameter choices for the isolated dwarf-galaxy experiment

Updated 2026-10-15. The current selected setup is **run3-fiducial**: an
isolated galaxy in a 59 kpc box, using AEOS individual-star physics and
selected h323 settings. Its disk and ambient initial metal mass fractions
are **5.4e-4**, matching Emerick's quoted absolute metallicity, and its initial
stop time is **120 Myr**. The original startup enables artificial SNe; the continuation disables
them as recorded below.

**Continuation update:** artificial SNe were disabled at DD0108
(108.000040 Myr), and the continuation target is 500 Myr. The test began
with the default `SmallRho = 1e-30`; the DD0252 restart parameter file
(250.000006 Myr) now uses **`SmallRho = 1e-6`**. With
`UsePhysicalUnit = 0` and `DensityUnits = 1e-27 g/cm³`, these are code
densities, corresponding to **1e-57** and **1e-33 g/cm³**, respectively.
The initial ambient floor remains **1e-34 g/cm³**; the new solver floor
is ten times that initial ambient density. This is a numerical experiment
following hydro failures; its effect on stability and added mass needs
measurement.

**How to read the comparison:** “AEOS” refers primarily to the **saved h323
parameters**. The AEOS cosmological methods manuscript describes a different
fiducial simulation; its differing values are explicitly identified below.
“Emerick” refers to the isolated-galaxy methods and follow-up experiments,
whose numerical resolutions also differ. “Not specified” means the cited
material does not establish the value; it does not imply the feature is absent.
The sections group choices by their main motivation, rather than claiming
that each choice is exclusive to one model.

## I. Parameters shared with Emerick’s test and AEOS

| Parameter or method | Our choice (run3) | Emerick’s choice | AEOS choice |
| --- | --- | --- | --- |
| Hydrodynamics and mesh | Enzo AMR; PPM (`HydroMethod = 0`) | Enzo AMR; PPM in the underlying methods | Enzo AMR; PPM |
| Gas self-gravity (`SelfGravity`) | Enabled | Enabled, alongside the imposed dark-matter potential | Enabled, alongside cosmological dark matter |
| Chemistry and cooling | Grackle; nine-species non-equilibrium primordial chemistry, metal cooling, gas-phase and dust H₂ formation | Same broad chemistry and cooling framework | Same broad framework, with later radiation/background updates |
| Shielding | Local shielding and H₂ shielding retained | Local shielding and H₂ shielding | Local shielding and H₂ shielding |
| Stellar population treatment | Stochastic formation of individual-star particles; low-mass aggregation as specified in Section III | Stochastically sampled individual stars | Stochastically sampled individual stars, with low-mass aggregation |
| Ionizing stellar radiation | Adaptive ray tracing, coupled to gas chemistry/heating | Adaptive ray tracing for H I and He I | Adaptive ray tracing |
| LW/FUV stellar radiation | LW dissociation and FUV photoelectric heating enabled | LW dissociation and FUV photoelectric heating | Both enabled; additional background/chemistry updates in Section III |
| Stellar feedback channels | Massive-star winds, AGB winds, core-collapse SNe, and Type Ia SNe | These channels are included in the full-feedback model | These channels are included |

Agreement in a method does not imply identical rates, tables, IMF, spatial
resolution, or injection geometry. Those distinctions appear below.

## II. Parameters following Emerick’s isolated test

| Parameter or method | Our choice (run3) | Emerick’s choice | AEOS choice |
| --- | --- | --- | --- |
| Simulation geometry (`ProblemType`, `ComovingCoordinates`) | Isolated galaxy; fixed physical coordinates (`31`, `0`) | Idealized isolated dwarf galaxy | h323: cosmological initial conditions and expansion (`30`, `1`) |
| Box width | **59 kpc physical**, adopted for this experiment | Exact width is not established by the inspected local manuscripts; this is an isolated-box design choice, not a verified numerical match | h323: 3.442 comoving Mpc/h; cosmological manuscript: a separate 1 cMpc simulation |
| Base grid (`TopGridDimensions`) | `128³` | Original setup described as using a `128³` base grid; local follow-up methods do not repeat its dimensions | h323: `64³` with nested initial grids |
| Fluid boundaries (`LeftFaceBoundaryCondition`, `RightFaceBoundaryCondition`) | Outflow, `1 1 1` on both sides | Outflow in the original isolated setup | h323: periodic, `3 3 3` |
| Gravity / radiation boundaries | Isolated gravity (`TopGridGravityBoundary = 1`); non-periodic radiation (`RadiativeTransferPeriodicBoundary = 0`) | Isolated-galaxy configuration; exact flags not established by the local manuscripts | h323: periodic gravity (`0`) and radiation (`1`) |
| Initial disk structure | Untapered analytic sech profile throughout the box; scale lengths **250 pc radial, 100 pc vertical** | Same quoted scale lengths; local manuscripts describe an exponential disk rather than specifying the exact sech expression | Cosmological gas density and velocity fields; no imposed isolated disk |
| Gas mass | `GalaxySimulationGasMass = 1.26e6 M☉` is the profile normalization; initialized total to be measured from run3 outputs | Initial total approximately `1.8e6 M☉` | Set by cosmological initial conditions |
| Initial metallicity | **`5.4e-4`** in disk and ambient, following Emerick | `isolated1.tex`: **`5.4e-4`**, i.e. `0.03 Z☉` with `Z☉ = 0.018` | Cosmological abundance evolution rather than an imposed enriched disk |
| Dark-matter gravity (`DiskGravity`) | Static analytic Burkert potential (`1`); scale radius 990 pc, central density `5.3536e-24 g cm⁻³` | Static Burkert halo; quoted virial mass `2.48e9 M☉`, virial radius 27.4 kpc | h323: evolving dark-matter particles; `DiskGravity = 0` |
| Diffuse-gas temperature threshold (`IndividualStarTemperatureLimit`) | **`8e6 K`** | `8e6 K` in the original isolated methods, as recorded in the startup summary | h323: **`1e8 K`**; the cosmological manuscript does not specify this threshold |
| Density interval for that threshold | Source-code bounds: `1e-30 < ρ < 1e-26 g cm⁻³` | Same quoted interval in the original prescription | Same bounds in the inspected implementation; not independent input parameters |
| Artificial-SN preparation | Startup rate `4e-7 yr⁻¹` = **0.4 Myr⁻¹**, followed by manual shutdown | Artificial SNe seed the ISM; intended shutdown approximately 25 Myr after the first star forms | h323: `IndividualStarICSupernovaRate = 0` |

Our disk is initialized using

`ρdisk(R,z) = [M₀ / (8πa²b)] sech(R/a) sech(z/b)`,

with `M₀ = 1.26e6 M☉`, `a = 250 pc`, and `b = 100 pc`. The initializer
uses cell-averaged disk density with a positive ambient floor. Matching
the scale lengths and approximate total gas mass does not establish an
exact reproduction of the published initial density field.

**Temperature-limit implementation:** the inspected routine lowers specific
thermal energy while increasing density, with multiplier capped by
`IndividualStarTemperatureLimitFactor = 100`. It can therefore add gas mass.
The threshold is not implemented as a purely energy-removing ceiling.

**Outflow-boundary implementation:** ghost cells copy adjacent interior
states. Inward mass flux remains possible; this boundary condition does
not guarantee constant gas-plus-stellar mass.

## III. Parameters following AEOS / h323

| Parameter or method | Our choice (run3) | Emerick’s choice | AEOS choice |
| --- | --- | --- | --- |
| Jeans refinement (`RefineByJeansLengthSafetyFactor`) | **4 cells** | 8 cells | **h323: 4; cosmological manuscript: 8** |
| Mass-refinement exponent (`MinimumMassForRefinementLevelExponent`) | **`−0.2`** | Local manuscripts quote a 50 M☉ cell threshold; exponent not specified | h323: first field exponent `−0.2` |
| Pressure floor (`UseMinimumPressureSupport`) | **`0`, disabled** | Original isolated methods describe extra pressure support at maximum refinement | h323: `0`; cosmological manuscript explicitly omits the floor |
| Individual-star mode (`StarParticleCreation`, `StarParticleFeedback`) | `32768`, `32768` | Individual-star model; numeric flags not specified in the manuscripts | h323: `32768`, `32768` |
| Star-formation density (`StarMakerOverDensityThreshold`, `IndividualStarSecondaryOverDensityThreshold`) | **2500 cm⁻³** | 50 cm⁻³ at 3.6 pc; 200 cm⁻³ at 1.8 pc in the local follow-ups | **h323: 2500 cm⁻³; cosmological manuscript: `1e4 cm⁻³`** |
| Gas temperature / reservoir (`IndividualStarTemperatureThreshold`, `IndividualStarSFGasMassThreshold`) | **500 K / 100 M☉** | Exact pair not established by the inspected local follow-up methods | h323 and cosmological manuscript: 500 K / 100 M☉ |
| Maximum star-forming mass fraction (`IndividualStarMassFraction`) | `0.5` | Not specified in the inspected local follow-ups | h323: `0.5` |
| IMF (`IndividualStarIMF`, mass cutoffs) | Kroupa (`2`), **0.08–120 M☉** | Salpeter, **1–100 M☉** | h323 and cosmological manuscript: Kroupa, 0.08–120 M☉ |
| Low-mass particle treatment (`IndividualStarIMFMassFloor`) | Aggregate stars below **2 M☉** | Individually sampled range starts at 1 M☉ in the local follow-ups | h323 and cosmological manuscript: aggregate below 2 M☉ |
| Feedback injection (`IndividualStarFeedbackStencilSize`, `IndividualStarFeedbackRadius`) | Fixed physical radius **1.5 pc**, stencil `−1` | Three-cell radius with cloud-in-cell mapping; 10.8 pc at 3.6 pc resolution | **h323: 1.5 pc; cosmological manuscript: 2 pc**, with physical-sphere overlap mapping |
| Massive-star winds (`IndividualStarStellarWindVelocity`, `IndividualStarMaximumStellarWindVelocity`) | **100 km s⁻¹** setting and cap | `isolated1.tex` reduces stellar winds to **10 km s⁻¹** | h323: 100 km s⁻¹; cosmological manuscript: 100 km s⁻¹ ceiling with thermalized energy |
| AGB winds (`IndividualStarAGBWindVelocity`) | **10 km s⁻¹** | 10 km s⁻¹ in the reduced-wind isolated suite | **h323: 10 km s⁻¹; cosmological manuscript: 20 km s⁻¹** |
| Core-collapse / direct-collapse limits | `IndividualStarSNIIMassCutoff = 8 M☉`; `IndividualStarDirectCollapseThreshold = 25 M☉` | Local follow-ups identify massive stars above 8 M☉; detailed collapse limits are not established there | h323 and cosmological manuscript: core-collapse range 8–25 M☉, direct collapse above 25 M☉ |
| Type Ia model (`IndividualStarSNIaModel`, `IndividualStarSNIaFraction`) | Ruiter implementation (`2`), fraction **0.1508** | Earlier single power-law delay model | h323 / cosmological manuscript: updated Ruiter multi-channel model and fraction 0.1508 |
| FUV background / PE efficiency (`UseFUVBackground`, `PhotoelectricHeatingDustModelEfficiency`) | Enabled (`1`); constant **0.05** efficiency | Older density-dependent efficiency | Updated AEOS prescription: background FUV and constant 0.05 efficiency |
| Additional radiation chemistry | Stellar IR/FUV/LW machinery retained, including H⁻/H₂-related radiation effects | Older treatment omits some later IR/FUV chemistry contributions | Updated AEOS radiation chemistry |
| Yield table / tracked species | `IndividualStarYields-Mix0.1.h5`; H, He, and **10 metals**: C, N, O, Na, Mg, Ca, Mn, Fe, Sr, Ba | `isolated1.tex`: **15 metals**, in addition to the primordial chemistry | AEOS: H/He plus these ten metals; updated yield prescriptions |
| Pop III machinery retained | Enabled; H₂ criterion **0.0005**, characteristic IMF mass **20 M☉** | Not part of the enriched isolated-disk setup | h323: same retained values; cosmological manuscript: **0.005**, fiducial **10 M☉**, with a separate 20 M☉ case |

The initial disk is enriched, so retaining Pop III machinery does not mean
the run begins with a Pop III population. Likewise, naming the mixture
yield table does not independently verify every yield modification,
rotation mixture, or Mg scaling described in the cosmological manuscript.

The four-cell Jeans criterion requests refinement; with the pressure floor
disabled it does not enforce four-cell Jeans resolution after the maximum
AMR level is reached.

## IV. Parameters chosen for this experiment

These are numerical or experimental choices. They should not be presented
as exact published Emerick or AEOS fiducial values.

| Parameter or method | Our choice (run3) | Emerick’s choice | AEOS choice |
| --- | --- | --- | --- |
| Exact physical box width | **59 kpc**; included in Section II for its isolated-setup motivation | Exact match not established by inspected local methods | h323 uses a cosmological box |
| Ambient floor (`GalaxySimulationUniformDensity`, `GalaxySimulationGasHalo`) | **`1e-34 g cm⁻³`**, no separate halo (`0`); optional comparison `1e-33 g cm⁻³` | Exact floor not established by the inspected manuscripts | No prescribed uniform ambient reservoir in h323 |
| Hydro density floor (`SmallRho`) | Startup default **`1e-30`** code units; DD0252 restart **`1e-6`** code units = **`1e-33 g cm⁻³`** | Not established by the inspected manuscripts | h323 saved value `1e-30` code units; physical conversion depends on redshift |
| Disk selection / truncation controls | `GalaxySimulationDiskRadius = 1.0` box unit = 59 kpc; `GalaxySimulationTruncationRadius = 0.1 Mpc` = 100 kpc | Exact cutoffs not established by local manuscripts | Not applicable to cosmological initial conditions |
| Finest spatial resolution / AMR limit | **0.90027 pc**, level **9**, factor-two refinement from `128³` | 1.8 pc in the original/mixing runs; 3.6 pc in the feedback follow-up | h323 physical-scale limiter approximately 1 pc; cosmological manuscript: 1 pc |
| Root gas-mass refinement trigger (`MinimumOverDensityForRefinement`) | `0.06912848219239826`, approximately **100 M☉** at the root level; decreases with level through exponent `−0.2` | Quoted cell-mass target **50 M☉** | h323 has multiple field thresholds; the isolated normalization is not copied directly |
| Refinement criteria (`CellFlaggingMethod`) | `2 6`: gas-mass and Jeans criteria | Mass and Jeans criteria described; exact flags not specified | h323: `2 4 6 8` |
| Active-source refinement (`IndividualStarRefineToPhysicalRadius`) | **5 pc**, requested level 9 | Three-cell radius around active feedback sources | Separate particle/refinement controls; cosmological levels are not directly transferable |
| Initial ambient temperature | **`1e4 K`** | Not established by the inspected local follow-up methods | Cosmological initial conditions |
| UV-background epoch (`RadiationFieldRedshift`) | Fixed **`z = 0`** | Local isolated background treatment; exact override not established here | h323 follows the evolving cosmological epoch |
| Artificial-SN event phase | First event **2.5 Myr**; nominal spacing **2.5 Myr** | Rate and relaxation motivate the driver; exact first-event phase not established here | Artificial driver disabled in h323 |
| Artificial-SN shutdown restart | DD0108 at **108.000040 Myr**, approximately **24.420118 Myr** after first birth at 83.579922 Myr | Intended approximately **25 Myr after the first star** | Artificial driver disabled |
| Output spacing / end time | **1 Myr** startup dumps, initial target **120 Myr**; continuation target **500 Myr** | Experiment-dependent | Cosmological redshift-based evolution |

The two disk cutoffs are deliberately outside the entire box: the selection
radius exceeds the center-to-corner distance, and tapering starts beyond
the largest cylindrical radius. Thus the initialized gas follows the sech
profile across the volume until it reaches the ambient floor. Deleting
these controls would restore finite defaults rather than disable them.

At `1e-34 g cm⁻³`, a uniform gas filling the entire 59 kpc box would contain
approximately **303 M☉**; at `1e-33 g cm⁻³`, approximately **3035 M☉**.
These are reference reservoir masses, not extra masses to add to the measured
disk-plus-ambient total, because the initializer applies a density floor.

Artificial SNe remain enabled in the original `input.enzo`. The shutdown
restart sets all four driver controls below, leaving ordinary stellar feedback
enabled. The current DD0252 continuation inherits this disabled driver.

```text
IndividualStarICSupernovaRate = 0
TimeActionType[0]      = 0
TimeActionTime[0]      = -1
TimeActionParameter[0] = -1
```

## Sources and executable provenance

- [Detailed startup comparison](59kpc_startup_parameters.md): derivations,
  original-methods context, boundary and temperature-limit implementation.
- [Run3 startup parameters](runs/run3-fiducial/input.enzo) and
  [run3 launch instructions](runs/run3-fiducial/README.md).
- [Emerick isolated feedback manuscript](references/isolated1.tex),
  especially the numerical methods and feedback sections.
- [Emerick isolated mixing manuscript](references/isolated2.tex),
  especially the methods section. Its stated three-cell injection radius
  and quoted 7.2 pc at 1.8 pc resolution are arithmetically inconsistent;
  the three-cell method is used for comparison, without adopting 7.2 pc.
- [AEOS cosmological methods manuscript](references/cosmological1.tex),
  especially numerical methods, star formation, feedback, and yields.
- h323 operational reference:
  `/home/wispedia/AA/ufds/h323/fixed1/parameter_file.txt` and
  `/home/wispedia/AA/ufds/h323/fixed1/DD0193/DD0193`.
  Cosmological refinement levels and other evolving snapshot state are not
  treated as universal startup values.
- Run3 uses the corrected `enzo-fixed1.exe` with the star-formation gas-debit
  fix on base branch `aeos`, commit `69abeb1a6`. Recorded SHA-256:
  `6ea8ff2691dae8ed58444d954a00d8f2016415c0d8dcf910776d6301b41ca7d5`.
  This source correction is independent of the parameter choices.
