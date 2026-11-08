"""Candidate duplicates and mislabels among the Torah Law records and the other Mosaic records."""
import json, sys, collections, re, itertools
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
B = Bible()
recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json")); byid = {r["id"]: r for r in recs}
MOS = [r for r in recs if r["mosaic_type"]]
TL = [r for r in MOS if r["mosaic_type"] == "Law"]
def vs(r): return set(B.expand(r["reference"])[0])
V = {r["id"]: vs(r) for r in MOS}
ADD = {r["id"]: set().union(*[set(B.expand(a["reference"])[0]) for a in r.get("additional_scripture") or []] or [set()]) for r in MOS}
STOP = set("the a an of to and or for in on with by from as at be is are his her their your you who whom that this these those shall not do any all its it into upon before god lord israel prescribed stated specified".split())
def toks(t): return {w for w in re.findall(r"[a-z]+", t.lower()) if w not in STOP and len(w) > 2}
def jac(a, b):
    A, Bt = toks(a), toks(b)
    return len(A & Bt) / max(1, len(A | Bt))
def text(r): return " ".join(B.verses[i]["text"] for i in sorted(V[r["id"]])[:8])
# 1. same-passage pairs (overlapping primary verses) among Mosaic records where at least one is Torah Law
same = []
for a, b in itertools.combinations(MOS, 2):
    if "Law" not in (a["mosaic_type"], b["mosaic_type"]): continue
    ov = V[a["id"]] & V[b["id"]]
    if not ov: continue
    j = jac(a["title"], b["title"])
    same.append({"a": a["id"], "b": b["id"], "overlap": len(ov), "jaccard": round(j, 2), "same_ref": a["reference"] == b["reference"],
                 "types": f'{a["mosaic_type"]}/{b["mosaic_type"]}'})
# 2. cross-passage restatements: TF-IDF on title + verse text, Torah Law vs any Mosaic record, no verse overlap
docs = [r["title"] + " " + r["title"] + " " + text(r) for r in MOS]
vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, ngram_range=(1, 2), min_df=1).fit(docs)
X = vec.transform(docs); S = cosine_similarity(X)
cross = []
for i, a in enumerate(MOS):
    if a["mosaic_type"] != "Law": continue
    for j in S[i].argsort()[::-1][1:6]:
        b = MOS[j]
        if V[a["id"]] & V[b["id"]]: continue
        if S[i][j] < 0.33: break
        key = tuple(sorted([a["id"], b["id"]]))
        linked = bool(V[b["id"]] & ADD[a["id"]]) or bool(V[a["id"]] & ADD[b["id"]])
        cross.append({"a": key[0], "b": key[1], "sim": round(float(S[i][j]), 2), "types": f'{byid[key[0]]["mosaic_type"]}/{byid[key[1]]["mosaic_type"]}', "linked_as_additional": linked})
uniq = {}
for c in cross: uniq[(c["a"], c["b"])] = c
cross = sorted(uniq.values(), key=lambda c: -c["sim"])
# 3. label screens
PROC = re.compile(r"^(?:[^:]+:\s*)?(sprinkle|slaughter|burn|wash|place|put|set|bring|make|take|offer|present|lay|pour|cut|kill|remove|anoint|clothe|eat|keep the lamp|arrange|install|erect|cover|carry|dip|apply|wave|burn the|kindle)\b", re.I)
PROH = re.compile(r"^(?:[^:]+:\s*)?(do not|don't|never|no one|none|not )", re.I)
law_proc = [r["id"] for r in TL if PROC.match(r["title"])]
other_proh = [r["id"] for r in MOS if r["mosaic_type"] in ("Instruction", "Command") and PROH.match(r["title"])]
out = {"same_passage": same, "cross_passage": cross, "law_procedural_titles": law_proc, "other_prohibition_titles": other_proh}
json.dump(out, open("/home/claude/work/round3/tl_candidates.json", "w"), indent=1)
print("same-passage pairs:", len(same), "| same ref:", sum(1 for s in same if s["same_ref"]), "| jaccard>=0.3:", sum(1 for s in same if s["jaccard"] >= 0.3),
      "| types:", collections.Counter(s["types"] for s in same))
print("cross-passage pairs (sim>=0.33):", len(cross), "| linked already:", sum(1 for c in cross if c["linked_as_additional"]), collections.Counter(c["types"] for c in cross))
print("Torah Law with procedural titles:", len(law_proc)); print("Instruction/Command prohibitions:", len(other_proh))
for s in sorted(same, key=lambda s: -s["jaccard"])[:25]:
    a, b = byid[s["a"]], byid[s["b"]]
    print(f'  {s["jaccard"]:.2f} {s["types"]:16s} {a["id"]} {a["reference"]} "{a["title"][:55]}" ~ {b["id"]} {b["reference"]} "{b["title"][:55]}"')
print("--- cross")
for c in cross[:25]:
    a, b = byid[c["a"]], byid[c["b"]]
    print(f'  {c["sim"]:.2f} {c["types"]:16s} {"L" if c["linked_as_additional"] else " "} {a["id"]} {a["reference"]} "{a["title"][:50]}" ~ {b["id"]} {b["reference"]} "{b["title"][:50]}"')
