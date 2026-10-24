"""Mechanism-level BrewFS overview: private maps, packed lookup, stored geometry.

This original vector drawing uses the AI concept only as a composition study.
Byte layouts are schematic supported configurations, never benchmark data.
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
OUT = ROOT/'figures/system-architecture-integrated'
QA = ROOT/'validation/architecture-integrated'
W, H = 504, 230
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
INK, BLUE, LOWER = '#16191C', '#326C86', '#E5EFF4'
AMBER, AMBER_EDGE, GRAY = '#F8E4C8', '#936019', '#EDF0F2'

def main():
    rl_config.useA85 = 0
    for name, file in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf')]:
        pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+file))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold',
                                 italic='Arial', boldItalic='Arial-Bold')
    get_global_font_map().register_font_family('Arial', 'C:/Windows/Fonts/arial.ttf',
                                               bold='C:/Windows/Fonts/arialbd.ttf')
    root = ET.Element(f'{{{NS}}}svg', width=f'{W}pt', height=f'{H}pt', viewBox=f'0 0 {W} {H}')
    texts, nodes, edges = [], {}, []

    def el(parent, tag, **attrs):
        return ET.SubElement(parent, f'{{{NS}}}{tag}',
                             {k.replace('_', '-'): str(v) for k, v in attrs.items()})
    def group(ident):
        return el(root, 'g', id=ident)
    def text(parent, x, y, label, size=9.5, anchor='middle', bold=False):
        subs = {'₁': '1', '₂': '2', 'ₒ': 'o', 'ᵢ': 'i', 'ⱼ': 'j'}
        face = 'Arial-Bold' if bold else 'Arial'
        width = sum(pdfmetrics.stringWidth(subs.get(c, c), face, 9.5 if c in subs else size)
                    for c in label)
        left = x if anchor == 'start' else x-width if anchor == 'end' else x-width/2
        assert 0 <= left and left+width <= W, (label, left, width)
        if any(c in subs for c in label):
            # Explicit live text runs avoid svglib's tspan/anchor differences.
            cursor, normal = left, ''
            runs = []
            for c in label:
                if c in subs:
                    if normal:
                        runs.append((normal, size, 0)); normal = ''
                    runs.append((subs[c], 9.5, 2.4))
                else:
                    normal += c
            if normal:
                runs.append((normal, size, 0))
            for content, font_size, offset in runs:
                lead = len(content)-len(content.lstrip())
                start = cursor+pdfmetrics.stringWidth(content[:lead], face, font_size)
                t = el(parent, 'text', x=start, y=y+offset, font_family='Arial',
                       font_size=font_size, font_weight='bold' if bold else 'normal',
                       text_anchor='start', fill=INK)
                t.text = content.strip()
                cursor += pdfmetrics.stringWidth(content, face, font_size)
        else:
            t = el(parent, 'text', x=x, y=y, font_family='Arial', font_size=size,
                   font_weight='bold' if bold else 'normal', text_anchor=anchor, fill=INK)
            t.text = label
        texts.append(dict(text=label, size_pt=size, bbox=[left, y-size, width, size]))
    def line(parent, pts, color=INK, width=.8, dashed=False):
        attrs = dict(points=' '.join(f'{x},{y}' for x, y in pts), fill='none',
                     stroke=color, stroke_width=width)
        if dashed:
            attrs['stroke_dasharray'] = '3 2'
        el(parent, 'polyline', **attrs)
    def rect(ident, x, y, w, h, fill='white', stroke=INK, width=.8):
        p = group(ident)
        el(p, 'rect', x=x, y=y, width=w, height=h, fill=fill, stroke=stroke, stroke_width=width)
        nodes[ident] = [x, y, w, h]
        return p
    def arrow(ident, pts, color=INK, dashed=False, meaning='reference'):
        p = group(ident)
        line(p, pts, color, 1, dashed)
        x, y = pts[-1]; u, v = pts[-2]
        a = math.atan2(y-v, x-u)
        bx, by = x-3.7*math.cos(a), y-3.7*math.sin(a)
        el(p, 'polygon', points=f'{x},{y} {bx+1.6*math.sin(a)},{by-1.6*math.cos(a)} {bx-1.6*math.sin(a)},{by+1.6*math.cos(a)}', fill=color)
        edges.append(dict(id=ident, points=pts, meaning=meaning))
    def agent(ident, x, y):
        p = group(ident)
        el(p, 'rect', x=x, y=y+3, width=14, height=11, rx=1.4,
           fill='white', stroke=INK, stroke_width=.9)
        line(p, [(x+7, y), (x+7, y+3)], width=.9)
        for cx in (x+4.3, x+9.7):
            el(p, 'circle', cx=cx, cy=y+8, r=1, fill=INK)
        line(p, [(x+5, y+11), (x+9, y+11)], width=.7)

    # Private state stays outside S. Both views bind the same snapshot.
    for key, x, labels in [('i', 66, ['S', 'Uᵢ', 'S']), ('j', 288, ['S', 'S', 'Uⱼ'])]:
        sub = 'ᵢ' if key == 'i' else 'ⱼ'
        agent('agent:'+key, x+43, 1)
        p = group('agent-label:'+key)
        text(p, x+64, 13, 'Agent '+key, 10, 'start')
        arrow('agent-access:'+key, [(x+75, 16), (x+75, 23)],
              meaning='external agent accesses its private logical view')
        p = rect('workspace:'+key, x, 23, 150, 45)
        text(p, x+75, 36, f'W{sub} = Resolve(S, Δ{sub})', 10)
        for col, label in enumerate(labels):
            private = label != 'S'
            cx = x+6+44*col
            q = rect(f'map:{key}:{col}', cx, 45, 44, 18,
                     AMBER if private else LOWER, AMBER_EDGE if private else BLUE, .7)
            text(q, cx+22, 57, label, 10.5)
            if private:
                private_x = cx+22
        p = rect('private-payload:'+key, private_x-19, 78, 38, 18, AMBER, AMBER_EDGE)
        text(p, private_x, 90, 'U'+sub, 10.5)
        arrow('private-reference:'+key, [(private_x, 63), (private_x, 78)], AMBER_EDGE,
              meaning='Data mapping points to private object, outside shared S')
        arrow('snapshot-binding:'+key, [(x+28, 63), (x+28, 101)], BLUE,
              meaning='explicit lower reference resolved against the same pinned snapshot')
        p = group('pin-label:'+key)
        text(p, x+20, 94, 'pin S', 9.5, 'end')
    p = group('range-map-label')
    text(p, 4, 56, 'Range maps', 9.5, 'start')

    # One shared snapshot contains the packed access structure and object identities.
    p = rect('snapshot:S', 4, 101, 496, 59)
    text(p, 14, 114, 'Shared snapshot S', 10.5, 'start', True)
    text(p, 16, 128, 'Packed metadata', 10, 'start')
    p = group('packed-record:back')
    line(p, [(190, 140), (194, 140), (194, 156), (20, 156), (20, 152)], '#A0B4BF', .65)
    for col, label in enumerate(('name', 'attrs', 'locator')):
        p = rect('packed-record:'+label, 16+58*col, 134, 58, 18, LOWER, BLUE, .7)
        text(p, 45+58*col, 146.5, label, 9.5)

    for key, x in [('1', 238), ('2', 378)]:
        sub = '₁' if key == '1' else '₂'
        p = rect('packed-object:O'+key, x, 121, 114, 31)
        text(p, x+57, 132, 'O'+sub, 10.5)
        for col in range(3):
            rect(f'packed-frame:{key}:{col}', x+6+34*col, 139, 34, 10,
                 '#BCD8E6' if key == '1' and col == 0 else LOWER, BLUE, .65)
    arrow('locator-frame', [(190, 144), (244, 144)], BLUE,
          meaning='representative packed record locates a frame within O1')
    p = group('frame-label')
    text(p, 215, 136, 'frame', 9.5)

    # The entire objects project to their own physical representations.
    # These are identity connectors, not execution/data-conversion arrows.
    p = group('same-object-projections')
    for key, x in [('1', 238), ('2', 378)]:
        for edge_x in (x, x+114):
            line(p, [(edge_x, 152), (edge_x, 181)], '#909BA2', .65)
        edges.append(dict(id='same-object:O'+key,
            points=[[x, 152], [x, 181], [x+114, 152], [x+114, 181]],
            meaning='whole logical O'+key+' and its stored physical representation; no read-time transformation'))
    text(p, 14, 173, 'Same objects, stored layouts', 9.5, 'start')

    # The backend band spans the same width as S; geometry columns stay aligned.
    p = rect('backend:RustFS', 4, 177, 496, 49)
    text(p, 14, 190, 'RustFS · stored (Bₒ, qₒ)', 10.5, 'start', True)
    for key, x, n in [('1', 238, 4), ('2', 378, 1)]:
        sub = '₁' if key == '1' else '₂'
        for col in range(n):
            q = rect(f'coding-block:{key}:{col}', x+114/n*col, 181, 114/n, 20,
                     GRAY, INK, .7)
            if col == 0:
                text(q, x+57/n, 194, 'B'+sub, 10)
    p = group('stripe-shard-label')
    text(p, 238, 218, 's = B₁/d', 9.5, 'start')
    for col in range(2):
        p = rect('verification-quantum:'+str(col), 290+31*col, 208, 31, 15,
                 GRAY, INK, .7)
        text(p, 305.5+31*col, 217, 'q₁', 9.5)

    # Creation is a compact side branch, not a step on the read path.
    p = group('upload-policy')
    text(p, 14, 215, 'finalized Lₒ', 9.5, 'start')
    arrow('upload-hint', [(78, 210), (146, 210)], dashed=True,
          meaning='configured B hint at finalized upload; selected integration is pending')
    text(p, 112, 203, 'client B hint', 9.5)
    p = rect('admission', 146, 200, 44, 20)
    text(p, 168, 214, 'admit', 9.5)
    arrow('persist-admitted-layout', [(190, 210), (218, 210), (218, 191), (238, 191)],
          meaning='RustFS admits B, chooses compatible q, and persists object layout')
    p = group('read-repair')
    text(p, 378, 220, 'Read / repair', 9.5, 'start')
    arrow('read-stored-layout', [(453, 216), (480, 216), (480, 201)],
          meaning='read and repair interpret the stored object layout without new admission')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(OUT.with_suffix('.svg'), encoding='utf-8', xml_declaration=True)
    drawing = svg2rlg(str(OUT.with_suffix('.svg')))
    renderPDF._PDFRenderer._font = renderPDF._PDFRenderer._fontName = 'Arial'
    renderPDF.STATE_DEFAULTS['fontName'] = 'Arial'
    renderPDF.drawToFile(drawing, str(OUT.with_suffix('.pdf')),
                        title='Shared snapshot, packed access, and per-object storage in one hierarchy')
    doc = pymupdf.open(OUT.with_suffix('.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(3, 3), alpha=False).save(OUT.with_suffix('.png'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False).save(QA/'print-size-72dpi.png')
    words = sum(len(t['text'].split()) for t in texts)
    (QA/'scene.json').write_text(json.dumps(dict(width_pt=W, height_pt=H, nodes=nodes,
        text=texts, edges=edges, word_count=words,
        alignment=dict(workspaces='equal dimensions and range coordinates',
                       layout_rows='O1/O2: common 114 pt extent; logical/physical x coordinates identical',
                       exemption='shard is an enlarged geometry inset, not the object byte scale')),
        indent=2), encoding='utf-8')
    print(f'Created {OUT.name}: {W} x {H} pt; {len(texts)} labels; {words} whitespace words')

if __name__ == '__main__':
    main()
