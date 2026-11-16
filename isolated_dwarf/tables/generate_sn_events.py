#!/usr/bin/env python3
"""Emit the seeded fiducial artificial-SN event list to standard output.

Geometry follows Enzo CheckForTimeAction.C, IndividualStarICSupernovaMethod=1:
theta=2*pi*U, r=R*sqrt(U), z=Z*(2*U-1), in that draw order. Python's
Random(42) reproduces the original archived 43 rows exactly; it is not
Enzo's private IC-SN RNG or a reconstruction of historical event positions.
"""
import argparse
import math
import random
import sys


def generate(end_myr):
    interval_myr = 2.5
    count = math.floor(end_myr / interval_myr)
    lines = [
        "# Fiducial artificial-SN driving: new seeded positions, fixed-rate event times.",
        "# Source: runs/run3-fiducial/input.enzo (0.4 events/Myr; R=250 pc, |z|<=100 pc).",
        "# Extended beyond the original DD0108 cutoff at code time 108.00004020963.",
        f"# {count} events, 2.5 through {count * interval_myr:g} Myr; no artificial events after table exhaustion.",
        "# Simulation target is 500 Myr; the original startup target was 120 Myr.",
        "# This fixed table does not automatically stop 25 Myr after a new run's first star.",
        "# Times use Enzo Myr_s=3.1556952e13 s; positions are absolute code coordinates.",
        "# This is a new reproducible realization, not recovered historical SN positions.",
        "# seed=42 time_sampling=periodic rate_per_year=3.9999999999999998e-07",
        "# box_pc=59000 radius_pc=250 half_height_pc=100",
        "# time_Myr x_code y_code z_code",
    ]
    rng = random.Random(42)
    for index in range(1, count + 1):
        theta = rng.random() * 2.0 * math.pi
        radius = math.sqrt(rng.random()) * 250.0 / 59000.0
        z = (2.0 * rng.random() - 1.0) * 100.0 / 59000.0
        values = (index * interval_myr,
                  0.5 + radius * math.cos(theta),
                  0.5 + radius * math.sin(theta), 0.5 + z)
        lines.append(" ".join(format(value, ".17g") for value in values))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--end-myr", type=float, default=250.0,
                        help="Include events up to this time (default: 250 Myr).")
    args = parser.parse_args()
    if not math.isfinite(args.end_myr) or args.end_myr < 2.5:
        parser.error("--end-myr must be finite and at least 2.5")
    sys.stdout.write(generate(args.end_myr))
