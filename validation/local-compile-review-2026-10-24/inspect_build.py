from pathlib import Path
import hashlib
import json
import re
import fitz

root = Path(__file__).resolve().parents[2]
audit = Path(__file__).resolve().parent
pdf_path = root / 'main.pdf'
doc = fitz.open(pdf_path)
log = (root / 'main.log').read_text(encoding='utf-8', errors='replace')
aux = (root / 'main.aux').read_text(encoding='utf-8', errors='replace')
page_map = []
changed_pages = []
for i, page in enumerate(doc, 1):
    text_path = audit / f'page-{i:02}.txt'
    page_text = page.get_text()
    if not text_path.exists() or text_path.read_text(encoding='utf-8') != page_text:
        changed_pages.append(i)
    text_path.write_text(page_text, encoding='utf-8')
    page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7)).save(audit / f'page-{i:02}.png')
    page_map.append({'page': i, 'chars': len(page_text)})

snapshot = json.loads((audit / 'final-source-hashes.json').read_text(encoding='utf-8-sig'))
changed_sources = [e['Path'] for e in snapshot
                   if hashlib.sha256(Path(e['Path']).read_bytes()).hexdigest().upper() != e['Hash']]
body = re.search(r'\\newlabel\{page:bodyend\}\{\{[^}]+\}\{([^}]+)\}', aux)
summary = {
    'pdf': str(pdf_path),
    'pages': len(doc),
    'body_last_page': int(body.group(1)) if body else None,
    'page_dimensions': list(doc[0].rect),
    'page_map': page_map,
    'overfull_count': log.count('Overfull'),
    'underfull_count': log.count('Underfull'),
    'undefined': [line for line in log.splitlines() if re.search(r'undefined|Missing character|^!', line, re.I)],
    'pdf_sha256': hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    'changed_pages_since_first_build': changed_pages,
    'changed_sources_during_final_build': changed_sources,
}
(audit / 'compile-summary-final.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k != 'page_map'}, ensure_ascii=False, indent=2))
