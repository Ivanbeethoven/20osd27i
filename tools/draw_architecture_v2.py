#!/usr/bin/env python3
"""Editable reconstruction of the imagegen folder/page/stack concept.

SVG geometry and live text are authoritative; no raster tracing or embedding.
Scientific connections follow the architecture brief, not the generated image.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
W, H = 504, 422
INK, BLUE, AMBER, GRAY = '#182B40', '#176CAC', '#AB6814', '#647484'
PALE_BLUE, PALE_AMBER = '#EAF4FC', '#FFF5E1'


def el(parent, tag, **attrs):
    return ET.SubElement(parent, '{'+NS+'}'+tag,
                         {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/arial.ttf'))
    ap.add_argument('--bold-font', type=Path, default=Path('C:/Windows/Fonts/arialbd.ttf'))
    ap.add_argument('--output', type=Path, default=ROOT/'paper/figures/system-architecture-v2')
    args = ap.parse_args()
    pdfmetrics.registerFont(TTFont('Arial', str(args.font)))
    pdfmetrics.registerFont(TTFont('Arial-Bold', str(args.bold_font)))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold',
                                 italic='Arial', boldItalic='Arial-Bold')
    rl_config.useA85 = False
    root = ET.Element('{'+NS+'}svg', dict(width=f'{W}pt', height=f'{H}pt',
                       viewBox=f'0 0 {W} {H}', version='1.1'))
    el(root, 'title').text = 'Private workspaces over a shared immutable snapshot'
    el(root, 'desc').text = ('Editable reconstruction of an AI visual concept. '
        'Three independent clients have private upper state and local Packed readers. '
        'Mutable metadata and the producer are outside object storage. '
        'Dashed paths show pending finalized-upload hint wiring only.')
    el(root, 'rect', x=0, y=0, width=W, height=H, fill='white')
    texts, edges, nodes = [], [], {}

    def g(ident):
        return el(root, 'g', id=ident)

    def rect(p, x, y, w, h, fill='white', stroke=GRAY, radius=0, sw=.8):
        return el(p, 'rect', x=x, y=y, width=w, height=h, rx=radius,
                  fill=fill, stroke=stroke, stroke_width=sw)

    def line(p, pts, color=INK, sw=.9, dashed=False):
        attrs = dict(points=' '.join(f'{x},{y}' for x, y in pts), fill='none',
                     stroke=color, stroke_width=sw, stroke_linejoin='round',
                     stroke_linecap='round')
        if dashed: attrs['stroke_dasharray'] = '3 2.5'
        return el(p, 'polyline', **attrs)

    def txt(p, x, y, value, size=8.2, anchor='middle', bold=False, color=INK):
        face = 'Arial-Bold' if bold else 'Arial'
        width = pdfmetrics.stringWidth(value, face, size)
        left = x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
        assert left>=0 and left+width<=W and y-size>=0 and y+2<=H, (value,left,y,width)
        el(p,'text',x=x,y=y,font_family=face,font_size=size,text_anchor=anchor,
           fill=color).text = value
        texts.append(dict(text=value,size_pt=size,bbox=[left,y-size,width,size+2]))

    def badge(p, x, y, value):
        el(p,'circle',cx=x,cy=y,r=7,fill=BLUE)
        txt(p,x,y+3,str(value),9.2,bold=True,color='white')

    def arrow(ident, points, color=INK, dashed=False, source=None, target=None, sw=1.1):
        p=g(ident); line(p,points,color,sw,dashed)
        x,y=points[-1]; px,py=points[-2]
        a=math.atan2(y-py,x-px); bx=x-4.4*math.cos(a); by=y-4.4*math.sin(a)
        pts=[(x,y),(bx+1.9*math.sin(a),by-1.9*math.cos(a)),
             (bx-1.9*math.sin(a),by+1.9*math.cos(a))]
        el(p,'polygon',points=' '.join(f'{u:.3f},{v:.3f}' for u,v in pts),fill=color)
        edges.append(dict(id=ident,source=source,target=target,points=points,
                          meaning='hint wiring pending' if dashed else 'logical request / dependency'))
        return p

    def page(p,x,y,w,h,color,fill,edits=False):
        fold=min(w*.24,7)
        el(p,'path',d=f'M{x},{y} H{x+w-fold} L{x+w},{y+fold} V{y+h} H{x} Z',
           fill=fill,stroke=color,stroke_width=.9,stroke_linejoin='round')
        line(p,[(x+w-fold,y),(x+w-fold,y+fold),(x+w,y+fold)],color,.75)
        for k in range(3):
            yy=y+9+k*5
            line(p,[(x+4,yy),(x+w-5-(k%2)*4,yy)],color,.8)
        if edits:
            line(p,[(x+w-11,y+17),(x+w-5,y+23)],AMBER,1.15)
            line(p,[(x+w-5,y+17),(x+w-11,y+23)],AMBER,1.15)
        else:
            for k in range(3):
                rect(p,x+4+k*6,y+h-7,4,3,fill='#8EC0E7',stroke='none')

    def slab(p,x,y,w,h,color,fill,depth=4):
        el(p,'polygon',points=f'{x},{y} {x+depth},{y-depth} {x+w+depth},{y-depth} {x+w},{y}',
           fill=fill,stroke=color,stroke_width=.7,stroke_linejoin='round')
        el(p,'polygon',points=f'{x+w},{y} {x+w+depth},{y-depth} {x+w+depth},{y+h-depth} {x+w},{y+h}',
           fill=fill,stroke=color,stroke_width=.7,stroke_linejoin='round')
        rect(p,x,y,w,h,fill=fill,stroke=color,radius=1.5)

    header=g('n:workspace-heading')
    badge(header,15,12,1)
    txt(header,28,15,'Private workspaces',11,anchor='start',bold=True)
    txt(header,496,15,'Wᵢ = Resolve(S, Δᵢ)',9.2,anchor='end')

    # Three explicit workspaces make independent private state visible.
    for i,x in enumerate((8,178,348)):
        ident=('1','2','N')[i]
        p=g(f'n:agent-tools-{ident}')
        rect(p,x+31,27,14,11,INK,INK,radius=1)
        line(p,[(x+34,30),(x+37,32.5),(x+34,35)],'white',.8)
        line(p,[(x+39,35),(x+42,35)],'white',.8)
        txt(p,x+51,36,'Agent tools',9.2,anchor='start')
        arrow(f'e:fuse-{ident}',[(x+74,40),(x+74,58)],source=f'n:agent-tools-{ident}',target=f'c:workspace-{ident}')
        txt(p,x+83,49,'FUSE',8.2,anchor='start')
        p=g(f'c:workspace-{ident}')
        el(p,'path',d=f'M{x+3},65 V57 Q{x+3},53 {x+8},53 H{x+39} L{x+48},61 H{x+139} Q{x+145},61 {x+145},66 H{x+3} Z',
           fill='#FFE5AD',stroke=AMBER,stroke_width=.9)
        rect(p,x,64,148,86,PALE_AMBER,AMBER,radius=5,sw=1.1)
        txt(p,x+74,79,f'Workspace {ident}',9.2,bold=True)
        page(p,x+19,88,27,32,AMBER,'#FFFDF6',True)
        page(p,x+100,88,27,32,BLUE,PALE_BLUE)
        txt(p,x+33,134,'Private upper',8.2)
        txt(p,x+114,134,'Packed reader',8.2)
        txt(p,x+74,146,'Upper first',8.2)
        nodes[f'c:workspace-{ident}']=[x,53,148,97]
        a=arrow(f'e:inherit-{ident}',[(x+50,105),(x+95,105)],BLUE,
                source=f'upper-{ident}',target=f'reader-{ident}')
        txt(a,x+72.5,99,'if visible',8.2)

    # Storage is separate from the mutable metadata service and producer.
    storage=g('c:object-store')
    rect(storage,140,223,356,177,'#F8FBFE','#9CB6CC',radius=6)
    txt(storage,485,238,'RustFS object store',11,anchor='end',bold=True)
    nodes['c:object-store']=[140,223,356,177]

    shared=g('n:shared-snapshot')
    badge(shared,165,257,2)
    txt(shared,179,260,'Shared immutable snapshot S',9.2,anchor='start',bold=True)
    for row,label in enumerate(('Manifest + indexes','Metadata pages','Data frames')):
        yy=276+21*row
        slab(shared,156,yy,200,17,BLUE,('#F5FAFE','#E8F3FC','#D5EAF9')[row],4)
        txt(shared,164,yy+11,label,8.2,anchor='start')
        for k in range(4):
            xx=260+k*19
            if row<2:
                rect(shared,xx,yy+3,12,10,'white','#6CA5D2',sw=.55)
                line(shared,[(xx+2,yy+6),(xx+9,yy+6)],BLUE,.55)
                line(shared,[(xx+2,yy+9),(xx+8,yy+9)],BLUE,.55)
            else:
                slab(shared,xx,yy+5,11,9,BLUE,'#94C4E8',2)
        txt(shared,344,yy+11,'···',8.2)
    nodes['n:shared-snapshot']=[154,245,208,91]

    private=g('n:private-objects')
    txt(private,435,259,'Private payload',9.2,bold=True)
    txt(private,435,271,'objects',9.2)
    for row in range(3):
        slab(private,393,282+17*row,78,11,AMBER,('#FFF4DE','#FFE4AF','#FFD78E')[row],4)
        for k in range(4):
            line(private,[(406+k*16,284+17*row),(406+k*16,290+17*row)],AMBER,.55)
    nodes['n:private-objects']=[393,278,82,49]

    service=g('n:metadata-service')
    txt(service,60,232,'Mutable metadata',9.2,bold=True)
    for row in range(2):
        slab(service,30,247+12*row,55,10,GRAY,'#E8EEF3',5)
        el(service,'circle',cx=36,cy=252+12*row,r=1.2,fill=GRAY)
        line(service,[(43,252+12*row),(77,252+12*row)],GRAY,.6)
    txt(service,60,283,'Upper state / control',8.2)
    txt(service,60,295,'Bindings · pins · leases',8.2)
    nodes['n:metadata-service']=[8,222,106,76]

    producer=g('n:snapshot-producer')
    page(producer,17,333,21,28,GRAY,'#F4F7F9')
    txt(producer,46,343,'Snapshot',9.2,anchor='start')
    txt(producer,46,355,'producer',9.2,anchor='start')
    txt(producer,60,379,'Finalized objects (Lₒ)',8.2)
    nodes['n:snapshot-producer']=[8,327,106,54]

    # Per-client lower readers fan in to shared objects, not a shared reader.
    for ident,points in (
        ('1',[(122,150),(122,187),(215,187),(215,245)]),
        ('2',[(292,150),(292,173),(280,173),(280,245)]),
        ('N',[(462,150),(462,199),(340,199),(340,245)])):
        arrow(f'e:lower-{ident}',points,BLUE,source=f'reader-{ident}',target='n:shared-snapshot',sw=1.35)
    a=arrow('e:upper-control',[(41,150),(41,221)],GRAY,
            source='upper-1',target='n:metadata-service')
    txt(a,48,211,'Upper / control',8.2,anchor='start')
    a=arrow('e:private-payload',[(381,150),(381,184),(485,184),(485,304),(475,304)],AMBER,
            source='upper-N',target='n:private-objects')
    txt(a,435,216,'Payload PUT / GET',8.2)
    a=arrow('e:producer-put',[(114,345),(130,345),(130,267),(154,267)],GRAY,
            source='n:snapshot-producer',target='n:shared-snapshot')
    txt(a,121,320,'PUT',8.2,anchor='end')

    layout=g('n:persisted-layout')
    rect(layout,156,346,328,50,'white','#9CB6CC',radius=3)
    badge(layout,167,357,3)
    txt(layout,179,360,'Stored layout',9.2,bold=True,anchor='start')
    txt(layout,179,374,'Effective (B, q)',8.2,anchor='start')
    txt(layout,179,388,'Read · verify · repair',8.2,anchor='start')
    for start in (302,394):
        rect(layout,start,363,80,14,'#EAF0F5',GRAY,radius=1)
        for k in range(4):
            rect(layout,start+2+k*13,365,11,10,'#BDD7EA','#7C9AB2',sw=.55)
        txt(layout,start+67,374,'···',8.2)
    line(layout,[(302,360),(302,356),(382,356),(382,360)],INK,.65)
    # Label background masks the bracket only; geometry remains editable.
    rect(layout,309,347,66,10,'white','none')
    txt(layout,342,354,'Encoding block B',8.2)
    line(layout,[(304,380),(304,383),(315,383),(315,380)],INK,.65)
    txt(layout,302,394,'q: verification/read quantum',8.2,anchor='start')
    nodes['n:persisted-layout']=[156,346,328,50]
    a=arrow('e:producer-hint',[(114,369),(156,369)],AMBER,True,
            source='n:snapshot-producer',target='n:persisted-layout')
    txt(a,126,362,'h(Lₒ)',8.2)
    a=arrow('e:private-hint',[(435,330),(435,346)],AMBER,True,
            source='n:private-objects',target='n:persisted-layout')
    txt(a,444,340,'h(Lₒ)',8.2,anchor='start')

    legend=g('n:legend')
    txt(legend,8,409,'Solid: logical requests. Upper/control and payload paths shown once; each client has both.',8.2,anchor='start')
    line(legend,[(8,418),(29,418)],AMBER,1.1,True)
    txt(legend,36,420,'Hint wiring pending; object geometry is schematic.',8.2,anchor='start')

    args.output.parent.mkdir(parents=True,exist_ok=True)
    ET.indent(root,space='  ')
    svg=args.output.with_suffix('.svg')
    ET.ElementTree(root).write(svg,encoding='utf-8',xml_declaration=True)
    drawing=svg2rlg(str(svg))
    assert drawing is not None and abs(drawing.width-W)<.01
    drawing.initialFontName='Arial'; renderPDF.STATE_DEFAULTS['fontName']='Arial'
    renderPDF.drawToFile(drawing,str(args.output.with_suffix('.pdf')),
                        title='Private workspaces over shared immutable objects')
    doc=pymupdf.open(args.output.with_suffix('.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False).save(args.output.with_suffix('.png'))
    qa=ROOT/'validation/architecture-v2'; qa.mkdir(parents=True,exist_ok=True)
    (qa/'scene.json').write_text(json.dumps(dict(width_pt=W,height_pt=H,nodes=nodes,
        text=texts,edges=edges),indent=2)+'\n',encoding='utf-8')
    print(f'Created {args.output.name}: editable SVG, vector PDF, PNG preview')


if __name__=='__main__':
    main()
