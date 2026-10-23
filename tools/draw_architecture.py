#!/usr/bin/env python3
"""Editable logical architecture; SVG is authoritative and is exported to PDF.

Run from any directory with Python + reportlab + svglib + pymupdf. Font paths
are configurable for other platforms. Node/edge IDs match the figure brief.
No performance values or generated raster content are used.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from reportlab import rl_config
from svglib.svglib import svg2rlg
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
INK, BLUE, PALE, GRAY = '#18232D', '#17689A', '#EDF5FA', '#F4F5F6'
WIDTH, HEIGHT = 504, 420


def element(parent, tag, **attrs):
    return ET.SubElement(parent, '{'+NS+'}'+tag,
                         {k.replace('_','-'):str(v) for k,v in attrs.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/arial.ttf'))
    ap.add_argument('--bold-font', type=Path, default=Path('C:/Windows/Fonts/arialbd.ttf'))
    ap.add_argument('--output', type=Path, default=ROOT/'paper/figures/system-architecture')
    args = ap.parse_args()
    pdfmetrics.registerFont(TTFont('Arial', str(args.font)))
    pdfmetrics.registerFont(TTFont('Arial-Bold', str(args.bold_font)))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold',
                                 italic='Arial', boldItalic='Arial-Bold')
    # Plain Flate streams remain inspectable by the publication font auditor.
    rl_config.useA85 = False
    root = ET.Element('{'+NS+'}svg', {'width':f'{WIDTH}pt','height':f'{HEIGHT}pt',
                     'viewBox':f'0 0 {WIDTH} {HEIGHT}', 'version':'1.1',
                     'font-family':'Arial', 'font-size':'9'})
    element(root,'title').text = 'Private workspace views, packed immutable lower, and persisted object layouts'
    element(root,'desc').text = ('Logical architecture of the Entity workspace design. '
                               'Solid arrows are requests/dependencies; dashed arrows are '
                               'layout-hint connections requiring integration and validation.')
    element(root,'rect',x=0,y=0,width=WIDTH,height=HEIGHT,fill='white')
    boxes, texts, edges = {}, [], []

    def group(ident):
        return element(root,'g',id=ident)

    def box(ident,x,y,w,h,fill='white',stroke='#78848E',radius=3):
        g=group(ident)
        element(g,'rect',x=x,y=y,width=w,height=h,rx=radius,
                fill=fill,stroke=stroke,stroke_width=.8)
        boxes[ident]=[x,y,w,h]
        return g

    def text(g,x,y,value,size=9,bold=False,anchor='middle',color=INK,max_width=None):
        width=pdfmetrics.stringWidth(value,'Arial-Bold' if bold else 'Arial',size)
        assert max_width is None or width <= max_width, (value,width,max_width)
        left=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
        assert left >= 0 and left+width <= WIDTH and y-size >= 0 and y+2 <= HEIGHT
        node=element(g,'text',x=x,y=y,font_size=size,font_family='Arial',
                     font_weight='bold' if bold else 'normal',text_anchor=anchor,fill=color)
        node.text=value
        texts.append(dict(text=value,size_pt=size,bbox=[left,y-size,width,size+2]))

    def badge(g,x,y,value):
        element(g,'circle',cx=x,cy=y,r=7.5,fill=BLUE)
        text(g,x,y+3.4,str(value),size=10.5,bold=True,color='white')

    def arrow(ident,points,dashed=False,width=1.2,source=None,target=None):
        g=group(ident)
        color=BLUE if dashed else INK
        attrs=dict(points=' '.join(f'{x},{y}' for x,y in points),fill='none',
                   stroke=color,stroke_width=width,stroke_linejoin='round')
        if dashed: attrs['stroke_dasharray']='4 3'
        element(g,'polyline',**attrs)
        x,y=points[-1]; px,py=points[-2]
        angle=math.atan2(y-py,x-px); length=5; half=2.3
        bx,by=x-length*math.cos(angle),y-length*math.sin(angle)
        corners=[(x,y),(bx+half*math.sin(angle),by-half*math.cos(angle)),
                 (bx-half*math.sin(angle),by+half*math.cos(angle))]
        element(g,'polygon',points=' '.join(f'{a:.3f},{b:.3f}' for a,b in corners),fill=color)
        edges.append(dict(id=ident,source=source,target=target,points=points,
                          meaning='hint integration gate' if dashed else 'logical request / dependency'))
        return g

    # Containers first; every coordinate is a point at the final 7-inch width.
    client=box('c:workspace-client',8,62,488,146,stroke='#8D9BA5',radius=4)
    text(client,272,77,'Workspace client i  (×N independent views)',10.5,bold=True)
    storage=box('c:object-store',196,244,300,145,fill='#FBFCFD',stroke='#8D9BA5',radius=4)
    text(storage,342,258,'RustFS object storage',10.5,bold=True)

    agents=box('n:agent-tools',8,8,488,29,fill=GRAY)
    text(agents,252,26,'Agent tasks: repository tools · editing · build / test',10.5)
    resolver=box('n:delta-resolver',22,96,198,38,fill=PALE,stroke=BLUE)
    badge(resolver,35,108,1)
    text(resolver,129,111,'Delta-based workspace',10.5,max_width=166)
    text(resolver,121,126,'Wᵢ = Resolve(S, Δᵢ)',9)
    upper=box('n:private-upper',22,158,198,36,fill=PALE,stroke=BLUE)
    text(upper,121,171,'Private Δᵢ: names / attrs / tombstones',9,max_width=182)
    text(upper,121,185,'Span maps: Data | LowerRange | Hole',8.2,max_width=182)

    reader=box('n:packed-reader',280,96,200,89,fill=PALE,stroke=BLUE)
    badge(reader,293,108,2)
    text(reader,389,111,'Packed lower reader',10.5,max_width=166)
    text(reader,380,129,'Pinned immutable snapshot S',9)
    text(reader,380,146,'Paged indexes · attributes + locators',8.2,max_width=182)
    text(reader,380,163,'Authenticated frame reads',9)
    text(reader,380,177,'Per-client reader; shared lower objects',8.2,max_width=184)

    kv=box('n:metadata-service',8,256,154,56,fill=GRAY)
    text(kv,85,272,'Mutable metadata service',9,max_width=138)
    text(kv,85,288,'Private upper + control state',8.2,max_width=138)
    text(kv,85,302,'Bindings · pins · leases',8.2)
    private=box('n:private-objects',208,269,124,43)
    text(private,270,283,'Private payload objects',9,max_width=112)
    text(private,270,298,'New upper bytes',8.2)
    shared=box('n:shared-snapshot',356,269,128,43)
    text(shared,420,282,'Shared snapshot S',9)
    text(shared,420,296,'Manifest / indexes / pages',8.2,max_width=116)
    text(shared,420,307,'Data frames + descriptors',8.2,max_width=116)

    producer=box('n:snapshot-producer',8,338,154,51,fill=GRAY)
    text(producer,85,352,'Snapshot producer',10.5)
    text(producer,85,367,'Selected fixed source view',8.2,max_width=138)
    text(producer,85,381,'Finalized objects (length Lₒ)',8.2,max_width=138)
    layout=box('n:persisted-layout',208,338,276,37,fill=PALE,stroke=BLUE)
    badge(layout,221,350,3)
    text(layout,354,353,'Persisted per-object layout',10.5)
    text(layout,346,367,'B: encoding block · q: verification/read frame',8.2,max_width=260)
    text(storage,346,384,'Reads and repair interpret the stored (B, q)',8.2,max_width=282)

    # The response path is omitted. Only hint connections use dashed lines.
    a=arrow('e:tool-fuse',[(121,37),(121,96)],width=1.4,
            source='n:agent-tools',target='n:delta-resolver')
    text(a,132,53,'FUSE requests',8.2,anchor='start')
    a=arrow('e:upper-first',[(85,134),(85,158)],source='n:delta-resolver',target='n:private-upper')
    text(a,95,149,'Check / mutate',8.2,anchor='start')
    a=arrow('e:inherit-lower',[(220,117),(280,117)],source='n:delta-resolver',target='n:packed-reader')
    text(a,250,109,'Visible lower',8.2,max_width=56)
    a=arrow('e:mutable-records',[(85,194),(85,256)],source='n:private-upper',target='n:metadata-service')
    text(a,75,235,'Upper / control',8.2,anchor='end')
    a=arrow('e:private-payload',[(220,176),(258,176),(258,269)],
            source='n:private-upper',target='n:private-objects')
    text(a,266,220,'PUT / GET',8.2,anchor='start')
    a=arrow('e:lower-object-requests',[(432,185),(432,269)],
            source='n:packed-reader',target='n:shared-snapshot')
    text(a,442,220,'GET / Range',8.2,anchor='start')
    arrow('e:private-layout',[(270,312),(270,338)],
          source='n:private-objects',target='n:persisted-layout')
    arrow('e:shared-layout',[(420,312),(420,338)],
          source='n:shared-snapshot',target='n:persisted-layout')
    text(storage,346,328,'Effective layout stored with each object',8.2,max_width=270)
    a=arrow('e:producer-put',[(162,350),(196,350)],source='n:snapshot-producer',target='c:object-store')
    text(a,179,343,'PUT',8.2)
    a=arrow('e:private-hint-gate',[(258,226),(202,226),(202,356),(208,356)],dashed=True,
            source='e:private-payload',target='n:persisted-layout')
    element(a,'circle',cx=258,cy=226,r=2,fill=BLUE)
    text(a,228,217,'h(Lₒ)*',8.2)
    text(a,228,238,'PUT only',8.2)
    a=arrow('e:producer-hint-gate',[(162,366),(208,366)],dashed=True,
            source='n:snapshot-producer',target='n:persisted-layout')
    text(a,183,380,'h(Lₒ)*',8.2)

    legend=group('n:edge-key')
    text(legend,8,407,'Solid: request / dependency paths.  Dashed*: hint wiring to complete and verify.',8.2,anchor='start')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    ET.indent(root,space='  ')
    svg=args.output.with_suffix('.svg')
    ET.ElementTree(root).write(svg,encoding='utf-8',xml_declaration=True)
    drawing=svg2rlg(str(svg))
    assert drawing is not None and abs(drawing.width-WIDTH)<.01
    # Avoid introducing the renderer's unembedded Times-Roman default resource.
    drawing.initialFontName='Arial'
    renderPDF.STATE_DEFAULTS['fontName']='Arial'
    renderPDF.drawToFile(drawing,str(args.output.with_suffix('.pdf')),
                         title='System architecture: private workspaces, packed metadata, object layouts')
    doc=pymupdf.open(args.output.with_suffix('.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False).save(args.output.with_suffix('.png'))
    qa=ROOT/'validation/architecture'
    qa.mkdir(parents=True,exist_ok=True)
    (qa/'scene.json').write_text(json.dumps(dict(width_pt=WIDTH,height_pt=HEIGHT,
                                 boxes=boxes,text=texts,edges=edges),indent=2)+'\n',encoding='utf-8')
    print(f'Created editable SVG, exported PDF and PNG: {args.output.name}')


if __name__=='__main__':
    main()
