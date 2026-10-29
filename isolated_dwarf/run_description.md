# Fiducial and legacy-IMF isolated runs

## Emerick l7/l8: second phase prepared 2026-10-23

Both Emerick runs completed startup through 120 Myr. The second phase disables
artificial SN driving in the first output at or after first stellar birth
plus 25 Myr, and ends at **500 Myr absolute simulation time**.

| Run | First birth (Myr) | First birth + 25 Myr | Restart | Actual shutoff (Myr) | Elapsed since first birth (Myr) |
| --- | ---: | ---: | --- | ---: | ---: |
| `runs/run3-emerick-l7` | 92.144052609485 | 117.144052609485 | `DD0118/DD0118` | 118.000002010130 | 25.855949400645 |
| `runs/run3-emerick-l8` | 84.283545427162 | 109.283545427162 | `DD0110/DD0110` | 109.999990218510 | 25.716444791348 |

Both restart files now have `IndividualStarICSupernovaRate = 0`,
`TimeActionType[0] = 0`, `TimeActionTime[0] = -1`,
`TimeActionParameter[0] = -1`, and `StopTime = 500`.
Ordinary stellar feedback remains enabled. These selected snapshots are the
first outputs after the deadline, rather than the nearest outputs selected by
the original helper. The 500 Myr endpoint supersedes the original
first-birth-plus-750-Myr plan.

The original restart parameter files were saved under each run's timestamped
`archive/phase2-*` directory. Later startup snapshots were moved there:
**l7 DD0119–DD0121** and **l8 DD0111–DD0121**. Exclude them from production
analysis. Each run's `shutdown.json` records exact times and archive paths;
`restart.path` selects the prepared checkpoint for the default local launcher.

Submit the prepared second-phase jobs separately:

```bash
cd /home/wispedia/AA/isolated/runs/run3-emerick-l7
qsub job_phase2_node01_64.pbs

cd /home/wispedia/AA/isolated/runs/run3-emerick-l8
qsub job_phase2_node01_64.pbs
```

Both request node01, 64 cores, and 24 hours, with start/abort/end email to
`wispedia@snu.ac.kr`. Each job explicitly selects its cutoff checkpoint.
Scripts are prepared, not submitted. For a subsequent continuation, select
the newest complete checkpoint explicitly instead of rerunning these cutoff
jobs.

## Earlier fiducial and legacy-IMF history

Recorded 2026-09-21. Paths below are relative to `/home/wispedia/AA/isolated`
unless an absolute path is given. These are non-cosmological simulations;
times are simulation Myr, not redshifts.

## Runs and executable provenance

| | Fiducial | Legacy / wrong IMF |
| --- | --- | --- |
| Run directory | `runs/no-artificial-SN-11229.happiness2-00` | `runs/wrong-IMF` |
| Executable | `enzo-69abeb1a6.exe` | `runs/wrong-IMF/enzo-wrongIMF.exe` |
| Source | `/home/wispedia/enzo/EnzoAeos` | `/home/wispedia/enzo/EnzoAeos-wrongIMF` |
| Source revision | `69abeb1a61827a5b2cea4003a47b3e5d7c005f15` | Same base revision, with staged reversal of `b1b85185e64873c1b1b83d23fbed03b4043b866a` |
| IMF implementation | Corrected Kroupa sampling | Legacy Kroupa sampling |

The legacy source is on local branch `legacy-wrong-kroupa-imf`. The reversal
has not been committed. Its executable was rebuilt cleanly on node03 and its
checksum is stored in `runs/wrong-IMF/executable.sha256`. A base Git revision
alone does not identify this executable's staged source difference.

The reverted commit, "Fix Kroupa IMF sampling on logarithmic grid", changes
only `src/enzo/StarParticleIndividual_IMFInitialize.C`. The corrected sampler
includes the mass factor for integrating on a logarithmic mass grid and
continuity factors between the Kroupa segments. The legacy version omits
these factors. The difference is in source code, **not in the input alpha
parameters**. Later isolated-galaxy fixes, including the rotation fix in
`69abeb1a6`, remain present in both versions.

## Shared numerical and IMF parameters

| Parameter | Value in both runs |
| --- | --- |
| `ComovingCoordinates` | `0` |
| `TopGridDimensions` | `32 32 32` |
| `LengthUnits` | `2.5277860481977e22` cm (8.192 kpc box) |
| `TimeUnits` | `31557600000000` s (1 Myr) |
| `MaximumRefinementLevel` | `8` (1 pc finest cell) |
| `CellFlaggingMethod` | `2 6` |
| `IndividualStarIMF` | `2` |
| `IndividualStarKroupaAlpha1/2/3` | `-0.3`, `-1.3`, `-2.3` |
| `IndividualStarIMFLowerMassCutoff` | `0.08` |
| `IndividualStarIMFUpperMassCutoff` | `120` |
| `IndividualStarIMFMassFloor` | `2` |
| `dtDataDump` | `1` (1 Myr) |

The legacy restart inherits the fiducial gas state and physics parameters.
It uses links to the same shielded cooling table, stellar yields, and stellar
radiation tables under `AA/isolated`. No separate feedback-parameter change
was introduced to make the IMF comparison.

## Starting the legacy branch before star formation

Copied `DD0117` from `runs/nonstatic-restart120-11216.happiness2-00` into
`runs/wrong-IMF/DD0117`. Its time is **115.99999775252 Myr**, and it contains
zero particles and zero IMF sampling calls. The copied restart's `StopTime`
was changed from `120` to `200`; `dtDataDump = 1` was retained.

The run initially retained artificial SN driving from the copied snapshot:
`IndividualStarICSupernovaRate = 4e-7` per year, or **0.4 per Myr**.
`TimeActionType[0] = 3` represents the scheduled artificial SN event;
`TimeActionParameter[0] = 2.5e6` is its interval in years.

## Turning off artificial SN driving at 131 Myr

Both runs use an approximately **131 Myr absolute simulation-time cutoff**.
This was a chosen comparison setup; it is not the paper's first-star-plus-25-Myr
prescription.

| | Fiducial | Legacy / wrong IMF |
| --- | ---: | ---: |
| First stellar creation time (Myr) | 116.16640941 | 116.40307372285 |
| Restart snapshot with driving disabled | `DD0133` | `DD0132` |
| Restart time (Myr) | 131.00002844663 | 131.00003922651 |
| Elapsed since first star (Myr) | 14.83361904 | 14.59696550 |
| First star + 25 Myr, for reference | 141.16640941 | 141.40307372285 |

The following four values were set in each cutoff restart:

```text
IndividualStarICSupernovaRate = 0
TimeActionType[0] = 0
TimeActionTime[0] = -1
TimeActionParameter[0] = -1
```

Setting the rate alone does not cancel a pending time action. The time-action
edits remove that scheduled artificial event as well. Stellar SN feedback
remains enabled. `IndividualStarICSupernovaTime = 1e6` was left unchanged;
it does not implement the cutoff once the rate and event are disabled.

The fiducial cutoff restart initially targeted 135 Myr; its subsequent
continuation target was extended to **200 Myr**. The wrong-IMF cutoff restart
already has `StopTime = 200`. Snapshots `wrong-IMF/DD0133` through `DD0141`
from the abandoned, still-driven continuation were moved into `wrong-IMF/old`.
These archived snapshots must not be mixed into the new continuation history.

## Latest prepared/submitted fiducial continuation

Job `11243.happiness2-00` was submitted from fiducial `DD0144` at
**140.99999452301 Myr**, on node01 with **64 MPI ranks**, a **24-hour walltime**,
`StopTime = 200`, and 1 Myr outputs. Artificial driving remains disabled.
Submission script:
`/home/wispedia/ai/ufds/job_node01_64_fiducial_DD0144.pbs`.
This records the submission, not a guarantee of its current scheduler state.

## Data organization and analysis

Earlier fiducial movie snapshots were moved from the two `nonstatic-*`
directories into `runs/no-artificial-SN-11229.happiness2-00`, with symlinks
left at the old paths. However, fiducial DD0070 still links to payloads in
`nonstatic-70Myr-11215.happiness2-00/DD0070`, and DD0133 still links to payloads
in `nonstatic-restart120-11216.happiness2-00/DD0133`. Do not remove those
source directories before materializing these linked files.

Snapshot numbers differ between runs: use `InitialTime * TimeUnits` to align
outputs, not the DD number. `sfr.ipynb` shifts each run's first stellar creation
time to zero and computes a trailing 50 Myr birth-mass SFR average. The movie
compares absolute simulation time and holds the last available snapshot when
one run ends earlier. Archived `old/` outputs are excluded.
