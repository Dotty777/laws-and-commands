"""Archive the staging catalogue's rendered audience pages without changing the site."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "source" / "audience"
SITE = "https://staging-8e0d-waywardnightjars.wpcomstaging.com"


def fetch(url: str) -> bytes:
    for attempt in range(8):
        request = urllib.request.Request(url, headers={"User-Agent": "SaintsBible-Catalogue-Archive/1.0", "Accept": "application/json,text/html"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504):
                raise
            wait = max(float(error.headers.get("Retry-After", "0") or 0), min(30 * (attempt + 1), 150))
            print(f"retry HTTP {error.code}: wait {wait:.0f}s", flush=True)
            time.sleep(wait)
        except (TimeoutError, urllib.error.URLError) as error:
            wait = min(15 * (attempt + 1), 90)
            print(f"retry {type(error).__name__}: wait {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"Unable to fetch {url}")


def content(payload: dict) -> str:
    return payload["content"]["rendered"]


def ids(markup: str) -> list[str]:
    return re.findall(r'id=["\']audience-([^"\']+)', markup)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=3.1)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    original = ROOT / "source" / "pages" / "43998-rest.json"
    if original.exists() and not (DEST / "general-001.json").exists():
        shutil.copyfile(original, DEST / "general-001.json")
    fetched = 0
    all_seen: set[str] = set()
    for audience, page_id, expected in (("general", 43998, 3869), ("personal", 43999, 571)):
        pages = (expected + 39) // 40
        seen: set[str] = set()
        for page in range(1, pages + 1):
            destination = DEST / f"{audience}-{page:03d}.json"
            if destination.exists():
                payload = json.loads(destination.read_text(encoding="utf-8-sig"))
            else:
                time.sleep(args.delay)
                url = f"{SITE}/wp-json/wp/v2/pages/{page_id}?_fields=id,modified,slug,link,title,content&instruction_page={page}"
                payload = json.loads(fetch(url))
                markup = content(payload)
                found = ids(markup)
                if not found or seen.intersection(found):
                    raise RuntimeError(f"REST pagination failed for {audience} page {page}; {len(found)} IDs, repeated={len(seen.intersection(found))}")
                temporary = destination.with_suffix(".tmp")
                temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                temporary.replace(destination)
                fetched += 1
            found = ids(content(payload))
            if len(found) != min(40, expected - (page - 1) * 40):
                raise RuntimeError(f"{destination.name}: expected page count, got {len(found)}")
            if seen.intersection(found) or all_seen.intersection(found):
                raise RuntimeError(f"Duplicate IDs in {destination.name}")
            seen.update(found)
            print(f"{audience} {page}/{pages}: {len(found)} records; {len(seen)}/{expected}", flush=True)
            if args.limit and fetched >= args.limit:
                return
        assert len(seen) == expected, (audience, len(seen), expected)
        all_seen.update(seen)
    assert len(all_seen) == 4440
    print("Completed: 4440 unique audience records archived", flush=True)


if __name__ == "__main__":
    main()
