# Input tables

These files are copied from the tables used by the isolated runs. The Mix0.1 yields are used by the AEOS and ABYSS inputs; the Emerick yields are used by the E20 inputs. Radiation and stellar-property table names are hardcoded in the Enzo reader and must be available in the launch working directory. Cooling and yield filenames are specified in the .enzo file.

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
