# Enzo–ABYSS run 11486 logs and initial parameter file

Source: /home/wispedia/AA/isolated/runs/run3-abyss-noFEWBODY on happiness2.
Only DD0000/DD0000 (the parameter file) is included, not the complete checkpoint. The original files remain untouched. Compressed archives larger than 90 MiB are split to fit GitHub file limits.

Reconstruct and extract from this directory:

```bash
cat stderr.11486.happiness2-00.gz.part* > stderr.11486.happiness2-00.gz
gzip -dk stdout.11486.happiness2-00.gz
gzip -dk stderr.11486.happiness2-00.gz
```

Verify tracked payloads before reconstruction with `sha256sum -c SHA256SUMS`.

## Executable and launcher for run 11486

`enzo.11486.exe.gz` contains the executable whose SHA256 matches the original run's executable.sha256. `job_node03.11486.pbs` is the retained fresh-start job script, and `rank_launch.sh` is its required per-rank CPU/thread wrapper. The launcher is copied from the run directory; it is not an independently archived PBS spool copy. Its original absolute paths refer to happiness2. It uses 40 Enzo ranks and one ABYSS rank with 16 threads on node03.

```bash
gzip -dk enzo.11486.exe.gz
sha256sum -c enzo.11486.exe.sha256
chmod +x enzo.11486.exe rank_launch.sh
```

The executable requires the happiness2 Intel MPI/compiler runtime, HDF5, Grackle, CUDA runtime, and actual NVIDIA driver. Extracting it does not install those dependencies. The copied job script stages its binary from its original build path; adapt that path before using the archived executable elsewhere. Startup input is exported at `../isolated_dwarf/runs/run3-abyss-noFEWBODY/input.enzo`; tables are under `../isolated_dwarf/tables/`.
