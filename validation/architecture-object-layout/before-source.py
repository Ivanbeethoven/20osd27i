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

# 1. Both view types feed common metadata/data interfaces. Workspaces are optional.
p=group('common-entry')
agent('agents',10,10,INK)
text(p,32,12,'Agents',7.5)
arrow('agent-fuse',[(48,9),(79,9)],INK,meaning='file operations through FUSE')
text(p,96,12,'FUSE',8.0,bold=True)
text(p,189,12,'1–3 independently optional',7.0)
line(p,[(96,16),(27.5,16),(27.5,46)],INK,.7)
arrow('fuse-workspace',[(96,16),(150,16),(150,21)],INK,meaning='select workspace view composition')
arrow('fuse-ordinary',[(27.5,42),(27.5,46)],INK,meaning='retain an ordinary volume without workspace composition')
p=box('ordinary-volume',4,46,47,25,GRAY,EDGE)
text(p,27.5,56,'Ordinary',7.3)
text(p,27.5,65,'volume',7.3)
p=group('view-alternative')
text(p,57.5,61,'or',7.0)
p=box('workspace-choice',64,21,172,63,'white',EDGE)
el(p,'circle',cx=73,cy=30,r=5,fill=INK)
text(p,73,33.1,'1',8,bold=True,color='white')
text(p,81,31,'Delta-Based Multi-Agent',8.5,anchor='start',bold=True)
text(p,81,41.5,'Workspaces',8.5,anchor='start',bold=True)
text(p,191,41.5,'Private state first',7.0,color='#7F3D1B')
for idx,x in [(1,71),(2,153)]:
    p=box(f'workspace-view-{idx}',x,45,75,20,WARM,ORANGE)
    text(p,x+37.5,51.5,'View W₁' if idx==1 else 'View W₂',7.1,bold=True)
    text(p,x+37.5,61.5,'Private state Δ₁' if idx==1 else 'Private state Δ₂',7.0,color='#7F3D1B')
p=group('pinned-baseline-references')
line(p,[(108.5,65),(108.5,71)],BLUE,.75)
line(p,[(190.5,65),(190.5,71)],BLUE,.75)
p=box('shared-baseline',71,71,157,10,BLUE,BLUE)
text(p,149.5,78.5,'Pinned shared immutable S',7.0,bold=True,color='white')
p=group('common-file-interfaces')
line(p,[(27.5,71),(27.5,93),(184,93)],INK,.8)
line(p,[(150,84),(150,93)],INK,.8)
el(p,'circle',cx=150,cy=93,r=1.2,fill=INK)
arrow('metadata-access',[(60,93),(60,107)],BLUE,meaning='both ordinary and workspace views expose metadata access; representation remains optional')
arrow('data-access',[(184,93),(184,107)],TEAL,meaning='both view types expose data access; each producer retains its own upload contract')

# 2 and 3 are parallel choices, with explicit default alternatives.
p=box('metadata-choice',4,107,112,141,'white','#B8C8D4')
el(p,'circle',cx=12,cy=116,r=5,fill=INK)
text(p,12,119.1,'2',8,bold=True,color='white')
text(p,21,119,'Packed Metadata',8.5,anchor='start',bold=True)
text(p,60,130,'Metadata access',7.0,color=BLUE)
p=box('native-records',8,137,50,14,GRAY,EDGE)
text(p,33,147,'Native records',7.0)
p=box('packed-records',68,137,44,14,PALE,BLUE)
text(p,90,147,'Packed',7.2,bold=True)
p=group('metadata-alternative')
text(p,63,147,'or',7.0)
p=box('readonly-mount',7,154,38,21,'white',BLUE)
text(p,26,162,'Read-only',7.0)
text(p,26,171,'mount',7.0)
arrow('readonly-entry',[(45,164.5),(51,164.5)],BLUE,meaning='standalone read-only access does not require a workspace or native metadata')
arrow('packed-index',[(90,151),(90,156)],BLUE)
p=box('name-range-index',51,156,59,20,PALE,BLUE)
text(p,80.5,164,'Name-range',7.0)
text(p,80.5,172.5,'index · /src',7.0)
arrow('index-page',[(80.5,176),(80.5,180)],BLUE,meaning='select a bounded joint-metadata page by directory and raw-name range')
p=box('joint-metadata-page',10,180,100,40,'white',BLUE)
text(p,60,189,'Joint metadata page',7.0,bold=True)
p=box('joint-records',12,193,96,24,'white',EDGE,0)
el(p,'rect',x=12,y=202,width=96,height=10,fill=PALE)
for x in [40,78]: line(p,[(x,193),(x,217)],EDGE,.5)
for y in [202,212]: line(p,[(12,y),(108,y)],EDGE,.5)
text(p,26,200,'Name',7.0)
text(p,59,200,'Attributes',7.0)
text(p,93,200,'Data ref.',7.0)
text(p,26,209.5,'main.py',7.0)
text(p,59,209.5,'size',7.0)
el(p,'rect',x=89,y=205,width=8,height=4,fill=BLUE)
for a,b in [(17,34),(45,71),(84,102)]: line(p,[(a,215),(b,215)],EDGE,.55)
p=box('referenced-bytes',10,230,100,12,PALE,BLUE)
text(p,60,238.5,'Referenced file bytes',7.0)
arrow('record-bytes',[(108,207),(119,207),(119,236),(110,236)],BLUE,meaning='reference existing file bytes, with descriptor resolution abstracted; never feed an upload slice')

p=box('granularity-choice',124,107,112,141,'white','#B8C8D4')
el(p,'circle',cx=132,cy=116,r=5,fill=INK)
text(p,132,119.1,'3',8,bold=True,color='white')
text(p,141,119,'Variable-Granularity',8.5,anchor='start',bold=True)
text(p,141,129,'Object Storage',8.5,anchor='start',bold=True)
# Compare the same raw slice under two FIXED configurations, not a time-varying
# policy. Values are illustrative raw MiB, never compressed object lengths.
p=group('ordinary-uploader')
text(p,180,145,'Ordinary upload · fixed g',7.5,bold=True)
text(p,149,171,'Written slice',7.0)
strip('same-written-slice',175,166,[55],[GRAY],h=8,stroke=TEAL)
p=group('same-slice-length')
text(p,202.5,172.3,'10 MiB',7.5)
p=group('fixed-configurations')
line(p,[(175,170),(171,170),(171,207)],TEAL,.65)
arrow('fixed-g-4',[(171,188),(175,188)],TEAL,meaning='alternative fixed g=4 MiB applied to the same 10 MiB raw slice')
arrow('fixed-g-8',[(171,207),(175,207)],TEAL,meaning='alternative fixed g=8 MiB applied to the same raw slice; no runtime adaptation')
for ident,y,g,parts in [('fine-blocks',183,4,[4,4,2]),('coarse-blocks',202,8,[8,2])]:
    p=group(ident+'-label')
    text(p,148,y+7.5,f'g = {g} MiB',7.7,bold=True)
    if g==4:
        text(p,148,199,'default',7.0,color=TEAL)
    strip(ident,175,y,[v*5.5 for v in parts],[AQUA]*len(parts),h=10,stroke=TEAL)
    p=group(ident+'-raw-values')
    pos=175
    for j,value in enumerate(parts):
        text(p,pos+value*2.75,y+7.5,str(value),7.8,bold=True)
        pos+=value*5.5
p=group('object-formation-label')
text(p,180,222,'Block → object',7.3)
p=box('optional-b-hint',129,229,43,14,GRAY,TEAL)
text(p,150.5,238.8,'B hint',7.5)
p=box('backend-q-policy',181,229,46,14,GRAY,TEAL)
text(p,204,238.8,'q policy',7.5)

# Persisted layout is shared infrastructure, outside the optional view/format choices.
p=box('backend',4,250,232,8,TEAL,TEAL)
text(p,25,256.3,'RustFS',7.0,bold=True,color='white')
text(p,95,256.3,'EC block B',7.0,color='white')
text(p,190,256.3,'Per-shard verify/read q',7.0,color='white')
arrow('referenced-storage',[(60,242),(60,250)],BLUE,meaning='referenced file bytes are stored objects; reference is not an upload action')
arrow('ordinary-storage',[(222,220),(233,220),(233,250)],TEAL,meaning='formed objects use effective persisted backend layouts, independently of the illustrated client partition')
arrow('b-hint-control',[(150.5,243),(150.5,250)],TEAL,True,meaning='optional client B hint is validated by the backend; it does not set q')
arrow('q-policy-control',[(204,243),(204,250)],TEAL,True,meaning='backend q policy has separate compatibility and geometry gates')


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
