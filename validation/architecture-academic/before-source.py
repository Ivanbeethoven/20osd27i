"""Rebuild the accepted single-column BrewFS schematic as live SVG/PDF objects."""
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
INK, BLUE, TEAL, ORANGE = '#102343', '#24689A', '#137D8D', '#C65C11'
PALE, WARM, AQUA, GRAY = '#EAF4FB', '#FFF0DD', '#E9F5F5', '#F3F4F5'
EDGE = '#7892A8'
for family, filename in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(family, 'C:/Windows/Fonts/' + filename))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
register_font('Arial', rlgFontName='Arial')
register_font('Arial', weight='bold', rlgFontName='Arial-Bold')
rl_config.useA85 = 0
root = ET.Element('{'+NS+'}svg', width=f'{W}pt', height=f'{H}pt', viewBox=f'0 0 {W} {H}')
records, nodes, edges = [], {}, []

def el(p, tag, **attrs):
    return ET.SubElement(p, '{'+NS+'}'+tag, {k.replace('_', '-'):str(v) for k,v in attrs.items()})

def group(ident):
    return el(root, 'g', id=ident)

def text(p, x, y, value, size=6.8, anchor='middle', bold=False, color=INK):
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

# 1. Preserve two views and show their file-operation interface explicitly.
title(1,11,'Delta-Based Multi-Agent Workspaces')
for idx,x in [(1,10),(2,150)]:
    agent(f'agent-{idx}',x,24,BLUE if idx==1 else TEAL)
    arrow(f'fuse-entry-{idx}',[(x+8,23),(x+46,23)],BLUE,meaning='FUSE file operations into workspace view')
    p=group(f'workspace-label-{idx}')
    text(p,x+28,19,'FUSE',6.8,bold=True)
    text(p,x+66,26,'View W₁' if idx==1 else 'View W₂',7.4,bold=True)
strip('view-1',6,32,[40,20,18,16],['#B9DBF3',WARM,'#B9DBF3','white'])
strip('view-2',140,32,[40,20,18,16],['#B9DBF3','#B9DBF3','#B9DBF3','white'])
p=group('map-labels')
text(p,26,49,'LowerRange',6.4)
text(p,60,49,'Data',6.4)
text(p,92,49,'Hole',6.4)
text(p,92,58,'zeros',6.4)
text(p,166,54,'Δᵢ: private writable upper',6.8)
text(p,166,67,'Wᵢ = Resolve(S, Δᵢ)',7.2)
p=box('private-payload',34,60,52,17,WARM,ORANGE)
text(p,60,66,'Private payload',6.2)
text(p,60,73.4,'U₁',6.3)
arrow('data-to-private',[(60,51),(60,60)],ORANGE)
p=box('shared-lower',87,77,142,14,PALE,BLUE)
text(p,158,86.5,'S  Shared immutable lower',7.0,bold=True)
# Undirected pin/read references avoid implying writes to immutable S.
p=group('pin-read-references')
line(p,[(22,51),(22,84),(87,84)],BLUE,.75)
line(p,[(210,40),(210,44),(237,44),(237,84),(229,84)],BLUE,.75)
text(p,50,93,'pinned reference',6.3)
line(p,[(1,96),(239,96)],'#B6C3CD',.45)

# 2. Native and Packed are alternatives. Expand only the Packed branch.
title(2,106,'Packed Metadata')
p=box('native-reader',83,113,61,13,GRAY)
text(p,113.5,122,'Native catalog',6.6)
p=box('packed-reader',169,113,56,13,PALE,BLUE)
text(p,197,122,'Packed snapshot',6.6)
p=group('baseline-choice')
line(p,[(158,91),(158,110)],BLUE,.75)
arrow('baseline-native',[(158,110),(113.5,110),(113.5,113)],BLUE)
arrow('baseline-packed',[(158,110),(197,110),(197,113)],BLUE)
text(p,156,123,'or',6.3)
arrow('expand-packed',[(197,126),(197,129)],BLUE)
p=box('packed-group',43,129,185,46,'#F7FAFD','#B5CADD')
p=box('read-only',2,144,35,20,'white',BLUE)
text(p,19.5,152,'Read-only',6.4)
text(p,19.5,160,'mount',6.4)
arrow('readonly-index',[(37,154),(45,154)],BLUE)
p=group('packed-labels')
text(p,64,137,'Name-range',6.2)
text(p,64,145,'index',6.2)
text(p,132,139,'GroupMeta page',6.8)
text(p,205,139,'Object Oₚ',6.2)
strip('name-index',45,149,[11,11,11],[PALE,PALE,PALE],h=16)
text(p,64,173,'(parent, name)',6.2)
p=box('groupmeta-table',87,143,89,23,'white',EDGE,0)
line(p,[(87,154),(176,154)],EDGE,.5)
for x in [114,140]: line(p,[(x,143),(x,166)],EDGE,.5)
text(p,100.5,151,'Name',6.3)
text(p,127,151,'Attrs',6.3)
text(p,158,151,'Locator',6.3)
text(p,100.5,163,'y',6.5)
# Abstract attribute values: no invented literal record or meaningless ellipsis.
line(p,[(119,159),(134,159)],EDGE,.5)
line(p,[(119,162),(130,162)],EDGE,.5)
el(p,'rect',x=150,y=158,width=14,height=5,fill=WARM,stroke=ORANGE,stroke_width=.55)
arrow('index-record',[(78,155),(87,155)],BLUE)
p=box('packed-payload',184,143,40,23,'white',ORANGE)
el(p,'rect',x=188,y=146,width=32,height=17,fill=WARM,stroke=ORANGE,stroke_width=.65)
arrow('locator-frame',[(176,160),(181,160),(181,154.5),(188,154.5)],ORANGE,meaning='resolve authenticated frame descriptor, then reference payload range')
# Matching reference port keeps this producer path out of the ordinary uploader.
p=group('packed-object-id')
text(p,204,153,'Packed',6.2)
text(p,204,160,'frame',6.2)
text(p,178,173,'via descriptor',6.2)
line(p,[(1,176),(239,176)],'#B6C3CD',.45)

# 3. Client object formation precedes, and differs from, backend layout.
title(3,186,'Variable-Granularity Object Storage')
p=box('ordinary-uploader',2,192,103,35,'#F7FAFD','#B5CADD')
text(p,53.5,200,'Ordinary upload · fixed g',6.6)
text(p,13,211,'Slice',6.4)
strip('input-slice',4,215,[19],[PALE],h=7)
p=group('g-configurations')
text(p,32,210,'g₁',7.0)
text(p,32,224,'g₂',7.0)
strip('fine-blocks',39,203,[10,10,10,5],[PALE,PALE,PALE,PALE],h=8)
strip('coarse-blocks',39,217,[20,15],[PALE,PALE],h=8)
text(p,91,209,'tail',6.3)
line(p,[(82,207),(74,207)],EDGE,.5)
text(p,91,223,'tail',6.3)
line(p,[(82,221),(74,221)],EDGE,.5)
arrow('slice-fine',[(23,218),(25,218),(25,207),(28,207)],BLUE)
arrow('slice-coarse',[(25,218),(25,221),(28,221)],BLUE)
p=group('encode-label')
text(p,127,196,'Compress',6.3)
text(p,127,204,'& frame',6.3)
arrow('encode-objects',[(105,212),(151,212)],TEAL,meaning='client-side compression and framing as applicable')
p=group('finalized-objects')
text(p,167,198,'Final length Lₒ',6.4)
line(p,[(151,205),(151,203),(181,203),(181,205)],TEAL,.55)
strip('final-object',151,207,[30],[AQUA],h=10,stroke=TEAL)
# The L_o label is a finalized length, not a g=B=q equality.
p=box('rustfs',121,237,59,18,AQUA,TEAL)
text(p,150.5,245,'RustFS',7.1,bold=True)
text(p,150.5,252,'Layout selection',6.2)
arrow('ordinary-storage',[(173,217),(173,237)],TEAL)
arrow('optional-layout-hint',[(181,203),(185,203),(185,235),(179,235),(179,237)],TEAL,True,'optional B hint from finalized upload length; distinct from independently gated backend q selection')
p=group('hint-label')
text(p,212,198,'Optional B hint',6.2)
text(p,212,207,'h(Lₒ)',6.3)
p=box('u1-reference',122,222,22,11,WARM,ORANGE)
text(p,133,230,'U₁',6.5)
p=box('packed-reference',146,222,22,11,WARM,ORANGE)
text(p,157,230,'Oₚ',6.5)
arrow('private-storage',[(133,233),(133,237)],ORANGE)
arrow('packed-storage',[(157,233),(157,237)],ORANGE)
p=box('persisted-layout',187,215,51,40,'white',EDGE)
text(p,212.5,223,'Persisted layout',6.2)
text(p,212.5,232,'EC block size B',6.2)
text(p,209,240,'Shard span s',6.3)
# Separate hierarchy: B -> shard, then q is a subinterval inside a shard.
arrow('block-to-shard',[(232,234.5),(232,243)],TEAL)
strip('shard-quanta',193,243,[8,32],[AQUA,AQUA],h=5,stroke=TEAL)
p=group('shard-continuation')
for x in [214,217,220]:
    el(p,'circle',cx=x,cy=245.5,r=.4,fill=TEAL)
p=group('q-bracket')
line(p,[(193,249),(193,251),(201,251),(201,249)],TEAL,.55)
text(p,220,253,'Verify/read q',6.2)
arrow('persist-layout',[(180,246),(187,246)],TEAL)

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
