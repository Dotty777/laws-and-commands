"""Round-2 import workbook, styled like the catalogue workbook.
python3 -I /home/claude/work/build_xlsx_r2.py <out.xlsx>"""
import sys, json, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

W = "/home/claude/work"; A = f"{W}/audit/round2"; REPO = "/home/claude/repos/laws-and-commands"
OUTFILE = sys.argv[1]
B = Bible()
recs = json.load(open(f"{REPO}/data/current/commands.json")); byid = {r["id"]: r for r in recs}
NEW = json.load(open(f"{A}/new_records.json")); EXT = json.load(open(f"{A}/extend.json"))
PAR = json.load(open(f"{A}/parallel.json")); DEC = json.load(open(f"{A}/declined.json")); SUP = json.load(open(f"{A}/superseded.json"))
REM = json.load(open(f"{A}/remaining.json"))
COV = json.load(open(f"{A}/coverage.json")); SUM = json.load(open(f"{A}/summary.json"))
TOPFIX = json.load(open(f"{A}/topic_fixes.json"))

GREEN, IVORY, INK, MUTED, IDC = "FF243C32", "FFFFFAF1", "FF322E27", "FF61584D", "FF255B47"
TITLE = Font(name="Arial", size=16, bold=True, color=GREEN); SUB = Font(name="Arial", size=10, color=MUTED)
HEAD = Font(name="Arial", size=10, bold=True, color=IVORY); BODY = Font(name="Arial", size=10, color=INK)
BOLD = Font(name="Arial", size=10, bold=True, color=INK); IDF = Font(name="Arial", size=10, color=IDC)
IVFILL = PatternFill("solid", fgColor=IVORY); HDFILL = PatternFill("solid", fgColor=GREEN)
WRAP = Alignment(wrap_text=True, vertical="top")
NT = set(B.order[B.order.index("Matthew"):])
DIV = {}
for v in B.verses: DIV.setdefault(v["book"], v["div"].capitalize())

# ---- the editor's conventions for audit records
LAWB = {"Exodus", "Leviticus", "Numbers", "Deuteronomy"}
cr = [r for r in recs if r["collection"] == "Completeness review"]
def usable(pl, book, ch):
    if "hostile" in pl or "Mosaic" in pl or "Torah" in pl: return False
    if "Temple vision" in pl and not (book == "Ezekiel" and ch >= 40): return False
    return True
by_tb = collections.defaultdict(collections.Counter); by_td = collections.defaultdict(collections.Counter); by_t = collections.defaultdict(collections.Counter)
for r in cr:
    k = (r["study_placement"], r["classification"])
    by_tb[(r["record_type"], r["book"])][k] += 1; by_td[(r["record_type"], DIV.get(r["book"], ""))][k] += 1; by_t[r["record_type"]][k] += 1


def convention(t, book, origin, ch):
    heavenly = origin.startswith("Heavenly")
    if book == "Genesis":
        return ("Historical direction", "Historical commissions" if t == "Commission" else "Historical")
    if book in LAWB:
        if t == "Commission": return ("Torah · Personal historical direction", "Historical commissions")
        if heavenly and t == "Law": return ("Torah Law", "Application under review")
        if heavenly: return (f"Mosaic {t}", "Application under review")
        return ("Torah · Historical direction", "Historical")
    for c in (by_tb.get((t, book)), by_td.get((t, DIV.get(book, ""))), by_t.get(t)):
        if not c: continue
        ok = [(k, n) for k, n in c.most_common() if usable(k[0], book, ch)]
        if ok and sum(n for _, n in ok) >= 3: return ok[0][0]
    return ("Historical direction", "Historical")


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


def body_rows(ws, rows, start_row=8, id_cols=(1,)):
    for r_i, row in enumerate(rows, start_row):
        for c_i, val in enumerate(row, 1):
            cell = ws.cell(r_i, c_i, val); cell.font = IDF if c_i in id_cols else BODY; cell.alignment = WRAP


def add_table(ws, name, ncols, start_row, nrows):
    if nrows == 0: return
    t = Table(displayName=name, ref=f"A{start_row}:{get_column_letter(ncols)}{start_row + nrows}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True); ws.add_table(t)


c = SUM["coverage"]
wb = Workbook(); ws = wb.active; ws.title = "Read me"
header(ws, "Round 2 · Associated verses for laws, commands, commissions, instructions and wisdom",
       [f"Checked against the updated catalogue (6,416 records, repository commit 2461b81), 8 November 2026. Every open item from the first audit and every directive-looking verse still unattached was given a final decision.",
        "Everything here is a draft for review: nothing has been changed on the website or in the catalogue data."],
       ["Sheet", "What it holds", "Rows"], [24, 112, 10])
body_rows(ws, [
    ["New records", "Directions that no record holds yet, in the Catalogue sheet's 24 columns plus two audit columns. IDs follow the published AUD- scheme (book number, chapter, first verse; '-2' where taken). Study placement and Classification follow the editor's most common choice for that record type and book.", len(NEW)],
    ["Extend Scripture", "Existing records whose Scripture should take in further verses carrying the same direction (one row per record; several decisions for one record are combined).", len(EXT)],
    ["Link as parallel", "Verses that restate, repeat, quote, report or recall a recorded direction elsewhere: add as Additional Scripture. First four columns match the Scripture Sources sheet. Includes the parallels for the new records.", len(PAR) + sum(len(o["additional"]) for o in NEW)],
    ["Declined or merged", "Items reviewed and not recorded, with the standard that applies (the editor's published review standard), and items merged because the same verses were decided in two places.", len(DEC) + len(SUP)],
    ["Coverage by book", f"Screened directive verses attached to a record before and after these changes: {c['covered_before']:,} → {c['covered_after']:,} of {c['directive_verses']:,} ({c['pct_before']}% → {c['pct_after']}%). In Genesis–Deuteronomy a verse counts only when an entry of 8 verses or fewer holds it.", len(COV["by_book"])],
    ["Housekeeping", "A valid topic for each record whose Topic is empty or holds the record type, and one Scripture link that points past the first verse.", len(TOPFIX) + 1],
    ["Still unattached", f"{REM['remaining']:,} screened directive verses remain unattached: " + "; ".join(f"{v:,} {k}" for k, v in REM["by_reason"].items()) + ".", None],
    ["Audit columns", "Audit confidence and Audit note are for review only; drop them before merging into the Catalogue sheet.", None],
])
# ---- New records
ws = wb.create_sheet("New records")
CAT_COLS = ["Record ID", "Scripture", "Study record", "Study placement", "Mosaic type", "Original audience or recipient", "Audience", "Origin",
            "Collection", "Topic", "Classification", "Bible book", "Testament", "Audience review", "Catalogue audience", "Context note",
            "Citation basis", "Origin basis", "Mosaic context", "Mosaic review note", "Record type", "Speaker or source",
            "Original audience (audit)", "Additional Scripture", "Audit confidence", "Audit note"]
widths = [23.8, 23, 50.2, 24, 12, 30, 12.8, 23.1, 22, 30, 24.8, 16, 11, 16, 30, 50, 12, 46, 14, 14, 14, 26, 30, 16, 12, 60]
header(ws, "New records · round 2",
       [f"{len(NEW)} records · same columns as the Catalogue sheet · drafts for review",
        "Collection is 'Completeness review', as the editor used for the first audit's additions."], CAT_COLS, widths)
rows = []
for o in NEW:
    t, book = o["record_type"], o["book"]; sp, rc = o["speaker"].strip(), o["recipient"].strip()
    ch = B.verses[B.expand(o["reference"])[0][0]]["ch"]
    place, cls = convention(t, book, o["origin"], ch); mosaic = place.startswith("Mosaic") or place == "Torah Law"
    note = o["reason"] + (f" (review item {o['item']}" + (f"; draft {o['draft_id']}" if o.get("draft_id") else "") + ")")
    rows.append([o["id"], o["reference"], o["title"], place, t if mosaic else "", rc if mosaic else "", o["audience"], o["origin"],
                 "Completeness review", o["topic"], cls, book, "New" if book in NT else "Old", "Assigned", rc,
                 f"{sp} addresses {rc} in this passage.", "Source", f"Source in this passage: {sp}. Original recipient: {rc}.",
                 (f"{sp[0].lower() + sp[1:] if sp.lower().startswith('the ') else sp} addresses {rc} in this passage.") if mosaic else "", "",
                 t, sp, rc, "; ".join(a["reference"] for a in o["additional"]), o["confidence"], note])
body_rows(ws, rows); add_table(ws, "NewRecords", len(CAT_COLS), 7, len(rows))
# ---- Extend
ws = wb.create_sheet("Extend Scripture")
cols = ["Record ID", "Current Scripture", "Study record", "Record type", "Verses to add", "Proposed Scripture", "Why", "Bible book", "Audit confidence", "Note"]
header(ws, "Existing records whose Scripture stops short",
       [f"{len(EXT)} records · {SUM['extension_verses']} verses · each record already states this direction, but its reference misses these verses"],
       cols, [23.8, 22, 46, 13, 22, 26, 64, 16, 12, 40])
rows = [[e["existing_id"], e["current"], e["title"], e["record_type"], e["add"], e["proposed"], " · ".join(dict.fromkeys(e["reasons"])),
         e["book"], e["confidence"], e.get("note", "")] for e in EXT]
body_rows(ws, rows); add_table(ws, "ExtendScripture", len(cols), 7, len(rows))
# ---- Parallel
ws = wb.create_sheet("Link as parallel")
cols = ["Record ID", "Scripture", "Study record", "Context for this source", "Primary Scripture of the record", "Bible book", "Audit confidence", "Why", "Record is"]
NADD = sum(len(o["additional"]) for o in NEW)
header(ws, "Parallels to link as Additional Scripture",
       [f"{len(PAR)} links on existing records and {NADD} on the new records · first four columns match the Scripture Sources sheet (Record ID, Scripture, Study record, Context for this source)"],
       cols, [23.8, 24, 46, 66, 22, 16, 12, 44, 16])
rows = [[p["existing_id"], p["reference"], p["title"], p["context"], p["existing_ref"], p["book"], p["confidence"], p["reason"], "existing"] for p in PAR]
for o in NEW:
    for a in o["additional"]:
        rows.append([o["id"], a["reference"], o["title"], a["context"], o["reference"], B.verses[B.expand(a["reference"])[0][0]]["book"], o["confidence"], "Parallel for a new record in this workbook", "new in this workbook"])
body_rows(ws, rows); add_table(ws, "LinkParallel", len(cols), 7, len(rows))
# ---- Declined
ws = wb.create_sheet("Declined or merged")
cols = ["Review item", "Kind", "Scripture", "Outcome", "Why", "Audit confidence"]
header(ws, "Reviewed and not recorded separately",
       [f"{len(DEC)} items declined · each was read against the Saints text and the current catalogue; the reason names the published standard that applies",
        f"{len(SUP)} items merged: the same verses were decided in two places, and are attached through the record named"],
       cols, [28, 18, 24, 12, 90, 12])
rows = [[d["item"], d["kind"], d["reference"], "Declined", d["reason"], d["confidence"]] for d in DEC]
rows += [[d["item"], d["kind"], d["reference"], "Merged", d["why"], ""] for d in SUP]
body_rows(ws, rows); add_table(ws, "Declined", len(cols), 7, len(rows))
# ---- Coverage by book
ws = wb.create_sheet("Coverage by book")
cols = ["Bible book", "Division", "Directive verses screened", "Attached before", "Attached after", "Before %", "After %", "Still unattached"]
header(ws, "Screened directive verses attached to a record",
       ["Directive verses = verses the language screen marks as commands, prohibitions, laws, requests or reported orders. Most still unattached were read and judged not to need a record (prayers to God, predictions, narrative).",
        "In Genesis–Deuteronomy a verse counts only when an entry of 8 verses or fewer holds it, so long passage summaries do not count there."],
       cols, [20, 13, 14, 12, 12, 10, 10, 12])
r0 = 8; books = [b for b in B.order if b in COV["by_book"]]
for i, bk in enumerate(books):
    s = COV["by_book"][bk]; row = r0 + i
    for col, v in enumerate([bk, DIV[bk], s["directive"], s["before"], s["after"]], 1): ws.cell(row, col, v).font = BODY
    ws.cell(row, 6, f"=IFERROR(D{row}/C{row},0)").font = BODY; ws.cell(row, 7, f"=IFERROR(E{row}/C{row},0)").font = BODY
    ws.cell(row, 8, f"=C{row}-E{row}").font = BODY
    ws.cell(row, 6).number_format = ws.cell(row, 7).number_format = "0.0%"
last = r0 + len(books) - 1; tot = last + 1
ws.cell(tot, 1, "All 70 books").font = BOLD
for col in (3, 4, 5, 8):
    L = get_column_letter(col); ws.cell(tot, col, f"=SUM({L}{r0}:{L}{last})").font = BOLD
ws.cell(tot, 6, f"=IFERROR(D{tot}/C{tot},0)").font = BOLD; ws.cell(tot, 7, f"=IFERROR(E{tot}/C{tot},0)").font = BOLD
ws.cell(tot, 6).number_format = ws.cell(tot, 7).number_format = "0.0%"
# ---- Housekeeping
ws = wb.create_sheet("Housekeeping")
cols = ["Record ID", "Scripture", "Study record", "Record type", "Collection", "Current topic", "Proposed topic or fix", "Audit confidence"]
header(ws, "Housekeeping",
       [f"{len(TOPFIX)} records whose Topic is empty or holds the record type, each with one of the 50 topics · 1 Scripture link that points past the first verse"],
       cols, [23.8, 24, 50, 13, 24, 16, 46, 12])
rows = [[t["id"], byid[t["id"]]["reference"], byid[t["id"]]["title"], byid[t["id"]]["record_type"], byid[t["id"]]["collection"],
         byid[t["id"]]["topic"] or "(empty)", t["topic"], t["confidence"]] for t in TOPFIX]
x = byid["X012"]
rows.append(["X012", x["reference"], x["title"], x["record_type"], x["collection"], x["topic"] or "(empty)",
             "Scripture link points to 22:9; point it at 22:8 (…/chapter-22/#v22-8)", "high"])
body_rows(ws, rows); add_table(ws, "Housekeeping", len(cols), 7, len(rows))
wb.save(OUTFILE)
print("saved", OUTFILE, len(NEW), len(EXT), len(PAR), len(DEC), len(TOPFIX))
