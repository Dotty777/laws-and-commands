"""Search first-pass audit findings (already proposed, not yet in the catalogue).
usage: python3 -I /home/claude/work/find_search.py at "Book ch:v[-v]"   |   words <w> [<w> ...]"""
import sys, json, glob
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
rows = []
for f in sorted(glob.glob("/home/claude/work/review/out/B*.jsonl")):
    for line in open(f):
        o = json.loads(line)
        if o.get("reference"):
            o["batch"] = f.split("/")[-1][:3]; rows.append(o)
def show(o):
    print(f'{o["batch"]} {o["pid"]} | {o["verdict"]} | {o["reference"]} | {o["record_type"]} | {o["title"]}' + (f' | existing {o["existing_id"]}' if o.get("existing_id") else ""))
if len(sys.argv) > 2 and sys.argv[1] == "at":
    B = Bible(); t = set(B.expand(sys.argv[2])[0])
    for o in rows:
        if t & set(B.expand(o["reference"])[0]): show(o)
elif len(sys.argv) > 2 and sys.argv[1] == "words":
    ws = [w.lower() for w in sys.argv[2:]]
    for o in rows:
        blob = (o["title"] + " " + o["reference"] + " " + o.get("note", "")).lower()
        if all(w in blob for w in ws): show(o)
else:
    print(__doc__)
