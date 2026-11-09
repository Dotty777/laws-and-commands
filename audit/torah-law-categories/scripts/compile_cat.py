"""Compile the category pass into the repository data file (data/current/torah-law-categories.json).

Reads the reviewer output in round4/out/C*.jsonl (and, when present, round4/decisions.json with
my adjudications), checks it, and writes the JSON the repository builder normalizes.
"""
import json, os, sys, collections, subprocess
W = "/home/claude/work"; R4 = f"{W}/round4"
REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/laws-and-commands"
recs = json.load(open(f"{REPO}/data/current/commands.json"))
TL = [r for r in recs if r["study_placement"] == "Torah Law"]
index = json.load(open(f"{R4}/index.json"))
batches = {}
for name in index:
    for x in json.load(open(f"{R4}/batches/{name}.json")): batches[x["id"]] = x
rows = {}
for name in index:
    ok = subprocess.run([sys.executable, "-I", f"{R4}/validate_cat.py", name], capture_output=True, text=True)
    if ok.returncode != 0: raise SystemExit(f"{name} fails validation:\n{ok.stdout}")
    for line in open(f"{R4}/out/{name}.jsonl"):
        if line.strip():
            o = json.loads(line)
            if "done" not in o: rows[o["id"]] = o
assert set(rows) == {r["id"] for r in TL}, "reviewer output does not cover the Torah Law records"

# adjudications: {id: {field: value, ..., "why": "..."}}
DEC = json.load(open(f"{R4}/decisions.json")) if os.path.exists(f"{R4}/decisions.json") else {}
PAIR = {"Israel’s civil and land laws": "Civil", "Covenant-specific instructions": "Ceremonial", "Fulfilled": "Ceremonial",
        "Everlasting": "Moral", "Unchanged": "Moral"}
import re


def plain(text):
    """Reviewers called the Maimonides matches 'seeds'; say it plainly in the published notes."""
    text = re.sub(r"\bno seeds?\b", "no 613 match", text)
    text = re.sub(r"\b(?:the )?(all-[PN]) seeds?\b", r"the \1 613 matches", text)
    text = re.sub(r"\b([PN]) seeds\b", r"\1 613 matches", text)
    text = re.sub(r"\bseeds\b", "613 matches", text)
    text = re.sub(r"\bSeeds\b", "613 matches", text)
    text = re.sub(r"\bseed\b", "613 match", text)
    text = re.sub(r"\bSeed\b", "613 match", text)
    return text


out = []
for r in TL:
    o = dict(rows[r["id"]]); b = batches[r["id"]]
    adj = DEC.get(r["id"], {})
    for k, v in adj.items():
        if k != "why": o[k] = v
    seeds = [s.split(":")[0] for s in b["maimonides"]]
    reasons = []
    if o["confidence"] != "high": reasons.append(f"{o['confidence']} confidence")
    if seeds and all(s.startswith("P") for s in seeds) and o["form"] != "Positive": reasons.append("differs from the 613 match")
    if seeds and all(s.startswith("N") for s in seeds) and o["form"] != "Negative": reasons.append("differs from the 613 match")
    p = PAIR.get(r["classification"])
    if p and p not in (o["category"], o["secondary"]): reasons.append("differs from the site's classification")
    out.append({
        "id": r["id"], "reference": r["reference"], "title": r["title"],
        "form": o["form"], "form_mixed": o["mixed"], "form_basis": plain(o["form_basis"]),
        "category": o["category"], "second_category": o["secondary"], "ceremonial_area": o["area"],
        "confidence": o["confidence"], "review_reasons": reasons, "note": plain(o["note"]),
        "adjudicated": adj.get("why", ""), "maimonides_613": seeds,
    })
data = {
    "schema_version": 1,
    "description": "Editorial study labels for the Torah Law records: form (Jewish division into positive and negative commandments) and category (traditional Christian division into moral, ceremonial and civil law). The site's classification field is separate and unchanged.",
    "catalogue": "data/current/commands.json",
    "definitions": {
        "form": {
            "Positive": "Requires an action, a procedure, or a status or penalty to be applied (mitzvat aseh).",
            "Negative": "Forbids an action (mitzvat lo ta'aseh).",
            "Permission": "Allows an action without requiring it.",
        },
        "category": {
            "Moral": "A duty of love toward God or neighbour, stated as right or wrong in itself.",
            "Ceremonial": "A rite or holiness rule of Israel's worship under the old covenant.",
            "Civil": "A rule for Israel as a nation: its courts, penalties, government, land and economy.",
        },
        "ceremonial_area": {
            "Sacrifice and offerings": "Sacrifices, offerings, tithes, firstfruits and firstborn animals for the altar.",
            "Priesthood and sanctuary": "Priests, Levites, the high priest, the tabernacle and its holy things.",
            "Dietary laws": "Clean and unclean animals, blood, fat, carcasses and other food prohibitions.",
            "Ritual purity": "Impurity and cleansing: corpses, skin disease, discharges, childbirth.",
            "Festivals and holy days": "Sabbath rites, new moons, the annual feasts, and the sacred side of the sabbatical year and Jubilee.",
            "Signs, vows and dedications": "Circumcision, tassels, mixed kinds, vows, Nazirites, valuations and devoted things.",
        },
        "form_mixed": "True when the provision holds both a requirement and a prohibition; form gives its main clause.",
        "maimonides_613": "Maimonides' commandments (Sefer HaMitzvot numbering) matched to the record in the Torah Law count check, carried to current IDs.",
    },
    "records": out,
}
os.makedirs(f"{REPO}/data/current", exist_ok=True)
json.dump(data, open(f"{REPO}/data/current/torah-law-categories.json", "w"), ensure_ascii=False, indent=1)
c = collections.Counter
print("form", c(x["form"] for x in out), "mixed", sum(x["form_mixed"] for x in out))
print("category", c(x["category"] for x in out), "second", c(x["second_category"] for x in out))
print("areas", c(x["ceremonial_area"] for x in out))
print("review", sum(bool(x["review_reasons"]) for x in out), c(r for x in out for r in x["review_reasons"]))
