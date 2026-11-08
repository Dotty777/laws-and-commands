"""Final compile: apply checker corrections and reconciliation ops, combine extends/parallels per record,
format references, assign proposed IDs, and write audit/findings.json + summary stats."""
import sys, json, collections, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import *

B = Bible(); recs = load_catalogue(); byid = {r["id"]: r for r in recs}
ORDER = B.order; BOOKNUM = {b: i + 1 for i, b in enumerate(ORDER)}
ALL = json.load(open("/home/claude/work/review/all_findings.json"))
K = {o["key"]: dict(o) for o in ALL}
log = collections.Counter()

# ---------- 1. corrections from the independent accuracy check (random sample)
def setref(k, ref): K[k]["reference"] = ref
setref("B01#1", "Genesis 14:22–24")
setref("B03#85", "Leviticus 23:27, 29, 32")
K["B05#33"]["note"] = (K["B05#33"].get("note", "") + " Retitle the record (listen and obey) when extending.").strip()
K["S02#41"]["audience"] = "Personal"; K["B10#31"]["audience"] = "Personal"
K["B23#7"].update({"verdict": "parallel", "reference": "2 Corinthians 11:30", "existing_id": "AUD-51-12-7"})
DROPS = {"B15#146", "B16#44", "B20#146", "B20#162", "S08#14"}
# the checker also asked to drop the Matthew parallel of the betrayal woe
for k, o in K.items():
    if o["reference"].startswith("Matthew 26:20") and o["verdict"] == "new" and "betray" in o["title"].lower():
        DROPS.add(k)
for k in DROPS:
    K[k]["_dead"] = "accuracy check: out of scope"; log["dropped by accuracy check"] += 1

# ---------- 2. reconciliation ops
absorbed_into = collections.defaultdict(list)
for line in open("/home/claude/work/review/merge.jsonl"):
    if not line.strip(): continue
    op = json.loads(line)
    t = op["op"]
    if t == "absorb":
        p = op["primary"]
        for a in op["absorb"]:
            if a in K and not K[a].get("_dead"):
                K[a]["_dead"] = f"absorbed into {p}"; absorbed_into[p].append(K[a]["reference"]); log["absorbed"] += 1
    elif t == "widen":
        if not K[op["keep"]].get("_dead"):
            K[op["keep"]]["reference"] = op["reference"]
        for d in op["drop"]:
            K[d]["_dead"] = f"widened into {op['keep']}"; log["widened"] += 1
    elif t == "to_parallel":
        K[op["key"]].update({"verdict": "parallel", "existing_id": op["existing_id"]}); log["to_parallel"] += 1
    elif t == "drop":
        K[op["key"]]["_dead"] = "reconciliation drop"; log["recon drop"] += 1

live = [o for o in K.values() if not o.get("_dead")]

# ---------- 3. reference formatting
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
            if na == last_name and ca == last_ch:
                piece = body
            elif na == last_name:
                piece = f"{ca}:{body}"
            else:
                piece = f"{na} {ca}:{body}"
            last_ch = ca
        else:
            body = f"{ca}:{va}–{cz}:{vz}"
            piece = body if na == last_name else f"{na} {body}"
            last_ch = cz
        last_name = na if a["ch"] == z["ch"] else nz
        out.append(piece)
    s = ""
    for i, p in enumerate(out):
        s += (", " if i else "") + p
    return s

def rec_verses(r, primary_only=False):
    s = set(B.expand(r["reference"])[0])
    if not primary_only:
        for a in r.get("additional_scripture") or []:
            s |= set(B.expand(a["reference"])[0])
    return s

# ---------- 4. new records
news = [o for o in live if o["verdict"] == "new"]
for o in news:
    o["idx"] = B.expand(o["reference"])[0]
    o["reference"] = fmt(o["idx"]) or o["reference"]
    o["additional"] = "; ".join(absorbed_into.get(o["key"], []))
# drop exact duplicates left (same verse set + type)
seen, keep = {}, []
for o in sorted(news, key=lambda o: (o["idx"][0], {"high": 0, "medium": 1, "low": 2}[o["confidence"]])):
    sig = (tuple(o["idx"]), o["record_type"])
    if sig in seen:
        log["exact duplicate new"] += 1
        seen[sig]["additional"] = "; ".join(x for x in [seen[sig]["additional"]] if x)
        continue
    seen[sig] = o; keep.append(o)
news = keep
cnt = collections.Counter()
for o in news:
    v = B.verses[o["idx"][0]]
    name, ch = ref_name(v["book"], v["ch"])
    ch = 13 if (v["book"], v["ch"]) == ("Daniel", 13) else (14 if (v["book"], v["ch"]) == ("Daniel", 14) else v["ch"])
    base = f'GAP-{BOOKNUM[v["book"]]:02d}-{ch}-{v["v"].split("-")[0]}'
    cnt[base] += 1
    o["proposed_id"] = base if cnt[base] == 1 else f"{base}-{cnt[base]}"
    o["book"] = v["book"]; o["first_idx"] = o["idx"][0]

# ---------- 5. extends grouped per existing record
ext_by = collections.defaultdict(list)
for o in live:
    if o["verdict"] == "extend": ext_by[o["existing_id"]].append(o)
extends = []
for rid, group in ext_by.items():
    r = byid[rid]
    prim, allv = rec_verses(r, True), rec_verses(r)
    add = set()
    for o in group: add |= set(B.expand(o["reference"])[0])
    add -= allv
    if not add:
        log["extend already covered"] += len(group); continue
    union = sorted(prim | add)
    contiguous = all(union[i + 1] - union[i] <= 1 for i in range(len(union) - 1)) and B.verses[union[0]]["book"] == B.verses[union[-1]]["book"]
    conf = min((o["confidence"] for o in group), key=lambda c: {"high": 0, "medium": 1, "low": 2}[c])
    notes = " / ".join(dict.fromkeys(o.get("note", "") or o["title"] for o in group))
    extends.append({"existing_id": rid, "current": r["reference"], "title": r["title"], "record_type": r["record_type"],
                    "add": fmt(add), "new_primary": fmt(union) if contiguous else "", "as_additional": "" if contiguous else fmt(add),
                    "confidence": conf, "note": notes[:600], "keys": [o["key"] for o in group], "book": r["book"],
                    "first_idx": min(add)})
# ---------- 6. parallels grouped per (record, verses)
parallels = []
par_seen = set()
for o in live:
    if o["verdict"] != "parallel": continue
    r = byid[o["existing_id"]]
    add = set(B.expand(o["reference"])[0]) - rec_verses(r)
    if not add:
        log["parallel already linked"] += 1; continue
    sig = (o["existing_id"], tuple(sorted(add)))
    if sig in par_seen:
        log["parallel duplicate"] += 1; continue
    par_seen.add(sig)
    parallels.append({"existing_id": o["existing_id"], "add": fmt(add), "title": r["title"], "existing_ref": r["reference"],
                      "record_type": r["record_type"], "confidence": o["confidence"], "note": o.get("note", "") or o["title"],
                      "key": o["key"], "book": B.verses[min(add)]["book"], "first_idx": min(add)})

# ---------- 7. Rambam status
rambam = json.load(open("/home/claude/work/check613.json"))
status = {}
for x in rambam:
    if x["fine"]:
        status[x["mitzva"]] = {"status": "itemized", "finding": ""}; continue
    idx = set(x["idx"]); hits = []
    for o in news:
        if idx & set(o["idx"]): hits.append(f'new record proposed: {o["proposed_id"]} "{o["title"]}"')
    for e in extends:
        if idx & set(B.expand(e["add"])[0] if e["add"] else []): hits.append(f'extend {e["existing_id"]} to cover it')
    for p in parallels:
        if idx & set(B.expand(p["add"])[0]): hits.append(f'link as parallel to {p["existing_id"]} ("{p["title"]}")')
    mentioned = [o for o in ALL if re.search(r"\b" + re.escape(x["mitzva"]) + r"\b", o.get("note", ""))]
    if hits:
        st = "new record proposed" if hits[0].startswith("new") else ("extend" if hits[0].startswith("extend") else "parallel link")
        status[x["mitzva"]] = {"status": st, "finding": "; ".join(dict.fromkeys(hits))[:400]}
    elif mentioned:
        status[x["mitzva"]] = {"status": "reviewed", "finding": mentioned[0].get("note", "")[:300]}
    else:
        status[x["mitzva"]] = {"status": "broad only", "finding": ""}
json.dump(status, open("/home/claude/work/audit/rambam_status.json", "w"), ensure_ascii=False, indent=1)

for o in news: o.pop("idx", None)
out = {"generated": "2026-11-08", "catalogue": {"records": len(recs), "sha256": "801c93948bdcf13f65c54fe54676fd4a04c4a49b71fab8b0a5ab468077e2b098"},
       "new": sorted(news, key=lambda o: o["first_idx"]), "extend": sorted(extends, key=lambda e: e["first_idx"]),
       "parallel": sorted(parallels, key=lambda p: p["first_idx"]), "log": dict(log),
       "removed": [{"key": k, "reference": o["reference"], "title": o["title"], "why": o["_dead"]} for k, o in K.items() if o.get("_dead")]}
json.dump(out, open("/home/claude/work/audit/findings_final.json", "w"), ensure_ascii=False, indent=1)
print(dict(log))
print("new", len(news), collections.Counter(o["confidence"] for o in news))
print("new by type", collections.Counter(o["record_type"] for o in news))
print("new high+medium by type", collections.Counter(o["record_type"] for o in news if o["confidence"] != "low"))
print("extend records", len(extends), collections.Counter(e["confidence"] for e in extends))
print("parallel links", len(parallels), collections.Counter(p["confidence"] for p in parallels))
print("rambam", collections.Counter(v["status"] for v in status.values()))
