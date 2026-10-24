"""Draw BrewFS from file-level concepts as editable single-column SVG/PDF."""
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
from svglib.fonts import register_font

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures/system-architecture-editable'
QA = ROOT / 'validation/architecture-editable'
W, H = 240, 258
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
INK, BLUE, TEAL, ORANGE = '#182B3A', '#2D6084', '#4C5965', '#B65F2D'
PALE, WARM, AQUA, GRAY = '#DDE8F0', '#F3DDCD', '#E5E9EC', '#F3F5F6'
EDGE = '#72808D'
for family, filename in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(family, 'C:/Windows/Fonts/' + filename))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
register_font('Arial', font_path='C:/Windows/Fonts/arial.ttf', rlgFontName='Arial')
register_font('Arial', font_path='C:/Windows/Fonts/arialbd.ttf', weight='bold', rlgFontName='Arial-Bold')
rl_config.useA85 = 0
root = ET.Element('{'+NS+'}svg', width=f'{W}pt', height=f'{H}pt', viewBox=f'0 0 {W} {H}')
records, nodes, edges = [], {}, []

def el(p, tag, **attrs):
    return ET.SubElement(p, '{'+NS+'}'+tag, {k.replace('_', '-'):str(v) for k,v in attrs.items()})

def group(ident):
    return el(root, 'g', id=ident)

def text(p, x, y, value, size=6.8, anchor='middle', bold=False, color=INK):
    size=max(7.0,size)
    # Arial lacks numeric Unicode subscripts. Keep true editable text by using
    # ordinary glyphs at a smaller, explicitly positioned subscript baseline.
    subs = dict(zip('₁₂ᵢₒₚ','12iop'))
    runs=[]
    for c in value:
        sub=c in subs
        run_size=max(5.2,size*.76) if sub else size
        run_y=y+1.45 if sub else y
        glyph=subs.get(c,c)
        if runs and runs[-1][1:]==(run_size,run_y):
            runs[-1]=(runs[-1][0]+glyph,run_size,run_y)
        else:
            runs.append((glyph,run_size,run_y))
    face='Arial-Bold' if bold else 'Arial'
    widths=[pdfmetrics.stringWidth(s,face,z) for s,z,_ in runs]
    width=sum(widths)
    left = x if anchor=='start' else x-width if anchor=='end' else x-width/2
    assert left >= 0 and left+width <= W, (value, left, width)
    cursor=left
    n=el(p,'g',aria_label=value)
    for (s,z,baseline),run_width in zip(runs,widths):
        item=el(n,'text',x=cursor,y=baseline,font_family='Arial',font_size=z,
                font_weight='bold' if bold else 'normal',text_anchor='start',fill=color)
        item.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        item.text=s
        cursor+=run_width
    records.append(dict(text=value, group=p.get('id'), size_pt=size, bbox=[left, y-size, left+width, y+1.5]))
    return n

def line(p, pts, color=INK, width=.7, dashed=False):
    a = dict(points=' '.join(f'{x},{y}' for x,y in pts), fill='none', stroke=color,
             stroke_width=width, stroke_linejoin='round', stroke_linecap='round')
    if dashed: a['stroke_dasharray']='2.5 1.8'
    el(p, 'polyline', **a)

def arrow(ident, pts, color=INK, dashed=False, meaning='reference/access'):
    p = group(ident)
    line(p, pts, color, .75, dashed)
    x,y = pts[-1]; px,py = pts[-2]
    a = math.atan2(y-py, x-px)
    bx,by=x-3*math.cos(a), y-3*math.sin(a)
    el(p,'polygon',points=f'{x},{y} {bx+1.25*math.sin(a)},{by-1.25*math.cos(a)} {bx-1.25*math.sin(a)},{by+1.25*math.cos(a)}', fill=color)
    edges.append(dict(id=ident,points=pts,meaning=meaning))

def box(ident, x, y, w, h, fill='white', stroke=EDGE, radius=2):
    p=group(ident)
    el(p,'rect',x=x,y=y,width=w,height=h,rx=radius,fill=fill,stroke=stroke,stroke_width=.65)
    nodes[ident]=[x,y,w,h]
    return p

def title(number,y,label):
    p=group(f'heading-{number}')
    el(p,'circle',cx=6,cy=y-3,r=5,fill=INK)
    text(p,6,y+.1,str(number),8,bold=True,color='white')
    text(p,14,y,label,8.5,anchor='start',bold=True)

def agent(ident,x,y,color):
    p=group(ident)
    el(p,'circle',cx=x,cy=y-4,r=2,fill='white',stroke=color,stroke_width=.8)
    # Outline bust built from editable straight segments.
    line(p,[(x-3.7,y+2.5),(x-3.5,y),(x-2,y-1.5),(x+2,y-1.5),(x+3.5,y),(x+3.7,y+2.5),(x-3.7,y+2.5)],color,.8)

def strip(ident,x,y,widths,fills,h=8,stroke=BLUE):
    p=group(ident)
    for idx,(w,fill) in enumerate(zip(widths,fills)):
        el(p,'rect',x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=.55)
        x+=w
    return p

def bracket(p,x1,x2,y,label,color=INK):
    line(p,[(x1,y-2),(x1,y),(x2,y),(x2,y-2)],color,.6)
    if label: text(p,(x1+x2)/2,y+7,label,6.3)

# 1. Workspace state and payload are separate; the baseline is shared and pinned.
title(1,11,'Delta-Based Multi-Agent Workspaces')
for idx,x in [(1,10),(2,150)]:
    agent(f'agent-{idx}',x,24,INK)
    arrow(f'fuse-entry-{idx}',[(x+8,23),(x+46,23)],INK,meaning='FUSE file operations into workspace view')
    p=group(f'workspace-label-{idx}')
    text(p,x+28,19,'FUSE',6.8,bold=True)
    text(p,x+66,26,'View W₁' if idx==1 else 'View W₂',7.4,bold=True)
for idx,x,w in [(1,4,106),(2,134,102)]:
    p=box(f'workspace-{idx}',x,29,w,27,'white',EDGE)
    p=box(f'private-state-{idx}',x+6,33,w-12,12,ORANGE,ORANGE)
    text(p,x+w/2,41.5,'Private state Δ₁' if idx==1 else 'Private state Δ₂',6.8,bold=True,color='white')
    text(p,x+w/2,52.5,'resolve private first',6.4)
p=box('private-payload',4,66,68,13,WARM,ORANGE)
text(p,38,75.5,'Private bytes U₁',6.6)
p=box('shared-lower',85,66,150,13,BLUE,BLUE)
text(p,160,75.5,'Shared immutable baseline S',6.8,bold=True,color='white')
arrow('data-to-private',[(26,56),(26,66)],ORANGE,meaning='private state references separately stored new bytes')
p=group('pin-read-references')
line(p,[(83,56),(83,61),(105,61),(105,66)],BLUE,.75)
line(p,[(187,56),(187,66)],BLUE,.75)
text(p,149,62.5,'pinned',6.3)
line(p,[(1,84),(239,84)],'#B6C3CD',.45)

# 2. A familiar directory entry explains metadata before any format internals.
title(2,94,'Packed Metadata')
p=box('native-reader',88,103,62,12,GRAY)
text(p,119,111.6,'Native records',6.4)
p=box('packed-reader',170,103,66,12,PALE,BLUE)
text(p,203,111.6,'Packed snapshot',6.4)
p=group('baseline-choice')
line(p,[(160,79),(160,100)],BLUE,.75)
arrow('baseline-native',[(160,100),(119,100),(119,103)],BLUE)
arrow('baseline-packed',[(160,100),(203,100),(203,103)],BLUE)
text(p,159,111.6,'or',6.3)
arrow('expand-packed',[(185,115),(185,120)],BLUE,meaning='expand indexed joint records within a packed snapshot')
p=box('read-only',2,128,35,25,'white',BLUE)
text(p,19.5,138,'Read-only',6.4)
text(p,19.5,146,'mount',6.4)
arrow('readonly-index',[(37,140.5),(42,140.5)],BLUE)
p=box('name-index',42,123,40,32,'white',BLUE)
text(p,62,131,'Name-range',6.2)
text(p,62,139,'index',6.2)
strip('index-pages',48,144,[8.5,8.5,8.5],[PALE,PALE,BLUE],h=7)
p=group('directory-context')
text(p,61.5,162,'dir: /src',6.4)
p=box('metadata-page',87,120,112,42,'white',BLUE)
text(p,143,128.5,'Packed metadata page',7.2,bold=True)
p=box('metadata-table',91,133,104,25,'white',EDGE,0)
el(p,'rect',x=91,y=142,width=104,height=10,fill=PALE)
for x in [125,161]: line(p,[(x,133),(x,158)],EDGE,.5)
for y in [142,152]: line(p,[(91,y),(195,y)],EDGE,.5)
text(p,108,139.7,'Name',6.2)
text(p,143,139.7,'Attributes',6.2)
text(p,178,139.7,'Data ref.',6.2)
text(p,108,149.6,'main.py',6.4)
text(p,143,149.6,'size, mode',6.2)
el(p,'rect',x=172,y=145,width=12,height=4,fill=BLUE)
for a,b in [(97,114),(131,153),(169,184)]: line(p,[(a,155),(b,155)],EDGE,.6)
arrow('index-record',[(73.5,147.5),(91,147.5)],BLUE,meaning='directory and name range select a joint-metadata page')
p=group('payload-label')
text(p,221.5,134,'Data object',6.2)
p=box('packed-payload',205,139,33,20,PALE,BLUE)
text(p,221.5,147,'Bytes',6.4)
text(p,221.5,155,'Oₚ',6.5)
arrow('record-bytes',[(195,147),(205,147)],BLUE,meaning='logical data reference; authenticated descriptor resolution is expanded in Figure 3')
p=group('section-rule-2')
line(p,[(1,166),(239,166)],'#B6C3CD',.45)

# 3. Logical addressing ranges precede raw upload blocks and physical layout.
title(3,176,'Variable-Granularity Object Storage')
p=group('ordinary-ranges')
text(p,40,185,'Ordinary file offsets',6.3)
text(p,114,185,'Slice: written range',6.3)
strip('file-chunks',4,191,[24,24,24],[GRAY,AQUA,GRAY],h=9,stroke=TEAL)
p=group('selected-slice')
el(p,'rect',x=34,y=193,width=12,height=5,fill=TEAL)
bracket(p,28,52,204,None,TEAL)
text(p,40,213,'Chunk',6.4,bold=True)
text(p,40,221,'address range',6.2)
# This connector expands a contained interval; it is not an upload edge.
arrow('expand-slice',[(40,193),(40,188),(114,188),(114,191)],TEAL,meaning='magnify a written slice interval within the selected logical chunk')
strip('input-slice',88,191,[52],[AQUA],h=9,stroke=TEAL)
arrow('partition-slice',[(114,200),(114,211)],TEAL,meaning='partition slice data into configured raw upload blocks')
strip('upload-blocks',88,211,[20,20,12],[AQUA,AQUA,AQUA],h=9,stroke=TEAL)
p=group('client-block-labels')
text(p,114,228,'Upload blocks',6.4,bold=True)
text(p,114,236,'configured g',6.2)
p=group('encode-label')
text(p,158,205,'Compress',6.2)
text(p,158,213,'& frame',6.2)
arrow('encode-objects',[(140,217.5),(176,217.5)],TEAL,meaning='format each block independently; compression/framing as applicable determines its finalized object length')
p=group('finalized-objects')
text(p,194,205,'Objects',6.4,bold=True)
strip('final-object',176,211,[34],[AQUA],h=9,stroke=TEAL)
for x in [214,217,220]: el(p,'circle',cx=x,cy=215.5,r=.45,fill=TEAL)
bracket(p,176,210,222,None,TEAL)
text(p,189,230,'length Lₒ',6.3)
p=box('u1-reference',4,229,28,11,WARM,ORANGE)
text(p,18,237,'U₁',6.5)
p=box('packed-reference',36,229,28,11,PALE,BLUE)
text(p,50,237,'Oₚ',6.5)
arrow('private-storage',[(18,240),(18,246)],ORANGE,meaning='private payload uses its own upload contract')
arrow('packed-storage',[(50,240),(50,246)],BLUE,meaning='snapshot payload uses its own upload contract')
p=group('backend-layout-label')
text(p,103,244,'Backend selects layout',6.2)
p=box('rustfs',3,246,234,11,TEAL,TEAL)
text(p,27,253.8,'RustFS',7.0,bold=True,color='white')
text(p,99,253.8,'EC block B',6.5,color='white')
text(p,191,253.8,'Per-shard verify/read q',6.3,color='white')
arrow('ordinary-storage',[(208,220),(208,246)],TEAL,meaning='store finalized object using backend-selected persisted geometry')
arrow('optional-layout-hint',[(210,222),(239,222),(239,241),(231,241),(231,246)],TEAL,True,'optional B hint from finalized upload length; distinct from independently gated q framing')
p=group('hint-label')
text(p,225,230,'B hint',6.2)
text(p,225,238,'optional',6.2)

OUT.parent.mkdir(parents=True,exist_ok=True)
QA.mkdir(parents=True,exist_ok=True)
ET.indent(root,space='  ')
svg=OUT.with_suffix('.svg')
ET.ElementTree(root).write(svg,encoding='utf-8',xml_declaration=True)
drawing=svg2rlg(str(svg))
assert drawing is not None
drawing.initialFontName='Arial'
renderPDF.STATE_DEFAULTS['fontName']='Arial'
renderPDF.drawToFile(drawing,str(OUT.with_suffix('.pdf')),title='BrewFS: editable single-column system schematic')
doc=pymupdf.open(OUT.with_suffix('.pdf'))
doc[0].get_pixmap(matrix=pymupdf.Matrix(4,4),alpha=False).save(OUT.with_suffix('.png'))
doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(QA/'figure-placement.png')
(QA/'scene.json').write_text(json.dumps(dict(width_pt=W,height_pt=H,nodes=nodes,text=records,edges=edges),indent=2),encoding='utf-8')
print(json.dumps(dict(svg=str(svg),pdf=str(OUT.with_suffix('.pdf')),text_objects=len(records),nodes=len(nodes),raster_objects=len(doc[0].get_images())),indent=2))
