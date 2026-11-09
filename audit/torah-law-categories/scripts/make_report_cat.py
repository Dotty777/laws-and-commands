"""Write audit/torah-law-categories/README.md from the category layer."""
import json, os, sys, collections
REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/laws-and-commands"
W = "/home/claude/work"; R4 = f"{W}/round4"
L = json.load(open(f"{REPO}/data/current/torah-law-categories.json"))
recs = {r["id"]: r for r in json.load(open(f"{REPO}/data/current/commands.json"))}
CHK = json.load(open(f"{REPO}/audit/torah-law-categories/accuracy-check.json")) if os.path.exists(f"{REPO}/audit/torah-law-categories/accuracy-check.json") else None
R = L["records"]; C = L["counts"]; D = L["definitions"]
FORMS = ["Positive", "Negative", "Permission"]; CATS = ["Moral", "Ceremonial", "Civil"]


def esc(s): return str(s).replace("|", "\\|").replace("\n", " ")


def table(head, rows, right=()):
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---:" if i in right else "---" for i in range(len(head))) + " |"]
    out += ["| " + " | ".join(esc(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


f, cat, area, sec = C["form"], C["category"], C["ceremonial_area"], C["second_category"]
flagged = [r for r in R if r["review_reasons"]]
reasons = collections.Counter(x for r in flagged for x in r["review_reasons"])
seeded = [r for r in R if r["maimonides_613"]]
agree = sum(1 for r in seeded if (all(s.startswith("P") for s in r["maimonides_613"]) and r["form"] == "Positive")
            or (all(s.startswith("N") for s in r["maimonides_613"]) and r["form"] == "Negative"))
single = sum(1 for r in seeded if all(s.startswith("P") for s in r["maimonides_613"]) or all(s.startswith("N") for s in r["maimonides_613"]))
cls = collections.defaultdict(collections.Counter)
for r in R: cls[recs[r["id"]]["classification"]][r["category"]] += 1

lines = [
    "# Torah Law categories", "",
    f"**All {C['torah_laws']} Torah Law records now carry two study labels: a form from the Jewish division of the commandments, and a category from the traditional Christian division of the Mosaic law.** "
    f"{f['Positive']} are positive, {f['Negative']} negative and {f['Permission']} permissions. {cat['Moral']} are moral, {cat['Ceremonial']} ceremonial and {cat['Civil']} civil. "
    f"{len(flagged)} records are flagged below for your decision.", "",
    "The labels sit in their own data file beside the catalogue. The site's classification field, which says how each law applies to Christians today, is unchanged.", "",
    "## What the labels mean", "",
    table(["Label", "Value", "Meaning"],
          [["Form (Jewish tradition)", k, v] for k, v in D["form"].items()] +
          [["Category (traditional Christian division)", k, v] for k, v in D["category"].items()] +
          [["Ceremonial area", k, v] for k, v in D["ceremonial_area"].items()]), "",
    "A record can have a second category when it clearly has two characters. The weekly Sabbath, for example, is moral as one of the Ten Commandments and ceremonial in its day-keeping. "
    "When a provision holds both a requirement and a prohibition, its form is that of its main clause, and it is marked as mixed.", "",
    "Form is judged from the operative words of the Saints Translation verse, not from the record's title. Following Maimonides, a court's duty to carry out a penalty and a rule that sets a status (such as an impurity period) count as positive.", "",
    "## Results", "",
    "### Form by category", "",
    table(["Category", "Positive", "Negative", "Permission", "Records"],
          [[k, *[C["form_by_category"][k][x] for x in FORMS], cat[k]] for k in CATS] +
          [["**All**", *[f[x] for x in FORMS], C["torah_laws"]]], right=(1, 2, 3, 4)), "",
    f"{C['form_mixed']} records hold both a requirement and a prohibition.", "",
    "### Ceremonial areas", "",
    table(["Area", "Records"], [[k, v] for k, v in area.items()] + [["**All ceremonial**", cat["Ceremonial"]]], right=(1,)), "",
    "### Second categories", "",
    f"{sum(sec.values())} records have a second category: " + ", ".join(f"{v} {k.lower()}" for k, v in sec.items() if v) + ".", "",
    "### Compared with the traditional 613", "",
    f"Maimonides counts 248 positive and 365 negative commandments, so 40% are positive. In this catalogue {round(100 * f['Positive'] / C['torah_laws'])}% are positive, "
    "because it itemizes many procedures, penalties and status rules, which count as positive, and lists permissions separately.", "",
    f"{len(seeded)} records were matched to Maimonides' commandments in the Torah Law count check. Of the {single} matched only to positive or only to negative commandments, {agree} take the same form here; "
    "the others are flagged below.", "",
    "## How the labels relate to the site's classification", "",
    "The classification field is left as it is. The site's legend keeps \"Israel’s civil and land laws\", \"Covenant-specific instructions\" and the historical categories so that these laws \"should not be forced into one of the four Christian-application marks\". "
    "They are statements about application, not a mix-up of kinds, so the new category sits beside them rather than replacing them.", "",
    table(["Site classification", "Moral", "Ceremonial", "Civil", "Records"],
          [[k, v["Moral"], v["Ceremonial"], v["Civil"], sum(v.values())] for k, v in sorted(cls.items(), key=lambda kv: -sum(kv[1].values()))], right=(1, 2, 3, 4)), "",
    "The usual pairings are civil and land laws with Civil, covenant-specific instructions and Fulfilled with Ceremonial, and Everlasting or Unchanged with Moral. Records that depart from them are flagged below.", "",
    "## Flagged for your decision", "",
    f"{len(flagged)} records are flagged. A record can be flagged for more than one reason:", "",
    *[f"- {v} {k}" for k, v in reasons.most_common()], "",
    "Each has a proposed form and category; confirm or change them in the data file or the workbook. A record appears once, under the first group that applies.", "",
]
GROUPS = [("Form departs from the 613 match", "differs from the 613 match"),
          ("Category departs from the site's classification", "differs from the site's classification"),
          ("Medium or low confidence", "confidence")]
done = set()


def proposed(r):
    one = lambda name: name + (f": {r['ceremonial_area']}" if name == "Ceremonial" else "")
    return (r["form"] + (" (mixed)" if r["form_mixed"] else "") + " · " + one(r["category"])
            + (f" · also {one(r['second_category'])}" if r["second_category"] else ""))


for heading, key in GROUPS:
    rows = [r for r in flagged if r["id"] not in done and any(key in x for x in r["review_reasons"])]
    done.update(r["id"] for r in rows)
    lines += [f"### {heading} ({len(rows)})", "",
              table(["Record", "Scripture", "Study record", "Proposed", "Site classification", "Reviewer's note"],
                    [[f"`{r['id']}`", r["reference"], r["title"], proposed(r), recs[r["id"]]["classification"], r["note"]] for r in rows]), ""]
assert done == {r["id"] for r in flagged}
if CHK:
    bk = CHK["by_field"]
    lines += ["## Accuracy check", "",
              f"A separate reviewer classified {CHK['sample']} records ({CHK['drawn_from']}) from the same brief, without seeing the reviewers' answers. "
              + CHK["summary"], ""]
    if CHK.get("changes"):
        lines += ["Changes made after the check:", "", *[f"- `{c['id']}`: {c['change']}" for c in CHK["changes"]], ""]
lines += [
    "## How it was done", "",
    "1. **Inputs.** Each of the 646 records was given with its Saints Translation verse text, its topic, the site's classification, its original audience and the Maimonides commandments matched to it in the Torah Law count check.",
    "2. **Review.** Seven reviewers each took about 93 records and assigned form, category, any second category and ceremonial area from the verse, following [the brief](method/brief.md). Each output passed [a validator](scripts/validate_cat.py).",
    "3. **Cross-checks.** Forms were compared with the 613 matches and categories with the site's classification, and recurring kinds of law (penalties, food laws, permissions, the Ten Commandments, the Sabbath) were compared across the seven batches. Records that differ, and anything below high confidence, are flagged.",
    "4. **Accuracy check.** A separate reviewer re-checked a random sample.", "",
    "## Files", "",
    table(["File", "What it holds"], [
        ["[data/current/torah-law-categories.json](../../data/current/torah-law-categories.json)", "The category layer: definitions, counts and one entry per Torah Law record"],
        ["[data/current/torah-law-categories.csv](../../data/current/torah-law-categories.csv)", "The same entries as a spreadsheet-ready CSV"],
        ["[Saints-Bible-Torah-Law-Categories-2026-11-08.xlsx](Saints-Bible-Torah-Law-Categories-2026-11-08.xlsx)", "Review workbook with dropdowns and live counts"],
        ["[browse/torah-law](../../browse/torah-law/README.md)", "Browse pages by category and form, and Form and Category columns on every Torah Law page"],
        ["[review-records/](review-records/), [method/](method/), [scripts/](scripts/)", "Reviewer output, the brief and inputs, and the scripts"],
    ]), "",
    "To rebuild the CSV, the counts and the browse pages after editing the JSON, run from the repository root:", "",
    "```sh", "python scripts/build_torah_law_categories.py", "python scripts/build_browse.py",
    "python scripts/build_torah_law_categories.py --check", "python scripts/build_browse.py --check", "```", "",
    "## Limits", "",
    "- Both schemes are interpretive traditions, not labels Scripture supplies. The moral, ceremonial and civil division follows Thomas Aquinas and the Westminster Confession (chapter 19); dispensational and Messianic readers use it differently.",
    "- Forms rest on the Saints Translation wording. Jewish enumerators also differ on some edge cases.",
    "- The labels were drafted by reviewers and cross-checked, not decided by the site's editors. The flagged records need your decision.",
]
os.makedirs(f"{REPO}/audit/torah-law-categories", exist_ok=True)
open(f"{REPO}/audit/torah-law-categories/README.md", "w").write("\n".join(lines) + "\n")
print("README words:", len(" ".join(lines).split()), "flagged:", len(flagged))
