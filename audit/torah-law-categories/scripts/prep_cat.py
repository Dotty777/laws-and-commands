"""Build review batches for the Torah Law category pass (form, category, ceremonial area)."""
import sys, json, os, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible

REPO = "/home/claude/repos/laws-and-commands"
W = "/home/claude/work"; OUT = f"{W}/round4"
os.makedirs(f"{OUT}/batches", exist_ok=True); os.makedirs(f"{OUT}/out", exist_ok=True)
B = Bible()
recs = json.load(open(f"{REPO}/data/current/commands.json"))
TL = [r for r in recs if r["study_placement"] == "Torah Law"]
assert len(TL) == 646
alias = json.load(open(f"{REPO}/audit/torah-law/followup-decisions.json"))["new_aliases"]
G = json.load(open(f"{W}/audit/torah-laws/findings-638.json"))

def resolve(i):
    seen = set()
    while i in alias and i not in seen:
        seen.add(i); i = alias[i]
    return i

seeds = collections.defaultdict(list)
for row in G["rows613_now"]:
    for i in row["records_now"]:
        j = resolve(i)
        if (row["m"], row["statement"]) not in seeds[j]:
            seeds[j].append((row["m"], row["statement"]))

def verse_text(ref, cap=1400):
    try:
        idx = B.expand(ref)[0]
    except Exception:
        return ""
    parts = []
    for k in idx:
        v = B.verses[k]
        parts.append(f"[{v['ch']}:{v['v']}] {v['text']}")
    t = " ".join(parts)
    return t if len(t) <= cap else t[:cap].rsplit(" ", 1)[0] + " …"

items = []
for r in TL:
    tlid = r["id"]
    items.append({
        "id": tlid, "reference": r["reference"], "title": r["title"], "topic": r["topic"],
        "classification": r["classification"], "original_audience": r["original_audience_or_recipient"],
        "context_note": (r.get("context_note") or "")[:400],
        "verse_text": verse_text(r["reference"]),
        "maimonides": [f"{m}: {s}" for m, s in seeds.get(tlid, [])],
    })
missing_text = [x["id"] for x in items if not x["verse_text"]]
n = 7; size = -(-len(items) // n)
index = {}
for b in range(n):
    chunk = items[b * size:(b + 1) * size]
    name = f"C{b + 1}"
    with open(f"{OUT}/batches/{name}.json", "w") as f:
        json.dump(chunk, f, ensure_ascii=False, indent=1)
    index[name] = [x["id"] for x in chunk]
json.dump(index, open(f"{OUT}/index.json", "w"), indent=1)
print({k: len(v) for k, v in index.items()}, "no text:", missing_text,
      "with seeds:", sum(1 for x in items if x["maimonides"]),
      "seed P only:", sum(1 for x in items if x["maimonides"] and all(s.startswith("P") for s in x["maimonides"])),
      "seed N only:", sum(1 for x in items if x["maimonides"] and all(s.startswith("N") for s in x["maimonides"])),
      "both:", sum(1 for x in items if any(s.startswith("P") for s in x["maimonides"]) and any(s.startswith("N") for s in x["maimonides"])))
