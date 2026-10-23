#!/usr/bin/env python3
"""Draw the compact, mechanism-oriented architecture at final print size.

SVG with live text is authoritative. No external paper artwork is reused.
See planning/architecture-compact-brief.md for sources and claim boundaries.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import pymupdf
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
W, H = 504, 230
INK, EDGE, BLUE = '#111111', '#555555', '#21618C'
PALE, GRAY = '#E8F1F7', '#F2F2F2'


def el(parent, tag, **attrs):
    return ET.SubElement(parent, '{'+NS+'}'+tag,
                         {k.replace('_','-'):str(v) for k,v in attrs.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path,
                    default=ROOT/'figures/system-architecture-compact')
    args = ap.parse_args()
    rl_config.useA85 = 0  # keep PDF text streams directly auditable
    pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
    root = ET.Element('{'+NS+'}svg', width=f'{W}pt', height=f'{H}pt',
                      viewBox=f'0 0 {W} {H}')
    text_records, edges, nodes = [], [], {}

    def group(ident):
        return el(root,'g',id=ident)

    def text(p,x,y,s,size=8,anchor='middle',bold=False):
        t=el(p,'text',x=x,y=y,font_family='Arial',font_size=size,
             text_anchor=anchor,fill=INK,font_weight='bold' if bold else 'normal')
        t.text=s
        width=pdfmetrics.stringWidth(s,'Arial-Bold' if bold else 'Arial',size)
        left=x if anchor=='start' else x-width if anchor=='end' else x-width/2
        assert left >= -0.1 and left+width <= W+.1, (s,left,width)
        text_records.append({'text':s,'size_pt':size,'bbox':[left,y-size,width,size+2]})

    def line(p,pts,color=EDGE,sw=.7,dashed=False):
        kw=dict(points=' '.join(f'{x},{y}' for x,y in pts),fill='none',
                stroke=color,stroke_width=sw,stroke_linejoin='miter')
        if dashed: kw['stroke_dasharray']='3 2'
        el(p,'polyline',**kw)

    def box(ident,x,y,w,h,fill='white',stroke=EDGE):
        p=group(ident)
        el(p,'rect',x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=.7)
        nodes[ident]=[x,y,w,h]
        return p

    def arrow(ident,pts,dashed=False,source=None,target=None):
        p=group(ident); line(p,pts,INK,.8,dashed)
        x,y=pts[-1]; px,py=pts[-2]
        a=math.atan2(y-py,x-px)
        bx,by=x-3.5*math.cos(a),y-3.5*math.sin(a)
        el(p,'polygon',points=f'{x},{y} {bx+1.55*math.sin(a)},{by-1.55*math.cos(a)} {bx-1.55*math.sin(a)},{by+1.55*math.cos(a)}',fill=INK)
        edges.append({'id':ident,'source':source,'target':target,'points':pts,
                      'meaning':'integration pending' if dashed else 'reference/access dependency'})

    p=group('panel-titles')
    text(p,2,11,'(a) Delta-based workspace i',9,anchor='start',bold=True)
    text(p,178,11,'(b) Packed snapshot S',9,anchor='start',bold=True)
    text(p,350,11,'(c) Stored layout',9,anchor='start',bold=True)
    # Thin horizontal rules identify panels without bulky enclosing cards.
    for x,w in [(2,158),(178,154),(350,152)]: line(p,[(x,18),(x+w,18)],EDGE,.6)

    p=box('n:upper',2,27,158,66,PALE)
    text(p,81,40,'Δᵢ in mutable metadata service',8.3)
    text(p,10,55,'present → private entity',anchor='start')
    text(p,10,69,'hidden → ENOENT',anchor='start')
    text(p,10,83,'absent + visible → S',anchor='start')
    p=group('n:map-heading')
    text(p,2,108,'Explicit file map after a write',8.3,anchor='start')
    x=2
    for idx,(label,w,fill) in enumerate([('LowerRange',50,'white'),('Data',28,PALE),
                                        ('LowerRange',50,'white'),('Hole',28,GRAY)]):
        p=box(f'n:span-{idx}',x,117,w,22,fill)
        text(p,x+w/2,131,label)
        x+=w
    p=box('n:private-objects',8,174,124,22,PALE)
    text(p,70,188,'Private payload object')
    p=group('n:upper-notes')
    text(p,44,164,'Data ref')
    text(p,144,153,'0')
    text(p,2,209,'Upper GET: verify whole object',anchor='start')
    text(p,2,224,'Durable PUT, then publish map',anchor='start')
    arrow('e:data-ref',[(66,139),(66,174)],source='n:span-1',target='n:private-objects')

    p=box('n:manifest',178,27,154,28)
    text(p,255,39,'Pinned manifest / roots',8.3)
    text(p,255,50,'Same S for all workspaces')
    p=box('n:index',178,70,154,25)
    text(p,255,85,'Paged directory-name index',8.3)
    p=box('n:groupmeta',178,110,154,27)
    text(p,255,121,'GroupMeta page',8.3)
    text(p,255,132,'name  |  attributes  |  data locator')
    p=box('n:frame',178,151,154,34)
    text(p,255,164,'Packed frame descriptor',8.3)
    text(p,255,177,'Authenticated payload range')
    arrow('e:visible-lower',[(160,81),(178,81)],source='n:upper',target='n:index')
    arrow('e:roots',[(255,55),(255,70)],source='n:manifest',target='n:index')
    arrow('e:name-page',[(255,95),(255,110)],source='n:index',target='n:groupmeta')
    arrow('e:locator',[(255,137),(255,151)],source='n:groupmeta',target='n:frame')
    arrow('e:lower-span',[(105,139),(105,166),(178,166)],source='n:span-2',target='n:frame')
    p=group('n:lower-notes')
    text(p,178,209,'Snapshot metadata on object storage',anchor='start')
    text(p,178,224,'No per-file lower database records',anchor='start')

    p=box('n:finalized-object',350,27,152,26)
    text(p,426,38,'Finalized upload length Lₒ',8.3)
    text(p,426,49,'Private or snapshot object')
    p=box('n:admission',350,70,152,32)
    text(p,426,82,'RustFS: validate B; choose q',8.3)
    text(p,426,95,'Eligible writes: q | s, qd | B')
    p=box('n:persisted-layout',350,113,152,22,GRAY)
    text(p,426,127,'Persist (B, q, d, p) with object')
    p=box('n:shards',350,155,152,64)
    text(p,426,165,'2+2 example: s = B/d = 2q')
    for i,label in enumerate(('D0','D1','P0','P1')):
        y=171+11*i
        text(p,354,y+8,label,anchor='start')
        for k in range(2):
            el(p,'rect',x=370+64*k,y=y,width=64,height=9,
               fill=PALE if i<2 else GRAY,stroke=EDGE,stroke_width=.5)
    arrow('e:hint',[(426,53),(426,70)],True,'n:finalized-object','n:admission')
    p=group('n:hint-label'); text(p,435,64,'B hint h(Lₒ)',anchor='start')
    arrow('e:commit-layout',[(426,102),(426,113)],source='n:admission',target='n:persisted-layout')
    arrow('e:stored-geometry',[(426,135),(426,155)],source='n:persisted-layout',target='n:shards')
    arrow('e:backend-range',[(332,168),(350,168)],source='n:frame',target='n:shards')
    p=group('n:read-repair'); text(p,426,228,'Reads / repair use stored layout')

    args.output.parent.mkdir(parents=True,exist_ok=True)
    ET.indent(root,space='  ')
    svg=args.output.with_suffix('.svg')
    ET.ElementTree(root).write(svg,encoding='utf-8',xml_declaration=True)
    drawing=svg2rlg(str(svg))
    assert drawing is not None and abs(drawing.width-W)<.01
    drawing.initialFontName='Arial'; renderPDF.STATE_DEFAULTS['fontName']='Arial'
    renderPDF.drawToFile(drawing,str(args.output.with_suffix('.pdf')),
                        title='Delta-based workspace, packed access and stored object layout')
    d=pymupdf.open(args.output.with_suffix('.pdf'))
    d[0].get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False).save(args.output.with_suffix('.png'))
    qa=ROOT/'validation/compact-figures'; qa.mkdir(exist_ok=True,parents=True)
    (qa/'architecture-scene.json').write_text(json.dumps(dict(width_pt=W,height_pt=H,
        nodes=nodes,text=text_records,edges=edges),indent=2)+'\n',encoding='utf-8')
    print(f'Created {args.output.name}: {W} x {H} pt, SVG/PDF/PNG')


if __name__=='__main__':
    main()
