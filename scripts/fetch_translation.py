"""Archive current per-book Saints Translation exports without altering the site."""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://staging-8e0d-waywardnightjars.wpcomstaging.com'
DEST = ROOT / 'source' / 'translation' / 'books'

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    books = json.loads((DEST.parent / 'book-index.json').read_text(encoding='utf-8'))
    for i, book in enumerate(books, 1):
        target = DEST / (book['slug'] + '.json')
        if target.exists():
            continue
        url = BASE + '/wp-json/saints/v1/text?book=' + book['slug'] + '&format=json'
        for attempt in range(8):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Saints.Bible catalogue repository export'})
                with urllib.request.urlopen(req, timeout=120) as response:
                    body = response.read()
                data = json.loads(body)
                assert data['slug'] == book['slug'] and data['chapters']
                target.write_bytes(body)
                print(f"{i}/{len(books)} {book['slug']}: {data['verse_count']} verses", flush=True)
                break
            except urllib.error.HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504):
                    raise
                delay = max(20 * (attempt + 1), int(error.headers.get('Retry-After', 0)))
                print(f'{book["slug"]}: HTTP {error.code}; retry in {delay}s', flush=True)
                time.sleep(delay)
        else:
            raise RuntimeError('Could not retrieve ' + book['slug'])
        time.sleep(6.5)

if __name__ == '__main__':
    main()
