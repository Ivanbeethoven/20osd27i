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
OUT = ROOT/'figures/system-architecture-mechanism'
QA = ROOT/'validation/architecture-mechanism'
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

    p = group('titles')
    text(p, 4, 12, 'Private views over shared state', 10.5, 'start', True)
    text(p, 313, 12, 'Object-bound layout', 10.5, 'start', True)

    for key, x, labels in [('i', 4, ['S', 'Uᵢ', 'S']), ('j', 149, ['S', 'S', 'Uⱼ'])]:
        sub = 'ᵢ' if key == 'i' else 'ⱼ'
        agent('agent:'+key, x+24, 23)
        p = group('agent-label:'+key)
        text(p, x+45, 35, 'Agent '+key, 10, 'start')
        arrow('agent-access:'+key, [(x+65, 39), (x+65, 51)],
              meaning='external agent accesses its own logical workspace; return omitted')
        p = rect('workspace:'+key, x, 51, 129, 60)
        text(p, x+64.5, 64, f'W{sub} = Resolve(S, Δ{sub})', 10)
        text(p, x+64.5, 78, 'Range map', 9.5)
        # Equal coordinates in both maps; every inherited cell is explicitly S.
        for col, label in enumerate(labels):
            private = label != 'S'
            cx = x+6+col*39
            q = rect(f'map:{key}:{col}', cx, 83, 39, 19,
                     AMBER if private else LOWER, AMBER_EDGE if private else BLUE, .7)
            text(q, cx+19.5, 95.5, label, 10.5)
            if private:
                private_x = cx+19.5
        p = rect('private-payload:'+key, private_x-21, 123, 42, 18, AMBER, AMBER_EDGE)
        text(p, private_x, 136, 'U'+sub, 10.5)
        arrow('private-reference:'+key, [(private_x, 102), (private_x, 123)], AMBER_EDGE,
              meaning='Data mapping references a separate private payload object')
        arrow('snapshot-reference:'+key, [(x+25.5, 102), (x+25.5, 160)], BLUE,
              meaning='explicit inherited range is resolved against pinned immutable S')
        p = group('pin-label:'+key)
        text(p, x+34, 153, 'pin S', 9.5, 'start')

    p = rect('snapshot:S', 4, 160, 274, 66)
    text(p, 141, 174, 'Shared packed snapshot S', 10.5, bold=True)
    # A stacked joint-record motif, not a fixed GET-count traversal.
    p = group('packed-record:back')
    line(p, [(164, 196), (168, 196), (168, 215), (18, 215), (18, 209)], '#A0B4BF', .65)
    for col, label in enumerate(('name', 'attrs', 'locator')):
        p = rect('packed-record:'+label, 14+50*col, 190, 50, 19, LOWER, BLUE, .7)
        text(p, 39+50*col, 203, label, 9.5)
    p = rect('packed-object:O1', 211, 182, 58, 33)
    text(p, 240, 194, 'O₁', 10.5)
    for col in range(3):
        rect('packed-frame:'+str(col), 215+col*16.67, 199, 16.67, 11,
             '#BCD8E6' if col == 0 else LOWER, BLUE, .65)
    arrow('locator-frame', [(164, 201), (215, 201)], BLUE,
          meaning='representative joint metadata record points to an authenticated frame')
    p = group('packed-frame-label')
    text(p, 188, 192, 'frame', 9.5)

    p = rect('finalized:O1', 313, 26, 84, 34)
    text(p, 355, 40, 'Finalized O₁', 10)
    text(p, 355, 53, 'length L₁', 9.5)
    p = rect('rustfs-admit-persist', 432, 26, 68, 34)
    text(p, 466, 40, 'Admit +', 10)
    text(p, 466, 53, 'persist', 10)
    text(p, 466, 22, 'RustFS', 9.5)
    arrow('finalized-hint', [(397, 45), (432, 45)], dashed=True,
          meaning='B hint derived from finalized wire length; selected wiring remains incomplete')
    p = group('hint-label')
    text(p, 414.5, 35, 'B hint', 9.5)
    arrow('persist-effective-layout', [(466, 60), (466, 80)],
          meaning='RustFS validates B and chooses compatible q, then persists effective geometry')

    p = rect('stored-layouts', 313, 80, 187, 132)
    text(p, 406.5, 94, 'Stored layouts (Bₒ, qₒ)', 10.5, bold=True)
    for key, y, n in [('1', 103, 4), ('2', 132, 1)]:
        p = group('object-label:O'+key)
        sub = '₁' if key == '1' else '₂'
        text(p, 329, y+13, 'O'+sub, 10)
        for col in range(n):
            q = rect(f'coding-block:{key}:{col}', 348+140/n*col, y, 140/n, 18,
                     GRAY, INK, .7)
            if col == 0:
                text(q, 348+70/n, y+13, 'B'+sub, 10)
    p = group('shard-heading')
    line(p, [(325, 158), (488, 158)], '#B8BEC2', .65)
    text(p, 325, 171, 'Stripe shard: s = B₁/d', 9.5, 'start')
    for col in range(2):
        p = rect('verification-quantum:'+str(col), 325+81.5*col, 178, 81.5, 15,
                 GRAY, INK, .7)
        text(p, 365.75+81.5*col, 187, 'q₁', 9.5)
    p = group('geometry-key')
    text(p, 406.5, 205, 'B: encode · q: verify', 9.5)

    # Non-directional representation connector anchors the WHOLE object, not a frame.
    p = group('same-object-representation')
    line(p, [(269, 203), (292, 203), (292, 112), (313, 112)], '#6A747B', .8)
    text(p, 292, 105, 'O₁', 9.5)
    edges.append(dict(id='same-object-representation', points=[[269, 203], [292, 203], [292, 112], [313, 112]],
                      meaning='whole O1 represented with persisted physical layout; not an I/O step'))
    p = group('read-repair-label')
    text(p, 313, 227, 'Read / repair', 10, 'start')
    arrow('read-stored-layout', [(399, 223), (466, 223), (466, 212)],
          meaning='read and repair interpret stored layout, never reselect from the current hint')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(OUT.with_suffix('.svg'), encoding='utf-8', xml_declaration=True)
    drawing = svg2rlg(str(OUT.with_suffix('.svg')))
    renderPDF._PDFRenderer._font = renderPDF._PDFRenderer._fontName = 'Arial'
    renderPDF.STATE_DEFAULTS['fontName'] = 'Arial'
    renderPDF.drawToFile(drawing, str(OUT.with_suffix('.pdf')),
                        title='Private views, packed shared state, object-bound layouts')
    doc = pymupdf.open(OUT.with_suffix('.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(3, 3), alpha=False).save(OUT.with_suffix('.png'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False).save(QA/'print-size-72dpi.png')
    words = sum(len(t['text'].split()) for t in texts)
    (QA/'scene.json').write_text(json.dumps(dict(width_pt=W, height_pt=H, nodes=nodes,
        text=texts, edges=edges, word_count=words,
        alignment=dict(workspaces='equal dimensions and range coordinates',
                       layout_rows='common 140 pt object-byte extent',
                       exemption='shard is an enlarged geometry inset, not the object byte scale')),
        indent=2), encoding='utf-8')
    print(f'Created {OUT.name}: {W} x {H} pt; {len(texts)} labels; {words} whitespace words')

if __name__ == '__main__':
    main()
