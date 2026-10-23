#!/usr/bin/env python3
"""A compact, claim-led workload figure from the complete measured capture.

The old detailed profile and time figures are preserved. This rendering uses
all events; size bins and busiest-window aggregation are explicitly documented.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
GROUPS = ('Core', 'Exploratory')
COLORS = {'Core': '#236DA0', 'Exploratory': '#C46A2C'}
MARKERS = {'Core': 'o', 'Exploratory': 'D'}
TASKS = [
    ('django__django-10097', 'Django'),
    ('matplotlib__matplotlib-13989', 'Matplotlib'),
    ('pallets__flask-5014', 'Flask'),
    ('psf__requests-1142', 'Requests'),
    ('sphinx-doc__sphinx-10323', 'Sphinx'),
    ('astropy__astropy-13398', 'Astropy'),
    ('pytest-dev__pytest-5787', 'Pytest'),
    ('sympy__sympy-12489', 'SymPy'),
]


def csv_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=HERE / 'derived')
    parser.add_argument('--output', type=Path, default=HERE.parents[1] / 'figures/agent-fuse')
    parser.add_argument('--qa-output', type=Path, default=HERE / 'qa/combined')
    parser.add_argument('--qa-scripts', type=Path, default=Path.home() / '.codex/skills/nature-figure/scripts')
    args = parser.parse_args()
    sys.path.insert(0, str(args.qa_scripts))
    from audit_panel_alignment import require_matplotlib_panel_alignment

    summary = json.loads((args.data / 'summary.json').read_text())
    size_rows = csv_rows(args.data / 'request-sizes.csv')
    time_rows = csv_rows(args.data / 'timeseries-1s.csv')
    task_rows = {r['task']: r for r in csv_rows(args.data / 'tasks.csv')}
    metadata = set(summary['metadata6_methods'])
    assert set(task_rows) == {task for task, _ in TASKS}
    assert sum(int(row['events']) for row in task_rows.values()) == summary['total_events'] == 1138884
    args.output.mkdir(exist_ok=True, parents=True)
    args.qa_output.mkdir(exist_ok=True, parents=True)

    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans'],
        'font.size': 9.5, 'axes.labelsize': 9.5, 'axes.titlesize': 10.5,
        'xtick.labelsize': 9.5, 'ytick.labelsize': 9.5, 'legend.fontsize': 9.5,
        'legend.frameon': False, 'axes.spines.top': False,
        'axes.spines.right': False, 'axes.linewidth': 0.65,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'hatch.linewidth': 0.5, 'savefig.dpi': 300,
    })
    # Actual manuscript width: no tight bounding box or placement downscaling.
    # All three final plot areas are 102 x 112 pt; labels use the intervening gutters.
    fig = plt.figure(figsize=(7, 2.75))
    width, height = fig.get_size_inches() * 72
    lefts = (55, 222, 389)
    axes = [fig.add_axes([left / width, 45 / height, 102 / width, 112 / height])
            for left in lefts]
    titles = ('a  Request mix', 'b  Sizes (KiB)', 'c  Bursty tasks')
    for ax, left, title in zip(axes, lefts, titles):
        ax.tick_params(axis='both', length=2.5, pad=2)
        ax.set_axisbelow(True)
        ax.grid(axis='x', color='#DDDDDD', linewidth=0.45)
        fig.text(left / width, 177 / height, title, weight='bold', fontsize=10.5)
    fig.legend(
        handles=[Line2D([], [], color=COLORS[g], marker=MARKERS[g], linestyle='None',
                        markersize=5, label=f'{g} ({5 if g == "Core" else 3} tasks)')
                 for g in GROUPS],
        loc='upper center', bbox_to_anchor=(0.53, 1.0), ncol=2,
        handletextpad=0.35, columnspacing=1.5, borderaxespad=0,
    )

    # a: A complete, mutually exclusive partition; metadata is the stated subset.
    ax = axes[0]
    mix_records = []
    for index, group in enumerate(GROUPS):
        record = summary['groups'][group]
        methods = record['methods']
        counts = [sum(methods.get(m, 0) for m in metadata), methods['read'], methods['write']]
        counts.append(record['events'] - sum(counts))
        errors = [sum(record['method_status'].get(m, {}).get('error', 0) for m in metadata), 0, 0]
        errors.append(record['statuses']['error'] - sum(errors))
        assert sum(counts) == record['events'] and sum(errors) == record['statuses']['error']
        assert all(0 <= error <= count for error, count in zip(errors, counts))
        total_pct = np.asarray(counts) / record['events'] * 100
        error_pct = np.asarray(errors) / record['events'] * 100
        ypos = np.arange(4) + (index - 0.5) * 0.31
        ax.barh(ypos, total_pct, height=0.27, color=COLORS[group], linewidth=0)
        ax.barh(ypos, error_pct, left=total_pct - error_pct, height=0.27,
                facecolor='white', edgecolor=COLORS[group], linewidth=0.7)
        for category, count, error in zip(('Metadata', 'Read', 'Write', 'Other'), counts, errors):
            mix_records.append({'group': group, 'category': category, 'count': count,
                                'error': error, 'denominator': record['events']})
    ax.set_yticks(range(4), ['Metadata', 'Read', 'Write', 'Other'])
    ax.set_ylim(3.55, -0.55)
    ax.set_xlim(0, 70)
    ax.set_xticks([0, 30, 60])
    ax.set_xlabel('All calls (%)', labelpad=3)
    ax.legend(handles=[Patch(facecolor='white', edgecolor='#555555', label='Error')],
              loc='lower left', bbox_to_anchor=(-0.04, 1.005), borderaxespad=0,
              handlelength=0.75, handletextpad=0.4)

    # b: Full histograms aggregated at the exact boundaries already used in text.
    # Hue remains the group encoding; fill intensity identifies the size interval.
    ax = axes[1]
    size_records = []
    for method_index, method in enumerate(('read', 'write')):
        for group_index, group in enumerate(GROUPS):
            source = [(int(r['request_bytes']), int(r['count'])) for r in size_rows
                      if r['scope'] == group and r['method'] == method]
            bins = [sum(count for size, count in source if size <= 4096),
                    sum(count for size, count in source if 4096 < size <= 65536),
                    sum(count for size, count in source if size > 65536)]
            expected = summary['groups'][group]['size'][method]['n']
            assert sum(bins) == expected == sum(count for size, count in source)
            assert min(size for size, _ in source) > 0
            cumulative = 0
            ypos = method_index * 1.9 + group_index * 0.48
            for bin_index, (count, alpha) in enumerate(zip(bins, (1.0, 0.30, 0.0))):
                pct = 100 * count / expected
                fill = matplotlib.colors.to_rgba(COLORS[group], alpha)
                ax.barh(ypos, pct, left=cumulative, height=0.34, color=fill,
                        edgecolor=COLORS[group], linewidth=0.6)
                cumulative += pct
                size_records.append({'group': group, 'method': method, 'bin': bin_index,
                                     'count': count, 'denominator': expected})
            assert abs(cumulative - 100) < 1e-9
    ax.set_yticks([0.24, 2.14], ['Read', 'Write'])
    ax.set_ylim(3.05, -0.65)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    ax.set_xlabel('Read/write calls (%)', labelpad=3)
    # This compact interval key is shared by all four bars.
    keys = [Patch(facecolor='#666666', edgecolor='#666666', label='≤4'),
            Patch(facecolor='#DDDDDD', edgecolor='#666666', label='4–64'),
            Patch(facecolor='white', edgecolor='#666666', label='>64')]
    ax.legend(handles=keys, loc='lower center', bbox_to_anchor=(0.50, 1.005), ncol=3,
              borderaxespad=0, handlelength=0.65, handletextpad=0.2, columnspacing=0.45,
              fontsize=9.5)

    # c: Recompute the burst statistic from every one-second window, including zeros.
    # Tasks are not pooled: every measured task receives one visible marker.
    ax = axes[2]
    burst_records = []
    for index, (task, label) in enumerate(TASKS):
        row = task_rows[task]
        counts = [int(r['calls']) for r in time_rows if r['task'] == task]
        assert sum(counts) == int(row['events'])
        selected = math.ceil(0.1 * len(counts))
        burst = 100 * sum(sorted(counts, reverse=True)[:selected]) / sum(counts)
        assert abs(burst - float(row['top_decile_bin_call_pct'])) < 1e-9
        group = row['group']
        ax.plot([0, burst], [index, index], color='#BBBBBB', linewidth=0.8, zorder=1)
        ax.plot(burst, index, marker=MARKERS[group], color=COLORS[group],
                markersize=5, linestyle='None', zorder=2)
        burst_records.append({'task': task, 'group': group, 'windows': len(counts),
                              'selected_windows': selected, 'calls': sum(counts), 'burst_pct': burst})
    ax.set_yticks(range(8), [label for _, label in TASKS])
    ax.set_ylim(7.65, -0.65)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    ax.set_xlabel('Calls in busiest\n10% of windows (%)', labelpad=3, linespacing=1.15)

    fig.canvas.draw()
    require_matplotlib_panel_alignment(
        fig, json_out=args.qa_output / 'fuse-combined-compact.alignment.json',
        panel_ids=['a', 'b', 'c'], row_groups=[['a', 'b', 'c']],
        tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True,
    )
    stem = args.output / 'fuse-combined-compact'
    fig.savefig(stem.with_suffix('.pdf'))
    fig.savefig(stem.with_suffix('.svg'))
    fig.savefig(stem.with_suffix('.png'), dpi=300)
    plt.close(fig)
    (args.qa_output / 'plotted-data.json').write_text(json.dumps({
        'all_events': summary['total_events'], 'mix': mix_records,
        'sizes': size_records, 'bursts': burst_records,
        'bin_intervals_bytes': ['(0,4096]', '(4096,65536]', '(65536,infinity)'],
        'exclusions': [], 'task_observations_per_task': 1,
    }, indent=2) + '\n')
    print(f'Rendered {stem}; all 1,138,884 events and all eight tasks preserved.')


if __name__ == '__main__':
    main()
