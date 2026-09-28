"""Verify that the local application's scripts, styling and data match its source."""
import base64
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
original = (root / 'reference-capture.html').read_text(encoding='utf-8')
local = (root / 'index.html').read_text(encoding='utf-8')
def payload(text):
    return re.search(r'const DATA_B64="([^"]+)"', text).group(1)
assert payload(original) == payload(local), 'Embedded data changed'
def app_scripts(text):
    text = text[text.index('<meta property'):]
    return re.findall(r'<script\b[^>]*>(.*?)</script>', text, re.S)
assert app_scripts(original) == app_scripts(local), 'Application scripts changed'
assert re.findall(r'<style>(.*?)</style>', original, re.S) == re.findall(r'<style>(.*?)</style>', local, re.S), 'Styles changed'
data = json.loads(gzip.decompress(base64.b64decode(payload(local))))
pool, records = data['pool'], data['recs']
def value(row, index):
    raw = row[index]
    return pool[raw] if isinstance(raw, int) else raw
counts = Counter((str(row[0]), str(value(row, 27)), str(value(row, 28))) for row in records)
report = {
    'referenceUrl': 'https://4kwbfu2sw743y.aiforce.cloud/app/app_17dv1zs9tfc/',
    'dataIdentical': True,
    'applicationScriptsIdentical': True,
    'stylesIdentical': True,
    'dataGzipSha256': hashlib.sha256(base64.b64decode(payload(local))).hexdigest(),
    'totalJobs': len(records),
    'jobsWithInterviewScore': sum(bool(value(row, 26)) for row in records),
    'counts': [{'year': k[0], 'exam': k[1], 'province': k[2], 'jobs': v} for k, v in sorted(counts.items())],
}
(root / 'source-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'counts'}, ensure_ascii=False, indent=2))
