# Running the AEOS isolated dwarf galaxy

This guide documents the corrected-Kroupa **fiducial** isolated dwarf run. It
is written to be portable: use the equivalent local locations for the source,
executable, parameter files, and data tables on another machine.

## Emerick parameter reproduction

[run3-emerick-l7](runs/run3-emerick-l7/README.md) is the separately prepared
Emerick `isolated1.tex` setup: 58.9824 kpc, level 7 (3.6 pc), Salpeter
1–100 Msun, archived stellar yields, 10 km/s winds, and a three-cell
feedback radius. Its README documents the retained current-code differences.
Start manually with `./local.sh 32` in that directory; use its
`prepare_restart.py` after startup to arrange artificial-SN shutoff near
first birth + 25 Myr and continuation through first birth + 750 Myr.
Preparation did not launch the simulation.

The [run3-emerick-l8](runs/run3-emerick-l8/README.md) variant uses level 8
(1.8 pc), a 200 cm⁻³ SF threshold, and a three-cell feedback radius of 5.4 pc.
It includes the same local launcher and node01/64-core PBS script with email
notifications, and has not been launched.

## Current 59 kpc test

The selected fresh setup is [run3-fiducial](runs/run3-fiducial/README.md):
59 kpc box, 128³ base grid, level 9 (0.9003 pc), ambient floor
`1e-34 g/cm³`, and disk/ambient initial metallicity **`5.4e-4`**.
The metallicity matches Emerick's quoted `0.03 Z☉` for `Z☉ = 0.018`;
the previous `4.3e-4` was inherited and does not reproduce that absolute
metal fraction. Run3's initial target is **120 Myr**, with 1 Myr outputs.
Use `./local.sh 32` from `runs/run3-fiducial` for fresh startup.
Artificial SNe remain active until a later shutdown restart selected using
this realization's first-star time.

Run3 uses four Jeans cells, refinement exponent -0.2, no minimum pressure
support, and the 8e6 K diffuse-gas threshold. See
[parameter choices](parameter_choices.md) for the full comparison.
The smaller-box fiducial table and root templates below describe the
earlier setup, not the current run3 parameters.

Run3's current continuation uses DD0252 (250.000006 Myr), targeting 500 Myr;
artificial SNe were disabled at DD0108. The test began with default
`SmallRho = 1e-30`, and DD0252 now sets **`SmallRho = 1e-6`**.
With `UsePhysicalUnit = 0` and density unit 1e-27 g/cm³, the latter is a
physical solver floor of **1e-33 g/cm³**, ten times the initial ambient
density. This is a numerical stability experiment and can introduce mass.

## Source and model provenance

The code used for this run is the [`aeos` branch of
`JungMinyong/enzo-dev`](https://github.com/JungMinyong/enzo-dev/tree/aeos), at
commit `69abeb1a61827a5b2cea4003a47b3e5d7c005f15` (`69abeb1a6`). The isolated
executable should be built from that source and then kept fixed for all
continuations of a realization.

The branch retains the AEOS individual-star physics used by the cosmological
calculations: stochastic Kroupa IMF sampling; star-by-star winds, core-collapse
SNe, SNe Ia, and yields; ionizing radiation; IR, FUV/photoelectric, and
Lyman-Werner radiation; Grackle non-equilibrium chemistry, dust, shielded UVB,
and metal cooling. The Kroupa logarithmic-grid sampler is the corrected version
(`IndividualStarKroupaAlpha1/2/3 = -0.3, -1.3, -2.3`).

The changes made to make this physics usable in the isolated `ProblemType = 31`
configuration are deliberately narrow:

- Initialize every isolated-disk velocity component, so the disk receives the
  intended circular rotation rather than an unphysical shear/collapse.
- Initialize isolated source-tracer fields and labels correctly.
- Select artificial-SN feedback grids using the requested *physical* injection
  radius rather than a resolution-dependent interpretation.
- Clean up an invalid timer iterator safely.
- Retain the corrected Kroupa IMF sampler used by the AEOS cosmological model.

These are compatibility/robustness corrections. They do not replace the AEOS
star-formation or stellar-feedback model with a separate idealized model.

## Fiducial model and why these values are used

The setup combines AEOS physics with the Leo-P-like isolated dwarf model of
Emerick and collaborators. The former supplies the stellar/chemical model; the
latter supplies an intentionally simple, static galaxy and an initial ISM
relaxation procedure.

| Component | Fiducial value | Rationale |
| --- | --- | --- |
| Coordinates and box | Physical (`ComovingCoordinates = 0`); 8.192 kpc box; `32^3` root grid | Isolated, non-expanding dwarf rather than cosmological initial conditions. |
| Resolution | `MaximumRefinementLevel = 8`; 1 pc finest cells | Resolves dense ISM/star-forming regions while retaining a practical global-box cost. |
| Gas disk | Exponential/sech disk, `M0 = 1.26e6 Msun`, radial/vertical scales 250/100 pc | The Emerick Leo-P-like initial condition; `M0` is the disk normalization, not a pre-existing stellar population. |
| Initial metallicity (earlier setup) | `Z = 4.3e-4` for disk and ambient gas | Inherited value, rationale unverified; current run3 uses `5.4e-4` to match the reference's absolute metallicity. |
| Halo | Static Burkert-like potential, scale radius 990 pc | Matches the intended low-mass-dwarf dynamical potential without live cosmological DM. |
| Analytic stellar disk | `DiskGravityStellarDiskMass = 1e-10 Msun` | Dynamically negligible workaround for the isolated initializer; there are no initial star particles. |
| Refinement | Mass plus Jeans criteria (`CellFlaggingMethod = 2 6`) | Follows the AEOS AMR machinery; there is no persistent, imposed 1-pc central refinement cube in the fiducial run. |
| Individual-star formation | Gas-mass threshold `100 Msun`, `T < 500 K`, secondary overdensity threshold `2500`, creation stencil `3` | AEOS individual-star formation at 1-pc resolution. The maximum converted fraction is 0.5, preventing a single formation event from removing all cell gas. |
| IMF | Kroupa, 0.08--120 `Msun`; tracked-particle mass floor 2 `Msun` | Same AEOS sampling model used for the cosmological calculations. |
| Stellar feedback | Winds, SN II, SNe Ia, radiation, IR/LW/FUV enabled | Preserve the AEOS multi-channel feedback model. |
| Diffuse radiation and cooling | Shielded HM2012 UVB, local stellar LW and FUV heating, dust/metal cooling | AEOS/Grackle physics; the physical isolated run uses the fixed low-redshift UVB rather than an evolving cosmological redshift. |
| Output cadence | `dtDataDump = 1` Myr | Time-resolves the star-formation and feedback history while keeping output volume manageable. |

The startup template is `isolated_ms_nonstatic_70Myr.enzo`. It includes the
Emerick-style artificial-SN relaxation. The corresponding restart template,
`restart_DD0133_no_artificial_SN.enzo`, is used after artificial driving is
removed. Adjust `StopTime` and the output cadence for the intended experiment,
but do not casually change the physical-model parameters above when continuing
a realization.

## Running and continuing a realization

1. Build Enzo from the pinned AEOS source with the same enabled individual-star,
   Grackle, radiation, and particle-ID options as the supplied executable.
2. Make a run directory containing the parameter file, executable, Grackle
   library, shielded cooling table, stellar-yield table, PARSEC table, and the
   q0/q1/q2 plus IR/FUV/LW stellar-radiation tables. The parameter file names
   these assets relative to the run directory.
3. Start a new realization with the startup template, for example:

   ```bash
   mpiexec -np <N> ./enzo.exe isolated_ms_nonstatic_70Myr.enzo > run.log 2>&1
   ```

   Use the MPI launcher and resource request appropriate for the local cluster.
   Set `StopCPUTime` below the scheduler walltime so Enzo stops cleanly.
4. To continue an existing calculation, use its last complete data dump as a
   restart input:

   ```bash
   mpiexec -np <N> ./enzo.exe -r DDxxxx/DDxxxx > restart.log 2>&1
   ```

   Before launching, edit the *copied restart parameter file* to increase
   `StopTime`. Preserve `InitialTime`, `InitialCycleNumber`, hierarchy/payload
   files, and the output counters. The next dump number then follows the
   existing series instead of overwriting the restart snapshot.

For example, the current fiducial continuation was restarted from 200 Myr with
`StopTime = 500` Myr and `dtDataDump = 1` Myr. This is a continuation choice,
not a new set of galaxy initial conditions.

## Artificial-SN relaxation requires a manual shutdown restart

The smooth initial disk needs artificial SNe to seed a turbulent ISM before
ordinary star formation and stellar feedback regulate the galaxy. The startup
configuration uses

```text
IndividualStarICSupernovaRate = 4e-7   # per year = 0.4 SN per Myr
```

with the prescribed injection radius and mean initial metallicity. These events
are an initialization device; they are not a real stellar population and should
not be allowed to continue indefinitely.

Emerick's intended procedure is to stop artificial driving **25 Myr after the
first star particle forms**. The simulation cannot know that star-formation
time in advance from a static parameter file. Therefore, inspect the outputs to
identify the first stellar birth, run until the chosen post-birth relaxation
interval has passed, then restart from a complete snapshot to disable the
artificial events. This manual restart after the initial few/tens of Myr of
star formation is required.

For the fiducial comparison already performed here, the chosen cutoff was an
absolute time of 131 Myr: the first star formed at 116.16640941 Myr, so this
was 14.83 Myr later. That is an explicit comparison choice and is **not** the
Emerick 25-Myr prescription.

In the shutdown-restart parameter file, set all four values:

```text
IndividualStarICSupernovaRate = 0
TimeActionType[0]      = 0
TimeActionTime[0]      = -1
TimeActionParameter[0] = -1
```

Setting only the rate to zero is unsafe: an already scheduled time-action event
can still inject an artificial SN. Do not turn off ordinary stellar feedback;
the edits above disable only the artificial initialization driver. After the
shutdown restart, continue normally to the desired final time.
