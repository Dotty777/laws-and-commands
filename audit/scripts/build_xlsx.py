"""Build the import-ready audit workbook from audit/findings_final.json, styled like the catalogue workbook."""
import sys, json, collections, os
sys.path.insert(0, "/home/claude/work")
from audit_lib import *
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

B = Bible(); recs = load_catalogue(); byid = {r["id"]: r for r in recs}
F = json.load(open("/home/claude/work/audit/findings_final.json"))
STATS = json.load(open("/home/claude/work/audit/verification_stats.json"))
OUTFILE = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/work/audit/Saints-Bible-Instructions-Completeness-Audit-2026-11-08.xlsx"

GREEN, IVORY, INK, MUTED, IDC = "FF243C32", "FFFFFAF1", "FF322E27", "FF61584D", "FF255B47"
TITLE = Font(name="Arial", size=16, bold=True, color=GREEN)
SUB = Font(name="Arial", size=10, color=MUTED)
HEAD = Font(name="Arial", size=10, bold=True, color=IVORY)
BODY = Font(name="Arial", size=10, color=INK)
BOLD = Font(name="Arial", size=10, bold=True, color=INK)
IDF = Font(name="Arial", size=10, color=IDC)
IVFILL = PatternFill("solid", fgColor=IVORY); HDFILL = PatternFill("solid", fgColor=GREEN)
WRAP = Alignment(wrap_text=True, vertical="top")

NT = set(B.order[B.order.index("Matthew"):]); GOSPELS = {"Matthew", "Mark", "Luke", "John"}
NARR = set(B.order[:B.order.index("Job")]); LAWBOOKS = {"Exodus", "Leviticus", "Numbers", "Deuteronomy"}
DIV = {}
for v in B.verses:
    DIV.setdefault(v["book"], v["div"].capitalize())


def placement(book, t):
    if book in GOSPELS: return f"Gospel {t.lower()}"
    if book == "Revelation": return f"Vision {t.lower()}"
    if book in NT: return f"Apostolic {t.lower()}"
    if t == "Wisdom": return "Wisdom teaching"
    if book in LAWBOOKS: return f"Mosaic {t}"
    return f"Historical {t.lower()}"


def classification(book, t):
    if t == "Commission": return "Historical commissions"
    if book in NT: return "Application under review"
    if book in NARR and t != "Wisdom": return "Historical"
    return "Uncertain"


def header(ws, title, sub_lines, cols, widths, start_row=7):
    ws.sheet_properties.tabColor = "243C32"
    for r in range(2, start_row - 1):
        for c in range(1, max(4, len(cols)) + 1):
            ws.cell(r, c).fill = IVFILL
    ws.cell(2, 1, title).font = TITLE
    for i, s in enumerate(sub_lines):
        ws.cell(3 + i, 1, s).font = SUB
    for i, (c, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(start_row, i, c)
        cell.font, cell.fill, cell.alignment = HEAD, HDFILL, WRAP
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(start_row + 1, 1)


def body_rows(ws, rows, start_row=8, id_cols=(1,)):
    for r_i, row in enumerate(rows, start_row):
        for c_i, val in enumerate(row, 1):
            cell = ws.cell(r_i, c_i, val)
            cell.font = IDF if c_i in id_cols else BODY
            cell.alignment = WRAP


def add_table(ws, name, ncols, start_row, nrows):
    if nrows == 0: return
    t = Table(displayName=name, ref=f"A{start_row}:{get_column_letter(ncols)}{start_row + nrows}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(t)


new, ext, par = F["new"], F["extend"], F["parallel"]
wb = Workbook()
# ---------------- Read me
ws = wb.active; ws.title = "Read me"
hm = sum(1 for o in new if o["confidence"] != "low")
header(ws, "Completeness audit · Laws, Commands, and Instructions",
       ["The Saints.Bible catalogue (4,999 records, workbook SHA-256 801c9394…b098) checked verse by verse across all 70 books, 8 November 2026.",
        "Everything here is a draft for review: nothing has been added to the website or the repository."],
       ["Sheet", "What it holds", "Rows"], [24, 112, 10])
body_rows(ws, [
    ["New records", f"Missing laws, commands, commissions, instructions and wisdom, in the Catalogue sheet's 24 columns plus two audit columns (confidence, note). {hm} are high or medium confidence. Record IDs use a GAP- prefix so they cannot collide with existing IDs.", len(new)],
    ["Extend Scripture", "Existing records whose Scripture stops short of verses stating the same direction, one row per record (several findings for one record are combined).", len(ext)],
    ["Link as parallel", "Directions already itemized from another passage (repeated laws, parallel accounts, quotations): add the verse as Additional Scripture. First four columns match the Scripture Sources sheet.", len(par)],
    ["Coverage by book", "Per-book verses, records, verses screened and reviewed, and the audit's findings (live formulas over the three findings sheets).", len(B.order)],
    ["Maimonides 613", "Each of Maimonides' 613 commandments, its traditional source verse, the records that itemize it, and its status after the audit.", 613],
    ["Housekeeping", "Records whose Topic is not one of the 50 topics, links that point past the first verse, and placeholder verse rows in the Genesis export.", None],
    ["Confidence", f"Independent check of a random sample of 110 findings: high {STATS['by_conf']['high']}, medium {STATS['by_conf']['medium']}, low {STATS['by_conf']['low']}. Treat high and medium as recommended additions and low as items to consider.", None],
    ["Coverage check", STATS["recall_text"], None],
    ["Drafted fields", "Topic, Study placement and Classification follow the catalogue's own conventions as drafts; every new record is marked 'Audience review pending'.", None],
])
# ---------------- New records
ws = wb.create_sheet("New records")
CAT_COLS = ["Record ID", "Scripture", "Study record", "Study placement", "Mosaic type", "Original audience or recipient",
            "Audience", "Origin", "Collection", "Topic", "Classification", "Bible book", "Testament", "Audience review",
            "Catalogue audience", "Context note", "Citation basis", "Origin basis", "Mosaic context", "Mosaic review note",
            "Record type", "Speaker or source", "Original audience (audit)", "Additional Scripture", "Audit confidence", "Audit note"]
widths = [23.8, 23, 50.2, 24, 12, 30, 12.8, 23.1, 25.2, 30, 24.8, 19.5, 12.5, 21.2, 30, 56, 14, 40, 14, 14, 16.2, 27.8, 33.8, 28, 14, 60]
header(ws, "New records proposed by the completeness audit",
       [f"{len(new)} records ({hm} high or medium confidence) · same columns as the Catalogue sheet · drafts for review",
        "Collection is 'Completeness audit 2026-11-08' so additions stay identifiable after import.",
        "Audit confidence and Audit note (last two columns) are for review only; drop them before merging."], CAT_COLS, widths)
rows = []
for o in new:
    book, t = o["book"], o["record_type"]
    rows.append([o["proposed_id"], o["reference"], o["title"], placement(book, t),
                 "Commission" if (t == "Commission" and book in LAWBOOKS) else "",
                 o.get("recipient", "") if book in LAWBOOKS else "", o["audience"], o["origin"],
                 "Completeness audit 2026-11-08", o["topic"], classification(book, t), book,
                 "New" if book in NT else "Old", "Audience review pending", o.get("recipient", ""), o.get("note", ""), "Source",
                 f'Speaker or source in this passage: {(o.get("speaker") or "").strip() or "unstated"}.', "", "", t,
                 o.get("speaker", ""), o.get("recipient", ""), o.get("additional", ""), o["confidence"], o.get("note", "")])
body_rows(ws, rows); add_table(ws, "NewRecords", len(CAT_COLS), 7, len(rows))
# ---------------- Extend
ws = wb.create_sheet("Extend Scripture")
cols = ["Record ID", "Current Scripture", "Study record", "Record type", "Verses to add", "Proposed Scripture", "Or add as Additional Scripture", "Why", "Bible book", "Audit confidence"]
header(ws, "Existing records whose Scripture stops short",
       [f"{len(ext)} records · each already states this direction, but its reference misses these verses",
        "Proposed Scripture is given when the added verses join the current reference; otherwise add them as Additional Scripture."],
       cols, [23.8, 22, 46, 13, 22, 24, 24, 64, 16, 13])
rows = [[e["existing_id"], e["current"], e["title"], e["record_type"], e["add"], e["new_primary"], e["as_additional"], e["note"], e["book"], e["confidence"]] for e in ext]
body_rows(ws, rows); add_table(ws, "ExtendScripture", len(cols), 7, len(rows))
# ---------------- Parallel
ws = wb.create_sheet("Link as parallel")
cols = ["Record ID", "Scripture", "Study record", "Context for this source", "Existing primary Scripture", "Bible book", "Audit confidence"]
header(ws, "Parallels to link as Additional Scripture",
       [f"{len(par)} links · first four columns match the Scripture Sources sheet (Record ID, Scripture, Study record, Context for this source)"],
       cols, [23.8, 24, 46, 70, 22, 16, 13])
rows = [[p["existing_id"], p["add"], p["title"], p["note"], p["existing_ref"], p["book"], p["confidence"]] for p in par]
body_rows(ws, rows); add_table(ws, "LinkParallel", len(cols), 7, len(rows))
# ---------------- Coverage by book
ws = wb.create_sheet("Coverage by book")
cs = json.load(open("/home/claude/work/audit/coverage_stats.json"))
cols = ["Bible book", "Division", "Verses", "Catalogue records", "Verses with a record", "Directive verses screened",
        "Verses reviewed", "New records proposed", "of which high or medium", "Extend Scripture", "Link as parallel", "New records per 100 verses"]
header(ws, "Coverage by book",
       ["Verses include Susanna, Bel and the Dragon, and the Proverbs continuation blocks. Columns H–K count the findings sheets live; L is computed."],
       cols, [20, 13, 9, 11, 11, 12, 11, 12, 12, 11, 11, 12])
r0 = 8
for i, b in enumerate(B.order):
    s = cs[b]; row = r0 + i
    for c, v in enumerate([b, DIV[b], s["verses"], s["records"], s["covered"], s["directive"], s["reviewed"]], 1):
        ws.cell(row, c, v).font = BODY
    ws.cell(row, 8, f"=COUNTIFS('New records'!$L$8:$L$5000,$A{row})").font = BODY
    ws.cell(row, 9, f"=COUNTIFS('New records'!$L$8:$L$5000,$A{row},'New records'!$Y$8:$Y$5000,\"<>low\")").font = BODY
    ws.cell(row, 10, f"=COUNTIFS('Extend Scripture'!$I$8:$I$5000,$A{row})").font = BODY
    ws.cell(row, 11, f"=COUNTIFS('Link as parallel'!$F$8:$F$5000,$A{row})").font = BODY
    ws.cell(row, 12, f"=IFERROR(ROUND(H{row}/C{row}*100,1),0)").font = BODY
last = r0 + len(B.order) - 1; tot = last + 1
ws.cell(tot, 1, "All 70 books").font = BOLD
for c in range(3, 12):
    L = get_column_letter(c); ws.cell(tot, c, f"=SUM({L}{r0}:{L}{last})").font = BOLD
ws.cell(tot, 12, f"=IFERROR(ROUND(H{tot}/C{tot}*100,1),0)").font = BOLD
ws.cell(tot + 2, 1, "Verses reviewed = candidate verses in the first pass plus second-sweep verses. Susanna and Bel count under Daniel.").font = SUB
# ---------------- Maimonides
ws = wb.create_sheet("Maimonides 613")
m = json.load(open("/home/claude/work/check613.json"))
mstat = json.load(open("/home/claude/work/audit/rambam_status.json"))
cols = ["Mitzva", "Source verse (Sefer HaMitzvot)", "Itemized records at that verse", "Broad passage records only", "Status", "Audit finding"]
header(ws, "Maimonides' 613 commandments against the catalogue",
       ["Source verses as indexed at betemunah.org/sederim/cmds613.html (Hebrew numbering, which the Saints Torah follows; Exodus 20 mapped to the Saints order).",
        "Status: itemized = a record of 8 verses or fewer covers it · parallel link = itemized from another verse, link this one · extend / new record proposed = see the findings sheets."],
       cols, [9, 26, 40, 30, 18, 72])
rows = []
for x in m:
    fine = ", ".join(x["fine"][:6]) + (" …" if len(x["fine"]) > 6 else "")
    broad = ", ".join([i for i in x["any"] if i not in x["fine"]][:4])
    s = mstat.get(x["mitzva"], {})
    rows.append([x["mitzva"], x["ref"], fine, broad, s.get("status", ""), s.get("finding", "")])
body_rows(ws, rows); add_table(ws, "Maimonides613", len(cols), 7, len(rows))
# ---------------- Housekeeping
ws = wb.create_sheet("Housekeeping")
cols = ["Record ID", "Scripture", "Study record", "Record type", "Collection", "Current topic", "Fix"]
TOP50 = set(json.load(open("/home/claude/work/audit/topics50.json")))
hk = [r for r in recs if r["topic"] not in TOP50]
header(ws, "Housekeeping",
       [f"{len(hk)} records whose Topic is not one of the 50 topics · 2 links that point past the first verse · 4 placeholder verse rows in the Genesis export"],
       cols, [23.8, 24, 50, 14, 22, 18, 62])
rows = [[r["id"], r["reference"], r["title"], r["record_type"], r["collection"], r["topic"] or "(empty)",
         "Choose one of the 50 topics (Topic holds the record type)" if r["topic"] else "Write 'Cross-Scripture studies' (assigned in the import notes)"] for r in hk]
rows += [["X009", "Revelation 2:4–7", byid["X009"]["title"], byid["X009"]["record_type"], byid["X009"]["collection"], byid["X009"]["topic"], "Scripture link points to 2:5; point it at 2:4"],
         ["X012", "Revelation 22:8–9", byid["X012"]["title"], byid["X012"]["record_type"], byid["X012"]["collection"], byid["X012"]["topic"], "Scripture link points to 22:9; point it at 22:8"]]
for lab in ["35:16a", "35:16b", "35:22a", "35:22b"]:
    rows.append(["(Bible text)", f"Genesis {lab}", "Placeholder row: 'Earlier label … see this chapter's reading text and numbering notes'", "", "Genesis export", "", "Remove the placeholder row from the Genesis export, or replace it with the verse text"])
body_rows(ws, rows); add_table(ws, "Housekeeping", len(cols), 7, len(rows))
wb.save(OUTFILE)
print("saved", OUTFILE, len(new), len(ext), len(par))
