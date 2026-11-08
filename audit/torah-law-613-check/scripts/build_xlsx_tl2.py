"""Review workbook for the Torah Law count check: the current 638 first, then the 556, both against Maimonides' 613."""
import sys, json, collections, os
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

W = "/home/claude/work"; A = f"{W}/audit/torah-laws"; OUTFILE = sys.argv[1]
REPO = "/home/claude/repos/laws-and-commands"
B = Bible()
new = json.load(open(f"{REPO}/data/current/commands.json")); nby = {r["id"]: r for r in new}
old = json.load(open(f"{W}/round3/commands-3d53008.json")); oby = {r["id"]: r for r in old}
DEC = json.load(open(f"{REPO}/audit/torah-law/decisions.json")); alias = DEC["aliases"]
F = json.load(open(f"{A}/findings.json")); M = json.load(open(f"{A}/maimonides-613.json"))
G = json.load(open(f"{A}/findings-638.json")); R = json.load(open(f"{A}/reconcile-638.json"))
CW = json.load(open(f"{A}/count-workings.json")); EN = json.load(open(f"{A}/edit-notes-638.json"))
ACC = json.load(open(f"{A}/accuracy-check.json")) if os.path.exists(f"{A}/accuracy-check.json") else None
TL_OLD = [r for r in old if r["mosaic_type"] == "Law"]; TL_NEW = [r for r in new if r["mosaic_type"] == "Law"]
assert len(TL_OLD) == 556 and len(TL_NEW) == 638, (len(TL_OLD), len(TL_NEW))

GREEN, IVORY, INK, MUTED, IDC = "FF243C32", "FFFFFAF1", "FF322E27", "FF61584D", "FF255B47"
TITLE = Font(name="Arial", size=16, bold=True, color=GREEN); SUB = Font(name="Arial", size=10, color=MUTED)
HEAD = Font(name="Arial", size=10, bold=True, color=IVORY); BODY = Font(name="Arial", size=10, color=INK)
BOLD = Font(name="Arial", size=10, bold=True, color=INK); IDF = Font(name="Arial", size=10, color=IDC)
IVFILL = PatternFill("solid", fgColor=IVORY); HDFILL = PatternFill("solid", fgColor=GREEN)
WRAP = Alignment(wrap_text=True, vertical="top")


def header(ws, title, sub_lines, cols, widths, start_row=7):
    ws.sheet_properties.tabColor = "243C32"
    for r in range(2, start_row - 1):
        for c in range(1, max(4, len(cols)) + 1): ws.cell(r, c).fill = IVFILL
    ws.cell(2, 1, title).font = TITLE
    for i, s in enumerate(sub_lines): ws.cell(3 + i, 1, s).font = SUB
    for i, (c, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(start_row, i, c); cell.font, cell.fill, cell.alignment = HEAD, HDFILL, WRAP
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(start_row + 1, 1)


def body(ws, rows, start_row=8, id_cols=(1,), bold_rows=()):
    for r_i, row in enumerate(rows, start_row):
        for c_i, val in enumerate(row, 1):
            cell = ws.cell(r_i, c_i, val)
            cell.font = BOLD if (r_i - start_row) in bold_rows else (IDF if c_i in id_cols else BODY)
            cell.alignment = WRAP


def table(ws, name, ncols, start_row, nrows):
    if nrows == 0: return
    t = Table(displayName=name, ref=f"A{start_row}:{get_column_letter(ncols)}{start_row + nrows}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True); ws.add_table(t)


def vkey(ref):
    try: return (B.expand(ref)[0] or [10 ** 7])[0]
    except Exception: return 10 ** 7


S556 = {"torah_law": "Itemized by a Torah Law record", "other_mosaic": "Only under another Mosaic type",
        "other_record": "Only in a record with no Mosaic type", "partial": "Not stated as Maimonides counts it (a record holds the verse)",
        "broad_only": "Not stated (only inside a passage group or broad study)"}
SNOW = {"torah_law": "Itemized by a Torah Law record", "other_mosaic:Instruction": "Only under Mosaic Instruction",
        "other_mosaic:Command": "Only under Mosaic Command", "other_mosaic:Commission": "Only under Mosaic Commission",
        "other_record": "Only in a record with no Mosaic type", "not_stated:text": "Not stated: the text states it, but no record does",
        "not_stated:saints": "Not stated: the Saints wording differs", "not_stated:reading": "Not stated: Maimonides' reading goes beyond the text"}
GROUP = {"1": "Clear correction", "2": "Positive duty under Instruction, negative twin under Torah Law",
         "3": "Standing observance under Instruction, comparable ones under Torah Law", "4": "Conquest-era bans split between Torah Law and historical directions",
         "5": "Ten Commandments filed as Mosaic Command", "6": "Other standing duties filed as Mosaic Command"}
now613 = {r["m"]: r for r in G["rows613_now"]}
c556 = collections.Counter((r["status"] + ":" + r["type"]) if r["status"] == "other_mosaic" else r["status"] for r in M)
gapcat = {g["m"]: g["category"] for g in F["gaps"]}
ns556 = collections.Counter()
for r in M:
    if r["status"] in ("partial", "broad_only"):
        ns556[{"Text states it, no record does": "text", "Saints wording differs": "saints"}.get(gapcat.get(r["m"]), "reading")] += 1
cnow = collections.Counter(r["status_now"] for r in G["rows613_now"])
tl_now_matched = collections.defaultdict(list)
for r in G["rows613_now"]:
    if r["status_now"] == "torah_law":
        for i in r["records_now"]:
            if i in nby and nby[i]["mosaic_type"] == "Law": tl_now_matched[i].append(r["m"])
gaps_now = {g["m"]: g for g in G["gaps_now"]}
dups = G["duplicates_open"]
labs_open = {x["id"]: x for x in G["labels_open"]}
absorbed = collections.defaultdict(list)
for o, s in alias.items():
    if o in oby: absorbed[s].append(f"{o} ({oby[o]['study_placement']})")
rel_from = collections.Counter(oby[r["id"]]["study_placement"] for r in TL_NEW if r["id"] in oby and oby[r["id"]]["mosaic_type"] != "Law")
added = [r for r in TL_NEW if r["id"] not in oby]
retired = [r["id"] for r in TL_OLD if r["id"] not in nby or nby[r["id"]]["mosaic_type"] != "Law"]
assert 556 + len(added) + sum(rel_from.values()) - len(retired) == 638
open_labels_n = len(G["labels_open"])

# ------------------------------------------------------------------ Read me
wb = Workbook(); ws = wb.active; ws.title = "Read me"
header(ws, "Torah Law count check · the 556, the revision to 638, and Maimonides' 613",
       [f"Saints.Bible Laws, Commands, and Instructions catalogue. Checked 8 November 2026 on the 556 Torah Law records (commit 3d53008) and carried forward to the current catalogue (commit 00f33d1: {len(new):,} records in all; its 638 Torah Law records are as revised in commit 467e928).",
        f"Still to fix now: {sum(1 for g in G['gaps_now'] if g['state'].startswith('open'))} commandments to add · {len(dups)} duplicate or overlap cases · {open_labels_n} records labelled inconsistently · {G['edit_notes_now']} public notes that read as editing instructions.",
        "Findings are for review: nothing has been changed in the catalogue or on the website."],
       ["Sheet", "What it holds", "Rows"], [24, 112, 10])
readme = [
    ["Count", "The current count (638) beside the 556: how one became the other, the 613 now and then, and what the count would be after each kind of fix.", None],
    ["Torah Law now (638)", "Every current Torah Law record: where it came from, what was merged into it, the commandments it itemizes and any open finding.", len(TL_NEW)],
    ["The 556", "Every record in the original 556, with what became of it.", len(TL_OLD)],
    ["Maimonides 613", "Each commandment: its status now and at the 556, the records that itemize it and their labels.", len(M)],
    ["Not stated", f"The {len(F['gaps'])} commandments that no Mosaic record stated as Maimonides counts them at the 556, sorted by why, with their state now.", len(F["gaps"])],
    ["Duplicates", f"{len(dups)} open duplicate or overlap cases ({sum(1 for d in dups if d['origin'].startswith('introduced'))} introduced by the revision), with the cases the revision resolved, those left as choices and three cross-references not counted.", len(dups) + len(G["duplicates_other"]) + len(G["cross_references_now"])],
    ["Labels", f"The 70 label findings from the 556 check and 1 new one: {open_labels_n} still open, {G['labels_resolved_by_revision']} resolved by the revision.", len(R["labels_now"]) + 1],
    ["Missing links", "Verses that restated a recorded law but were attached to no record at the 556, with their state now.", len(R["links_now"])],
    ["Edit notes", "Public notes that still read as editing instructions or audit references (all books, not only the Torah).", len(EN)],
    ["Method", "Each of the 613 was matched by a reviewer against the Saints text and the 556-record catalogue; duplicates and labels were screened by text and reviewed pair by pair. Every finding was then carried forward to the 638-record catalogue using the revision's merge index and change ledger, and the revision's new and relabelled records were screened again. Maimonides' source verses follow the betemunah.org index (Hebrew numbering, mapped to the Saints text); where the index was wrong, the commandment was matched by its number.", None],
]
if ACC:
    readme.append(["Accuracy check", ACC["summary"], ACC["sample"]])
body(ws, readme)

# ------------------------------------------------------------------ Count
ws = wb.create_sheet("Count")
header(ws, "The Torah Law count, now and at the 556",
       ["Torah Law = records whose study placement is Torah Law (Mosaic type Law). The revision defines it as 'distinct standing provisions within their stated covenant setting', not a reconciliation to a traditional count."],
       ["Item", "Now (638)", "At the 556", "Note"], [62, 13, 13, 90])
rows, bold = [], set()


def add(item, now=None, then=None, note="", is_bold=False):
    if is_bold: bold.add(len(rows))
    rows.append([item, now, then, note]); return 8 + len(rows) - 1


add("Torah Law records", len(TL_NEW), len(TL_OLD), "Study placement Torah Law", True)
for bk in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]:
    add(f"   in {bk}", sum(1 for r in TL_NEW if r["book"] == bk), sum(1 for r in TL_OLD if r["book"] == bk),
        "The Genesis laws on blood, homicide and circumcision have no Mosaic type" if bk == "Genesis" else "")
dec_ids = [r["id"] for r in new if r["book"] == "Exodus" and r["reference"].startswith("Exodus 20:") and r["id"] in {x["id"] for x in old if x["study_placement"] == "Mosaic Command" and x["reference"].startswith("Exodus 20:")}]
dec_old = [r["id"] for r in old if r["study_placement"] == "Mosaic Command" and r["reference"].startswith("Exodus 20:")]
add("   Ten Commandments records (Exodus 20)", sum(1 for i in dec_ids if nby[i]["mosaic_type"] == "Law"), 0,
    f"All {len(dec_old)} were Mosaic Command at the 556; the revision merged " + ", ".join(f"{i} into {alias[i]}" for i in dec_old if i in alias) + f", leaving {len(dec_ids)}, all Torah Law")
add("Other Mosaic types", None, None, "", True)
for k in ["Instruction", "Command", "Wisdom", "Commission"]:
    add(f"   Mosaic {k}", sum(1 for r in new if r["mosaic_type"] == k), sum(1 for r in old if r["mosaic_type"] == k))
add("All records in the catalogue", len(new), len(old))
add("How the 556 became 638", None, None, "Commit 467e928, the contextual Torah Law audit", True)
r0 = add("   Torah Law records at the 556", 556)
r1 = add("   + new records added by the revision (TL ids)", len(added))
r2 = add("   + records relabelled as Torah Law", sum(rel_from.values()), None, "; ".join(f"{v} from {k}" for k, v in rel_from.most_common()))
r3 = add("   − Torah Law records merged into others", len(retired), None, ", ".join(retired))
r4 = add("   − Torah Law records relabelled out", 0)
add("   = Torah Law records now", f"=B{r0}+B{r1}+B{r2}-B{r3}-B{r4}", None, "Should equal 638", True)
add("Maimonides' 613", None, None, "Which record, if any, itemizes each commandment", True)
first = len(rows) + 8
for k in ["torah_law", "other_mosaic:Instruction", "other_mosaic:Command", "other_mosaic:Commission", "other_record"]:
    add(f"   {SNOW[k]}", cnow[k], c556[k])
for k in ["text", "saints", "reading"]:
    add(f"   {SNOW['not_stated:' + k]}", cnow["not_stated:" + k], ns556[k])
last = len(rows) + 7
add("   Total", f"=SUM(B{first}:B{last})", f"=SUM(C{first}:C{last})", "Should equal 613", True)
add("Torah Law records that itemize at least one of the 613", len(tl_now_matched), len(CW["tl_matched"]),
    "Now includes 4 of the revision's 21 new records: " + ", ".join(sorted(i for i in tl_now_matched if i not in oby)))
add("Torah Law records that itemize none of the 613", len(TL_NEW) - len(tl_now_matched), len(TL_OLD) - len(CW["tl_matched"]),
    "Mostly penalties, sub-cases and details Maimonides counts within a broader commandment")
add("What the count would be after each fix, from 638", None, None, "Each step adds to the one before", True)
for s in G["steps_from_638"][1:]:
    add(f"   {s['step']}", s["count"], None, f"{s['change']:+d}" if s["change"] else "net 0")
add("What it would have been, from the 556", None, None, "Kept for reference; the revision has made many of these changes", True)
for s in F["scenarios"][1:]:
    add(f"   {s['step']}", None, s["count"] if s["count"] is not None else "", (f"{s['change']:+d}" if isinstance(s["change"], int) and s["change"] else "stands on its own: +5 or −1"))
body(ws, rows, id_cols=(), bold_rows=bold)

# ------------------------------------------------------------------ Torah Law now (638)
ws = wb.create_sheet("Torah Law now (638)")
dup_note = collections.defaultdict(list)
for d in dups:
    for x in d["records"]:
        dup_note[x].append("with " + ", ".join(y for y in d["records"] if y != x) + (" (introduced by the revision)" if d["origin"].startswith("introduced") else ""))
cols = ["Record ID", "Scripture", "Study record", "Classification", "Topic", "Bible book", "Since the 556", "Merged into it", "Maimonides commandments itemized", "Open duplicate", "Open label finding"]
header(ws, "The 638 Torah Law records in the current catalogue",
       ["One row per record in the current catalogue (commit 00f33d1). 'Maimonides commandments itemized' comes from the 613 matching, carried forward; a blank means the record itemizes none of them."],
       cols, [23.8, 24, 50, 16, 28, 13, 30, 30, 22, 30, 40])
rows = []
for r in sorted(TL_NEW, key=lambda r: vkey(r["reference"])):
    i = r["id"]
    since = "In the 556" if i in oby and oby[i]["mosaic_type"] == "Law" else ("Added by the revision" if i not in oby else f"Relabelled from {oby[i]['study_placement']}")
    lo = labs_open.get(i)
    rows.append([i, r["reference"], r["title"], r["classification"], r["topic"], r["book"], since, ", ".join(absorbed.get(i, [])),
                 ", ".join(tl_now_matched.get(i, [])), "; ".join(dup_note.get(i, [])), f"{lo['group']} → {lo['suggest']}" if lo else ""])
body(ws, rows); table(ws, "TorahLawNow", len(cols), 7, len(rows))

# ------------------------------------------------------------------ The 556
ws = wb.create_sheet("The 556")
dup_of = collections.defaultdict(list)
for d in F["duplicates"]:
    for x in d["records"]: dup_of[x].append(d["kind"])
labf = {x["id"]: x for x in F["labels"]}
cols = ["Record ID", "Scripture", "Study record", "Classification", "Topic", "Bible book", "Added", "Now (638)", "Maimonides commandments itemized", "Duplicate finding", "Label finding"]
header(ws, "The 556 Torah Law records, and what became of them",
       ["One row per record as it stood at commit 3d53008. 'Now' gives its state in the current catalogue; the findings are those of the 556 check."],
       cols, [23.8, 22, 50, 16, 28, 13, 18, 30, 22, 30, 40])
rows = []
for r in sorted(TL_OLD, key=lambda r: vkey(r["reference"])):
    i = r["id"]; lf = labf.get(i)
    if i in nby and nby[i]["mosaic_type"] == "Law": now_s = "Still Torah Law"
    elif i in alias: now_s = f"Merged into {alias[i]} ({nby[alias[i]]['study_placement']})"
    else: now_s = "Not in the current catalogue"
    rows.append([i, r["reference"], r["title"], r["classification"], r["topic"], r["book"],
                 "completeness review" if i.startswith("AUD") else "original", now_s, ", ".join(CW["tl_matched"].get(i, [])),
                 "; ".join(sorted(set(dup_of.get(i, [])))), (f"{lf['category'][4:]} → {lf['suggest']}" if lf else "")])
body(ws, rows); table(ws, "TorahLaw556", len(cols), 7, len(rows))

# ------------------------------------------------------------------ Maimonides 613
ws = wb.create_sheet("Maimonides 613")
cols = ["Commandment", "As Maimonides counts it", "Status now (638)", "Record(s) now", "Their label(s) now", "Status at the 556", "Record(s) at the 556",
        "Their label(s) at the 556", "Label flagged at the 556", "Source (index)", "Saints verse", "Confidence", "Reviewer note"]
header(ws, "Maimonides' 613 commandments against the catalogue, now and at the 556",
       ["P = positive (1–248), N = negative (1–365), Sefer HaMitzvot numbering. Source verses follow the betemunah.org index; the Saints verse is where it falls in the Saints text."],
       cols, [12, 40, 30, 24, 30, 30, 24, 30, 12, 18, 20, 11, 70])
rows = []
for r in M:
    n_ = now613[r["m"]]
    rows.append([r["m"], r["statement"], SNOW[n_["status_now"]], ", ".join(n_["records_now"]), "; ".join(dict.fromkeys(n_["labels_now"])),
                 S556[r["status"]], ", ".join(r["records"]), "; ".join(dict.fromkeys(r["labels"])), "yes" if r["mislabel"] else "",
                 r["source"], r["saints"], r["confidence"], r["note"]])
body(ws, rows); table(ws, "Maimonides613", len(cols), 7, len(rows))

# ------------------------------------------------------------------ Not stated
def order_first2(g): return g["category"] in ("Text states it, no record does", "No itemized Mosaic record (only a Genesis record or a topical study)")
ws = wb.create_sheet("Not stated")
cols = ["Commandment", "As Maimonides counts it", "Saints verse", "Why (at the 556)", "Detail", "Record holding the verse (556)", "Now (638)"]
gc = collections.Counter(g["category"] for g in F["gaps"])
header(ws, "Commandments no record stated as Maimonides counts them",
       ["At the 556: " + " · ".join(f"{k} ({v})" for k, v in gc.most_common()) + ".",
        f"Now: {cnow['not_stated:text'] + cnow['not_stated:saints'] + cnow['not_stated:reading']} are still not stated; the revision fixed {sum(1 for g in G['gaps_now'] if g['state'] == 'fixed')} of the {sum(1 for g in F['gaps'] if order_first2(g))} in the first two groups."],
       cols, [12, 40, 20, 34, 80, 26, 70])
order = {"Text states it, no record does": 0, "No itemized Mosaic record (only a Genesis record or a topical study)": 1, "Saints wording differs": 2, "Maimonides' reading goes beyond the plain text": 3}
rows = []
for g in sorted(F["gaps"], key=lambda g: (order[g["category"]], g["m"][0], int(g["m"][1:]))):
    gn = gaps_now.get(g["m"])
    now_s = f"{gn['state'][0].upper() + gn['state'][1:]}: {gn['what']}" if gn else ("Still not stated" if now613[g["m"]]["status_now"].startswith("not_stated") else SNOW[now613[g["m"]]["status_now"]])
    rows.append([g["m"], g["statement"], g["saints"], g["category"], g["why"], ", ".join(g["records"]), now_s])
body(ws, rows); table(ws, "NotStated", len(cols), 7, len(rows))

# ------------------------------------------------------------------ Duplicates
ws = wb.create_sheet("Duplicates")
cols = ["Status now", "Kind", "Records", "Their Scripture", "Their labels now", "What to do", "Origin"]
header(ws, "Records that repeat another record",
       [f"{len(dups)} open now: {sum(1 for d in dups if not d['origin'].startswith('introduced'))} found in the 556 check and {sum(1 for d in dups if d['origin'].startswith('introduced'))} introduced by the revision.",
        "Also listed: cases the revision resolved, cases left as choices, and Additional Scripture links to verses that now have their own records (common in the catalogue, so not counted)."],
       cols, [14, 30, 30, 34, 34, 90, 24])


def ref_of(i): return nby[i]["reference"] if i in nby else (oby[i]["reference"] if i in oby else "")


rows = [["Open", d["kind"], ", ".join(d["records"]), "; ".join(ref_of(x) for x in d["records"]), "; ".join(d["labels"]), d["action"], d["origin"]] for d in dups]
for d in G["duplicates_other"]:
    rows.append([d["status"], d["kind"], ", ".join(d["records"]), "; ".join(ref_of(x) for x in d["records"]),
                 "; ".join(nby[x]["study_placement"] for x in d["records"] if x in nby), d["action"], d["origin"]])
for x in G["cross_references_now"]:
    rows.append(["Not counted", "Additional Scripture points at a verse that now has its own record", ", ".join(x["records"]), "; ".join(ref_of(i) for i in x["records"]),
                 "; ".join(nby[i]["study_placement"] for i in x["records"]), x["note"], "introduced by the revision"])
body(ws, rows, id_cols=(3,)); table(ws, "Duplicates", len(cols), 7, len(rows))

# ------------------------------------------------------------------ Labels
ws = wb.create_sheet("Labels")
cols = ["Status now", "Group", "Record ID", "Scripture", "Study record", "Label at the 556", "Label now", "Suggested", "Evidence", "Found by", "Confidence"]
header(ws, "Records whose label looks inconsistent",
       [f"70 findings from the 556 check and 1 new one. Now: {open_labels_n} open, {G['labels_resolved_by_revision']} resolved by the revision (the Ten Commandments, most positive duties beside their negative twins, the regular offerings)."],
       cols, [30, 40, 23.8, 22, 46, 26, 26, 34, 80, 16, 11])
rows = []
for x in sorted(R["labels_now"], key=lambda x: (x["now"] != "unchanged", x["category"][0])):
    g = x["category"][0]; i = x["id"]
    if x["now"] == "unchanged":
        grp, ev = GROUP[g], x["evidence"]
        if i == "C0995": st, sug = "Label now consistent; still a duplicate", "Link Deuteronomy 6:14 to C0146 (see Duplicates)"
        elif i == "C0709": st, sug = "Resolved: re-pointed to Leviticus 24:16, the standing law (24:14 kept as Additional Scripture)", x["suggest"]
        else: st, sug, grp, ev = "Open", labs_open[i]["suggest"], labs_open[i]["group"], labs_open[i]["evidence"]
        lab_now = nby[i]["study_placement"]
    else:
        surv = x.get("survivor", i)
        lab_now = nby[surv]["study_placement"] if surv in nby else ""
        st = "Resolved: " + x["now"]; sug = x["suggest"]
        grp, ev = GROUP[g], x["evidence"]
        if g == "4": st = "Moved: now Torah Law; group still split until C0997 and C1197 match"
    rows.append([st, grp, i, nby[i]["reference"] if i in nby else x["reference"], x["title"], oby[i]["study_placement"] if i in oby else x["current"], lab_now, sug, ev,
                 ", ".join(x.get("checks", [])), x.get("confidence", "")])
c573 = labs_open["C0573"]
rows.sort(key=lambda r: (not r[0].startswith("Open"), not r[0].startswith("Label now")))
rows.insert(sum(1 for r in rows if r[0].startswith("Open")),
            ["Open (new)", c573["group"], "C0573", c573["reference"], c573["title"], oby["C0573"]["study_placement"], nby["C0573"]["study_placement"], c573["suggest"], c573["evidence"], "revision rescreen", "high"])
body(ws, rows, id_cols=(3,)); table(ws, "Labels", len(cols), 7, len(rows))

# ------------------------------------------------------------------ Missing links
ws = wb.create_sheet("Missing links")
cols = ["Verse", "Restates the law of", "That record's Scripture", "That record's label now", "Now (638)"]
header(ws, "Verses that restated a recorded law but were attached to no record", ["Found in the 556 check. The revision has dealt with all four."], cols, [52, 20, 24, 24, 70])
LN = {"linked": "Linked as Additional Scripture on that record"}
rows = []
for u in R["links_now"]:
    now_s = LN.get(u["now"], u["now"])
    if u["record"] == "C0201": now_s = "Now its own record, TL-03-20-15, which states the same penalty as C0201 (see Duplicates)"
    rows.append([u["verse"], u["record"], ref_of(u["record"]), nby[u["record"]]["study_placement"], now_s])
body(ws, rows, id_cols=(2,)); table(ws, "MissingLinks", len(cols), 7, len(rows))

# ------------------------------------------------------------------ Edit notes
ws = wb.create_sheet("Edit notes")
cols = ["Record ID", "Field", "Public text"]
header(ws, "Public notes that still read as editing instructions",
       [f"{len(EN)} notes on {len({h['id'] for h in EN})} records in the current catalogue (134 at the 556). Phrases such as 'extend to …', 'link as Additional Scripture' and 'Rambam P103 is itemized…' read as instructions to an editor, not notes for readers."],
       cols, [23.8, 36, 120])
rows = [[h["id"], h["field"], h["text"]] for h in EN]
body(ws, rows); table(ws, "EditNotes", len(cols), 7, len(rows))
wb.save(OUTFILE); print("saved", OUTFILE)
