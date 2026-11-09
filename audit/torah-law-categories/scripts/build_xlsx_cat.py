"""Review workbook for the Torah Law categories: every record with dropdowns, live counts, flagged list, definitions."""
import sys, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

REPO = sys.argv[1]; OUTFILE = sys.argv[2]
L = json.load(open(f"{REPO}/data/current/torah-law-categories.json"))
cat = {r["id"]: r for r in json.load(open(f"{REPO}/data/current/commands.json"))}
R = L["records"]; D = L["definitions"]; C = L["counts"]
FORMS = ["Positive", "Negative", "Permission"]; CATS = ["Moral", "Ceremonial", "Civil"]; AREAS = list(D["ceremonial_area"])

GREEN, IVORY, INK, MUTED, IDC = "FF243C32", "FFFFFAF1", "FF322E27", "FF61584D", "FF255B47"
TITLE = Font(name="Arial", size=16, bold=True, color=GREEN); SUB = Font(name="Arial", size=10, color=MUTED)
HEAD = Font(name="Arial", size=10, bold=True, color=IVORY); BODY = Font(name="Arial", size=10, color=INK)
BOLD = Font(name="Arial", size=10, bold=True, color=INK); IDF = Font(name="Arial", size=10, color=IDC)
IVFILL = PatternFill("solid", fgColor=IVORY); HDFILL = PatternFill("solid", fgColor=GREEN)
WRAP = Alignment(wrap_text=True, vertical="top")


def header(ws, title, subs, cols, widths, start=7):
    ws.sheet_properties.tabColor = "243C32"
    for r in range(2, start - 1):
        for c in range(1, max(4, len(cols)) + 1): ws.cell(r, c).fill = IVFILL
    ws.cell(2, 1, title).font = TITLE
    for i, s in enumerate(subs): ws.cell(3 + i, 1, s).font = SUB
    for i, (c, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(start, i, c); cell.font, cell.fill, cell.alignment = HEAD, HDFILL, WRAP
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(start + 1, 1)


def body(ws, rows, start=8, id_cols=(1,), bold_rows=()):
    for ri, row in enumerate(rows, start):
        for ci, v in enumerate(row, 1):
            cell = ws.cell(ri, ci, v)
            cell.font = BOLD if (ri - start) in bold_rows else (IDF if ci in id_cols else BODY)
            cell.alignment = WRAP


def table(ws, name, ncols, start, nrows):
    if not nrows: return
    t = Table(displayName=name, ref=f"A{start}:{get_column_letter(ncols)}{start + nrows}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True); ws.add_table(t)


flagged = [r for r in R if r["review_reasons"]]
wb = Workbook(); ws = wb.active; ws.title = "Read me"
header(ws, "Torah Law categories · form and category for the 646 Mosaic Torah Laws",
       [f"Form follows the Jewish division into positive and negative commandments; category follows the traditional Christian division into moral, ceremonial and civil law. Drafted 8 November 2026.",
        f"{C['form']['Positive']} positive · {C['form']['Negative']} negative · {C['form']['Permission']} permissions · {C['category']['Moral']} moral · {C['category']['Ceremonial']} ceremonial · {C['category']['Civil']} civil · {len(flagged)} flagged for your decision.",
        "Edit the Form, Category, Second category and Ceremonial area columns on the Categories sheet; the Counts sheet updates. The site's classification field is unchanged."],
       ["Sheet", "What it holds", "Rows"], [22, 110, 10])
body(ws, [
    ["Categories", "Every Torah Law record with its form, category, second category, ceremonial area, confidence, review flags and the reviewer's note, beside the site's classification and topic.", len(R)],
    ["Counts", "Live counts from the Categories sheet: form by category, ceremonial areas, second categories, and the site's classification against the new category.", None],
    ["Flagged", "Records flagged for your decision, with the reasons.", len(flagged)],
    ["Definitions", "What each form, category and ceremonial area means.", len(D["form"]) + len(D["category"]) + len(D["ceremonial_area"])],
])

ws = wb.create_sheet("Categories")
cols = ["Record ID", "Scripture", "Study record", "Bible book", "Topic", "Site classification", "Form", "Form mixed", "Form basis",
        "Category", "Second category", "Ceremonial area", "Confidence", "Flagged for review", "Reviewer's note", "Adjudication", "Maimonides 613"]
header(ws, "The 646 Torah Law records with their form and category",
       ["Dropdowns on Form, Category, Second category, Ceremonial area and Confidence. One row per record, in catalogue order."],
       cols, [23.8, 22, 46, 13, 26, 24, 12, 10, 34, 13, 15, 26, 11, 28, 50, 30, 16])
rows = [[r["id"], r["reference"], r["title"], cat[r["id"]]["book"], cat[r["id"]]["topic"], cat[r["id"]]["classification"],
         r["form"], "yes" if r["form_mixed"] else "", r["form_basis"], r["category"], r["second_category"], r["ceremonial_area"],
         r["confidence"], "; ".join(r["review_reasons"]), r["note"], r["adjudicated"], ", ".join(r["maimonides_613"])] for r in R]
body(ws, rows); table(ws, "Categories", len(cols), 7, len(rows))
last = 7 + len(rows)
for col, values in (("G", FORMS), ("J", CATS), ("K", CATS), ("L", AREAS), ("M", ["high", "medium", "low"])):
    dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(f"{col}8:{col}{last}")

ws = wb.create_sheet("Counts")
header(ws, "Counts, live from the Categories sheet", ["Formulas count the Categories sheet, so they follow your edits."],
       ["Item", "Positive", "Negative", "Permission", "Records"], [44, 12, 12, 12, 12])
rng = lambda c: f"Categories!${c}$8:${c}${last}"
rows, bold = [], set()
bold.add(0); rows.append(["Form by category", None, None, None, None])
for k in CATS:
    r0 = 8 + len(rows)
    rows.append([k] + [f'=COUNTIFS({rng("J")},"{k}",{rng("G")},"{x}")' for x in FORMS] + [f"=SUM(B{r0}:D{r0})"])
first_cat, last_cat = 9, 8 + len(rows) - 1
r0 = 8 + len(rows); bold.add(len(rows))
rows.append(["All"] + [f"=SUM({c}{first_cat}:{c}{last_cat})" for c in "BCD"] + [f"=SUM(B{r0}:D{r0})"])
rows.append(["Mixed (both a requirement and a prohibition)", None, None, None, f'=COUNTIF({rng("H")},"yes")'])
bold.add(len(rows)); rows.append(["Ceremonial areas (main category Ceremonial)", None, None, None, None])
for a in AREAS:
    rows.append([a, None, None, None, f'=COUNTIFS({rng("J")},"Ceremonial",{rng("L")},"{a}")'])
bold.add(len(rows)); rows.append(["Second categories", None, None, None, None])
for k in CATS:
    rows.append([k, None, None, None, f'=COUNTIF({rng("K")},"{k}")'])
bold.add(len(rows)); rows.append(["Site classification against main category", "Moral", "Ceremonial", "Civil", "Records"])
for k in sorted({cat[r["id"]]["classification"] for r in R}, key=lambda k: -sum(1 for r in R if cat[r["id"]]["classification"] == k)):
    r0 = 8 + len(rows)
    rows.append([k] + [f'=COUNTIFS({rng("F")},"{k}",{rng("J")},"{x}")' for x in CATS] + [f"=SUM(B{r0}:D{r0})"])
bold.add(len(rows)); rows.append(["Flagged for review", None, None, None, f'=COUNTIF({rng("N")},"?*")'])
body(ws, rows, id_cols=(), bold_rows=bold)

ws = wb.create_sheet("Flagged")
cols = ["Record ID", "Scripture", "Study record", "Form", "Category", "Second category", "Ceremonial area", "Why flagged", "Reviewer's note", "Site classification"]
header(ws, "Records flagged for your decision", [f"{len(flagged)} records. Change them on the Categories sheet (this list is a snapshot)."],
       cols, [23.8, 22, 46, 13, 13, 15, 26, 40, 60, 24])
rows = [[r["id"], r["reference"], r["title"], r["form"] + (" (mixed)" if r["form_mixed"] else ""), r["category"], r["second_category"],
         r["ceremonial_area"], "; ".join(r["review_reasons"]), r["note"], cat[r["id"]]["classification"]] for r in flagged]
body(ws, rows); table(ws, "Flagged", len(cols), 7, len(rows))

ws = wb.create_sheet("Definitions")
cols = ["Label", "Value", "Meaning"]
header(ws, "What the labels mean", ["Form: Jewish division of the commandments. Category: traditional Christian division (Aquinas; Westminster Confession, chapter 19)."],
       cols, [36, 30, 100])
rows = [["Form", k, v] for k, v in D["form"].items()] + [["Category", k, v] for k, v in D["category"].items()] + \
       [["Ceremonial area", k, v] for k, v in D["ceremonial_area"].items()] + [["Form mixed", "yes", D.get("form_mixed", "")], ["Maimonides 613", "P / N numbers", D.get("maimonides_613", "")]]
body(ws, rows, id_cols=()); table(ws, "Definitions", len(cols), 7, len(rows))
wb.save(OUTFILE); print("saved", OUTFILE)
