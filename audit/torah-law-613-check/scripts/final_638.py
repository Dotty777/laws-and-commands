"""Current-state findings for the 638-record Torah Law set (after the contextual Torah Law audit, commit 467e928)."""
import json, sys, collections
sys.path.insert(0, "/home/claude/work")
W = "/home/claude/work"; A = f"{W}/audit/torah-laws"; REPO = "/home/claude/repos/laws-and-commands"
new = json.load(open(f"{REPO}/data/current/commands.json")); nby = {r["id"]: r for r in new}
L = json.load(open(f"{REPO}/audit/torah-law/decisions.json")); alias = L["aliases"]
R = json.load(open(f"{A}/reconcile-638.json")); F = json.load(open(f"{A}/findings.json")); M = json.load(open(f"{A}/maimonides-613.json"))
gapcat = {g["m"]: g["category"] for g in F["gaps"]}
# ---------------- 613 now, with the gap items checked one by one
OVER = {"P83": ("torah_law", ["TL-05-12-05"]), "P85": ("torah_law", ["TL-05-12-05"]), "P155": ("torah_law", ["C0129"]),
        "N184": ("torah_law", ["TL-03-17-10"]), "N286": ("torah_law", ["C0157"]),
        "P215": ("other_record", ["C0036"])}
# new records from the revision that also itemize a commandment already itemized by an older record
ALSO = {"P60": ["TL-03-22-27"], "P128": ["TL-05-14-22"], "N171": ["S126"]}
rows = []
for x in R["rows613_now"]:
    st, recs = x["new_status"], x["records_now"]
    if x["m"] in OVER: st, recs = OVER[x["m"]]
    recs = recs + [i for i in ALSO.get(x["m"], []) if i not in recs]
    if st == "not_stated_check_addition": st = "partial"
    types = [nby[i]["mosaic_type"] for i in recs if i in nby]
    if st in ("partial", "broad_only"):
        bucket = "not_stated:" + {"Text states it, no record does": "text", "Saints wording differs": "saints", "Maimonides' reading goes beyond the plain text": "reading"}.get(gapcat.get(x["m"]), "reading")
    elif st == "torah_law": bucket = "torah_law"
    elif st == "other_mosaic": bucket = "other_mosaic:" + next((t for t in types if t and t != "Law"), "?")
    else: bucket = "other_record"
    rows.append({"m": x["m"], "statement": x["statement"], "status_556": x["old_status"], "status_now": bucket, "records_now": recs,
                 "labels_now": [nby[i]["study_placement"] for i in recs if i in nby]})
now = collections.Counter(r["status_now"] for r in rows)
# ---------------- gaps now
gaps_now = [
    {"m": "N133", "state": "open", "what": "Leviticus 22:10a ('no outsider shall eat the holy thing') still has no record; AUD-03-22-10 states only the lodger and hired-worker clause."},
    {"m": "P222", "state": "open (borderline)", "what": "Deuteronomy 24:1's written bill of divorce has no record; C1166 states the remarriage ban. The bill is part of the case's background."},
    {"m": "P215", "state": "linked by choice", "what": "Leviticus 12:3 is now linked to the Genesis 17 record C0036, which the revision keeps as the primary (no Mosaic type)."},
    {"m": "P83", "state": "fixed", "what": "TL-05-12-05 now itemizes Deuteronomy 12:5–6, 11, 26–27."}, {"m": "P85", "state": "fixed", "what": "TL-05-12-05."},
    {"m": "P155", "state": "fixed", "what": "Exodus 20:8 is now Additional Scripture on C0129."},
    {"m": "N184", "state": "fixed", "what": "TL-03-17-10 now itemizes Leviticus 17:10–12, 14."},
    {"m": "P99", "state": "fixed", "what": "S062 is now Torah Law."}, {"m": "P176", "state": "fixed", "what": "S135 is now Torah Law."},
    {"m": "N286", "state": "fixed", "what": "Exodus 23:1 is now Additional Scripture on C0157 (false witness)."}]
# ---------------- duplicates now
dups_open = []
for d in R["duplicates_now"]:
    if d["now"] == "merged": continue
    labs = [nby[alias.get(x, x)]["study_placement"] for x in d["records"] if alias.get(x, x) in nby]
    recs = [alias.get(x, x) for x in d["records"]]
    if len(set(recs)) < len(recs): continue
    dups_open.append({"kind": d["kind"], "records": list(dict.fromkeys(recs)), "labels": labs, "action": d["action"], "origin": "found in the 556 check, still open"})
dups_open += [
    {"kind": "Same law recorded again in another passage", "records": ["C0201", "TL-03-20-15"], "labels": ["Torah Law", "Torah Law"],
     "action": "TL-03-20-15 (Leviticus 20:15–16) states the human death penalty that C0201 (Exodus 22:18) already states. The revision's note names C0651 and C0593 but not C0201. Link Leviticus 20:15–16 to C0201 instead, as the 556 check suggested.", "origin": "introduced by the revision"}]
# cross-references to verses the revision gave their own records: the catalogue does this in about 44 places, so not counted as duplicates
cross_refs_now = [
    {"records": ["C0733", "TL-03-25-54"], "note": "C0733 (Leviticus 25:41) lists Leviticus 25:54 as Additional Scripture; the revision made 25:54 its own record for the foreign-master case."},
    {"records": ["C0212", "TL-03-22-27"], "note": "C0212 (Exodus 22:29) lists Leviticus 22:27 as Additional Scripture; the revision also made 22:27 its own record for the eighth-day rule."},
    {"records": ["C0019", "TL-03-17-10"], "note": "C0019 (Genesis 9:4) and TL-03-17-10 both list Leviticus 3:17, 7:26–27 and Deuteronomy 12:23–25, 15:23 as Additional Scripture."}]
# merge rows that now name the same records
seen, merged = {}, []
for d in dups_open:
    key = tuple(sorted(d["records"]))
    if key in seen: continue
    seen[key] = d; merged.append(d)
dups_open = merged
for d in dups_open:
    if set(d["records"]) == {"C0391", "C0389"}:
        d["records"] = ["C0391", "C0389", "C0390"]; d["action"] = "C0391 repeats the leaven and honey bans of C0389 and C0390; narrow C0391 to the firstfruit permission in Leviticus 2:12."
dups_open = [d for d in dups_open if set(d["records"]) != {"C0390", "C0391"}]
for d in dups_open:
    if set(d["records"]) == {"C0096", "C0097"}:
        d["action"] = "C0096 (Instruction) still contains the not-raw and not-boiled rule now merged into C0097 (Torah Law); narrow C0096 to the positive manner of eating."
for d in dups_open:
    if set(d["records"]) == {"C0129", "AUD-02-31-13", "C0152"}:
        d["action"] = "Three Torah Law records keep the Sabbath: C0129 (Exodus 16:23, now with Exodus 20:8), AUD-02-31-13 (Exodus 31:13–17) and C0152 (Exodus 20:10). Choose one host and link the others."
# the revision itself dealt with two more cases
dups_other = [
    {"status": "Resolved by the revision", "kind": "Same passage, same direction", "records": ["C1120", "C1122"], "labels": ["Torah Law"],
     "action": "The revision merged C1122 into C1120.", "origin": "found in the 556 check"},
    {"status": "Resolved by the revision", "kind": "Same passage, one record contains the other", "records": ["C0391", "C0389", "C0390"], "labels": ["Torah Law", "Torah Law", "Torah Law"],
     "action": "The revision retitled C0391 as the firstfruit permission ('Leaven and honey may be brought as firstfruits'). Its reference still includes Leviticus 2:11; narrowing it to 2:12 would finish the fix.", "origin": "found in the 556 check"},
    {"status": "Left as a choice", "kind": "Same law recorded again in another passage", "records": ["C0129", "AUD-02-31-13"], "labels": ["Torah Law", "Torah Law"],
     "action": "C0129 (keep the Sabbath holy: Exodus 16:23, with 20:8) and AUD-02-31-13 (keep the Sabbath as a sign: Exodus 31:13–17) state the same keeping of the day. The revision keeps the holy-day command and the covenant sign apart on purpose, so this report does not count it. C0152 (the weekly work and rest) is a separate clause.",
     "origin": "found in the 556 check; narrowed by the accuracy check"}]
dups_other.append({"status": "Left as a choice", "kind": "Same law recorded again in another passage", "records": ["C0607", "C1175"], "labels": ["Torah Law", "Torah Law"],
     "action": "Leviticus 19:13 (do not hold a worker's wages overnight) and Deuteronomy 24:14–15 (pay them before sunset) are the negative and positive forms of one duty. Maimonides counts both (N238 and P200), and the catalogue keeps positive and negative forms apart elsewhere, so this report does not count it.",
     "origin": "found in the 556 check; reconsidered against the 613 matching"})
dups_open = [d for d in dups_open if set(d["records"]) not in ({"C0391", "C0389", "C0390"}, {"C0129", "AUD-02-31-13", "C0152"}, {"C0607", "C1175"})]
# Deut 6:14 restatement is now a same-label duplicate
for d in dups_open:
    if set(d["records"]) == {"C0146", "C0995"}:
        d["action"] = "Deuteronomy 6:14 restates Exodus 20:3; both are now Torah Law. Link Deuteronomy 6:14 to C0146 instead of keeping two records."
# ---------------- labels still inconsistent
GROUP = {"1": "Clear correction", "2": "Positive duty under Instruction, negative twin under Torah Law", "3": "Standing observance under Instruction, comparable ones under Torah Law",
         "4": "Conquest-era ban still a historical direction while its siblings are now Torah Law", "6": "Standing duty still under Mosaic Command"}
labels_open = []
for x in R["labels_now"]:
    if x["now"] != "unchanged": continue
    g = x["category"][0]
    if g == "5": continue
    if x["id"] == "C0995": continue  # now a duplicate (see duplicates)
    if x["id"] == "C0709": continue  # re-pointed by the revision to the standing law in Leviticus 24:16
    cur = nby[x["id"]]["study_placement"]
    sug = x["suggest"] if g != "4" else "Torah Law (as C0244, C0245, C0998 and AUD-05-20-17 now are)"
    grp, ev = GROUP[g], x["evidence"]
    if x["id"] in ("C0800", "C0801"):
        grp = "Same ban under two labels"
        ev = (f"C0418 (Leviticus 5:11, Torah Law) now forbids both oil and frankincense on the flour sin offering; {x['id']} states the same "
              f"{'oil' if x['id'] == 'C0800' else 'frankincense'} ban for the jealousy offering (Numbers 5:15) as Instruction.")
    if x["id"] == "C0827":
        ev = "The revision made the comparable standing priestly duties Torah Law: the lamps (C0284), the incense (C0337) and the daily offering (C0333). The priestly blessing is still Instruction."
    labels_open.append({"group": grp, "id": x["id"], "reference": nby[x["id"]]["reference"], "title": nby[x["id"]]["title"], "current": cur, "suggest": sug, "evidence": ev})
labels_open.append({"group": "New: same practice under two labels", "id": "C0573", "reference": nby["C0573"]["reference"], "title": nby["C0573"]["title"],
                    "current": nby["C0573"]["study_placement"], "suggest": "Torah Law",
                    "evidence": "The new TL-05-12-16 ('pour the blood onto the ground', Deuteronomy 12:16, 24) is Torah Law; C0573 states the same draining of blood in Leviticus 17:13 as Instruction."})
lg = collections.Counter(x["group"] for x in labels_open)
# ---------------- count steps from 638
to_law = [x for x in labels_open if "Torah Law" in x["suggest"]]
out = [x for x in labels_open if x["current"] == "Torah Law" and "Torah Law" not in x["suggest"]]
dup_tl = ["C0995", "TL-03-20-15"]
step1 = 638 - len(dup_tl) - len(out) + len([x for x in to_law if x["group"] == GROUP["1"]])
g23 = [x for x in to_law if x["group"] in (GROUP["2"], GROUP["3"], "Same ban under two labels", "New: same practice under two labels")]
step2 = step1 + len(g23)
g4 = [x for x in to_law if x["group"] == GROUP["4"]]; g6 = [x for x in to_law if x["group"] == GROUP["6"]]
steps = [{"step": "Current Torah Law count", "change": None, "count": 638},
         {"step": f"Clear fixes: fold C0995 into C0146 and TL-03-20-15 into C0201; move {len([x for x in to_law if x['group'] == GROUP['1']])} in" + (f"; move {len(out)} out" if out else ""), "change": step1 - 638, "count": step1},
         {"step": f"Finish the Instruction / Torah Law alignment ({len(g23)} records)", "change": len(g23), "count": step2},
         {"step": f"Conquest-era bans still historical ({len(g4)})", "change": len(g4), "count": step2 + len(g4)},
         {"step": f"Standing duties still under Mosaic Command ({len(g6)}), if they are to count", "change": len(g6), "count": step2 + len(g4) + len(g6)}]
change = R["count_change"]
res = {"count_change": change, "status_613_now": now, "rows613_now": rows, "gaps_now": gaps_now, "duplicates_open": dups_open, "duplicates_other": dups_other,
       "cross_references_now": cross_refs_now, "labels_open": labels_open,
       "labels_open_by_group": lg, "steps_from_638": steps, "edit_notes_now": R["edit_notes_now"], "edit_notes_records_now": R["edit_notes_records_now"],
       "labels_resolved_by_revision": R["labels_state"].get("resolved", 0) + 1,  # + C0709, re-pointed to Leviticus 24:16
       "labels_resolved_note": "C0709 counts as resolved: the revision re-pointed it from the one-off sentence (Leviticus 24:14) to the standing law (24:16)."}
json.dump(res, open(f"{A}/findings-638.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("count_change", "status_613_now", "labels_open_by_group", "steps_from_638", "edit_notes_now", "labels_resolved_by_revision")}, ensure_ascii=False, indent=1))
print("open duplicates:", len(dups_open)); [print("  ", d["records"], d["origin"]) for d in dups_open]
