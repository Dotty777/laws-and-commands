"""Turn the reviewed batches into categorized findings for the Torah Law (556) check."""
import json, sys, collections, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
W = "/home/claude/work"; R3 = f"{W}/round3"; OUT = f"{W}/audit/torah-laws"
recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json")); byid = {r["id"]: r for r in recs}
rows = json.load(open(f"{OUT}/maimonides-613.json")); rowby = {r["m"]: r for r in rows}
pairs = json.load(open(f"{R3}/pairs.json"))
def load(b): return [json.loads(l) for l in open(f"{R3}/out/{b}.jsonl") if l.strip() and not json.loads(l).get("done")]
D1 = {o["id"]: o for o in load("D1")}; D2 = {o["id"]: o for o in load("D2")}; L1 = {o["id"]: o for o in load("L1")}
TL = [r for r in recs if r["mosaic_type"] == "Law"]; TLids = {r["id"] for r in TL}
lab = lambda i: byid[i]["study_placement"]

# ---------------- commandments no record states, by why (judged from each reviewer note)
TEXT_GAP = {"P83": "Deuteronomy 12:5–6 (bring offerings to the chosen place) is attached to no record; C0571 gives the general rule from Leviticus 17.",
            "P85": "Deuteronomy 12:26 (take your holy things to the chosen place) is attached to no record.",
            "P155": "Exodus 20:8 ('remember the Sabbath day to keep it holy') is attached to no record.",
            "P222": "Deuteronomy 24:1 describes the written bill of divorce; the only record there (C1166) states the remarriage ban.",
            "N133": "Leviticus 22:10 ('no outsider shall eat the holy thing') has no record of its own; AUD-03-22-10 states only the lodger and hired-worker clause.",
            "N286": "Exodus 23:1b (do not join the wicked as an unrighteous witness) has no record; C0216 states only the false-report clause."}
SAINTS_DIFF = {"P82": "The Saints (Greek) text says 'redeem it' / 'give its value', with no neck-breaking.",
               "P175": "The Saints (Greek) text of Exodus 23:2 lacks 'incline after the majority'.",
               "N88": "The Saints text has a purpose clause ('so that it is not torn'), not a prohibition.",
               "N195": "The Saints text of Leviticus 19:26 reads 'eat on the mountains'.",
               "N297": "The Saints text of Leviticus 19:16 reads 'conspire against the blood'; C0614 states that.",
               "N309": "The Saints text describes the ravine as already untilled."}
MISSING_MOSAIC = {"N184": "only the Genesis 9:4 record C0019 (no Mosaic type) states it; Leviticus 17:10–12, 14 are attached to no record.",
                  "P215": "only the Genesis 17 record C0036 states it; Leviticus 12:3 is attached to no record.",
                  "P99": "Leviticus 15:19–24 is held only by the topical study S062; no itemized record.",
                  "P53": "only the topical studies S050 and S134 hold it; Exodus 23:17 has no itemized record.",
                  "N171": "Deuteronomy 14:1 is held only by the topical study S126; C0655 covers priests only.",
                  "P176": "Deuteronomy 16:18 is held only by the topical study S135; C0956 is the one-time appointment of Deuteronomy 1:13."}
gaps = []
for r in rows:
    if r["status"] in ("partial", "broad_only"):
        cat = "Text states it, no record does" if r["m"] in TEXT_GAP else ("Saints wording differs" if r["m"] in SAINTS_DIFF else "Maimonides' reading goes beyond the plain text")
        why = TEXT_GAP.get(r["m"]) or SAINTS_DIFF.get(r["m"]) or r["note"]
        gaps.append(dict(r, category=cat, why=why))
    elif r["m"] in MISSING_MOSAIC:
        gaps.append(dict(r, category="No itemized Mosaic record (only a Genesis record or a topical study)", why=MISSING_MOSAIC[r["m"]]))
gap_counts = collections.Counter(g["category"] for g in gaps)

# ---------------- duplicates
dups = []
for k, o in D1.items():
    if o["verdict"] in ("duplicate", "overlap"):
        a, b = pairs[k]
        dups.append({"kind": "Same passage, same direction" if o["verdict"] == "duplicate" else "Same passage, one record contains the other",
                     "records": [a, b], "keep": o["keep"], "action": o["note"], "check": f"pair {k}", "confidence": o["confidence"]})
for k, o in D2.items():
    if o["verdict"] == "restatement":
        a, b = pairs[k]
        dups.append({"kind": "Same law recorded again in another passage", "records": [a, b], "keep": o["keep"], "action": o["note"], "check": f"pair {k}", "confidence": o["confidence"]})
dups += [
    {"kind": "Same law recorded again in another passage", "records": ["C0129", "AUD-02-31-13", "C0152"], "keep": "C0129",
     "action": "Three records keep the Sabbath (Exodus 16:23, 31:13–17 as Torah Law; Exodus 20:10 as Mosaic Command); Exodus 20:8 itself is attached to none.",
     "check": "613 cross-check (P154)", "confidence": "medium"},
    {"kind": "Same law recorded again in another passage", "records": ["C0949", "C1054"], "keep": "C1054",
     "action": "Numbers 35:30 and Deuteronomy 17:6 both forbid a death sentence on one witness; one record could carry the other as Additional Scripture.",
     "check": "613 cross-check (N288)", "confidence": "medium"}]

# ---------------- labels, record level
labels = {}
def add(rid, suggest, category, evidence, check, conf):
    if rid not in byid: return
    if rid in labels:
        labels[rid]["checks"].append(check); return
    labels[rid] = {"id": rid, "reference": byid[rid]["reference"], "title": byid[rid]["title"], "current": lab(rid), "suggest": suggest,
                   "category": category, "evidence": evidence, "checks": [check], "confidence": conf}
CAT_CLEAR = "1 · Clear correction (matches the catalogue's own sibling records)"
CAT_TWIN = "2 · Positive half filed as Instruction while its negative half is Torah Law"
CAT_OBS = "3 · Standing observance filed as Instruction while comparable ones are Torah Law"
CAT_HIST = "4 · Conquest-era bans split between Torah Law and historical directions"
CAT_DEC = "5 · Ten Commandments filed as Mosaic Command (a convention choice)"
CAT_CMD = "6 · Other standing duties filed as Mosaic Command"
DECALOGUE = [f"C0{n}" for n in range(146, 160)]
CONQUEST = {"AUD-05-20-17", "C0244", "C0245", "C0997", "C0998", "C1197"}
for rid, o in L1.items():
    if o["verdict"] == "relabel":
        if rid in CONQUEST:
            add(rid, "One label for all six (now Torah Law)", CAT_HIST, o["note"], "label review", o["confidence"]); continue
        add(rid, o["suggest"], CAT_CLEAR, o["note"], "label review", o["confidence"])
TWIN = {"C1121": "C1120", "C1055": "C1056", "C1124": "C1123", "C1150": "C1151", "C0215": "C0214", "C1128": "C1127",
        "C1043": "C1042", "C1039": "C1037", "C0105": "C0109", "C0800": "C0418", "C0801": "C0419"}
for k, o in D1.items():
    if o.get("label_conflict"):
        a, b = pairs[k]
        for x in (a, b):
            if byid[x]["mosaic_type"] in ("Instruction",) and x in TWIN:
                add(x, "Torah Law", CAT_TWIN, f"Twin {TWIN[x]} ({lab(TWIN[x])}): " + o["note"], f"pair {k}", o["confidence"])
for r in rows:
    if not r["mislabel"] or not r["records"]: continue
    rid = r["records"][0]
    cur = byid[rid]["mosaic_type"] or ""
    if cur == "Instruction":
        cat = CAT_TWIN if rid in TWIN else CAT_OBS
        add(rid, "Torah Law", cat, (f"Twin {TWIN[rid]} ({lab(TWIN[rid])}). " if rid in TWIN else "") + r["note"], f"613 {r['m']}", r["confidence"])
    elif cur == "Command":
        if rid == "C0956": continue   # one-time appointment; the gap is Deuteronomy 16:18 (see gaps)
        if rid in DECALOGUE:
            add(rid, "Torah Law, if the Ten Commandments are to count as laws", CAT_DEC, r["note"], f"613 {r['m']}", r["confidence"])
        else:
            add(rid, "Torah Law", CAT_CMD, r["note"], f"613 {r['m']}", r["confidence"])
        for extra in r["records"][1:]:
            if extra in byid and byid[extra]["mosaic_type"] == "Command" and extra not in DECALOGUE and extra != "C0956":
                add(extra, "Torah Law", CAT_CMD, r["note"], f"613 {r['m']}", r["confidence"])
    elif rid in CONQUEST:
        add(rid, "One label for all six (now historical direction)", CAT_HIST, r["note"], f"613 {r['m']}", r["confidence"])
# D1 label conflict involving a Command record
for k, o in D1.items():
    if o.get("label_conflict"):
        for x in pairs[k]:
            if byid[x]["mosaic_type"] == "Command":
                add(x, "Torah Law", CAT_DEC if x in DECALOGUE else CAT_CMD, o["note"], f"pair {k}", o["confidence"])
for x in DECALOGUE:
    add(x, "Torah Law, if the Ten Commandments are to count as laws", CAT_DEC, "Exodus 20:3–17 are all filed as Mosaic Command; their parallels in Leviticus 19 and 26 are Torah Law.", "label pattern", "high")
for k, o in D2.items():
    if o.get("label_conflict"):
        a, b = pairs[k]
        add(b if byid[b]["mosaic_type"] == "Law" else a, "Mosaic Command (fold into C0146)", CAT_CLEAR, o["note"], f"pair {k}", o["confidence"])
labels = sorted(labels.values(), key=lambda x: (x["category"], B.expand(x["reference"])[0][0] if B.expand(x["reference"])[0] else 0))
lab_counts = collections.Counter(x["category"] for x in labels)

# ---------------- count scenarios
def cat_ids(cat): return {x["id"] for x in labels if x["category"] == cat}
clear_in = {x["id"] for x in labels if x["category"] == CAT_CLEAR and x["suggest"] == "Torah Law" and byid[x["id"]]["mosaic_type"] != "Law"}
clear_out = {x["id"] for x in labels if x["category"] == CAT_CLEAR and byid[x["id"]]["mosaic_type"] == "Law"}
redundant = {d["records"][1] if d["keep"] == d["records"][0] else d["records"][0] for d in dups if d["kind"] == "Same passage, same direction"}
s1 = len(TL) - len(redundant & TLids) - len(clear_out) + len(clear_in)
cons = (cat_ids(CAT_TWIN) | cat_ids(CAT_OBS)) - clear_in
s2 = s1 + len(cons)
dec = cat_ids(CAT_DEC); cmd = cat_ids(CAT_CMD); conq = cat_ids(CAT_HIST)
conq_in = {i for i in conq if byid[i]["mosaic_type"] != "Law"}
scen = [{"step": "Current Torah Law count", "change": 0, "count": len(TL)},
        {"step": f"Clear fixes: remove {len(redundant & TLids)} duplicate, move {len(clear_out)} out, move {len(clear_in)} in", "change": s1 - len(TL), "count": s1},
        {"step": f"Make the Instruction / Torah Law split consistent ({len(cons)} standing rules now filed as Instruction)", "change": len(cons), "count": s2},
        {"step": f"Conquest-era bans: one label for all {len(conq)} (all Torah Law: +{len(conq_in)}; all historical: −1)", "change": None, "count": None},
        {"step": f"Count the Ten Commandments ({len(dec)}) and the other standing duties filed as Mosaic Command ({len(cmd)}) as Torah Law", "change": len(dec) + len(cmd), "count": s2 + len(dec) + len(cmd)}]

edit_notes = json.load(open(f"{R3}/edit_notes.json"))
F = {"gaps": gaps, "gap_counts": gap_counts, "duplicates": dups, "labels": labels, "label_counts": lab_counts, "scenarios": scen,
     "edit_notes": edit_notes, "unlinked_restatements": [
         {"verse": "Leviticus 19:11 ('you shall not steal')", "record": "C0155"}, {"verse": "Leviticus 19:15 (impartial judgment)", "record": "C0219"},
         {"verse": "Leviticus 20:15–16 (penalty for intercourse with an animal)", "record": "C0201"},
         {"verse": "Numbers 5:7 (confess, restore and add a fifth)", "record": "C0425"},
         {"verse": "Numbers 18:9–10 (most-holy portions eaten by every male)", "record": "C0445, C0437, C0388"}]}
json.dump(F, open(f"{OUT}/findings.json", "w"), ensure_ascii=False, indent=1)
print("gaps:", dict(gap_counts)); print("duplicates:", collections.Counter(d["kind"] for d in dups)); print("labels:", dict(lab_counts))
for s in scen: print(s)
print("edit notes:", len(edit_notes))
