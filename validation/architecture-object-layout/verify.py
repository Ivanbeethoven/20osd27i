"""Inspect final figure exports and render integrated manuscript pages for QA."""
from pathlib import Path
import json
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
results = []
for name in ['main', 'anonymous-preview']:
    doc = pymupdf.open(ROOT / (name + '.pdf'))
    figures = []
    for i, page in enumerate(doc):
        text = page.get_text()
        for number in [1, 2]:
            if f'Figure {number}:' in text:
                output = QA / f'{name}-figure{number}-page.png'
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(output)
                figures.append(dict(figure=number, page=i + 1, render=output.name))
    log = (ROOT / (name + '.log')).read_text(encoding='utf-8', errors='replace')
    flags = [line for line in log.splitlines() if any(
        token in line for token in ['Overfull', 'Missing character', 'undefined', 'contains only floats'])]
    results.append(dict(document=name + '.pdf', page_count=len(doc), figures=figures, log_flags=flags))
    assert not flags, flags
(QA / 'integrated-pages.json').write_text(json.dumps(results, indent=2), encoding='utf-8')

scene = json.loads((ROOT / 'validation/architecture-editable/scene.json').read_text())
(QA / 'after-scene.json').write_text(json.dumps(scene, indent=2), encoding='utf-8')
(QA / 'after-source.py').write_text(
    (ROOT / 'tools/draw_architecture_editable.py').read_text(encoding='utf-8'), encoding='utf-8')
pdf = pymupdf.open(ROOT / 'figures/system-architecture-editable.pdf')
assert (scene['width_pt'], scene['height_pt']) == (240, 258)
assert min(item['size_pt'] for item in scene['text']) >= 7
assert len(pdf[0].get_images()) == 0
reference = next(item for item in scene['edges'] if item['id'] == 'record-bytes')
assert reference['points'] == [[93, 220], [93, 230]]
checks = dict(canvas_pt=[240, 258], minimum_body_pt=7.0,
              live_labels=len(scene['text']), raster_images=0,
              reference_arrow=reference,
              object_geometry='two full B spans plus short tail; not raw-MiB scale',
              shard_geometry='q within one shard; d/p counts unspecified')
(QA / 'export-check.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps(dict(integrated=results, export=checks), indent=2))
