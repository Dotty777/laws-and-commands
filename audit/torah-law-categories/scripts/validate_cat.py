"""Validate a category-pass output file against its batch. Usage: python3 -I validate_cat.py C1"""
import json, sys
name = sys.argv[1]
W = "/home/claude/work/round4"
batch = json.load(open(f"{W}/batches/{name}.json"))
ids = [x["id"] for x in batch]; seeds = {x["id"]: x["maimonides"] for x in batch}; cls = {x["id"]: x["classification"] for x in batch}
FORMS = {"Positive", "Negative", "Permission"}; CATS = {"Moral", "Ceremonial", "Civil"}
AREAS = {"Sacrifice and offerings", "Priesthood and sanctuary", "Dietary laws", "Ritual purity", "Festivals and holy days", "Signs, vows and dedications"}
PAIR = {"Israel’s civil and land laws": "Civil", "Covenant-specific instructions": "Ceremonial", "Fulfilled": "Ceremonial", "Everlasting": "Moral", "Unchanged": "Moral"}
KEYS = {"id", "form", "mixed", "form_basis", "category", "secondary", "area", "confidence", "note"}
problems, rows, done = [], [], None
for n, line in enumerate(open(f"{W}/out/{name}.jsonl"), 1):
    if not line.strip(): continue
    try: o = json.loads(line)
    except Exception as e: problems.append(f"line {n}: not JSON ({e})"); continue
    if "done" in o: done = o; continue
    rows.append(o)
    i = o.get("id")
    if set(o) != KEYS: problems.append(f"{i}: keys {sorted(set(o) ^ KEYS)} differ")
    if o.get("form") not in FORMS: problems.append(f"{i}: form {o.get('form')!r}")
    if o.get("category") not in CATS: problems.append(f"{i}: category {o.get('category')!r}")
    if o.get("secondary") not in CATS | {""} or o.get("secondary") == o.get("category"): problems.append(f"{i}: secondary {o.get('secondary')!r}")
    cer = "Ceremonial" in (o.get("category"), o.get("secondary"))
    if cer and o.get("area") not in AREAS: problems.append(f"{i}: area required, got {o.get('area')!r}")
    if not cer and o.get("area"): problems.append(f"{i}: area must be empty when not Ceremonial")
    if o.get("confidence") not in {"high", "medium", "low"}: problems.append(f"{i}: confidence {o.get('confidence')!r}")
    if not isinstance(o.get("mixed"), bool): problems.append(f"{i}: mixed must be true/false")
    if not str(o.get("form_basis", "")).strip(): problems.append(f"{i}: form_basis empty")
    need = o.get("confidence") != "high" or o.get("mixed") is True
    s = seeds.get(i, [])
    if s and all(x.startswith("P") for x in s) and o.get("form") != "Positive": need = True
    if s and all(x.startswith("N") for x in s) and o.get("form") != "Negative": need = True
    p = PAIR.get(cls.get(i))
    if p and p not in (o.get("category"), o.get("secondary")): need = True
    if need and not str(o.get("note", "")).strip(): problems.append(f"{i}: note required (confidence, mixed, seed disagreement or classification pairing)")
    if len(str(o.get("note", "")).split()) > 40: problems.append(f"{i}: note longer than 40 words")
got = [o.get("id") for o in rows]
if got != ids:
    miss = [i for i in ids if i not in got]; extra = [i for i in got if i not in ids]
    dup = sorted({i for i in got if got.count(i) > 1})
    problems.append(f"ids differ from batch order: missing {miss[:10]}, extra {extra[:10]}, duplicates {dup[:10]}")
if not done or done.get("n") != len(ids): problems.append(f"final done line missing or wrong (expected n={len(ids)})")
print(f"{name}: {len(rows)} rows, {len(problems)} problems")
for p in problems[:60]: print(" -", p)
sys.exit(1 if problems else 0)
