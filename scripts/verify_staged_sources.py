"""Check that Git will commit the exact archived bytes, without newline conversion."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'source/manifest.json').read_text(encoding='utf-8'))
process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
try:
    for entry in manifest:
        process.stdin.write((':' + entry['file'] + '\n').encode('utf-8'))
        process.stdin.flush()
        header = process.stdout.readline().decode('utf-8').strip().split()
        assert len(header) == 3 and header[1] == 'blob', entry['file']
        body = process.stdout.read(int(header[2]))
        assert process.stdout.read(1) == b'\n'
        assert len(body) == entry['bytes'], entry['file']
        assert hashlib.sha256(body).hexdigest() == entry['sha256'], entry['file']
finally:
    process.stdin.close()
    process.wait(timeout=20)
assert process.returncode == 0
print(f'Verified {len(manifest)} staged source archives against the SHA-256 manifest.')
