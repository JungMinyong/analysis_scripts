# Isolated galaxy startup: old and 59 kpc cases

Prepared 2026-10-14; updated 2026-10-15. **The current selected test is
[run3-fiducial](runs/run3-fiducial/README.md)**: disk and ambient metallicity
`5.4e-4`, initial stop time 120 Myr, ambient density `1e-34 g/cm³`.
Other startup parameter values follow run2. Artificial SNe remain enabled
in run3's startup; its shutdown epoch must use its own first stellar birth.
See [the comparison document](parameter_choices.md).

Run3 continuation update: artificial SNe were disabled at DD0108 and the
target extended to 500 Myr. The default startup `SmallRho = 1e-30` is
changed to **`1e-6` in DD0252** (250.000006 Myr). Both are code densities
(`UsePhysicalUnit = 0`): the physical solver floor changes from
1e-57 to **1e-33 g/cm³**. The initial ambient floor remains 1e-34 g/cm³.
The solver-floor change and any resulting mass addition must be accounted
for when comparing the continuation with earlier outputs.

The root templates and comparison tables below retain the original run2
values (`4.3e-4`, 70 Myr) as historical records. Run2 completed its 70 Myr
segment; its launcher now restarts DD0106 toward 150 Myr with artificial
SNe disabled. The original selected ambient case was **`1e-34` g/cm³**, using
[`isolated_59kpc_ambient1e-34.enzo`](isolated_59kpc_ambient1e-34.enzo).
[`isolated_59kpc_ambient1e-33.enzo`](isolated_59kpc_ambient1e-33.enzo)
is retained as an optional ambient-density comparison.
Both derive from [`isolated_ms_nonstatic_70Myr.enzo`](isolated_ms_nonstatic_70Myr.enzo).
Their only difference is `GalaxySimulationUniformDensity`.

Both run directories contain `input.enzo` and an executable `local.sh`.
For a fresh run3 startup, run `./local.sh 32` from `runs/run3-fiducial`.
Run2's launcher performs a DD0106 restart instead. Each launcher
uses the corrected `enzo-fixed1.exe`, whose checksum matches the current
EnzoAeos build, and writes `stdout` and `stderr`. Preparation does not start
the simulation.

The selected Jeans and feedback settings follow the **actual h323 saved
parameters**, even where the cosmological manuscript gives different
values:

| Setting | Selected value in both startup files / h323 | Cosmological manuscript |
| --- | --- | --- |
| Jeans refinement target | 4 cells | 8 cells |
| AGB wind velocity | 10 km/s | 20 km/s |
| Feedback injection radius | 1.5 pc | 2 pc |

These differences are intentional. The separately selected diffuse-gas
temperature threshold remains `8e6` K from Emerick's approach, versus
h323's `1e8` K. Minimum pressure support remains disabled.

## Geometry, gas, and boundaries

| Setting | Old fiducial startup | New: `1e-33` | New: `1e-34` |
| --- | ---: | ---: | ---: |
| Physical box width | 8.192 kpc | 59 kpc | 59 kpc |
| `TopGridDimensions` | `32 32 32` | `128 128 128` | `128 128 128` |
| Root cell width | 256 pc | 460.9375 pc | 460.9375 pc |
| Finest AMR level | 8 | 9 | 9 |
| Finest cell width | 1 pc | 0.9002686 pc | 0.9002686 pc |
| `LengthUnits` | `2.527786048197728e22` cm | `1.8205490337361566e23` cm | same |
| `DensityUnits` | `1e-27` g/cm³ | same | same |
| `TimeUnits` | `3.15576e13` s (1 Myr) | same | same |
| Disk center, box coordinates | `(0.5, 0.5, 0.5)` | same | same |
| `GalaxySimulationDiskRadius`, box coordinates | `0.245` | `1.0` (covers whole box) | same |
| Physical disk initialization radius (spherical selection) | 2.00704 kpc | 59 kpc; inactive within box | same |
| `GalaxySimulationGasMass` | `1.26e6` M☉ | same | same |
| Disk radial scale height | 250 pc | same | same |
| Disk vertical scale height | 100 pc | same | same |
| `GalaxySimulationTruncationRadius` (Mpc) | `0.0019` (1.9 kpc) | `0.1` (100 kpc; inactive within box) | same |
| `GalaxySimulationUniformDensity` | `1e-29` g/cm³ | `1e-33` g/cm³ | `1e-34` g/cm³ |
| Uniform-density mass across the whole box | ≈81,227 M☉ | ≈3,035 M☉ | ≈303 M☉ |
| `GalaxySimulationGasHalo` | `0` | same | same |
| Initial ambient temperature | `1e4` K | same | same |
| Initial disk and ambient metallicity | `4.3e-4` each | same | same |
| Left and right fluid boundary types, all axes | `1 1 1` | same | same |

The uniform-density masses are `density × box volume` and are reference
values, not a prediction of the initialized disk-plus-ambient gas mass.
The new inputs evaluate the untapered disk model throughout the box:

`rho_disk(R,z) = [M0 / (8 pi a² b)] sech(R/a) sech(z/b)`,

with `M0 = 1.26e6` M☉, `a = 250` pc, and `b = 100` pc. The initializer
computes cell-averaged disk density and applies it where it exceeds the
positive ambient floor (`1e-33` or `1e-34` g/cm³). Thus the far tails
approach this numerical floor rather than literal zero.

The source has no parameter switch to disable its spherical selection or
radial taper/truncation. Both are made inactive in the simulated volume:
the 59 kpc selection radius exceeds the 51.095 kpc center-to-corner
distance; the 100 kpc truncation radius puts the source's taper onset
at 76.923 kpc, beyond the 41.719 kpc maximum cylindrical radius.
Deleting these parameter lines would restore finite defaults rather
than disable the cutoffs. These are initialization controls, not
boundaries during later evolution.

For the untapered analytic profile, the central density is approximately
`5.43e-25` g/cm³. At the 59 kpc box boundary, the side-face center in the
disk plane has density approximately `6.15e-76` g/cm³; the top/bottom face
center has `8.30e-153` g/cm³. These are far below either ambient floor.
The initialized boundary gas therefore has approximately `1e-34` g/cm³
in the selected first case, and `1e-33` g/cm³ in the comparison case.
Changing the ambient density and box size together means these runs do not
isolate the effect of box size alone. The two new cases do isolate the
effect of the chosen ambient density.

In this Enzo source, fluid boundary type `1` means **outflow**. Its ghost
cells copy the adjacent interior state; inward gas motion is therefore
possible. A larger ambient density can raise inward mass flux at a fixed
velocity, but the velocity and pressure also respond to the setup. Measure
the signed flux at the six box faces in snapshots rather than assuming it
vanishes. The original Emerick setup is described as using outflow
boundaries on its 128³ base grid; this matches the selected boundary
behavior, without implying that its box width was 59 kpc.

## Refinement, gravity, and gas physics

The five level settings—`MaximumRefinementLevel`,
`MaximumGravityRefinementLevel`, `MaximumParticleRefinementLevel`,
`IndividualStarRefineToLevel`, and `MustRefineParticlesRefineToLevel`—are
all 9 in the new inputs, versus 8 in the old input. `RefineBy = 2`,
`CellFlaggingMethod = 2 6`, and `GalaxySimulationRefineAtStart = 1` are
retained. The Jeans-length target is now four cells, and
`MinimumMassForRefinementLevelExponent = -0.2`, following the h323
cosmological choices. The old isolated settings were eight cells and
exponent zero. The mass-refinement parameter
`MinimumOverDensityForRefinement` changes from `0.4035183151300021` to
`0.06912848219239826`, scaled by the old-to-new root-cell volume ratio to
retain the same approximate root-level physical gas-mass trigger;
the new exponent makes that threshold decrease with refinement level.

Minimum pressure support is explicitly disabled:
`UseMinimumPressureSupport = 0`. No active
`MinimumPressureSupportParameter` is specified. This follows h323 and
the intentional omission described in
[`references/cosmological1.tex`](references/cosmological1.tex), line 172:
the authors rely on high resolution, conversion of dense gas into stars,
and subsequent feedback to disperse gas. It differs from the additional
pressure floor described in the original Emerick methods paper. The four-cell Jeans
criterion requests refinement but does not enforce a pressure floor when
the maximum AMR level is reached.

The runs retain self gravity, isolated gravity boundary
(`TopGridGravityBoundary = 1`), the same static disk/dark-matter gravity
parameters, `HydroMethod = 0`, `FluxCorrection = 2`, Grackle cooling,
metal cooling, UV background, shielding, and dust-chemistry settings.
`GravitationalConstant`, density and time units, disk normalization and
scale heights are unchanged. The old disk taper/truncation and spherical
selection are now inactive throughout the box. The initial stellar
distribution remains disabled.

## Stars, feedback, and run schedule

| Setting | Old and both new startup inputs |
| --- | --- |
| Individual-star formation/feedback | `StarParticleCreation = 32768`, `StarParticleFeedback = 32768` |
| IMF | Corrected Kroupa sampling, `IndividualStarIMF = 2`; slopes `-0.3, -1.3, -2.3` |
| IMF masses | `0.08`–`120` M☉, `IndividualStarIMFMassFloor = 2` M☉ |
| Star-forming gas and temperature thresholds | `100` M☉, `500` K |
| `IndividualStarMassFraction` | `0.5` |
| Artificial SN startup rate | `4e-7` per year = `0.4` per Myr |
| Artificial SN schedule | First event 2.5 Myr; interval 2.5 Myr (`TimeActionType[0] = 3`) |
| Startup stop and output spacing | `StopTime = 70.0` Myr; `dtDataDump = 1.0` Myr |

The artificial SN schedule remains active in the startup files. Run2's
DD0106 restart disables the rate and time-action fields at 106.000023 Myr,
24.94118 Myr after its first stellar birth. Run3's eventual shutdown must
be selected from its own star-formation history; its startup does not
encode that later cutoff.

### Diffuse-gas temperature limit

Both new input files set `IndividualStarTemperatureLimit = 8e6` K,
following [Emerick et al., Section 2.1](https://academic.oup.com/mnras/article/482/1/1304/5115580),
and retain `IndividualStarTemperatureLimitFactor = 100`. The old isolated
inputs and the inspected h323 cosmological runs use `1e8` K and the same
factor. This Enzo source hardcodes the physical density interval
`1e-30 < density < 1e-26` g/cm³; those bounds are not input parameters.
The new threshold is 12.5 times lower than the cosmological setting.

`ApplyTemperatureLimit` implements the reduction by *increasing gas
density* by `min(temperature / limit, limit factor)` while lowering
specific thermal energy. It can add gas mass to affected cells. The
factor limit also means the temperature threshold is not an absolute
ceiling for arbitrarily hot gas. The `1e-33` and `1e-34` g/cm³ uniform
ambient values start below the eligible density range. Lowering the
threshold makes more hot cells eligible and increases the density
multiplier at a given temperature, so its mass contribution must be
included when interpreting gas-mass evolution.

## Explicit differences from the h323 cosmological setup

The comparison below uses `/home/wispedia/AA/ufds/h323/fixed1`:
`parameter_file.txt` describes startup choices and `DD0193/DD0193`
records effective values at redshift 0.103485. Refinement levels in
cosmological runs evolve; snapshot values should not be mistaken for
their initial values. The h323 `run1` and `stencil3` inputs also use
the `1e8` K temperature threshold.

| Setting or behavior | New isolated startup | h323 cosmological reference |
| --- | --- | --- |
| `ProblemType`, `ComovingCoordinates` | `31`, `0`: isolated galaxy, fixed physical coordinates | `30`, `1`: cosmological initial conditions and expansion |
| Box and root grid | 59 kpc physical; 128³ | 3.442 comoving Mpc/h; 64³ with nested initial grids |
| Fluid / gravity boundaries | Outflow `1 1 1` / isolated `1` | Periodic `3 3 3` / periodic `0` |
| Radiation boundaries | `RadiativeTransferPeriodicBoundary = 0` | `1` |
| Initial gas | Prescribed enriched disk and uniform ambient gas at `1e-33` or `1e-34` g/cm³ | Cosmological density/velocity fields; no prescribed uniform ambient reservoir |
| Dark matter gravity | Static analytic potential, `DiskGravity = 1` | Evolving dark-matter particles, `DiskGravity = 0` |
| Units and gravity normalization | Fixed density, length, and time units; `GravitationalConstant = 8.352838e-7` | Cosmological units evolve with expansion; `GravitationalConstant = 1` |
| AMR limit | Fixed level 9, 0.9003 pc cells; physical-scale limiter `-1` | Physical-scale limiter 1 pc; maximum levels 17 in DD0193 |
| Refinement criteria | `CellFlaggingMethod = 2 6` | `2 4 6 8` |
| Jeans resolution target | 4 cells | 4 cells |
| Minimum pressure support | `UseMinimumPressureSupport = 0` | `0`; saved support parameter `100` is inactive |
| Mass-refinement controls | Threshold `0.06912848219239826`, exponent `-0.2` | Multiple field thresholds; first exponent `-0.2` |
| Particle refinement | Both requested level settings 9 | Individual-star level 14 and must-refine level 5 in DD0193; startup template values were 4 |
| Diffuse-gas temperature threshold | **`8e6` K** | **`1e8` K** |
| Artificial SN preparation | `0.4` events/Myr, pending a later manual cutoff | `IndividualStarICSupernovaRate = 0` |
| UV-background epoch | Fixed `RadiationFieldRedshift = 0` | Follows the cosmological epoch (override unset) |
| Maximum ray length, box units | `1.7320508` | `0.13548` |
| Run timing | 70 Myr startup segment, 1 Myr dumps | Cosmological redshift-based evolution |
| Executable provenance | Requires the isolated star-formation gas-debit fix on base `69abeb1a6` | h323 fixed1 build records base `b1b85185`; run1 records `cd676c7d` |

The temperature routine, its density interval, and the factor 100 are
shared. The individual-star formation and feedback mode (`32768`),
Kroupa IMF parameters, gas-mass threshold (100 M☉), star-formation
temperature threshold (500 K), and maximum star-forming mass fraction
(0.5) are also retained from the cosmological model. In particular,
the **1.5 pc feedback radius and 100 km/s stellar-wind speed/cap are
unchanged from h323** (`run1/DD0065` and `fixed1/DD0193`):
`IndividualStarFeedbackStencilSize = -1`,
`IndividualStarFeedbackRadius = 1.5`,
`IndividualStarStellarWindVelocity = 100`,
`IndividualStarMaximumStellarWindVelocity = 100`, and
`IndividualStarAGBWindVelocity = 10`. The sections below compare these
retained settings separately with the cosmological and older isolated
manuscripts.
Setting `8e6` K
matches the paper's quoted temperature threshold; it does not reproduce
every initial condition or numerical choice in that paper.

## Changes explicitly described by the cosmological methods paper

[`references/cosmological1.tex`](references/cosmological1.tex),
*Aeos: Star-by-Star Cosmological Simulations of Early Chemical Enrichment
and Galaxy Formation*, describes updates to Emerick (2019). This paper's
fiducial 1 cMpc simulation is distinct from the inspected h323 zoom.
The paper's stated methods and h323's saved parameters are separate
sources of evidence.

| Change or choice in the cosmological paper | Relation to our selected inputs / h323 | Reference lines |
| --- | --- | --- |
| Deliberately omit the artificial pressure floor, relying on high resolution and star formation/feedback | Matches `UseMinimumPressureSupport = 0` | 172 |
| Add Pop III star formation, radiation, feedback, and enrichment based on an updated Wise model | Aeos machinery is retained; our disk starts already enriched, unlike the primordial cosmological initial conditions | 160, 204–214, 234–242 |
| Replace the Pop II Salpeter IMF with Kroupa over 0.08–120 M☉; aggregate stars below 2 M☉ | Matches the retained IMF settings | 216 |
| Add UV-background FUV heating and use constant photoelectric efficiency `0.05`, replacing the density-dependent efficiency | Matches `UseFUVBackground = 1` and `PhotoelectricHeatingDustModelEfficiency = 0.05` | 181–183 |
| Add FUV/IR effects on H₂-related and H⁻ reaction rates | IR/FUV/LW stellar radiation settings are retained | 181, 228–232 |
| Extend the UV background to high redshift, starting at z=50 with a 30,000 K blackbody, joining HM2012 at z=10; update high-redshift LW rates using Qin (2020) | Our isolated run uses the z=0 epoch. Exact agreement of background rates requires the cooling-table/Grackle implementation, not the input filename alone | 181 |
| Use a fixed physical injection sphere and Monte Carlo overlap calculation rather than the three-cell/CIC scheme in the older local manuscripts | Our code uses a physical radius, but h323 and our inputs use **1.5 pc**, whereas the paper specifies **2 pc** | 190–194 |
| Massive winds have a 100 km/s ceiling and their kinetic energy is thermalized | Retained speed/cap matches; the older `isolated1.tex` suite used 10 km/s | 196 |
| Update SNIa from a single power-law delay distribution to Ruiter A1 with four channels, Cummings white-dwarf masses, and exploding-progenitor fraction `0.1508` | `IndividualStarSNIaModel = 2` selects the Ruiter implementation; fraction `0.1508` is retained | 253–255 |
| Update yield sets: Heger–Woosley Pop III; Cristallo AGB; Limongi–Chieffi massive stars with a metallicity-dependent rotation mixture; massive-star Mg yields multiplied by 2.2 | Our input names the mixture yield table; its filename alone does not prove the Mg multiplier or all table contents | 282–295 |
| Track ten individual metals plus H/He and source tracers | Our 12 configured yield species are H, He, and these ten metals | 263–274 |

Additional paper-versus-input differences must remain explicit:

- Paper Jeans refinement target: **8 cells** (line 168); h323 and our
  selected target: **4 cells**.
- Paper star-formation density: **10⁴ cm⁻³** (line 202); h323 and our
  inputs: **2500 cm⁻³**. Both use 500 K and a 100 M☉ gas reservoir.
- Paper AGB wind speed: **20 km/s** (line 251); h323 and our inputs:
  **10 km/s**.
- Paper Pop III H₂ fraction requirement: **0.005**, characteristic
  mass **10 M☉** (with a separate 20 M☉ case); our retained input
  values: **0.0005** and **20 M☉**.
- The cosmological manuscript does not specify the diffuse-gas
  temperature ceiling in its methods section. The observed h323 value
  is `1e8` K; our explicitly selected value is `8e6` K.

This review updates the documentation only; it does not replace the
user-selected h323 settings with the paper's different fiducial values.

## Numerical methods in the local isolated Emerick references

The two local isolated files are follow-up manuscripts, rather than a
complete source branch or the original numerical-methods paper:

- [`references/isolated1.tex`](references/isolated1.tex), *The Role of Stellar
  Feedback in the Chemical Evolution of a Low Mass Dwarf Galaxy*:
  methods at lines 127–154; the feedback comparison uses 3.6 pc cells.
- [`references/isolated2.tex`](references/isolated2.tex), the metal-mixing
  experiments: methods at lines 89–100; it describes 1.8 pc cells.

Both refer to Emerick (2019) for the full numerical implementation.
They use Enzo AMR, a static Burkert dark-matter potential, eight cells
per Jeans length, Grackle nine-species chemistry including dust/gas H₂
formation and self-shielding, and ray tracing for H I/He I ionizing
radiation. LW/FUV radiation is treated as optically thin with local
attenuation. These agree with the broad methods retained in our inputs,
except that our selected Jeans target is now four cells.

| Numerical or physical choice | Local Emerick manuscripts | Our 59 kpc inputs |
| --- | --- | --- |
| Coarsest cell width | 921.6 pc | 460.9375 pc |
| Finest cell width | 3.6 pc (`isolated1.tex`); 1.8 pc (`isolated2.tex`) | 0.9002686 pc |
| Mass-refinement target | 50 M☉ per cell | Approximately 100 M☉ at root level, decreasing with exponent `-0.2` |
| Jeans-length resolution | 8 cells | 4 cells |
| Pressure floor at maximum refinement | Original Emerick methods paper describes additional non-thermal support | `UseMinimumPressureSupport = 0`, as in h323 |
| Star-formation number density | 50 cm⁻³ at 3.6 pc; 200 cm⁻³ at 1.8 pc | `StarMakerOverDensityThreshold = 2500` cm⁻³ |
| IMF and individually sampled mass range | Salpeter, 1–100 M☉ | Kroupa, 0.08–120 M☉, particle mass floor 2 M☉ |
| Region refined around active feedback sources | Three cell radii | Requested physical radius 5 pc |
| Wind/SN injection radius | Three cell radii | `IndividualStarFeedbackRadius = 1.5` pc, overriding the stencil radius |
| Wind speed | `isolated1.tex` reduces stellar winds to 10 km/s | Stellar-wind settings/cap 100 km/s; AGB winds 10 km/s |
| Tracked species | `isolated1.tex`: 15 individual metals | 12 configured yield species, including H and He |
| Initial total metallicity | `isolated1.tex`: `5.4e-4` | `4.3e-4` |

The gas mass quoted by both manuscripts is an initialized total of
`1.8e6` M☉. Our `GalaxySimulationGasMass = 1.26e6` is the disk-profile
normalization inherited from the original setup, rather than a measured
initialized total; these two numbers should not be compared as identical
definitions. The initialized total must be measured from the new output.

There is a numerical inconsistency in `isolated2.tex`: it gives a 1.8 pc
finest cell and also writes `3 × dx = 7.2 pc`. Three 1.8 pc cells are
5.4 pc. `isolated1.tex` explicitly corrects its analogous injection radius
to 10.8 pc for 3.6 pc cells. The prose supports a three-cell-radius
method, but the mixing manuscript's quoted 7.2 pc value needs independent
confirmation. Neither local methods section specifies the root-grid
dimensions or full box width, so 921.6 pc alone does not determine the
physical box size. Neither repeats the diffuse-gas temperature ceiling.

These differences are recorded for comparison; the startup inputs retain
the Aeos star/feedback settings, with the explicitly selected `8e6` K
diffuse-gas threshold.

`UseMinimumPressureSupport` is independent of the Jeans refinement
criterion. In the inspected Enzo PPM implementation, enabling it supplies
a pressure floor to the hydro solver only on maximum-refinement grids:
`P_used = max(P_thermal, C (Gamma - 1) rho²)`. The coefficient `C` is
computed in `Grid_SetMinimumSupport.C`, including the cosmological
expansion factor when appropriate. Its parameter `K =
MinimumPressureSupportParameter` sets a supported Jeans-length target
of `sqrt(K)` cells; `K = 100` means ten cells and `K = 16` means four.
The routine does not raise gas density like the diffuse-gas temperature
limiter. h323's recorded source revision and the current isolated source
have the same coefficient and pressure-floor implementations.
The original paper does not establish the historical value of `K`;
its description of a pressure floor should not be taken as evidence that
h323 has it enabled.

The earlier wrong fiducial continuation used `enzo-69abeb1a6.exe`
(SHA-256 `0aceacc11be0d6fccd2f5708fd9c83c4b2943086e08cd52ce73ccd920f922685`).
`runs/fiducial_fixed1` used `enzo-fixed1.exe`
(SHA-256 `6ea8ff2691dae8ed58444d954a00d8f2016415c0d8dcf910776d6301b41ca7d5`).
Both identify base branch `aeos` at
`69abeb1a61827a5b2cea4003a47b3e5d7c005f15`; the fixed executable
also contains an uncommitted correction to the star-formation gas debit.
The startup parameter files cannot apply this source-code fix. Use a
confirmed fixed executable for the new runs and record its checksum when
the launch is prepared. The old comparison runs turned off artificial SN
driving near 131 Myr; that historical cutoff is not prescribed for these
new cases.
