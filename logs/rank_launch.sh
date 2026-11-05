#!/bin/bash
set -eu

# Rank source: Intel MPI / PMIx / OpenMPI / Slurm.
RANK="${PMI_RANK:-${PMIX_RANK:-${OMPI_COMM_WORLD_RANK:-${SLURM_PROCID:-0}}}}"

ENZO_RANKS="${ENZO_PROCESSOR_NUM:?ENZO_PROCESSOR_NUM is required}"
ABYSS_OMP_THREADS="${ABYSS_OMP_THREADS:-16}"
TOTAL_CORES="${TOTAL_CORES:-56}"

if [ "$RANK" -lt "$ENZO_RANKS" ]; then
    CPULIST="$RANK"
    export OMP_NUM_THREADS="${ENZO_OMP_THREADS:-1}"
else
    ABYSS_INDEX=$((RANK - ENZO_RANKS))
    START_CORE=$((ENZO_RANKS + ABYSS_INDEX * ABYSS_OMP_THREADS))
    END_CORE=$((START_CORE + ABYSS_OMP_THREADS - 1))
    if [ "$END_CORE" -ge "$TOTAL_CORES" ]; then
        echo "Rank $RANK CPU binding exceeds TOTAL_CORES=$TOTAL_CORES" >&2
        exit 2
    fi
    CPULIST="${START_CORE}-${END_CORE}"
    export OMP_NUM_THREADS="$ABYSS_OMP_THREADS"
fi

exec taskset -c "$CPULIST" "$@"
