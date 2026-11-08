"""Carry the 556-based findings forward to the catalogue as revised by the contextual Torah Law audit (638 Torah Law records)."""
import json, sys, collections, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
W = "/home/claude/work"; A = f"{W}/audit/torah-laws"; REPO = "/home/claude/repos/laws-and-commands"
new = json.load(open(f"{REPO}/data/current/commands.json")); nby = {r["id"]: r for r in new}
L = json.load(open(f"{REPO}/audit/torah-law/decisions.json")); alias = L["aliases"]
F = json.load(open(f"{A}/findings.json")); M = json.load(open(f"{A}/maimonides-613.json"))
old_prev = L["previous"]
def cur(i):
    i = alias.get(i, i)
    return nby.get(i)
def mt(i):
    r = cur(i); return (r["mosaic_type"] if r else "retired")
def verses(ref): return set(B.expand(ref)[0])
BROAD = ("Torah · Passage group", "Torah · Topical study", "Passage group", "Topical study", "Torah · Passage study", "Passage study")
span = collections.defaultdict(set)
for r in new:
    for ref in [r["reference"]] + [a["reference"] for a in r.get("additional_scripture") or []]:
        for v in verses(ref): span[v].add(r["id"])
m613 = {x["m"]: x for x in json.load(open(f"{W}/round3/m613.json"))}
addv = {a["id"]: verses(a["reference"]) for a in L["additions"]}
# ---------------- 613 status now
rows = []
for r in M:
    recs_now = list(dict.fromkeys(alias.get(x, x) for x in r["records"]))
    types = [nby[x]["mosaic_type"] for x in recs_now if x in nby]
    vs = set(m613[r["m"]]["idx"])
    added_here = [a for a, av in addv.items() if av & vs]
    if r["status"] in ("partial", "broad_only"):
        st = "not stated" + (" (an addition now holds the verse: " + ", ".join(added_here) + ")" if added_here else "")
        new_status = "not_stated_check_addition" if added_here else r["status"]
    elif "Law" in types: new_status = "torah_law"
    elif any(t for t in types): new_status = "other_mosaic"
    else: new_status = r["status"]
    rows.append({"m": r["m"], "statement": r["statement"], "old_status": r["status"], "new_status": new_status, "records_now": recs_now,
                 "types_now": types, "additions_on_verse": added_here})
stat = collections.Counter(x["new_status"] for x in rows)
moved = collections.Counter((x["old_status"], x["new_status"]) for x in rows if x["old_status"] != x["new_status"])
om_now = collections.Counter()
for x in rows:
    if x["new_status"] == "other_mosaic":
        om_now[next(t for t in x["types_now"] if t)] += 1
# ---------------- the 12 to add
def itemized_on(vs):
    out = []
    for v in vs:
        for rid in span.get(v, ()):
            r = nby[rid]
            if r["study_placement"] in BROAD: continue
            out.append(rid)
    return sorted(set(out))
gap_now = []
for g in F["gaps"]:
    if g["category"] not in ("Text states it, no record does", "No itemized Mosaic record (only a Genesis record or a topical study)"): continue
    gap_now.append({"m": g["m"], "statement": g["statement"], "why": g["why"], "additions_on_verse": [a for a, av in addv.items() if av & set(m613[g["m"]]["idx"])]})
# ---------------- duplicates
dup_now = []
for d in F["duplicates"]:
    survivors = [alias.get(x, x) for x in d["records"]]
    merged = len(set(survivors)) < len(survivors)
    state = "merged" if merged else "still separate"
    if not merged and d["kind"] == "Same law recorded again in another passage":
        a = cur(d["keep"]) if d["keep"] in nby or d["keep"] in alias else None
        others = [x for x in d["records"] if alias.get(x, x) != alias.get(d["keep"], d["keep"])]
        if a:
            av = set().union(*[verses(x["reference"]) for x in a.get("additional_scripture") or []] or [set()])
            if all(verses(nby[alias.get(o, o)]["reference"]) <= av for o in others if alias.get(o, o) in nby): state = "linked"
    dup_now.append(dict(d, now=state, survivors=survivors, labels_now=[mt(x) for x in d["records"]]))
# ---------------- labels
lab_now = []
for x in F["labels"]:
    s = alias.get(x["id"], x["id"]); r = nby.get(s)
    now = r["study_placement"] if r else "retired"
    want_law = "Torah Law" in x["suggest"]
    if x["id"] in alias: state = f"merged into {s} ({now})"
    elif want_law and r and r["mosaic_type"] == "Law": state = "now Torah Law"
    elif (not want_law) and r and r["mosaic_type"] != "Law" and x["current"] == "Torah Law": state = f"now {now}"
    elif r and now != x["current"]: state = f"now {now}"
    else: state = "unchanged"
    lab_now.append(dict(x, now=state, survivor=s))
lab_state = collections.Counter(("resolved" if (y["now"] != "unchanged") else "open") for y in lab_now)
lab_open_by_cat = collections.Counter(y["category"] for y in lab_now if y["now"] == "unchanged")
# ---------------- links and notes
links_now = []
for u in F["unlinked_restatements"]:
    r = nby.get(alias.get(u["record"], u["record"]))
    m = re.match(r"(.+?) \(", u["verse"]); ref = m.group(1) if m else u["verse"]
    vs = verses(ref)
    have = set().union(*[verses(a["reference"]) for a in (r.get("additional_scripture") or [])] or [set()]) | verses(r["reference"]) if r else set()
    links_now.append(dict(u, now="linked" if vs and vs <= have else "still unattached"))
pat = re.compile(r"(\b[Ee]xtend (?:to |from |C\d|C\d{4}|[A-Z][a-z]+ \d|\d)|\bLink (?:this|the|it) |link as Additional Scripture|\bshould be linked\b|\bRambam\b|\bnot itemized\b|\bfirst-pass\b|\bfold into\b|\bre-?reference\b|could instead attach)", re.I)
notes_now = []
for r in new:
    for f, t in [("context note", r.get("context_note") or "")] + [(f"Additional Scripture {a['reference']}", a.get("context_note") or "") for a in r.get("additional_scripture") or []]:
        if pat.search(t): notes_now.append({"id": r["id"], "field": f, "text": t})
# ---------------- what changed in the count
old_tl = {i for i, p in old_prev.items() if p.get("mosaic_type") == "Law"}
TLnew = [r for r in new if r["mosaic_type"] == "Law"]
newly = [r["id"] for r in TLnew if r["id"] in old_prev and old_prev[r["id"]].get("mosaic_type") != "Law"]
from_types = collections.Counter(old_prev[i].get("study_placement") for i in newly)
retired_tl = [x["record"]["id"] for x in L["retired"] if x["record"].get("mosaic_type") == "Law"]
moved_out = [i for i, p in old_prev.items() if p.get("mosaic_type") == "Law" and i in nby and nby[i]["mosaic_type"] != "Law"]
change = {"before": 556, "after": len(TLnew), "added_new_records": len([a for a in L["additions"] if nby.get(a["id"], {}).get("mosaic_type") == "Law"]),
          "relabelled_to_law": len(newly), "relabelled_from": dict(from_types), "retired_law_records": len(retired_tl), "moved_out_of_law": len(moved_out)}
# ---------------- quick new-duplicate screen among Torah Law (same reference, near-identical titles), excluding pairs already reviewed
STOP = set("the a an of to and or for in on with by from as at be is are his her their your you who that this shall not do any all its it into upon before god lord israel prescribed stated specified".split())
def toks(t): return {w for w in re.findall(r"[a-z]+", t.lower()) if w not in STOP and len(w) > 2}
reviewed = {tuple(sorted(v)) for v in json.load(open(f"{W}/round3/pairs.json")).values()}
cand = []
TLv = {r["id"]: verses(r["reference"]) for r in TLnew}
ids = sorted(TLv)
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        if not (TLv[a] & TLv[b]): continue
        if tuple(sorted([a, b])) in reviewed: continue
        A_, B_ = toks(nby[a]["title"]), toks(nby[b]["title"])
        j = len(A_ & B_) / max(1, len(A_ | B_))
        if j >= 0.34: cand.append({"a": a, "b": b, "jaccard": round(j, 2), "a_title": nby[a]["title"], "b_title": nby[b]["title"], "ref": nby[a]["reference"] + " / " + nby[b]["reference"]})
out = {"status_613_now": stat, "moved": {f"{k[0]} → {k[1]}": v for k, v in moved.items()}, "other_mosaic_now": om_now,
       "gaps_to_add_now": gap_now, "duplicates_now": dup_now, "labels_now": lab_now, "labels_state": lab_state, "labels_open_by_group": lab_open_by_cat,
       "links_now": links_now, "edit_notes_now": len(notes_now), "edit_notes_records_now": len({n["id"] for n in notes_now}), "count_change": change,
       "new_duplicate_candidates": cand, "rows613_now": rows}
json.dump(out, open(f"{A}/reconcile-638.json", "w"), ensure_ascii=False, indent=1)
json.dump(notes_now, open(f"{A}/edit-notes-638.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k in ("status_613_now", "moved", "other_mosaic_now", "labels_state", "labels_open_by_group", "edit_notes_now", "edit_notes_records_now", "count_change")}, ensure_ascii=False, indent=1))
print("gaps:", [(g["m"], g["additions_on_verse"]) for g in gap_now])
print("dups:", [(d["records"], d["now"]) for d in dup_now])
print("links:", [(u["verse"][:30], u["now"]) for u in links_now])
print("new dup candidates:", len(cand)); [print("  ", c) for c in cand[:15]]
