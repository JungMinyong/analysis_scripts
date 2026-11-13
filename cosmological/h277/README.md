# h277 fresh initial conditions and aeos-v2 run configuration

This records the fresh-IC configuration from
`/home/wispedia/AA/ufds/h277/aeos-v2-20261113-uvfix`, launched as job 11647.
The original MUSIC ICs come from `/home/wispedia/AA/ufds/h277/run1`.
They start at **z=70**, not z=100, and this run targets **z=8**.

- `parameter_file.txt`: exact initial run parameters, including corrected
  RR dust (`dust_chemistry=5`) and `dtDataDump=0.283`, twice the original interval.
- `job.pbs`: original node01/64-rank launcher, archived with its absolute paths.
- `manifest.json`: preparation provenance and required asset names.
- `assets.sha256`: original complete run-asset checksum list, including the
  executable and frozen library; this is not a list of files included here.
- `startup-validation.json`: initial snapshot checks from the run.
- `ic-manifest.json` and `IC_SHA256SUMS`: sizes and independently recomputed
  SHA-256 hashes for the 66 original IC field files (3.22 GiB total).

The configuration reads the original `GridDensity.*`, `GridVelocities_*`,
`ParticleDisplacements_*`, `ParticleVelocities_*`, and `RefinementMask.*` ICs.
It starts a new hierarchy without `-r`. Generated DD snapshots are not ICs.
The parameter file retains the original `IndividualStarYields-Mix0.1.h5` table;
it does not substitute the separately corrected PopIII yield table.

To reproduce the run, assemble the IC fields, the exact intended Enzo executable
and matching Grackle library, and the chemistry/yield/radiation tables listed in
`manifest.json` in a new run directory. Adapt the archived launcher's absolute
paths. Verify the IC files from that directory with
`sha256sum -c /path/to/IC_SHA256SUMS`. Do not launch the archived script unchanged
against the existing active run directory.

The IC binary files have not been included in this metadata commit. Their
storage choice is being confirmed separately; several exceed ordinary GitHub
Git file-size limits.
