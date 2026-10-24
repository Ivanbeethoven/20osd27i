"""Record the final text/geometry budget and render integrated Figure 2 pages."""
import json
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
before = json.loads((QA / 'before-scene.json').read_text(encoding='utf-8'))
after = json.loads((ROOT / 'validation/architecture-editable/scene.json').read_text(encoding='utf-8'))
(QA / 'after-scene.json').write_text(json.dumps(after, indent=2), encoding='utf-8')
(QA / 'after-source.py').write_text(
    (ROOT / 'tools/draw_architecture_editable.py').read_text(encoding='utf-8'), encoding='utf-8')

def counts(scene):
    labels = [item['text'] for item in scene['text']]
    return dict(labels=len(labels), characters=sum(len(item) for item in labels),
                whitespace_tokens=sum(len(item.split()) for item in labels))

old, new = counts(before), counts(after)
assert new['labels'] <= old['labels']
assert new['characters'] <= old['characters']
assert new['whitespace_tokens'] <= old['whitespace_tokens']
assert min(item['size_pt'] for item in after['text']) >= 7
assert (after['width_pt'], after['height_pt']) == (240, 258)
old_svg = (QA / 'before.svg').read_text(encoding='utf-8')
new_svg = (ROOT / 'figures/system-architecture-editable.svg').read_text(encoding='utf-8')
first_panel_unchanged = old_svg.split('<g id="metadata-choice"')[0] == new_svg.split('<g id="metadata-choice"')[0]
assert first_panel_unchanged
pdf = pymupdf.open(ROOT / 'figures/system-architecture-editable.pdf')
assert not pdf[0].get_images()
checks = dict(before=old, after=new, canvas_pt=[240, 258], minimum_body_pt=7,
              raster_images=0, first_panel_and_parallel_connections_unchanged=first_panel_unchanged,
              b_choices='equal object extents; 10+10+10+5 versus 20+15 drawing units',
              g_policy='fixed volume geometry; no per-file g',
              layout_policy='optional eligible-object choices, not automatic per-file selection')
(QA / 'export-check.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')

records = []
for name in ['main', 'anonymous-preview']:
    doc = pymupdf.open(ROOT / (name + '.pdf'))
    figures = []
    for i, page in enumerate(doc):
        if 'Figure 2:' in page.get_text():
            output = QA / f'{name}-figure2-page.png'
            page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(output)
            figures.append(dict(page=i + 1, render=output.name))
    log = (ROOT / (name + '.log')).read_text(encoding='utf-8', errors='replace')
    flags = [line for line in log.splitlines() if any(token in line for token in
             ['Overfull', 'Missing character', 'undefined', 'contains only floats'])]
    assert not flags, flags
    records.append(dict(document=name + '.pdf', page_count=len(doc), figure2=figures, log_flags=flags))
(QA / 'integrated-pages.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
print(json.dumps(dict(export=checks, integrated=records), indent=2))
