"""Editable, final-size BrewFS architecture: shared base as the visual anchor.

All artwork is original. The two file maps and eligible 2+2 layout are
illustrations, not workload observations. See the companion brief/caption.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
import pymupdf
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures/system-architecture-shared'
QA = ROOT / 'validation/architecture-shared'
W, H = 504, 230
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
INK, EDGE = '#16232B', '#53636C'
BLUE, PALE = '#247B9A', '#E4F1F5'
WARM, WARM_EDGE = '#FAE3BF', '#A76C22'
GRAY = '#F0F2F3'


def main():
    rl_config.useA85 = 0
    for name, file in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf')]:
        pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
    svg = ET.Element(f'{{{NS}}}svg', width=f'{W}pt', height=f'{H}pt',
                     viewBox=f'0 0 {W} {H}')
    texts, nodes, edges = [], {}, []

    def el(parent, kind, **attrs):
        return ET.SubElement(parent, f'{{{NS}}}{kind}',
                             {k.replace('_', '-'): str(v) for k, v in attrs.items()})

    def group(ident):
        return el(svg, 'g', id=ident)

    def text(p, x, y, label, size=8, anchor='middle', bold=False):
        font = 'Arial-Bold' if bold else 'Arial'
        width = pdfmetrics.stringWidth(label, font, size)
        left = x if anchor == 'start' else x-width if anchor == 'end' else x-width/2
        assert 0 <= left and left+width <= W, (label, left, width)
        t = el(p, 'text', x=x, y=y, font_family='Arial', font_size=size,
               text_anchor=anchor, font_weight='bold' if bold else 'normal', fill=INK)
        t.text = label
        texts.append(dict(text=label, size_pt=size, bbox=[left, y-size, width, size]))

    def line(p, points, color=EDGE, width=.7, dashed=False):
        attrs = dict(points=' '.join(f'{x},{y}' for x,y in points), fill='none',
                     stroke=color, stroke_width=width, stroke_linejoin='round')
        if dashed: attrs['stroke_dasharray'] = '3 2'
        el(p, 'polyline', **attrs)

    def box(ident, x, y, w, h, fill='white', stroke=EDGE, width=.7, rounded=0):
        p = group(ident)
        attrs = dict(x=x, y=y, width=w, height=h, fill=fill,
                     stroke=stroke, stroke_width=width)
        if rounded: attrs.update(rx=rounded, ry=rounded)
        el(p, 'rect', **attrs)
        nodes[ident] = [x,y,w,h]
        return p

    def arrow(ident, points, color=INK, dashed=False, meaning='reference'):
        p=group(ident)
        line(p, points, color, .85, dashed)
        x,y=points[-1]; a,b=points[-2]
        theta=math.atan2(y-b,x-a)
        u,v=x-3.5*math.cos(theta),y-3.5*math.sin(theta)
        el(p,'polygon', points=f'{x},{y} {u+1.5*math.sin(theta)},{v-1.5*math.cos(theta)} {u-1.5*math.sin(theta)},{v+1.5*math.cos(theta)}', fill=color)
        edges.append(dict(id=ident, points=points, meaning=meaning))

    p=group('panel-headings')
    text(p,4,11,'(a) Private views, one shared base',9,anchor='start',bold=True)
    text(p,350,11,'(b) Stored object layout',9,anchor='start',bold=True)

    # Two independently mutable views; changing positions make privacy visible.
    for ident,x,letter,spec in [
        ('i',4,'i',[('Lower A',47,PALE),('Data B′',47,WARM),('Lower C',48,PALE)]),
        ('j',174,'j',[('Lower A',47,PALE),('Lower B',47,PALE),('Data C′',48,WARM)])
    ]:
        p=box('view:'+ident,x,23,154,52,rounded=3)
        text(p,x+77,35,'Workspace '+letter,9,bold=True)
        text(p,x+77,47,'Δ'+('ᵢ' if ident=='i' else 'ⱼ')+' in mutable metadata service')
        cx=x+6; data_center=None
        for idx,(label,width,fill) in enumerate(spec):
            cell=box(f'map:{ident}:{idx}',cx,55,width,17,fill,EDGE,.6)
            text(cell,cx+width/2,66.5,label)
            if label.startswith('Data'): data_center=cx+width/2
            cx+=width
        p=box('payload:'+ident,x+37,83,80,17,WARM,WARM_EDGE,.7)
        text(p,x+77,94.5,'Private object '+letter)
        # The arrow is a Data object reference; it does not encode PUT ordering.
        arrow('data-ref:'+ident,[(data_center,72),(x+77,83)],WARM_EDGE)

    p=group('upper-read-policy')
    text(p,166,114,'Upper GET: whole-object verification, then slice')
    arrow('binding:i',[(28,75),(28,129)],BLUE,meaning='binding to the same pinned snapshot S')
    arrow('binding:j',[(304,75),(304,129)],BLUE,meaning='binding to the same pinned snapshot S')
    p=group('binding-labels')
    text(p,43,124,'pin S',anchor='start')
    text(p,289,124,'pin S',anchor='end')

    # A broad, shared substrate rather than a third identical pipeline column.
    p=box('snapshot:S',4,129,324,86,PALE,BLUE,1,rounded=3)
    text(p,166,142,'Pinned immutable snapshot S (object storage)',9,bold=True)
    p=box('snapshot:roots',14,151,92,22)
    text(p,60,165,'Manifest / roots')
    p=box('snapshot:index',119,151,75,22)
    text(p,156.5,165,'Paged name index')
    p=box('snapshot:groupmeta',207,151,111,22)
    text(p,262.5,160,'GroupMeta page')
    text(p,262.5,169.5,'name | attrs | locator')
    arrow('roots-index',[(106,162),(119,162)],meaning='representative name lookup')
    arrow('index-group',[(194,162),(207,162)],meaning='representative name lookup')
    p=group('frames-label')
    text(p,14,185,'Packed data frames',anchor='start')
    # The selected frame remains independent of the backend q subdivision.
    for n in range(4):
        p=box(f'frame:{n}',14+n*76,192,76,16,'#C5E3EC' if n==3 else 'white',BLUE,.6)
        text(p,52+n*76,203.5,'frame '+str(n))
    arrow('locator-frame',[(280,173),(280,192)],BLUE,meaning='data locator to authenticated frame')

    # Per-object layout is a separate storage contract, not a per-request optimizer.
    p=box('backend:rustfs',350,23,150,192,stroke=EDGE,rounded=3)
    text(p,425,36,'Finalized object length Lₒ',8)
    text(p,425,48,'Upper or snapshot object')
    arrow('hint-pending',[(425,52),(425,67)],dashed=True,
          meaning='hint integration pending in Entity/producer paths')
    p=group('hint-label');text(p,438,61,'h(Lₒ)',anchor='start')
    p=box('backend:admit',360,67,130,25,GRAY)
    text(p,425,77,'RustFS: admit B; choose q')
    text(p,425,88,'Small q: gated (default off)')
    arrow('admit-persist',[(425,92),(425,104)],meaning='persist admitted effective layout')
    p=box('backend:persist',360,104,130,19)
    text(p,425,116.5,'Stored: B | q | d | p')
    p=group('backend:geometry-label')
    text(p,425,136,'2+2: B = 256 KiB; gates on')
    for row,label in enumerate(('D0','D1','P0','P1')):
        y=145+12*row
        p=group('shard-label:'+label);text(p,355,y+8.5,label,anchor='start')
        for col in range(2):
            p=box(f'shard:{label}:{col}',374+58*col,y,58,10,
                  PALE if row<2 else GRAY,EDGE,.55)
            if row==0:
                text(p,403+58*col,y+8,'64 KiB',8)
    p=group('backend:read-note')
    text(p,425,203,'Reads / repair use stored layout')
    # This connection targets the backend container, not a particular parity cell.
    arrow('snapshot-backend',[(328,198),(350,198)],BLUE,
          meaning='snapshot object access uses its stored backend layout')
    p=group('footer')
    text(p,4,228,'A, B, C: same logical file ranges',anchor='start')
    text(p,182,228,'Each shard cell = q; frame ≠ q',anchor='start')
    text(p,500,228,'Dashed hint: integration pending',anchor='end')

    OUT.parent.mkdir(parents=True,exist_ok=True)
    QA.mkdir(parents=True,exist_ok=True)
    ET.indent(svg,space='  ')
    ET.ElementTree(svg).write(OUT.with_suffix('.svg'),encoding='utf-8',xml_declaration=True)
    drawing=svg2rlg(str(OUT.with_suffix('.svg')))
    renderPDF._PDFRenderer._font=renderPDF._PDFRenderer._fontName='Arial'
    renderPDF.STATE_DEFAULTS['fontName']='Arial'
    renderPDF.drawToFile(drawing,str(OUT.with_suffix('.pdf')),
                        title='BrewFS: private views over a shared immutable base')
    doc=pymupdf.open(OUT.with_suffix('.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False).save(OUT.with_suffix('.png'))
    (QA/'scene.json').write_text(json.dumps(dict(width_pt=W,height_pt=H,
        nodes=nodes,text=texts,edges=edges),indent=2),encoding='utf-8')
    print(f'Created {OUT}: {W} x {H} pt; {len(texts)} live-text labels')


if __name__=='__main__':
    main()
