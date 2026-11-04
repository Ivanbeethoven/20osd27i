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
# Keep the lower panels' internal coordinates and translate the row as a unit.
ROW_GAP = 11
ROW_TOP = 84 + ROW_GAP
BUS_Y = 84 + ROW_GAP // 2
LOWER_DY = ROW_TOP - 107
W, H = 240, 280 + LOWER_DY
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
layer, scene_dy = root, 0  # Scene records use final canvas coordinates.

def el(p, tag, **attrs):
    return ET.SubElement(p, '{'+NS+'}'+tag, {k.replace('_', '-'):str(v) for k,v in attrs.items()})

def group(ident):
    return el(layer, 'g', id=ident)

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
    records.append(dict(text=value, group=p.get('id'), size_pt=size, bbox=[left, y+scene_dy-size, left+width, y+scene_dy+1.5]))
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
    edges.append(dict(id=ident,points=[(px,py+scene_dy) for px,py in pts],meaning=meaning))

def box(ident, x, y, w, h, fill='white', stroke=EDGE, radius=2):
    p=group(ident)
    el(p,'rect',x=x,y=y,width=w,height=h,rx=radius,fill=fill,stroke=stroke,stroke_width=.65)
    nodes[ident]=[x,y+scene_dy,w,h]
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
arrow('agent-fuse',[(48,9),(80,9)],INK,meaning='file operations enter the FUSE node')
p=box('fuse-entry',80,1,32,13,GRAY,EDGE)
text(p,96,11,'FUSE',8.0,bold=True)
p=group('fuse-view-junction')
line(p,[(96,14),(96,18)],INK,.75)
el(p,'circle',cx=96,cy=18,r=1.0,fill=INK)
edges.append(dict(id='fuse-to-view-choice',points=[(96,14),(96,18)],meaning='continuous connection from FUSE to the ordinary/workspace view choice'))
arrow('fuse-workspace',[(96,18),(96,21)],INK,meaning='select workspace view composition')
arrow('workspace-bypass',[(96,18),(10,18),(10,BUS_Y),(35,BUS_Y)],INK,meaning='an ordinary volume reaches the shared metadata and data paths without workspace composition')
# Match the mechanism badges using vector circles, without relying on a font's
# circled-digit glyphs. The dashed border marks this as a legend, not a stage.
p=group('optional-mechanisms-legend')
el(p,'rect',x=129,y=1,width=108,height=15,rx=2,fill='white',stroke=EDGE,stroke_width=.6,stroke_dasharray='2.5 1.8')
nodes['optional-mechanisms-legend']=[129,1,108,15]
for number,x in [(1,135),(2,146),(3,157)]:
    el(p,'circle',cx=x,cy=8.5,r=4.2,fill=INK)
    text(p,x,11,str(number),7.0,bold=True,color='white')
text(p,165,11,'independently optional',7.0,anchor='start')
p=box('workspace-choice',24,21,212,63,'white',EDGE)
el(p,'circle',cx=33,cy=30,r=5,fill=INK)
text(p,33,33.1,'1',8,bold=True,color='white')
text(p,41,32,'Delta-Based Workspaces (§4)',8.5,anchor='start',bold=True)
text(p,228,32,'Private state first',7.0,anchor='end',color='#7F3D1B')
for idx,x in [(1,31),(2,133)]:
    p=box(f'workspace-view-{idx}',x,39,95,23,WARM,ORANGE)
    text(p,x+47.5,48,'View 1' if idx==1 else 'View 2',7.1,bold=True)
    text(p,x+47.5,58.5,'Private changes',7.0,color='#7F3D1B')
p=group('pinned-baseline-references')
line(p,[(78.5,62),(78.5,69)],BLUE,.75)
line(p,[(180.5,62),(180.5,69)],BLUE,.75)
p=box('shared-baseline',31,69,197,12,BLUE,BLUE)
text(p,129.5,77.5,'Pinned shared immutable baseline',7.0,bold=True,color='white')
p=group('common-file-interfaces')
line(p,[(35,BUS_Y),(184,BUS_Y)],INK,.8)
line(p,[(130,84),(130,BUS_Y)],INK,.8)
el(p,'circle',cx=130,cy=BUS_Y,r=1.2,fill=INK)
arrow('metadata-access',[(60,BUS_Y),(60,ROW_TOP)],BLUE,meaning='both ordinary and workspace views expose metadata access; representation remains optional')
arrow('data-access',[(184,BUS_Y),(184,ROW_TOP)],TEAL,meaning='both view types expose data access; each producer retains its own upload contract')

# 2 and 3 are parallel choices, with explicit default alternatives.
layer=el(root,'g',id='metadata-and-data-row',transform=f'translate(0 {LOWER_DY})')
scene_dy=LOWER_DY
p=box('metadata-choice',4,107,112,161,'white','#B8C8D4')
el(p,'circle',cx=12,cy=116,r=5,fill=INK)
text(p,12,119.1,'2',8,bold=True,color='white')
text(p,21,119,'Packed Metadata (§5)',8.5,anchor='start',bold=True)
# A fixed version is built once; a running lookup enters at the index.
# Use exact inclusive name bounds for one parent in the worked example.
p=group('version-build')
text(p,10,131,'Publish once per version',7.5,anchor='start',bold=True)
text(p,10,143,'Fixed tree',7.2,anchor='start')
arrow('build-index-and-pages',[(46,140.5),(58,140.5)],EDGE,
      meaning='build and publish the name-range index and packed pages from one consistent directory version')
text(p,62,143,'Index + pages',7.2,anchor='start')
line(p,[(10,150),(110,150)],'#B8C8D4',.55)
p=group('lookup-key')
text(p,10,163,'Find cat in D',7.3,anchor='start',bold=True)
arrow('lookup-index',[(57,160.5),(65,160.5)],BLUE,
      meaning='a live query submits the parent directory identity D and the raw name cat to the pinned index')
p=box('name-range-index',65,154,45,13,PALE,BLUE)
text(p,87.5,163,'Range index',7.0)
arrow('index-page',[(87.5,167),(87.5,172),(60,172),(60,184)],BLUE,
      meaning='the authenticated reference identifies the object, metadata offset, length, and digest for cat through dog')
p=group('packed-object-label')
text(p,10,179,'Packed object',7.3,anchor='start')
p=box('packed-object',10,184,100,16,GRAY,EDGE,0)
el(p,'rect',x=41,y=184,width=38,height=16,fill=BLUE,stroke=BLUE,stroke_width=.75)
for x,label in [(25.5,'ant–bee'),(94.5,'eel–fox')]:
    text(p,x,194.5,label,7.0)
text(p,60,194.5,'cat–dog',7.5,bold=True,color='white')
# These leaders enlarge the selected byte range. They are not data-flow edges.
p=group('enlarge-one-page')
line(p,[(41,200),(10,212)],BLUE,.65)
line(p,[(79,200),(110,212)],BLUE,.65)
p=box('joint-metadata-page',10,212,100,48,'white',BLUE,0)
text(p,60,222,'Verified metadata page',7.5,bold=True)
line(p,[(10,225),(110,225)],BLUE,.5)
el(p,'rect',x=10.5,y=237,width=99,height=11.5,fill=PALE)
el(p,'rect',x=10.5,y=237,width=1.7,height=11.5,fill=BLUE)
for x in (39,70): line(p,[(x,225),(x,260)],'#A4B3BE',.4)
for y in (237,248.5): line(p,[(10,y),(110,y)],'#A4B3BE',.4)
for x,label in [(24.5,'Name'),(54.5,'Size'),(90,'Data ref.')]:
    text(p,x,233.5,label,7.0)
for y,name,size,ref,selected in [(245.3,'cat','4 KiB','A',True),(256.8,'dog','8 KiB','B',False)]:
    for x,val in [(24.5,name),(54.5,size),(90,ref)]:
        text(p,x,y,val,7.2,bold=selected)

p=box('granularity-choice',124,107,112,161,'white','#B8C8D4')
el(p,'circle',cx=132,cy=116,r=5,fill=INK)
text(p,132,119.1,'3',8,bold=True,color='white')
text(p,141,119,'Variable-Granularity',8.5,anchor='start',bold=True)
text(p,141,129,'Object Storage (§6)',8.5,anchor='start',bold=True)
# Different files form objects under one fixed volume geometry. Backend B
# choices below are alternatives for eligible objects, not an automatic
# per-file policy or different g values within the same mounted volume.
p=box('ordinary-uploader',128,136,104,46,'white',EDGE)
text(p,180,144,'BrewFS uploader · fixed g',7.2,bold=True)
text(p,149,158,'Files',7.5)
text(p,149,176,'Objects',7.5)
for ident,x in [('source-file-a',178),('source-file-b',216)]:
    p=group(ident)
    el(p,'polygon',points=f'{x},149 {x+8},149 {x+12},153 {x+12},162 {x},162',fill='white',stroke=TEAL,stroke_width=.7)
    line(p,[(x+8,149),(x+8,153),(x+12,153)],TEAL,.6)
    for yy in [156,159]: line(p,[(x+3,yy),(x+9,yy)],TEAL,.6)
arrow('file-a-objects',[(184,162),(184,169)],TEAL,meaning='one example file forms a short object under fixed g, after applicable formatting')
arrow('file-b-objects',[(222,162),(222,169)],TEAL,meaning='another file can form multiple objects under the same fixed g; no per-file g selection')
box('file-a-object',176,169,16,8,AQUA,TEAL,0)
for i,(x,w) in enumerate([(207,7),(215.5,7),(224,5)]):
    box(f'file-b-object-{i}',x,169,w,8,AQUA,TEAL,0)
# Payload transfer is unconditional; only the B hint is optional. They cross
# the client/backend boundary separately, before RustFS admits a layout.
arrow('layout-hint',[(158,182),(158,200)],ORANGE,True,meaning='optional client hint requests B; RustFS admits or retains the default; q is not a client hint')
arrow('object-upload',[(216,182),(216,200)],TEAL,meaning='formed object bytes are uploaded with or without a block-size hint')
p=group('client-backend-interface')
text(p,154,193.5,'Hint B',7.0,anchor='end',color='#7F3D1B')
text(p,212,193.5,'Bytes',7.0,anchor='end')
p=box('backend-layout-scope',128,200,104,64,'#F8FAFB',TEAL)
el(p,'rect',x=128,y=200,width=104,height=13,rx=2,fill=TEAL)
text(p,180,209.5,'RustFS optimizations',7.5,bold=True,color='white')
text(p,180,220,'Per-object block size B',7.0)
# Equal object extents compare two B choices. Both retain an unpadded tail.
# No file lane maps to a particular B, and no numerical policy is claimed.
strip('object-small-b-choice',136,225,[10,10,10,5],[PALE,GRAY,GRAY,GRAY],h=10,stroke=TEAL)
strip('object-large-b-choice',190,225,[20,15],[PALE,GRAY],h=10,stroke=TEAL)
p=group('coding-layout-labels')
text(p,141,232.5,'B',7.5,bold=True)
text(p,200,232.5,'B',7.5,bold=True)
text(p,180,232.5,'or',7.0)
# Expand one complete coding block only. The shard count and all backend
# dimensions are schematic; q remains within a shard, not within object bytes.
p=group('erasure-code-fanout')
line(p,[(141,235),(141,241),(224,241)],TEAL,.7)
arrow('coding-to-shard-example',[(186,241),(186,250)],TEAL,meaning='backend erasure coding of the selected B block produces shard pieces')
arrow('coding-to-other-shards',[(224,241),(224,250)],TEAL,meaning='additional data/parity shards; count and coding geometry are abstracted')
for ident,x in [('shard-example',180),('other-shard-example',218)]:
    p=box(ident,x,250,12,10,GRAY,TEAL,0)
    if ident=='shard-example':
        el(p,'rect',x=x,y=250,width=12,height=5,fill=BLUE)
        line(p,[(x,255),(x+12,255)],TEAL,.55)
p=group('additional-shards')
for x in [201,204,207]: el(p,'circle',cx=x,cy=255,r=.65,fill=TEAL)
p=group('shard-read-quantum')
line(p,[(179,250),(176,250),(176,255),(179,255)],TEAL,.6)
text(p,173,256,'Verify unit q',7.0,anchor='end')
line(p,[(174,252.5),(176,252.5)],TEAL,.6)
text(p,204,248,'Shards',7.0)

# Persisted layout is shared infrastructure, outside the optional view/format choices.
p=box('backend',4,272,232,8,TEAL,TEAL)
text(p,120,278.3,'Stored objects · layout retained for reads and repair',7.0,color='white')
arrow('packed-object-storage',[(110,192),(113,192),(113,272)],BLUE,
      meaning='the physical pack resides in the object store; a metadata lookup ends at the verified record and does not follow its data reference')
arrow('encoded-object-storage',[(224,260),(224,272)],TEAL,meaning='encoded objects retain their effective backend layout for subsequent reads and repair; B and q have independent admission gates')


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
