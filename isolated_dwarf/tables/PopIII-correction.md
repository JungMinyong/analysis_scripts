# PopIII CCSN yield correction

Created 2026-11-06 as `IndividualStarYields-Mix0.1-PopIIICorrected.h5`.
The original `IndividualStarYields-Mix0.1.h5` is preserved.

## What changed

Only the 120 PopIII CCSN yield rows from 10 through 100 solar masses changed.
Their source is the author's HW2010 stable-isotope database:

- [Source database](https://2sn.org/starfit/data/znuc.S4.star.deciso.y.stardb.gz)
- [Author's description of the datasets](https://2sn.org/starfit/)
- Model: S4 piston, 1.2 Bethe, mixing 0.1 of the helium-core mass.
- Download SHA256: `9d4530cce575bef0ca1fbf654ccff9d8a46caa892d1b9f5df74aa3a4808468e9`.

The old total-ejecta column contained progenitor mass. Its elemental yields
also matched conversion of elemental molar abundances using natural atomic
weights, introducing a smaller isotope-mixture discrepancy. The correction uses:

```text
Mtot = source progenitor mass − source remnant mass
element ejecta = Mtot × Σ(source isotope molar abundance × isotope mass number A)
Metal_Mtot = sum of element ejecta with atomic number > 2
```

Tc and Pm are zero in the corrected CCSN rows because they are absent from the
source's stable-isotope set. Their previous yields were at most approximately
`4.6e-14` and `5.2e-15` solar masses.

For a 70 solar-mass progenitor, total ejecta changes from 70 to 34.648 solar
masses, and the elemental sum changes from 34.805752 to approximately 34.648.
The source remnant mass is 35.352 solar masses.

The 14 PISN rows, AGB, SN, Wind, and SN+Wind datasets are unchanged. All mass
and metallicity axes, atomic-number mappings, dataset types, and shapes are
unchanged. Added `Correction*` attributes on the PopIII group record provenance;
Enzo does not need to interpret these attributes.

## How Enzo reads it

For an EnzoAeos-v2 executable built with `CONFIG_NEWYIELDTABLES = yes`, select
the file through the runtime parameter:

```ini
StellarYieldsFilename = IndividualStarYields-Mix0.1-PopIIICorrected.h5
```

Place or link the table in the launch working directory, or supply its absolute
path. Changing this filename requires no recompile. Existing run parameter
files in this repository have not been switched.

`ReadParameterFile.C` parses `StellarYieldsFilename`.
`StellarYields_Initialize.C::InitializeStellarYields` opens that HDF5 file
and loads the SN, Wind, PopIII, and AGB/Massive_star groups. Stellar-yield
initialization also depends on the individual-star/yield configuration;
the usual Aeos setup enables `IndividualStarFollowStellarYields = 1` and
`MultiMetals = 2`.

Each group provides `M`, `Z`, `atomic_numbers`, and `yields`. The first two
yield columns have atomic-number markers `-1` (total ejecta) and `0` (total
metals); subsequent columns contain individual element masses.
`StellarYieldsAtomicNumbers` selects which species Enzo tracks.
PopIII interpolation uses the birth mass; feedback obtains total ejecta and
element yields separately. Hence correcting the file fixes these values
without a change to the interpolation or feedback code.

## Validation

The rebuild verifies the input hashes and reader revision, the source isotope
mass budget, every group's total/element and metal/element closure, and that
all other datasets and the PISN rows are preserved. Source isotope mass
fractions close within `1.50e-9`; stored float32 yields close within `1e-6`
relative tolerance. All yield entries are finite and nonnegative.

The sidecars contain detailed results:

- `IndividualStarYields-Mix0.1-PopIIICorrected.validation.json`
- `IndividualStarYields-Mix0.1-PopIIICorrected.mass-budget.csv`

The EnzoAeos-v2 interpolation regression was also run against all five groups
of this file under Valgrind. This verifies lookup boundaries; no full grid
feedback event or galaxy simulation was run for this table change.

Verify the distributed HDF5 file with `sha256sum -c SHA256SUMS`.

## Rebuild

`correct_popiii_yields.py` reads the base HDF5 and the author database and writes
a new HDF5 plus the two validation sidecars. It refuses to overwrite the base
or an existing output. It requires NumPy, h5py, and the dependencies of the
pinned StarFit reader (including SciPy).

The source download and reader used here are cached outside this repository:

```bash
python3 correct_popiii_yields.py \
  --source-db /home/wispedia/AA/isolated/physics-audit/popiii-evidence/source/znuc.S4.star.deciso.y.stardb.gz \
  --starfit-root /home/wispedia/AA/isolated/physics-audit/popiii-evidence/source/starfit \
  --output /tmp/IndividualStarYields-Mix0.1-PopIIICorrected.h5
```

Run from this directory, choosing a fresh output path. For another machine,
download the linked database and clone
`https://github.com/conradtchan/starfit.git`, checking out revision
`21c59a9cc5ace231296ed7fd141b7d35e40e0962`, then supply those local paths.
The script applies an in-memory compatibility shim for an obsolete isotope
constructor keyword in that reader; it does not edit the reader or source data.
Numerical contents and provenance are reproducible; an HDF5 rebuild can have a
different binary hash because HDF5 can record object modification times.
