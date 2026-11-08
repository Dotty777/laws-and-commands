import json, re, collections, sys
sys.path.insert(0, "/home/claude/work")
from r2_residual import B, U, r2, af, final, finalobj, removed, fv, cov, byid
import cov2
vc = json.load(open("/home/claude/repos/laws-and-commands/audit/verified-completeness.json"))
held = {}
for s in vc["review_sections"]:
    if isinstance(s.get("held"), list):
        for h in s["held"]: held[h["key"]] = h["reason"]
pubkey = {}
for kind in ("new", "extend", "parallel"):
    for p in vc["published"][kind]:
        if p.get("key"): pubkey[p["key"]] = (kind, p.get("catalogue_id") or p.get("existing_id"), p.get("reference") or p.get("add"))
def fate(k):
    f = af[k]; fo = finalobj.get(k, {})
    if k in pubkey:
        kind, cid, ref = pubkey[k]; return f"editor published it as {kind} {cid} ({ref}) but this verse is not attached"
    for hk in (k, fo.get("proposed_id")):
        if hk and hk in held: return "editor held it: " + held[hk]
    if k in removed: return "dropped in round-1 merge: " + removed[k]
    if k in final: return "in round-1 final list; not published and no hold reason recorded"
    return f"not recommended in round 1 ({f.get('confidence')} confidence)"
resid = [i for i in sorted(U) if i not in r2 and i in fv]
groups = []
for i in resid:
    if groups and B.verses[i]["book"] == B.verses[groups[-1][-1]]["book"] and B.verses[i]["ch"] == B.verses[groups[-1][-1]]["ch"] and i - groups[-1][-1] <= 2:
        groups[-1].append(i)
    else: groups.append([i])
def disp(i):
    v = B.verses[i]; bk = "Greek Psalm" if v["book"] == "Psalms" else v["book"]
    return f'{bk} {v["ch"]}:{v["v"]}'
out, ids = [], []
for n, g in enumerate(groups, 1):
    iid = f"V{n:03d}"; ids.append(iid); a, b = g[0], g[-1]
    rng = disp(a) + (("–" + B.verses[b]["v"]) if b != a else "")
    L = [f"### {iid} · uncovered directive verse{'s' if len(g) > 1 else ''} {rng} · a round-1 finding touched it but it is still unattached"]
    for k in sorted({k for i in g for k in fv[i]}):
        f = af[k]
        L.append(f'   round-1 finding {k}: {f.get("verdict")} · {f.get("reference")} · {f.get("record_type", "")} · "{f.get("title", "")}" · conf {f.get("confidence")}')
        if f.get("existing_id"): L.append(f'      names existing {f["existing_id"]}: {byid.get(f["existing_id"], {}).get("title", "(not in current catalogue)")}')
        if f.get("note"): L.append(f'      note: {f["note"][:220]}')
        L.append(f'      outcome: {fate(k)}')
    near = sorted({rid for i in range(max(0, a - 2), b + 3) for rid in cov.get(i, ())})[:6]
    for rid in near:
        r = byid[rid]; L.append(f'   nearby record {rid} | {r["reference"]} | {r["record_type"]} | {r["title"]}')
    for i in range(max(0, a - 1), b + 2):
        if i >= len(B.verses) or B.verses[i]["book"] != B.verses[a]["book"]: continue
        L.append(f'   {"" if i in g else "[ctx] "}{disp(i)} {B.verses[i]["text"]}')
    out.append("\n".join(L))
k = len(out); third = (k + 2) // 3
idx = json.load(open("/home/claude/work/round2/index.json"))
for j, name in enumerate(["R8a", "R8b", "R8c"]):
    chunk = out[j * third:(j + 1) * third]
    open(f"/home/claude/work/round2/batches/{name}.md", "w").write(f"# Round-2 batch {name}: {len(chunk)} items\n\n" + "\n\n".join(chunk) + "\n")
    idx[name] = ids[j * third:(j + 1) * third]; print(name, len(chunk))
json.dump(idx, open("/home/claude/work/round2/index.json", "w"), ensure_ascii=False, indent=0)
json.dump({"verses": len(resid), "items": len(groups)}, open("/home/claude/work/audit/r2_residual_stats.json", "w"))
print(len(resid), "verses in", len(groups), "items"); print(out[0][:1400]); print(); print(out[len(out)//2][:1400])
