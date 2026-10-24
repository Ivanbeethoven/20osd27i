"""Redraw the image_gen concept as live-text, final-size SVG/PDF.

The B comparison is two supported fixed policies for one illustrative object;
it is not the current automatic policy. No data are plotted in this schematic.
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
from svglib.fonts import get_global_font_map

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'figures/system-architecture-technical'
QA = ROOT/'validation/architecture-technical'
W,H = 504,230
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
INK='#16191C'
BLUE='#326C86'
LOWER='#E5EFF4'
PRIVATE='#F8E4C8'
PRIVATE_EDGE='#936019'
GRAY='#EDF0F2'

def main():
    rl_config.useA85=0
    for font,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:
        pdfmetrics.registerFont(TTFont(font,'C:/Windows/Fonts/'+file))
    pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',
                                 italic='Arial',boldItalic='Arial-Bold')
    get_global_font_map().register_font_family('Arial','C:/Windows/Fonts/arial.ttf',
                                              bold='C:/Windows/Fonts/arialbd.ttf')
    root=ET.Element(f'{{{NS}}}svg',width=f'{W}pt',height=f'{H}pt',viewBox=f'0 0 {W} {H}')
    texts=[]; nodes={}; edges=[]

    def el(p,tag,**a):
        return ET.SubElement(p,f'{{{NS}}}{tag}',{k.replace('_','-'):str(v) for k,v in a.items()})
    def group(ident): return el(root,'g',id=ident)
    def text(p,x,y,s,size=9.5,anchor='middle',bold=False):
        font='Arial-Bold' if bold else 'Arial'
        width=pdfmetrics.stringWidth(s,font,size)
        left=x if anchor=='start' else x-width if anchor=='end' else x-width/2
        assert left>=0 and left+width<=W,(s,left,width)
        t=el(p,'text',x=x,y=y,font_family='Arial',font_size=size,
             font_weight='bold' if bold else 'normal',text_anchor=anchor,fill=INK)
        t.text=s
        texts.append(dict(text=s,size_pt=size,bbox=[left,y-size,width,size]))
    def line(p,pts,color=INK,width=.8,dashed=False):
        a=dict(points=' '.join(f'{x},{y}' for x,y in pts),fill='none',stroke=color,stroke_width=width)
        if dashed:a['stroke_dasharray']='3 2'
        el(p,'polyline',**a)
    def rect(ident,x,y,w,h,fill='white',stroke=INK,width=.8):
        p=group(ident)
        el(p,'rect',x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=width)
        nodes[ident]=[x,y,w,h]
        return p
    def arrow(ident,pts,color=INK,dashed=False,meaning='reference'):
        p=group(ident);line(p,pts,color,1,dashed)
        x,y=pts[-1];u,v=pts[-2];a=math.atan2(y-v,x-u)
        bx,by=x-3.7*math.cos(a),y-3.7*math.sin(a)
        el(p,'polygon',points=f'{x},{y} {bx+1.6*math.sin(a)},{by-1.6*math.cos(a)} {bx-1.6*math.sin(a)},{by+1.6*math.cos(a)}',fill=color)
        edges.append(dict(id=ident,points=pts,meaning=meaning))

    p=group('headings')
    text(p,4,12,'(a) Shared base, private deltas',10.5,'start',True)
    text(p,291,12,'(b) Per-object EC layout',10.5,'start',True)
    line(p,[(280,22),(280,214)],'#B8BEC2',.65)

    for ident,x,labels in [('i',4,['A','B′','C']),('j',146,['A','B','C′'])]:
        p=rect('view:'+ident,x,27,124,60)
        text(p,x+62,41,'Workspace '+ident,10.5,bold=True)
        text(p,x+62,55,'Δᵢ' if ident=='i' else 'Δⱼ',10)
        for k,label in enumerate(labels):
            private='′' in label
            cx=x+6+k*112/3
            q=rect(f'view:{ident}:range:{k}',cx,63,112/3,20,
                   PRIVATE if private else LOWER,width=.7)
            text(q,cx+56/3,77,label,10.5)
            if private:private_cx=cx+56/3
        p=rect('object:'+ident,private_cx-24,98,48,18,PRIVATE,PRIVATE_EDGE)
        text(p,private_cx,111,'Uᵢ' if ident=='i' else 'Uⱼ',10.5)
        arrow('private-ref:'+ident,[(private_cx,83),(private_cx,98)],PRIVATE_EDGE,
              meaning='Data span references an immutable private payload object')
        arrow('pin:'+ident,[(x+12,87),(x+12,145)],BLUE,
              meaning='workspace pins immutable snapshot S, not a read-step sequence')
        p=group('pin-label:'+ident);text(p,x+21,135,'pin S',9.5,'start')

    p=rect('snapshot:S',4,145,266,67)
    text(p,137,158,'Immutable snapshot S',10.5,bold=True)
    p=rect('snapshot:index',14,167,48,20)
    text(p,38,181,'Index',10)
    p=rect('snapshot:record',87,167,173,20)
    text(p,173.5,181,'name | attrs | locator',10)
    arrow('index-record',[(62,177),(87,177)],meaning='representative name-index lookup to GroupMeta record')
    p=group('frame-label');text(p,14,207,'Frames',9.5,'start')
    for k in range(4):
        rect('snapshot:frame:'+str(k),64+k*49,198,49,12,
             '#BCD8E6' if k==3 else LOWER,BLUE,.65)
    arrow('locator-frame',[(234,187),(234,198)],BLUE,
          meaning='locator to authenticated packed frame; other queries may use other indexes')
    p=rect('legend:inherited',14,218,10,9,LOWER,BLUE,.65)
    text(p,30,226,'inherited',9.5,'start')
    p=rect('legend:private',145,218,10,9,PRIVATE,PRIVATE_EDGE,.65)
    text(p,161,226,'private',9.5,'start')

    p=rect('layout:finalized',291,27,78,33)
    text(p,330,41,'Finalized',10)
    text(p,330,54,'object',10)
    p=rect('layout:admit',415,27,85,33)
    text(p,457.5,41,'Admit + persist',9.5)
    text(p,457.5,54,'B, q',10)
    arrow('layout:hint',[(369,44),(415,44)],dashed=True,
          meaning='finalized-length layout hint, pending integration in selected paths')
    p=group('layout:hint-label');text(p,392,36,'hint',9.5)

    p=group('layout:comparison-label')
    text(p,291,78,'Fixed layouts: 1 MiB object',10,'start',True)
    text(p,291,100,'B = 256 KiB',9.5,'start')
    text(p,291,130,'B = 1 MiB',9.5,'start')
    # Equal 140 pt extents are the same 1 MiB byte scale in these two rows.
    for k in range(4):
        rect(f'layout:256k:block:{k}',360+35*k,87,35,20,GRAY,width=.75)
    rect('layout:1m:block',360,117,140,20,GRAY,width=.75)

    p=group('layout:shard-heading')
    line(p,[(291,145),(500,145)],'#B8BEC2',.65)
    text(p,291,157,'Shard detail: B = 256 KiB, EC 2+2',9.5,'start')
    text(p,291,181,'q = 64 KiB',9.5,'start')
    text(p,291,199,'s = 128 KiB',9.5,'start')
    # This is an enlarged geometry inset, not the byte scale above.
    for row,label in enumerate(('D0','D1','P0','P1')):
        y=163+13*row
        p=group('shard-label:'+label);text(p,355,y+8.8,label,9.5,'start')
        for col in range(2):
            p=rect(f'shard:{label}:{col}',379+60.5*col,y,60.5,11,
                   GRAY if row<2 else '#FAFAFA',INK,.65)
            if row==0:text(p,409.25+60.5*col,y+8.8,'q',9.5)
    p=group('layout:read')
    text(p,395.5,227,'Read / repair: stored B, q',9.5)

    OUT.parent.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
    ET.indent(root,space='  ')
    ET.ElementTree(root).write(OUT.with_suffix('.svg'),encoding='utf-8',xml_declaration=True)
    drawing=svg2rlg(str(OUT.with_suffix('.svg')))
    renderPDF._PDFRenderer._font=renderPDF._PDFRenderer._fontName='Arial'
    renderPDF.STATE_DEFAULTS['fontName']='Arial'
    renderPDF.drawToFile(drawing,str(OUT.with_suffix('.pdf')),
                        title='Private deltas, shared snapshot, per-object EC layout')
    doc=pymupdf.open(OUT.with_suffix('.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False).save(OUT.with_suffix('.png'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False).save(QA/'print-size-72dpi.png')
    words=sum(len(t['text'].split()) for t in texts)
    (QA/'scene.json').write_text(json.dumps(dict(width_pt=W,height_pt=H,nodes=nodes,
        text=texts,edges=edges,word_count=words),indent=2),encoding='utf-8')
    print(f'Created {OUT.name}: {W} x {H} pt; {len(texts)} text elements; {words} whitespace words')

if __name__=='__main__':main()
