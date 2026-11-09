#!/usr/bin/env python3
"""Render one isolated Enzo history as side-by-side z and x density projections.

Repeat --run-dir in chronological restart order to splice histories by physical
simulation time. Archived subdirectories are excluded by the default DD???? glob.
Use --preview for the first/middle/last frames, or --dry-run to list frames.

Example:
  mpirun -np 12 python movie-isolated-1x2.py --parallel \
      --run-dir runs/run3-fiducial --output movie-run3-1x2
  ffmpeg -framerate 10 -i movie-run3-1x2/frame_%06d.png \
      -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' \
      -c:v libx264 -pix_fmt yuv420p -crf 18 movie-run3-1x2/movie.mp4
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import re

# Set caches before importing yt/matplotlib; each MPI process has its own cache.
os.environ.setdefault('MPLCONFIGDIR', f'/tmp/isolated-mpl-{os.getuid()}-{os.getpid()}')
os.environ.setdefault('XDG_CACHE_HOME', f'/tmp/isolated-cache-{os.getuid()}-{os.getpid()}')

SECONDS_PER_MYR = 31557600000000.0
FIELD = ('gas', 'density')
TIME_TOLERANCE = 1e-4  # Myr: merge roundoff-separated final/scheduled dumps.


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--run-dir', type=Path, action='append', required=True,
                   help='repeat in restart order; later directories supersede earlier history')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--label', default='Fiducial', help='run label shown above each panel')
    p.add_argument('--outputs', default='DD????', help='comma-separated directory globs')
    p.add_argument('--resolution', type=int, default=800)
    p.add_argument('--width', type=float, default=2.0, help='panel width in physical kpc')
    p.add_argument('--particle-depth', type=float, default=3.0, help='overlay depth in kpc')
    p.add_argument('--min-time', type=float)
    p.add_argument('--max-time', type=float)
    p.add_argument('--preview', action='store_true', help='first, middle and last frames')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--overwrite', action='store_true')
    p.add_argument('--parallel', action='store_true', help='enable yt MPI frame distribution (requires working mpi4py)')
    return p.parse_args(argv)


def snapshot_time(path):
    values = {}
    for line in path.read_text().splitlines():
        m = re.match(r'^\s*(InitialTime|TimeUnits|ComovingCoordinates)\s*=\s*(\S+)', line)
        if m:
            values[m[1]] = float(m[2])
    if values.get('ComovingCoordinates', 0) != 0:
        raise ValueError(f'Not an isolated physical-coordinate snapshot: {path}')
    return values['InitialTime'] * values['TimeUnits'] / SECONDS_PER_MYR


def dataset_records(run_dirs, outputs='DD????'):
    """Splice physical histories, not lexically sorted DD output numbers."""
    history = []
    for directory in run_dirs:
        directory = directory.resolve()
        paths = set()
        for pattern in outputs.split(','):
            for candidate in directory.glob(pattern.strip()):
                path = candidate / candidate.name if candidate.is_dir() else candidate
                if path.is_file() and Path(str(path)+'.hierarchy').is_file():
                    paths.add(path)
        if not paths:
            raise ValueError(f'No snapshots with hierarchy files in {directory}')
        branch = sorted(((snapshot_time(path), path) for path in paths),
                        key=lambda item: (item[0], str(item[1])))
        # Keep the later-written dump for effectively identical times.
        unique = []
        for record in branch:
            if unique and abs(record[0]-unique[-1][0]) <= TIME_TOLERANCE:
                unique[-1] = max(unique[-1], record, key=lambda item: str(item[1]))
            else:
                unique.append(record)
        start = unique[0][0]
        history = [record for record in history if record[0] < start-TIME_TOLERANCE]
        history.extend(unique)
    return history


def add_stellar_filters(ds):
    import numpy as np
    from yt.data_objects.particle_filters import add_particle_filter, filter_registry
    if ('all', 'particle_type') not in ds.derived_field_list:
        if sum(ds.particle_type_counts.values()) == 0:
            return False
        raise ValueError(f'Missing particle_type field in particle-bearing dataset {ds}')
    for name, types in [('isolated_live', (11, 15)), ('isolated_remnant', (12, 13))]:
        if name not in filter_registry:
            def select(pfilter, data, selected=types):
                return np.isin(data[(pfilter.filtered_type, 'particle_type')], selected)
            add_particle_filter(name, function=select, filtered_type='all', requires=['particle_type'])
        if not ds.add_particle_filter(name):
            raise RuntimeError(f'Cannot add {name} filter')
    return True


def history_frames(history):
    """Create one frame per selected saved time, without gas interpolation."""
    return [{'time_myr': t, 'columns': [
        {'time_myr': t, 'dataset': str(path), 'held': False}]
    } for t, path in history]


def merge_incremental_manifest(previous, current):
    """Validate an append-only update and return the current manifest.

    New output dumps normally extend a movie at its end.  In that case the
    existing frame records must remain an exact prefix: changing an earlier
    dataset, time, or held-state would make the existing PNG numbering
    ambiguous and requires ``--overwrite``.  Plot settings are likewise
    immutable for an incremental update.
    """
    if previous is None:
        return current
    previous_static = {key: value for key, value in previous.items() if key != 'frames'}
    current_static = {key: value for key, value in current.items() if key != 'frames'}
    if previous_static != current_static:
        raise ValueError(
            'Frame selection/settings changed; use a new output directory or --overwrite'
        )
    old_frames = previous.get('frames')
    new_frames = current.get('frames')
    if not isinstance(old_frames, list) or not isinstance(new_frames, list):
        raise ValueError('Existing frames.json has an invalid frame list; use --overwrite')
    if len(old_frames) > len(new_frames) or new_frames[:len(old_frames)] != old_frames:
        raise ValueError(
            'Earlier frame selection changed; use a new output directory or --overwrite'
        )
    return current


def stellar_mass_label(mass):
    """One-decimal scientific notation, with a mass-appropriate exponent."""
    if mass == 0:
        return r'$M_\star = 0.0\ M_\odot$'
    mantissa, exponent = f'{mass:.1e}'.split('e')
    return rf'$M_\star = {mantissa}\times 10^{{{int(exponent)}}}\ M_\odot$'


def render_frame(datasets, frame, destination, args):
    import yt
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from mpl_toolkits.axes_grid1 import AxesGrid

    figure = plt.figure(figsize=(16, 7.5))
    figure.suptitle(f'Simulation time = {frame["time_myr"]:.2f} Myr')
    grid = AxesGrid(figure, (0.07, 0.10, 0.85, 0.78), nrows_ncols=(1, 2),
                    axes_pad=(1.75, 0.95), share_all=False, label_mode='all',
                    cbar_location='right', cbar_mode='each', cbar_size='4%', cbar_pad='2%')
    plots = []
    try:
        ds = datasets[0]
        has_particles = add_stellar_filters(ds)
        for i, axis in enumerate(('z', 'x')):
            column = 0
            label = args.label
            # Full-domain, unweighted line-of-sight projection, as in vis.ipynb.
            p = yt.ProjectionPlot(ds, axis, FIELD, center=ds.domain_center,
                                  width=(args.width, 'kpc'))
            p.set_buff_size(args.resolution)
            p.set_font_size(12)
            p.set_axes_unit('kpc')
            p.set_unit(FIELD, 'g/cm**2')
            p.set_zlim(FIELD, 1e-5, 1e-2)
            if has_particles:
                for name, color in [('isolated_live', 'black'), ('isolated_remnant', 'red')]:
                    p.annotate_particles((args.particle_depth, 'kpc'), ptype=name,
                                         p_size=7, col=color, marker='o', alpha=0.9)
            held = ' (held)' if frame['columns'][column]['held'] else ''
            p.annotate_text((0.03, 0.97), f't = {ds.current_time.to_value("Myr"):.2f} Myr{held}',
                            coord_system='axis', text_args={'color': 'white', 'va': 'top',
                            'bbox': {'facecolor': 'black', 'alpha': 0.5, 'edgecolor': 'none'}})
            if i == 0:
                # Current live stellar mass across the full dataset, not birth
                # mass or remnant mass; matches the black particle population.
                mass = (float(ds.all_data()[('isolated_live', 'particle_mass')]
                              .sum().to_value('Msun')) if has_particles else 0.0)
                p.annotate_text((0.03, 0.90), stellar_mass_label(mass),
                                coord_system='axis', text_args={'color': 'white', 'va': 'top',
                                'bbox': {'facecolor': 'black', 'alpha': 0.5, 'edgecolor': 'none'}})
            panel = p.plots[FIELD]
            panel.figure, panel.axes, panel.cax = figure, grid[i].axes, grid.cbar_axes[i]
            p.render()
            grid[i].axes.set_title(f'{label} — {axis} projection')
            plots.append(p)
        handles = [Line2D([], [], color=color, marker='o', linestyle='none', label=label)
                   for color, label in [('black', 'Live stars (11, 15)'), ('red', 'Remnants (12, 13)')]]
        grid[0].axes.legend(handles=handles, loc='lower right', fontsize=8, framealpha=0.8)
        # yt may resize the shared figure while rendering each projection.
        figure.set_size_inches(16, 7.5, forward=True)
        # Avoid treating a partially written frame as complete on restart.
        temporary = destination.with_name(destination.stem+f'.{os.getpid()}.tmp.png')
        figure.savefig(temporary, dpi=100)
        temporary.replace(destination)
    finally:
        plt.close(figure)
        plots.clear()
        gc.collect()


def main(argv=None):
    args = parse_args(argv)
    if args.resolution < 16 or not 0 < args.width < float('inf') or not 0 < args.particle_depth < float('inf'):
        raise ValueError('Require resolution >=16 and positive finite width/depth')
    histories = [dataset_records(args.run_dir, args.outputs)]
    records = [frame for frame in history_frames(histories[0])
               if (args.min_time is None or frame['time_myr'] >= args.min_time)
               and (args.max_time is None or frame['time_myr'] <= args.max_time)]
    if not records:
        raise ValueError('No snapshots in the requested time range')
    if args.preview:
        records = [records[i] for i in sorted({0, len(records)//2, len(records)-1})]
    manifest = {'width_kpc': args.width, 'particle_depth_kpc': args.particle_depth,
                'resolution': args.resolution, 'axes': ['z', 'x'], 'layout': [1, 2],
                'run_label': args.label,
                'stellar_mass': 'current live types 11,15; full domain; Msun',
                'frames': [dict(frame, frame=f'frame_{i:06d}.png')
                           for i, frame in enumerate(records)]}
    for frame in manifest['frames']:
        print(f'{frame["frame"]}: {frame["time_myr"]:.8f} Myr {frame["columns"]}', flush=True)
    if args.dry_run:
        return 0
    import yt
    if args.parallel:
        yt.enable_parallelism()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output/'frames.json'
    previous_manifest = None
    if manifest_path.exists() and not args.overwrite:
        previous_manifest = json.loads(manifest_path.read_text())
        merge_incremental_manifest(previous_manifest, manifest)
    if yt.is_root():
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    for frame in yt.parallel_objects(manifest['frames'], njobs=-1):
        destination = output/frame['frame']
        if destination.exists() and not args.overwrite:
            continue
        datasets = [None if column is None else yt.load(column['dataset'])
                    for column in frame['columns']]
        render_frame(datasets, frame, destination, args)
        del datasets
        gc.collect()
        print(f'Saved {destination}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
