"""Write reviewer batch files (Markdown) from passages.json, balanced by words, books kept in order."""
import sys, json, collections, os, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import *

B = Bible(); recs = load_catalogue()
P = json.load(open("/home/claude/work/passages.json"))
TARGET_WORDS = int(sys.argv[1]) if len(sys.argv) > 1 else 14000
os.makedirs("/home/claude/work/review/batches", exist_ok=True)
os.makedirs("/home/claude/work/review/out", exist_ok=True)

# records by chapter for the "nearby records" list
by_ch = collections.defaultdict(list)
for r in recs:
    for ref in [r["reference"]] + [a["reference"] for a in r["additional_scripture"]]:
        ii, _ = B.expand(ref)
        if ii:
            v = B.verses[ii[0]]
            by_ch[(v["book"], v["ch"])].append((ii[0], ii[-1], r, ref))

rambam = collections.defaultdict(list)
for row in json.load(open("/home/claude/work/check613.json")):
    if not row["fine"]:
        for i in row["idx"]:
            rambam[i].append(row["mitzva"])


def nearby(p):
    first = p["verses"][0]["i"]; last = p["verses"][-1]["i"]
    rows = []
    for lo, hi, r, ref in by_ch[(p["book"], p["ch"])]:
        dist = 0 if (lo <= last and hi >= first) else min(abs(lo - last), abs(hi - first))
        rows.append((dist, lo, r, ref))
    rows.sort(key=lambda x: (x[0], x[1]))
    seen, out = set(), []
    for d, lo, r, ref in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(f'{r["id"]} ({ref.split(" ",1)[1] if not ref.startswith(("Greek Psalm","Bel and","Susanna","1 ","2 ","3 ","Song of","Wisdom of")) else ref} {r["record_type"]}: {r["title"][:64]})')
        if len(out) >= 6:
            break
    return out


def words(p):
    return sum(len(v["text"].split()) for v in p["verses"])


batches, cur, cw = [], [], 0
for p in P:
    w = words(p)
    if cur and cw + w > TARGET_WORDS:
        batches.append(cur); cur, cw = [], 0
    cur.append(p); cw += w
if cur:
    batches.append(cur)

index = []
for n, bt in enumerate(batches, 1):
    name = f"B{n:02d}"
    lines = [f"# Review batch {name}: {bt[0]['first']} to {bt[-1]['last']}",
             f"{len(bt)} passages, {sum(p['n_candidates'] for p in bt)} candidate verses.", ""]
    for p in bt:
        lines.append(f"## {p['pid']} · {p['chapter_name']} · candidates {p['first']} – {p['last']}")
        nb = nearby(p)
        lines.append("Near: " + ("; ".join(nb) if nb else "no records in this chapter"))
        for v in p["verses"]:
            tag = "[C]" if v["role"] == "candidate" else "[ctx]"
            extra = ""
            if v["role"] == "candidate":
                bits = []
                if v["sig"]:
                    bits.append("sig " + ",".join(v["sig"]))
                if "broad-only" in v["why"]:
                    bits.append("broad-only " + ",".join(v["covered_by"][:2]))
                if rambam.get(v["i"]):
                    bits.append("Rambam " + ",".join(rambam[v["i"]]))
                if bits:
                    extra = "  {" + "; ".join(bits) + "}"
            short = v['ref'].rsplit(" ", 1)[1] if not v['ref'].startswith(("Susanna", "Bel and")) else v['ref']
            lines.append(f"{tag} {short} {v['text']}{extra}")
        lines.append("")
    open(f"/home/claude/work/review/batches/{name}.md", "w").write("\n".join(lines))
    index.append({"batch": name, "first": bt[0]["first"], "last": bt[-1]["last"], "passages": len(bt),
                  "candidates": sum(p["n_candidates"] for p in bt), "words": sum(words(p) for p in bt),
                  "pids": [p["pid"] for p in bt]})
json.dump(index, open("/home/claude/work/review/index.json", "w"), indent=1)
for x in index:
    print(x["batch"], x["first"], "→", x["last"], "| passages", x["passages"], "| cand", x["candidates"], "| words", x["words"])
