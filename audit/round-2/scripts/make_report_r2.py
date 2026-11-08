"""Write the round-2 report (markdown for the repository) and the per-book CSV from the compiled JSON."""
import json, sys, collections, csv, re, os
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
W = "/home/claude/work"; A = f"{W}/audit/round2"
S = json.load(open(f"{A}/summary.json")); C = json.load(open(f"{A}/coverage.json")); REM = json.load(open(f"{A}/remaining.json"))
N = json.load(open(f"{A}/new_records.json")); E = json.load(open(f"{A}/extend.json")); P = json.load(open(f"{A}/parallel.json"))
DEC = json.load(open(f"{A}/declined.json")); SUP = json.load(open(f"{A}/superseded.json")); T = json.load(open(f"{A}/topic_fixes.json"))
D = json.load(open(f"{A}/decisions.json"))
CHK = json.load(open(f"{A}/accuracy_check.json")) if os.path.exists(f"{A}/accuracy_check.json") else None
DIV = {}
for v in B.verses: DIV.setdefault(v["book"], v["div"].capitalize())
DIVN = {"Law": "Law (Genesis–Deuteronomy)", "Judgement": "Judgement (Joshua–Job)", "Wisdom": "Wisdom (Psalms–Sirach)",
        "Providence": "Providence (Isaiah–Malachi)", "Salvation": "Salvation (Gospels)", "Discipleship": "Discipleship (Acts–Jude)", "Glory": "Glory (Revelation)"}
f = lambda n: f"{n:,}"

# ---- review table
KINDS = [("held new record", "Held new records (deferred or held without a reason)"), ("held extension", "Held extensions"),
         ("held parallel", "Held parallels"), ("similarity candidate", "Unattached verses whose wording restates a recorded direction"),
         ("sweep verse", "Unread verses with appointment, handover or summons wording"),
         ("residual verse", "Directive verses a first-round finding touched but left unattached"), ("reconciliation", "Loose ends the reviewers pointed to")]
def kind(item):
    if item.startswith("RC"): return "reconciliation"
    return {"N": "held new record", "E": "held extension", "P": "held parallel", "S": "similarity candidate", "U": "sweep verse", "V": "residual verse"}[item[0]]
cnt = collections.defaultdict(collections.Counter)
for d in D: cnt[kind(d["item"])][d["decision"]] += 1
rows = []
tot = collections.Counter()
for k, label in KINDS:
    c = cnt[k]; n = sum(c.values()); tot.update(c); tot["n"] += n
    rows.append(f"| {label} | {f(n)} | {c['record_new']} | {c['record_extend']} | {c['record_parallel']} | {c['no_record']} | {c['superseded']} |")
rows.append(f"| **All items** | **{f(tot['n'])}** | **{tot['record_new']}** | **{tot['record_extend']}** | **{tot['record_parallel']}** | **{tot['no_record']}** | **{tot['superseded']}** |")
review_table = "\n".join(["| What was reviewed | Items | New record | Extend | Parallel | Declined | Merged |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"] + rows)

# ---- division table
dn = collections.Counter(DIV[o["book"]] for o in N); de = collections.Counter(DIV[e["book"]] for e in E)
dp = collections.Counter(DIV[p["book"]] for p in P)
cb = collections.defaultdict(lambda: [0, 0, 0])
for bk, s in C["by_book"].items():
    x = cb[DIV[bk]]; x[0] += s["directive"]; x[1] += s["before"]; x[2] += s["after"]
drows = ["| Division | New records | Records extended | Parallel links | Directive verses attached, before → after |", "| --- | ---: | ---: | ---: | --- |"]
for dv in ["Law", "Judgement", "Wisdom", "Providence", "Salvation", "Discipleship", "Glory"]:
    x = cb[dv]
    drows.append(f"| {DIVN[dv]} | {dn[dv]} | {de[dv]} | {dp[dv]} | {f(x[1])} → {f(x[2])} of {f(x[0])} ({100 * x[1] / x[0]:.1f}% → {100 * x[2] / x[0]:.1f}%) |")
division_table = "\n".join(drows)

# ---- types
tc = collections.Counter(o["record_type"] for o in N); cc = collections.Counter(o["confidence"] for o in N)
type_line = ", ".join(f"{tc[t]} {t}" for t in ["Command", "Commission", "Wisdom", "Law", "Instruction"] if tc[t])
conf_line = f"{cc['high']} high, {cc['medium']} medium and {cc['low']} low confidence"
APPT = re.compile(r"\b(makes? .*king|anoints?|appoints?|installs?|crowns?)\b", re.I)
appt = [o for o in N if APPT.search(o["title"])]

# ---- notable records (picked by reference)
def find_new(ref_start):
    for o in N:
        if o["reference"].startswith(ref_start): return o
NOTABLE = ["Joshua 6:26", "1 Kings 11:37", "2 Chronicles 15:12", "2 Chronicles 30:2", "2 Chronicles 35:25", "2 Maccabees 7:1", "2 Maccabees 15:5",
           "Matthew 4:3", "Matthew 15:21", "Matthew 26:59", "Matthew 27:24", "John 11:47", "Luke 14:15", "Judges 11:36"]
notable = []
for r in NOTABLE:
    o = find_new(r)
    if o:
        add = f" (with {'; '.join(a['reference'] for a in o['additional'])})" if o["additional"] else ""
        notable.append(f"- `{o['id']}` {o['reference']}{add}: {o['title']}")

# ---- accuracy check
if CHK:
    v = CHK["verdicts"]; n = sum(v.values())
    chk = (f"An independent reviewer, who did not see the reviewers' reasoning, re-checked a random sample of {n} decisions "
           f"(20 new records, 15 extensions, 15 parallels, 15 declines) against the Saints text and the catalogue: "
           f"**{v.get('correct', 0)} correct, {v.get('partly', 0)} partly right and {v.get('wrong', 0)} wrong**. " + CHK["summary"])
else:
    chk = "(accuracy check pending)"

rem = REM["by_reason"]
md = f"""# Associated verses: round 2 of the completeness audit, 8 November 2026

This pass checked the updated catalogue for verses that state, continue, repeat, quote or recall a law, command, commission, instruction or wisdom saying but are not attached to any record. It used the 6,416 records at repository commit `2461b81`, the version the repository describes as published on staging and production. Every item the first audit left open, and every directive-looking verse still unattached after the editorial review, now has a final decision. Everything here is a draft for review: nothing was changed on the website or in the catalogue data.

**Result.** The audit proposes **{len(N)} new records**, **{len(E)} existing records whose Scripture should take in {S['extension_verses']} more verses**, and **{len(P)} verses to link as Additional Scripture** on existing records, plus {S['new_additional_links']} links on the new records. {len(DEC)} items were declined, each with the standard that applies. {len(SUP)} were merged because the same verses had been decided in two places. With these changes, **{f(C['covered_after'])} of the {f(C['directive_verses'])} screened directive verses would be attached to a record, up from {f(C['covered_before'])} ({C['pct_before']}% → {C['pct_after']}%)**. In all, {f(C['newly_attached_verses'])} verses would gain a record.

{review_table}

The table counts review items. Several items can extend the same record, so the {tot['record_extend']} extend decisions combine into {len(E)} records. The parallel decisions give {len(P)} links once duplicates are merged and one long reference is split into its parts. The new records are {type_line}, at {conf_line}.

{division_table}

The import-ready workbook is [Saints-Bible-Associated-Verses-Round-2-2026-11-08.xlsx](Saints-Bible-Associated-Verses-Round-2-2026-11-08.xlsx). Its New records sheet uses the Catalogue sheet's 24 columns, and its Link as parallel sheet uses the Scripture Sources columns.

## Notable additions

{chr(10).join(notable)}

Links that gather scattered restatements:
- General "keep my commandments" verses go to the most exact record: AUD-03-18-4 for Leviticus, AUD-05-5-32 for Deuteronomy, and C0124 where no closer record exists.
- Deuteronomy 27's curses go to their direct commands: 27:16 to C0153 (honour parents), 27:24 to C0156 (murder), and 27:19 to AUD-05-24-17.
- The Synoptic demands to crucify go to AUD-47-19-6.
- The priest's examinations in Leviticus 13 go to C0485.

## What is still unattached, and why

{f(REM['remaining'])} screened directive verses remain unattached:

- **{f(rem.get('read in round 1 and judged not to need a record', 0))}** were read in the first round and judged not to need a record. Most are in the Prophets (743), the history books (742) and the Psalms (553): oracles and predictions, prayers addressed to God, and narrative, which the screen flags for their grammar. The first round's recall check found 2 low-confidence misses in a sample of 45 such passages.
- **{f(rem.get('held only by a long passage record (Genesis–Deuteronomy, over 8 verses)', 0))}** in Genesis–Deuteronomy are held by a long passage record (over 8 verses) but by no itemized record. This audit counts them as unattached so that Torah laws are itemized.
- **{f(rem.get('reviewed again in round 2 and declined, with a stated reason', 0))}** were reviewed again in this round and declined. The reasons are in the workbook's Declined or merged sheet.

## Accuracy check

{chk}

## Decisions for the editor

- **Narrated appointments and king-makings.** About {len(appt)} of the new records are narrated appointments, anointings and king-makings (for example AUD-12-14-21, AUD-12-23-30 and AUD-14-36-10). They were recorded because the catalogue already publishes such records (AUD-10-2-4, AUD-10-2-8 and AUD-06-11-1). If you prefer not to record narrated appointments, these can be dropped as a group.
- **Pilate's release custom** (John 18:38–40) is low confidence. One reviewer recorded it, and another judged the Mark parallel an offer and a custom rather than a direction.
- **Leviticus 13 and Numbers 15** are linked to C0485 and C0857 as Additional Scripture rather than widening those records past 8 verses. This follows how C0484, C0486 and C0487 already hold their in-chapter repeats.
- **Leviticus 18:5.** Romans 10:5 and Galatians 3:12 quote it but sit on the group record torah-leviticus-18-1, while Nehemiah 9:29 is now linked to AUD-03-18-4. You may want them in one place.
- **The devil's demands** (Matthew 4:3, 5–6, 8–9) carry the origin Earthly (Man-made), because none of the three origin values fits.

## Housekeeping

- **Topics.** {len(T)} records have an empty Topic or one that holds the record type. These are 559 records in the 70-book audit collection, 24 Harmony study records and 12 Supplemental passage records. The Housekeeping sheet gives each one a topic from the 50: {sum(1 for t in T if t['confidence'] == 'high')} high, {sum(1 for t in T if t['confidence'] == 'medium')} medium and {sum(1 for t in T if t['confidence'] == 'low')} low confidence.
- **X012** (Revelation 22:8–9) links to verse 22:9. It is the only record whose Scripture link does not open at the first verse of its reference.

## How it was done

1. The catalogue (6,416 records) was re-read from `data/current/commands.json`, and the first audit's tools were pointed at it.
2. Open items were collected:
   - held new records, extensions and parallels whose hold was deferred or gave no reason;
   - 168 unattached verses whose wording closely restates a recorded directive verse (text similarity);
   - 42 never-read verses with appointment, handover or summons wording;
   - 321 directive verses that a first-round finding touched but that remain unattached. Where the editor had held a finding for a specific reason, the reviewers followed that reason.
3. Seventeen reviewers decided every item against the Saints text and the current catalogue, using the editorial review's own standard ([BRIEF2.md](method/BRIEF2.md)). Every output was machine-validated.
4. Verses decided in two places were reconciled ([reconcile.json](method/reconcile.json)). Extensions were combined per record, IDs were assigned in the published `AUD-` scheme, and coverage was recomputed.
5. A separate reviewer checked a random sample of decisions (above).

Coverage measure: directive verses are those the language screen marks as commands, prohibitions, laws, requests or reported orders (11,464 verses). A verse counts as attached when a record's Scripture or Additional Scripture includes it. In Genesis–Deuteronomy, the entry holding it must be 8 verses or fewer.

## Files

| File | What it holds |
| --- | --- |
| [Saints-Bible-Associated-Verses-Round-2-2026-11-08.xlsx](Saints-Bible-Associated-Verses-Round-2-2026-11-08.xlsx) | Import-ready sheets: New records, Extend Scripture, Link as parallel, Declined or merged, Coverage by book, Housekeeping |
| [new-records.json](new-records.json), [extend.json](extend.json), [parallel.json](parallel.json) | The proposals in machine-readable form |
| [declined.json](declined.json), [merged.json](merged.json) | Items not recorded, and items merged, with reasons |
| [decisions.json](decisions.json) | All {f(len(D))} decisions with reasons, as compiled |
| [topic-fixes.json](topic-fixes.json) | The proposed topic for each of the {len(T)} records |
| [coverage-by-book.csv](coverage-by-book.csv), [coverage.json](coverage.json), [remaining.json](remaining.json) | Coverage before and after, and why verses remain unattached |
| [accuracy-check.json](accuracy-check.json) | The independent sample check |
| [review-records/](review-records/) | Each reviewer's raw decisions (JSON lines) |
| [method/](method/) and [scripts/](scripts/) | The brief, the reconciliation and the scripts |

## Limits

- The live site was not fetched for this pass. The comparison rests on the repository's statement that the catalogue workbook matches production and staging.
- The language screen and the similarity search find verses by their wording. A verse that directs without imperative or legal wording can be missed, though the first round's recall check suggests such misses are few and minor.
- Study placement and Classification for the new records follow the editor's conventions for that record type, book and origin, and should be checked on import.
"""
open(f"{A}/README.md", "w").write(md)
with open(f"{A}/coverage-by-book.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["book", "division", "directive_verses", "attached_before", "attached_after", "new_records", "records_extended", "parallel_links"])
    nb = collections.Counter(o["book"] for o in N); eb = collections.Counter(e["book"] for e in E); pb = collections.Counter(p["book"] for p in P)
    for bk in B.order:
        s = C["by_book"].get(bk, {"directive": 0, "before": 0, "after": 0})
        w.writerow([bk, DIV[bk], s["directive"], s["before"], s["after"], nb[bk], eb[bk], pb[bk]])
print("report written", len(md.split()), "words")
