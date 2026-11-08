"""Why the screened directive verses still unattached after round 2 are unattached."""
import json, sys, collections, copy, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible, coverage
import cov2
B = Bible()
W = "/home/claude/work"; A = f"{W}/audit/round2"
recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))
after = copy.deepcopy(recs); aid = {r["id"]: r for r in after}
for o in json.load(open(f"{A}/new_records.json")):
    after.append({"id": o["id"], "reference": o["reference"], "additional_scripture": [{"reference": a["reference"]} for a in o["additional"]], "book": o["book"]})
for x in json.load(open(f"{A}/extend.json")): aid[x["existing_id"]]["reference"] = x["proposed"]
for p in json.load(open(f"{A}/parallel.json")): aid[p["existing_id"]].setdefault("additional_scripture", []).append({"reference": p["reference"]})
D = cov2.directive_set(); C = cov2.covered(B, after); anyc, _, _ = coverage(B, after)
U = sorted(i for i in D if i not in C)
dec = json.load(open(f"{A}/decisions.json")); declined_v = set()
sims = json.load(open(f"{W}/audit/sim_cands.json"))
for d in dec:
    if d["decision"] != "no_record": continue
    it = d["item"]
    if it.startswith("SIM"): declined_v.add(sims[int(it[3:]) - 1][1]); continue
    if it.startswith("U"): declined_v.add(int(it[1:])); continue
    ref = it.split("|", 1)[1] if it[:2] in ("E:", "P:") else ""
    if it.startswith("N:"):
        dr = {x["proposed_id"]: x for x in json.load(open(f"{W}/audit/round2_open_new.json"))}.get(it[2:])
        ref = dr["reference"] if dr else ""
    if it.startswith("V"):
        t = open(f"{W}/round2/batches/" + d["batch"] + ".md").read()
        m = re.search(r"^### " + re.escape(it) + r" · uncovered directive verses? (.+?) · ", t, re.M)
        ref = m.group(1) if m else ""
    if ref: declined_v |= set(B.expand(ref)[0])
cat = collections.Counter(); byb = collections.defaultdict(collections.Counter)
for i in U:
    if i in anyc: k = "held only by a long passage record (Genesis–Deuteronomy, over 8 verses)"
    elif i in declined_v: k = "reviewed again in round 2 and declined, with a stated reason"
    else: k = "read in round 1 and judged not to need a record"
    cat[k] += 1; byb[B.verses[i]["book"]][k] += 1
res = {"remaining": len(U), "by_reason": dict(cat.most_common())}
json.dump(res, open(f"{A}/remaining.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
