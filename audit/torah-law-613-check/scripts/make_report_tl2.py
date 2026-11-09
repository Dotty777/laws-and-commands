"""Repository report: the 556 Torah Laws, the revision to 638, and Maimonides' 613 (current state first)."""
import json, sys, collections, os
W = "/home/claude/work"; A = f"{W}/audit/torah-laws"; REPO = "/home/claude/repos/laws-and-commands"
new = json.load(open(f"{REPO}/data/current/commands.json")); nby = {r["id"]: r for r in new}
F = json.load(open(f"{A}/findings.json")); N = json.load(open(f"{A}/findings-638.json")); M = json.load(open(f"{A}/maimonides-613.json"))
CHK = json.load(open(f"{A}/accuracy-check.json")) if os.path.exists(f"{A}/accuracy-check.json") else None
s0 = collections.Counter(r["status"] for r in M); s1 = N["status_613_now"]; ch = N["count_change"]
om0 = collections.Counter(r["type"] for r in M if r["status"] == "other_mosaic")
ns0 = s0["partial"] + s0["broad_only"]
ns1 = s1["not_stated:text"] + s1["not_stated:saints"] + s1["not_stated:reading"]
om1 = s1["other_mosaic:Instruction"] + s1["other_mosaic:Command"] + s1["other_mosaic:Commission"]
lg = N["labels_open_by_group"]; st = N["steps_from_638"]
fixed = [g for g in N["gaps_now"] if g["state"] == "fixed"]; openg = [g for g in N["gaps_now"] if g["state"].startswith("open")]
gstate = {g["m"]: g for g in N["gaps_now"]}
stmt = {r["m"]: r["statement"] for r in M}
KIND = {"613": "Commandment matches", "label": "Label findings", "duplicate": "Duplicate findings"}
if CHK:
    bk = CHK["by_kind"]
    chk = (f"A separate reviewer, who had not seen the work, re-checked {CHK['sample']} findings against the 556-record catalogue: "
           f"{CHK['drawn_from']}. **{CHK['verdicts'].get('correct', 0)} were correct, {CHK['verdicts'].get('partly', 0)} partly right and {CHK['verdicts'].get('wrong', 0)} wrong.**\n\n"
           "| Findings | Checked | Correct | Partly right | Wrong |\n| --- | ---: | ---: | ---: | ---: |\n"
           + "\n".join(f"| {KIND[k]} | {sum(v.values())} | {v.get('correct', 0)} | {v.get('partly', 0)} | {v.get('wrong', 0)} |" for k, v in bk.items())
           + "\n\nWhat changed as a result:\n" + "\n".join(f"- **{c['ref'].replace(',', ', ')}** ({c['verdict']}): {c['action']}" for c in CHK["cases"]))
else:
    chk = "(pending)"
L = []
L.append(f"""# Torah Laws: the 556, the revision to 638, and Maimonides' 613 — 8 November 2026

**The catalogue now counts {ch['after']} Torah Law records.** It counted {ch['before']} when this check began. The contextual Torah Law audit (commit `467e928`) made the change during the check:
- added {ch['added_new_records']} new records;
- relabelled {ch['relabelled_to_law']} records as Torah Law, among them all of the Ten Commandments;
- merged {ch['retired_law_records']} Torah Law records into others.

The record type audit that followed (commit `00f33d1`) changed no Torah Law record and no record in the open findings (it did fix one of the editing notes), so the figures below hold for the current catalogue. This report gives that current state first, then what the 556 counted.

**Against Maimonides' 613, in the current catalogue:**
- **{s1['torah_law']}** commandments are itemized by a Torah Law record (up from {s0['torah_law']}).
- **{om1}** sit only under another Mosaic label: {s1['other_mosaic:Instruction']} Instruction, {s1['other_mosaic:Command']} Command and {s1['other_mosaic:Commission']} Commission.
- **{s1['other_record']}** sit only in records with no Mosaic type.
- **{ns1}** are not stated as Maimonides counts them. In {s1['not_stated:reading']} of these his reading goes beyond the plain text, and in {s1['not_stated:saints']} the Saints (Greek) wording differs.

**Still to fix in the current catalogue:**
- {len(openg)} commandments to add;
- {len(N['duplicates_open'])} duplicate or overlap cases, {sum(1 for d in N['duplicates_open'] if d['origin'] == 'introduced by the revision')} of them introduced by the revision;
- {len(N['labels_open'])} records still labelled inconsistently;
- {N['edit_notes_now']} public notes that still read as editing instructions.

Nothing was changed in the catalogue by this check. The review workbook is [Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx](Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx).

## The 613 in the current catalogue

| Status | Now ({ch['after']}) | Before ({ch['before']}) |
| --- | ---: | ---: |
| Itemized by a Torah Law record | {s1['torah_law']} | {s0['torah_law']} |
| Only under Mosaic Instruction | {s1['other_mosaic:Instruction']} | {om0['Instruction']} |
| Only under Mosaic Command | {s1['other_mosaic:Command']} | {om0['Command']} |
| Only under Mosaic Commission | {s1['other_mosaic:Commission']} | {om0['Commission']} |
| Only in a record with no Mosaic type | {s1['other_record']} | {s0['other_record']} |
| Not stated: the text states it, but no record does | {s1['not_stated:text']} | 6 |
| Not stated: the Saints wording differs | {s1['not_stated:saints']} | 6 |
| Not stated: Maimonides' reading goes beyond the text | {s1['not_stated:reading']} | 58 |

The counts are not meant to match one to one. The catalogue often splits one commandment into several records. Many Torah Law records are penalties, sub-cases or details that Maimonides counts inside a broader commandment. The revision's own report says its total "is not a reconciliation to a traditional count of mitzvot".

### Commandments to add
""")
for g in openg:
    L.append(f"- **{g['m']}** {stmt[g['m']]}: {g['what']}")
L.append(f"""
The 556 check found {len(fixed) + len(openg) + 1} commandments in this position, after the accuracy check showed that two more (N171 and P53) were already itemized by C0655 and C0230. The revision has since fixed {len(fixed)} of them: """ + "; ".join(f"{g['m']} ({g['what'].rstrip('.')})" for g in fixed) + f""". It also linked Leviticus 12:3 to the Genesis circumcision record (P215) and keeps that record as the primary, by choice.

## Duplicates still open

| Records | Their labels | What to do | Origin |
| --- | --- | --- | --- |""")
for d in N["duplicates_open"]:
    L.append(f"| {', '.join(d['records'])} | {'; '.join(d['labels'])} | {d['action']} | {d['origin']} |")
L.append(f"""
""" + "\n".join(f"- **{d['status']}: {', '.join(d['records'])}.** {d['action']}" for d in N["duplicates_other"]) + f"""

Three Additional Scripture links now point at verses the revision gave their own records. The catalogue already does this in about 44 places, so they are not counted as duplicates:
""" + "\n".join(f"- {x['note']}" for x in N["cross_references_now"]) + f"""

## Labels still inconsistent

The revision resolved {N['labels_resolved_by_revision']} of the 70 label findings: the Ten Commandments, most positive duties beside their negative twins, and the regular offerings. It also re-pointed C0709 from the one-off sentence in Leviticus 24:14 to the standing law in 24:16. Still open:

| Group | Records |
| --- | --- |""")
byg = collections.defaultdict(list)
for x in N["labels_open"]: byg[x["group"]].append(x)
for g, xs in byg.items():
    L.append(f"| {g} ({len(xs)}) | " + "; ".join(f"{x['id']} '{x['title']}' ({x['current']})" for x in xs) + " |")
L.append(f"""
The revision deferred some items on purpose. It keeps love of God and cleaving to him as covenant commands rather than reclassifying them "solely to match Maimonides' count". It also keeps the Deuteronomy 26:14 abstentions inside the tithe declaration. This report does not count those as errors.

## What the count would be

| Step | Change | Torah Law count |
| --- | ---: | ---: |""")
for s in st:
    L.append(f"| {s['step']} | {'' if s['change'] is None else ('+' if s['change'] > 0 else '') + str(s['change'])} | {s['count']} |")
L.append(f"""
Each step adds to the one before. The last step is a choice about the convention, not an error.

## What the 556 counted

The 556 were the records whose study placement was **Torah Law** (Mosaic type Law): God-given rules for a General audience in Exodus–Deuteronomy.
- **By book:** 251 in Leviticus, 140 in Deuteronomy, 106 in Exodus and 59 in Numbers. None were in Genesis.
- **Origin of the records:** 512 were original Torah requirement records and 44 were completeness-review additions.

The 556 left out several groups:
- **The Ten Commandments:** all 14 records were Mosaic Command.
- **Other Mosaic types:** 417 Mosaic Instruction, 10 Wisdom and 9 Commission records, plus the 58 Command records outside Exodus 20.
- **The Genesis laws** on blood, homicide and circumcision.
- **Broad records:** 177 passage groups and 144 topical studies.

Against the 613, the 556 itemized {s0['torah_law']} commandments. {s0['other_mosaic']} sat under other Mosaic labels, {s0['other_record']} sat in records with no Mosaic type, and {ns0} were not stated.

The 556 check also found:
- 1 duplicate, 4 records overlapping others in the same passage, and 5 laws recorded twice (2 of the 5 are now left as choices, as explained above);
- 70 label inconsistencies.

The workbook keeps every original finding, with its status in the current catalogue.

## Accuracy check

{chk}

## Other findings

- **Editing notes in public text.** {N['edit_notes_now']} public notes on {N['edit_notes_records_now']} records still read as instructions to an editor, such as "extend to 22:9–10", "link as Additional Scripture" and "Rambam P103 is itemized…". Most come from audit notes copied into the catalogue. They are listed in the Edit notes sheet.
- **Errors in the source index.** For 12 commandments the index's source verse, or its mapping to the Saints text, was wrong: P43, P48, P58, P192, N45, N116, N119, N228, N266, N318, and N267 and N268, which are swapped. Each was matched by its number instead.

## How it was done

1. **The 613.** Six reviewers matched each of the 613 against the Saints text and every record on or near its source verse, starting from the 556-record catalogue (commit `3d53008`). The source verses come from the betemunah.org index of Sefer HaMitzvot, mapped to the Saints text.
2. **Duplicates and labels.**
   - All 214 same-passage pairs with a Torah Law record were reviewed, with the 78 closest cross-passage pairs.
   - 159 records picked by screens were reviewed for their labels.
3. **The revision.** Every finding was carried forward to the revised catalogue (commit `467e928`) using its merge index and change ledger, then checked again against the current catalogue (commit `00f33d1`). The revision's additions and new Torah Law records were screened again for duplicates.

## Files

| File | What it holds |
| --- | --- |
| [Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx](Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx) | The review workbook, with each finding's status in the current catalogue |
| [findings-638.json](findings-638.json) | Current-state findings: the 613 now, gaps, open duplicates, open labels, count steps |
| [reconcile-638.json](reconcile-638.json), [edit-notes-638.json](edit-notes-638.json) | How each 556 finding was carried forward, and the edit notes in the current catalogue |
| [accuracy-check.json](accuracy-check.json) | The independent check: verdicts by kind and what changed |
| [maimonides-613.json](maimonides-613.json), [findings.json](findings.json) | The 556-based matching and findings |
| [summary.json](summary.json) | The 556-based totals |
| [review-records/](review-records/), [method/](method/), [scripts/](scripts/) | Reviewer output, briefs and scripts |

## Limits

- Matching a commandment to a record is a judgment.
- The label conventions were inferred from the catalogue's own usage and from the revision's stated criteria.
- The current-state statuses were carried forward from the 556 review, not reviewed again from scratch. The revision's new records were matched to the 613 by hand.
- The accuracy check covered a sample. Most label findings and commandment matches were not re-checked one by one.
- The live website was not opened. The catalogue was read from the repository.
""")
open(f"{A}/README.md", "w").write("\n".join(L))
print(len(" ".join(L).split()), "words")
