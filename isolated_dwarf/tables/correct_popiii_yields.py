#!/usr/bin/env python3
"""Build the source-faithful HW2010 PopIII CCSN correction; preserve other data."""
import argparse
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys

import h5py
import numpy as np

BASE_SHA256 = "31b72501574c6488eb65a49dbeb6d6a4b885192a43603a92a5d452c795801189"
SOURCE_SHA256 = "9d4530cce575bef0ca1fbf654ccff9d8a46caa892d1b9f5df74aa3a4808468e9"
READER_REVISION = "21c59a9cc5ace231296ed7fd141b7d35e40e0962"
SOURCE_URL = "https://2sn.org/starfit/data/znuc.S4.star.deciso.y.stardb.gz"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-db", type=Path, required=True)
    parser.add_argument("--starfit-root", type=Path, required=True)
    parser.add_argument("--base", type=Path,
                        default=directory / "IndividualStarYields-Mix0.1.h5")
    parser.add_argument("--output", type=Path, default=directory /
                        "IndividualStarYields-Mix0.1-PopIIICorrected.h5")
    args = parser.parse_args()
    require(args.base.resolve() != args.output.resolve(), "Never overwrite the base table")
    require(not args.output.exists(), "Output already exists; choose a new output path")
    require(sha256(args.base) == BASE_SHA256, "Unexpected base table SHA256")
    require(sha256(args.source_db) == SOURCE_SHA256, "Unexpected source database SHA256")
    revision = subprocess.check_output(
        ["git", "-C", str(args.starfit_root), "rev-parse", "HEAD"], text=True).strip()
    require(revision == READER_REVISION, "Unexpected StarFit reader revision")
    subprocess.run(["git", "-C", str(args.starfit_root), "diff", "--exit-code",
                    "HEAD", "--", "src/starfit/autils"], check=True,
                   stdout=subprocess.DEVNULL)
    sys.path.insert(0, str(args.starfit_root / "src/starfit"))
    from autils import isotope, stardb

    # Compatibility shim for an obsolete keyword in this pinned reader.
    # Construct the same isotope using its atomic and mass numbers.
    stardb.ufunc_isotope_from_ZA = np.frompyfunc(
        lambda z, a: isotope.ion(Z=int(z), A=int(a)), 2, 1)
    with contextlib.redirect_stdout(io.StringIO()):
        source = stardb.StarDB(str(args.source_db))
    require((source.abundance_type, source.abundance_class,
             source.abundance_unit, source.abundance_total,
             source.abundance_data) == (1, 2, 4, 1, 0),
            "Expected stable-isotope molar abundances of all ejecta")
    select = (np.isclose(source.fielddata["energy"], 1.2, rtol=0, atol=1e-10)
              & np.isclose(source.fielddata["mixing"], 0.1, rtol=0, atol=1e-10))
    ix = np.flatnonzero(select)
    ix = ix[np.argsort(source.fielddata["mass"][ix])]
    birth = source.fielddata["mass"][ix]
    remnant = source.fielddata["remnant"][ix]
    ejecta = birth - remnant
    atomic = np.array([ion.Z for ion in source.ions])
    mass_number = np.array([ion.A for ion in source.ions])
    isotope_mass = source.data[ix] * mass_number * ejecta[:, None]
    require(len(ix) == 120, "Expected 120 HW2010 CCSN models")
    require(np.allclose(isotope_mass.sum(axis=1), ejecta, rtol=2e-9, atol=0),
            "Source isotope masses do not close the source ejecta budget")

    metadata = {
        "CorrectionVersion": "PopIII-CCSN-HW2010-v1",
        "CorrectionDate": "2026-11-06",
        "CorrectionScope": "Only PopIII CCSN rows, 10-100 Msun; other data preserved",
        "CorrectionBaseSHA256": BASE_SHA256,
        "CorrectionSourceURL": SOURCE_URL,
        "CorrectionSourceSHA256": SOURCE_SHA256,
        "CorrectionReaderRevision": revision,
        "CorrectionModel": "HW2010; S4 piston; 1.2 Bethe; mixing=0.1 He core fraction",
        "CorrectionConversion": "element mass=sum(isotope molar abundance*A)*(M-remnant)",
        "CorrectionTotal": "Mtot=M-remnant; Metal_Mtot=sum(elements with Z>2)",
        "CorrectionMissingStableSpecies": "Tc and Pm set to zero: absent from source stable set",
        "CorrectionGeneratorSHA256": sha256(Path(__file__)),
    }
    with h5py.File(args.base, "r") as base:
        group = base["PopIII"]
        target = group["yields"][:]
        rows = np.flatnonzero((group["M"][:] >= 10) & (group["M"][:] <= 100))
        numbers = group["atomic_numbers"][:]
        require(np.array_equal(numbers[:2], [-1, 0]), "Unexpected total column layout")
        require(np.array_equal(numbers[2:], np.arange(1, 84)), "Expected H through Bi")
        require(len(rows) == 120 and target.shape == (134, 1, 85),
                "Unexpected PopIII table dimensions")
        require(np.allclose(group["M"][:][rows], birth, rtol=1e-6, atol=0),
                "Source and target mass axes differ")
        elements = np.column_stack([
            isotope_mass[:, atomic == z].sum(axis=1) for z in numbers[2:]])
        require(np.allclose(elements.sum(axis=1), ejecta, rtol=2e-9, atol=0),
                "Source ejecta outside target H-Bi element range")
        corrected = target.copy()
        corrected[rows, 0, 0] = ejecta
        corrected[rows, 0, 1] = elements[:, numbers[2:] > 2].sum(axis=1)
        corrected[rows, 0, 2:] = elements

    # Build a new file with the same schema and storage types as the base.
    shutil.copyfile(args.base, args.output)
    with h5py.File(args.output, "r+") as file:
        file["PopIII/yields"][:] = corrected
        for key, value in metadata.items():
            file["PopIII"].attrs[key] = value

    closure = {}
    preserved = []
    with h5py.File(args.base, "r") as base, h5py.File(args.output, "r") as file:
        require(list(base) == list(file), "Group structure changed")

        def check_preserved(name, obj):
            new = file[name]
            for key, value in obj.attrs.items():
                require(np.array_equal(value, new.attrs[key]), f"Changed original attr: {name}/{key}")
            if isinstance(obj, h5py.Dataset):
                require(obj.shape == new.shape and obj.dtype == new.dtype,
                        f"Changed dataset schema: {name}")
                if name != "PopIII/yields":
                    require(np.array_equal(obj[:], new[:]), f"Changed preserved data: {name}")
                    preserved.append(name)
        base.visititems(check_preserved)
        require(dict(base.attrs) == dict(file.attrs), "Changed original root attributes")
        require(np.array_equal(base["PopIII/yields"][:][120:],
                               file["PopIII/yields"][:][120:]), "PISN yields changed")
        for name, group in file.items():
            values = group["yields"][:].astype(float)
            numbers = group["atomic_numbers"][:]
            total = values[..., numbers == -1][..., 0]
            metals = values[..., numbers == 0][..., 0]
            require(np.isfinite(values).all() and (values >= 0).all(),
                    f"Invalid yields in {name}")
            require(np.allclose(total, values[..., numbers > 0].sum(axis=-1),
                                rtol=1e-6, atol=1e-12), f"Total mass mismatch in {name}")
            require(np.allclose(metals, values[..., numbers > 2].sum(axis=-1),
                                rtol=1e-6, atol=1e-12), f"Metal mass mismatch in {name}")
            closure[name] = {"rows": int(total.size), "mass_and_metals_close": True}
        stored = file["PopIII/yields"][:120, 0, :].astype(float)
        require(np.allclose(stored[:, 0], ejecta, rtol=1e-6),
                "Stored total differs from source")
        require(np.allclose(stored[:, 2:], elements, rtol=1e-6, atol=1e-30),
                "Stored elements differ from source")

    require(sha256(args.base) == BASE_SHA256, "Base table changed")
    report = {
        **metadata, "output": args.output.name, "output_sha256": sha256(args.output),
        "corrected_rows": 120, "preserved_PISN_rows": 14,
        "preserved_datasets": preserved, "group_validation": closure,
        "max_source_isotope_budget_relative_error": float(np.max(abs(
            isotope_mass.sum(axis=1) / ejecta - 1))),
        "validation_scope": "HDF5 schema, source yields, unchanged data, and mass budgets; no full grid run",
    }
    args.output.with_suffix(".validation.json").write_text(json.dumps(report, indent=2) + "\n")
    with args.output.with_suffix(".mass-budget.csv").open("w") as file:
        writer = csv.writer(file)
        writer.writerow(["birth_mass", "source_remnant_mass", "source_ejecta",
                         "old_Mtot", "old_element_sum", "new_Mtot", "new_element_sum"])
        writer.writerows(zip(birth, remnant, ejecta, target[:120, 0, 0],
                             target[:120, 0, 2:].astype(float).sum(axis=1),
                             stored[:, 0], stored[:, 2:].sum(axis=1)))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
