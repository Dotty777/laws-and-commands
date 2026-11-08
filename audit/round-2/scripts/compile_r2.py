"""Compile round-2 decisions into proposals and recompute coverage.
python3 -I /home/claude/work/compile_r2.py [--partial]"""
import json, re, sys, collections, copy
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
import cov2

PARTIAL = "--partial" in sys.argv
W = "/home/claude/work"
REPO = "/home/claude/repos/laws-and-commands"
OUT = f"{W}/audit/round2"
import os; os.makedirs(OUT, exist_ok=True)
B = Bible()
recs = json.load(open(f"{REPO}/data/current/commands.json")); byid = {r["id"]: r for r in recs}
ix = json.load(open(f"{W}/round2/index.json"))
TOP = set(json.load(open(f"{W}/audit/topics50.json")))
drafts = {("N:" + d["proposed_id"]): d for d in json.load(open(f"{W}/audit/round2_open_new.json"))}
sims = json.load(open(f"{W}/audit/sim_cands.json"))
CONF = {"high": 0, "medium": 1, "low": 2}


# ---------------------------------------------------------------- reference formatting (as round 1)
def ref_name(book, ch):
    if (book, ch) == ("Daniel", 13): return "Susanna", 1
    if (book, ch) == ("Daniel", 14): return "Bel and the Dragon", 1
    if book == "Psalms": return "Greek Psalm", ch
    return book, ch


def fmt(idxs):
    idxs = sorted(set(idxs))
    if not idxs: return ""
    runs, cur = [], [idxs[0]]
    for i in idxs[1:]:
        if i == cur[-1] + 1 and B.verses[i]["book"] == B.verses[cur[-1]]["book"]:
            cur.append(i)
        else:
            runs.append(cur); cur = [i]
    runs.append(cur)
    out, last_name, last_ch = [], None, None
    for r in runs:
        a, z = B.verses[r[0]], B.verses[r[-1]]
        na, ca = ref_name(a["book"], a["ch"]); nz, cz = ref_name(z["book"], z["ch"])
        va, vz = a["v"].split("-")[0], (z["v"].split("-")[-1] if "-" in z["v"] else z["v"])
        if a["ch"] == z["ch"]:
            body = f"{va}" if r[0] == r[-1] else f"{va}–{vz}"
            piece = body if (na == last_name and ca == last_ch) else (f"{ca}:{body}" if na == last_name else f"{na} {ca}:{body}")
            last_ch = ca
        else:
            body = f"{ca}:{va}–{cz}:{vz}"
            piece = body if na == last_name else f"{na} {body}"
            last_ch = cz
        last_name = na if a["ch"] == z["ch"] else nz
        out.append(piece)
    return ", ".join(out)


def verses_of(r, primary_only=False):
    s = set(expand_strict(r["reference"])[0])
    if not primary_only:
        for a in r.get("additional_scripture") or []:
            s |= set(expand_strict(a["reference"] if isinstance(a, dict) else str(a))[0])
    return s


def expand_strict(ref):
    """Bible.expand, but a bare verse number does not pull in the lettered verses that follow it
    (1 Kings 2:35 is not 2:35-35o) unless the range runs past them or the letter is named."""
    idx, p = B.expand(ref)
    keep, seen_after = [], set()
    for i in sorted(idx, reverse=True):
        v = B.verses[i]; chap = (v["book"], v["ch"])
        if v.get("let"):
            named = re.search(r"(?<!\d)" + re.escape(str(v["n0"])) + re.escape(v["let"]) + r"\b", ref)
            if not named and chap not in seen_after:
                continue
        keep.append(i); seen_after.add(chap)
    return sorted(keep), p


def url_for(i):
    return B.verses[i]["url"].replace("https://staging-8e0d-waywardnightjars.wpcomstaging.com", "https://saints.bible")


# ---------------------------------------------------------------- load decisions
dec, problems, order = {}, [], []
for b, items in ix.items():
    path = f"{W}/round2/out/{b}.jsonl"
    try:
        rows = [json.loads(l) for l in open(path) if l.strip()]
    except FileNotFoundError:
        problems.append(f"{b}: no output"); continue
    done = any(r.get("done") for r in rows)
    if not done: problems.append(f"{b}: not finished")
    for r in rows:
        if r.get("done"): continue
        r["batch"] = b
        if r.get("item") not in items: problems.append(f"{b}: stray item {r.get('item')}"); continue
        if r["item"] not in dec: order.append(r["item"])
        dec[r["item"]] = r
    miss = [i for i in items if i not in dec]
    if miss: problems.append(f"{b}: {len(miss)} items undecided")
if problems and not PARTIAL:
    print("\n".join(problems)); sys.exit("incomplete — rerun with --partial to compile what exists")


def item_kind(item):
    if item.startswith("RC"): return "reconciliation"
    return {"N": "held new record", "E": "held extension", "P": "held parallel", "S": "similarity candidate",
            "U": "sweep verse", "V": "residual verse"}[item[0]]


def item_ref(item):
    """the verses the item was about"""
    if item.startswith("N:"): return drafts[item]["reference"] if item in drafts else ""
    if item[:2] in ("E:", "P:"): return item.split("|", 1)[1]
    if item.startswith("SIM"):
        s = sims[int(item[3:]) - 1]; return fmt([s[1]])
    if item.startswith("U"): return fmt([int(item[1:])])
    return ""


def addl(d, item):
    out = []
    items = list(d.get("additional_scripture") or [])
    if isinstance(d.get("additional"), str): items += [x.strip() for x in d["additional"].split(";") if x.strip()]
    elif isinstance(d.get("additional"), list): items += d["additional"]
    for a in items:
        ref = a.get("reference") if isinstance(a, dict) else str(a)
        ai, ap = expand_strict(ref)
        if not ai or ap: flags.append(f"{item}: bad additional reference {ref!r}"); continue
        out.append({"reference": fmt(ai), "context": (a.get("context") or a.get("context_note") or "") if isinstance(a, dict) else "", "url": url_for(ai[0])})
    return out


# ---------------------------------------------------------------- reconciliation overrides (round2/reconcile.json)
REC = {"drop": {}, "set": {}}
if os.path.exists(f"{W}/round2/reconcile.json"):
    REC = json.load(open(f"{W}/round2/reconcile.json"))
superseded = []
for item, why in REC.get("drop", {}).items():
    if item in dec:
        superseded.append({"item": item, "kind": item_kind(item), "decision": dec[item]["decision"], "reference": dec[item].get("reference", ""), "why": why})
        dec[item] = dict(dec[item], decision="superseded", reason=why)
for item, ch in REC.get("set", {}).items():
    if item in dec:
        dec[item] = dict(dec[item], **ch, reconciled=True)
for a in REC.get("add", []):
    a = dict(a, batch="reconciliation", reconciled=True); dec[a["item"]] = a; order.append(a["item"])
for item, adds in REC.get("add_additional", {}).items():
    if item in dec:
        dec[item] = dict(dec[item], additional_scripture=list(dec[item].get("additional_scripture") or []) + adds, reconciled=True)

# ---------------------------------------------------------------- build proposals
def build_one(item, d):
    kind = d["decision"]
    idx, p = expand_strict(d.get("reference", ""))
    if not idx or p:
        flags.append(f"{item}: bad reference {d.get('reference')!r}"); return
    ref = fmt(idx)
    if kind == "record_new":
        newrecs.append({"item": item, "kind": item_kind(item), "idx": idx, "reference": ref, "record_type": d["record_type"],
                        "title": d["title"].strip().rstrip("."), "speaker": d["speaker"], "recipient": d["recipient"],
                        "origin": d["origin"], "audience": d["audience"], "topic": d["topic"], "confidence": d["confidence"],
                        "reason": d["reason"], "draft_id": item[2:] if item.startswith("N:") else "", "batch": d["batch"],
                        "book": B.verses[idx[0]]["book"], "additional": addl(d, item)})
    elif kind == "record_extend":
        e = d["existing_id"]; r = byid[e]
        add = set(idx) - verses_of(r, primary_only=True)
        if not add: flags.append(f"{item}: extend {e} adds nothing new"); return
        ext[e]["add"] |= add; ext[e]["items"].append(item); ext[e]["reasons"].append(d["reason"]); ext[e]["conf"].append(d["confidence"])
    elif kind == "record_parallel":
        e = d["existing_id"]; r = byid[e]
        if set(idx) <= verses_of(r):
            flags.append(f"{item}: parallel {ref} already in {e}"); return
        key = (e, ref)
        if key in par:
            par[key]["items"].append(item); return
        par[key] = {"existing_id": e, "reference": ref, "idx": idx, "context": d.get("context", "").strip(), "items": [item],
                    "confidence": d["confidence"], "reason": d["reason"], "batch": d["batch"]}


newrecs, ext, par, declined, flags = [], collections.defaultdict(lambda: {"add": set(), "items": [], "reasons": [], "conf": []}), {}, [], []
for item in list(order):
    d = dec[item]; kind = d["decision"]
    if kind == "superseded": continue
    if kind == "no_record":
        declined.append({"item": item, "kind": item_kind(item), "reference": item_ref(item) or d.get("reference", ""),
                         "confidence": d["confidence"], "reason": d["reason"], "batch": d["batch"]})
        continue
    parts = [x.strip() for x in d.get("reference", "").split(";") if x.strip()]
    if kind == "record_parallel" and len(parts) > 1:
        for k, part in enumerate(parts):
            build_one(item, dict(d, reference=part))
    else:
        build_one(item, d)

# ---- dedupe new records: identical verse sets and type
seen, keep = {}, []
for o in sorted(newrecs, key=lambda o: (o["idx"][0], CONF[o["confidence"]])):
    sig = (tuple(o["idx"]), o["record_type"])
    if sig in seen:
        seen[sig]["merged_items"] = seen[sig].get("merged_items", []) + [o["item"]]; continue
    seen[sig] = o; keep.append(o)
newrecs = keep
# ---- overlaps worth a look: new record vs existing record of the same type sharing verses, or new vs new
cov_prim = collections.defaultdict(set)
for r in recs:
    for i in verses_of(r, primary_only=True): cov_prim[i].add(r["id"])
for o in newrecs:
    same = sorted({rid for i in o["idx"] for rid in cov_prim.get(i, ()) if byid[rid]["record_type"] == o["record_type"]})
    if same: o["overlap_existing"] = same
for a in range(len(newrecs)):
    for b in range(a + 1, len(newrecs)):
        x, y = newrecs[a], newrecs[b]
        if x["book"] == y["book"] and set(x["idx"]) & set(y["idx"]):
            x.setdefault("overlap_new", []).append(y["item"]); y.setdefault("overlap_new", []).append(x["item"])

# ---- IDs in the published scheme: AUD-<book no>-<chapter>-<first verse>, "-2" on collision
taken = set(byid)
for o in sorted(newrecs, key=lambda o: o["idx"][0]):
    v = B.verses[o["idx"][0]]
    base = f"AUD-{B.order.index(v['book']) + 1:02d}-{v['ch']}-{v['v'].split('-')[0]}"
    cid, n = base, 1
    while cid in taken:
        n += 1; cid = f"{base}-{n}"
    taken.add(cid); o["id"] = cid
    o["scripture_url"] = url_for(o["idx"][0])

# ---- combined extensions
LAW = cov2.LAW
extl = []
for e, x in ext.items():
    r = byid[e]; prim = verses_of(r, primary_only=True)
    newp = sorted(prim | x["add"])
    row = {"existing_id": e, "current": r["reference"], "title": r["title"], "record_type": r["record_type"], "add": fmt(x["add"]),
           "proposed": fmt(newp), "items": x["items"], "reasons": x["reasons"], "confidence": min(x["conf"], key=lambda c: -CONF[c]),
           "book": r["book"]}
    if r["book"] in LAW and len(newp) > 8:
        row["note"] = f"Law book: the record would span {len(newp)} verses (over the 8-verse itemization line)."
    extl.append(row)
extl.sort(key=lambda r: min(B.expand(r["current"])[0] or [0]))
parl = sorted(par.values(), key=lambda p: p["idx"][0])
for p in parl:
    p["url"] = url_for(p["idx"][0]); p["existing_ref"] = byid[p["existing_id"]]["reference"]; p["title"] = byid[p["existing_id"]]["title"]
    p["book"] = B.verses[p["idx"][0]]["book"]

# ---------------------------------------------------------------- coverage before / after
D = cov2.directive_set()
n0, h0, by0, c0 = cov2.stats(B, recs, D)
after = copy.deepcopy(recs); aid = {r["id"]: r for r in after}
for o in newrecs:
    after.append({"id": o["id"], "reference": o["reference"], "additional_scripture": [{"reference": a["reference"]} for a in o["additional"]], "book": o["book"]})
for x in extl:
    aid[x["existing_id"]]["reference"] = x["proposed"]
for p in parl:
    aid[p["existing_id"]].setdefault("additional_scripture", []).append({"reference": p["reference"], "url": p["url"], "context_note": p["context"]})
n1, h1, by1, c1 = cov2.stats(B, after, D)
from audit_lib import coverage
any0, _, _ = coverage(B, recs); any1, _, _ = coverage(B, after)
newly_attached = sorted(set(any1) - set(any0))
cov = {"directive_verses": n0, "covered_before": h0, "covered_after": h1,
       "pct_before": round(100 * h0 / n0, 1), "pct_after": round(100 * h1 / n0, 1),
       "verses_attached_any_before": len(any0), "verses_attached_any_after": len(any1), "newly_attached_verses": len(newly_attached),
       "by_book": {bk: {"directive": by0[bk][0], "before": by0[bk][1], "after": by1[bk][1]} for bk in B.order if bk in by0}}

summary = {
    "items": len(order), "by_kind_decision": collections.Counter(f"{item_kind(i)} → {dec[i]['decision']}" for i in order),
    "by_decision": collections.Counter(dec[i]["decision"] for i in order),
    "new_records": len(newrecs), "extended_records": len(extl), "extension_verses": sum(len(ext[e]["add"]) for e in ext),
    "parallel_links": len(parl), "declined": len(declined), "superseded": len(superseded),
    "new_additional_links": sum(len(o["additional"]) for o in newrecs), "flags": flags, "problems": problems, "coverage": {k: v for k, v in cov.items() if k != "by_book"},
    "new_by_type": collections.Counter(o["record_type"] for o in newrecs), "new_by_conf": collections.Counter(o["confidence"] for o in newrecs),
}
for o in newrecs: o.pop("idx", None)
for p in parl: p.pop("idx", None)
json.dump([dec[i] for i in order], open(f"{OUT}/decisions.json", "w"), ensure_ascii=False, indent=1)
json.dump(newrecs, open(f"{OUT}/new_records.json", "w"), ensure_ascii=False, indent=1)
json.dump(extl, open(f"{OUT}/extend.json", "w"), ensure_ascii=False, indent=1)
json.dump(parl, open(f"{OUT}/parallel.json", "w"), ensure_ascii=False, indent=1)
json.dump(declined, open(f"{OUT}/declined.json", "w"), ensure_ascii=False, indent=1)
json.dump(superseded, open(f"{OUT}/superseded.json", "w"), ensure_ascii=False, indent=1)
json.dump(cov, open(f"{OUT}/coverage.json", "w"), ensure_ascii=False, indent=1)
json.dump(summary, open(f"{OUT}/summary.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1)[:3500])
