#!/usr/bin/env python3
"""Validate the standalone manuscript; experiment validation lives in the AX repo."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
required = ['main.tex', 'references.bib', 'sections/08-evaluation.tex',
            'usenix2019_v3.sty', 'templates/usenix-official/usenix2019_v3.sty']
for name in required:
    if not (ROOT / name).is_file():
        errors.append('Missing file: ' + name)
if errors:
    print(json.dumps({'passed': False, 'errors': errors}, indent=2))
    sys.exit(1)
bib = (ROOT / 'references.bib').read_text(encoding='utf-8')
keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
if len(keys) != len(set(keys)):
    errors.append('Duplicate BibTeX keys')
tex = '\n'.join(p.read_text(encoding='utf-8') for p in
                [ROOT / 'main.tex', *sorted((ROOT / 'sections').glob('*.tex'))])
cited = set()
for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', tex):
    cited.update(k.strip() for k in group.split(','))
if cited - set(keys):
    errors.append('Undefined bibliography keys: ' + ', '.join(sorted(cited - set(keys))))
rqs = re.findall(r'\\researchq\{(\d+)\}', tex)
if sorted(rqs) != ['1', '2', '3', '4', '5']:
    errors.append('Expected exactly one declaration for each of RQ1 through RQ5')
expected = '4ed9aa9d0c5daec54ce3b4188a4bf6d3bef3462c79ff65551d567511d3c45ff6'
for name in ['usenix2019_v3.sty', 'templates/usenix-official/usenix2019_v3.sty']:
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
        errors.append('Official style hash mismatch: ' + name)
log_status = 'not available; compile main.tex to inspect diagnostics'
log_path = ROOT / 'main.log'
if log_path.exists():
    log = log_path.read_text(encoding='utf-8', errors='replace')
    problems = [s for s in ['Overfull', 'Missing character'] if s in log]
    if re.search(r'(?:Citation|Reference).*undefined', log):
        problems.append('undefined citation/reference')
    if problems:
        errors.append('LaTeX issues: ' + ', '.join(problems))
    log_status = 'checked' if not problems else problems
print(json.dumps({'passed': not errors, 'scope': 'standalone manuscript only; no runtime experiments',
                  'bibliography_entries': len(keys), 'cited_entries': len(cited),
                  'research_questions': ['RQ' + n for n in sorted(rqs)],
                  'official_style_sha256': expected, 'latex_log': log_status,
                  'errors': errors}, indent=2))
sys.exit(1 if errors else 0)
