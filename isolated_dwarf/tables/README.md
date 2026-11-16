# Input tables

These files are copied from the tables used by the isolated runs. The Mix0.1 yields are used by the AEOS and ABYSS inputs; the Emerick yields are used by the E20 inputs. Radiation and stellar-property table names are hardcoded in the Enzo reader and must be available in the launch working directory. Cooling and yield filenames are specified in the .enzo file.

`IndividualStarYields-Mix0.1-PopIIICorrected.h5` corrects the 120 PopIII CCSN
rows using the HW2010 isotope yields (S4, 1.2 Bethe, mixing 0.1). The original
Mix0.1 file and existing run parameters are preserved. See
[the correction and usage notes](PopIII-correction.md) for validation,
provenance, and the rebuild command. To select it in a new run:

```ini
StellarYieldsFilename = IndividualStarYields-Mix0.1-PopIIICorrected.h5
```

Verify the files:

```bash
cd isolated_dwarf/tables
sha256sum -c SHA256SUMS
```

For a run in its exported directory, link the shared tables before launching:

```bash
cd isolated_dwarf/runs/run3-abyss-noFEWBODY
for table in ../../tables/*.h5 ../../tables/*.in; do
    ln -s "$(realpath "$table")" "$(basename "$table")"
done
```

Use the same procedure for the other run directories. A compatible Enzo binary, MPI/runtime libraries, and (for restarts) the full matching checkpoint are still required. The MBH insertion filename in full restart decks is an inactive default, not an input required for these isolated runs.

## Seeded artificial-SN event schedule

`sn-events-fiducial-seed42.txt` contains **100 events from 2.5 to 250 Myr
inclusive**, separated by 2.5 Myr (0.4 SN/Myr). The first 43 rows, through
107.5 Myr, are unchanged from the original archived schedule. Extending the
schedule deliberately continues artificial driving beyond the historical
DD0108 shutdown; it does not stop automatically relative to first-star birth.

Rebuild the table from this directory:

```bash
python3 generate_sn_events.py --end-myr 250 > sn-events-fiducial-seed42.txt
```

The generator follows the uniform-cylinder geometry in Enzo's
`src/enzo/CheckForTimeAction.C` (`IndividualStarICSupernovaMethod=1`):
`theta=2*pi*U1`, `r=R*sqrt(U2)`, `z=Z*(2*U3-1)`. It uses `R=250 pc`,
`Z=100 pc`, a 59 kpc box centered at `(0.5, 0.5, 0.5)`, and Python
`random.Random(42)`. Continuing the same stream reproduces every original
row exactly. This matches the sampling geometry, rather than Enzo's private
IC-SN RNG sequence or recovered historical event locations.

Columns are `time_Myr x_code y_code z_code`; times use Enzo's
`Myr_s=3.1556952e13 s` convention and positions are absolute code coordinates.
This four-column event list is distinct from the tabulated SN **rate** input
read by `IndividualStarICSupernovaFromFile` in the inspected Enzo source.
Extending this file alone does not enable it in a running simulation.
