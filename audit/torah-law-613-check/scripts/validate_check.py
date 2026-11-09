import json
key = json.load(open("/home/claude/work/round3/check/key.json")); ns = {k["n"] for k in key}
errs, seen = [], set()
for ln, l in enumerate(open("/home/claude/work/round3/check/out.jsonl"), 1):
    if not l.strip(): continue
    try: o = json.loads(l)
    except Exception: errs.append(f"line {ln}: not JSON"); continue
    if o.get("done"): continue
    if o.get("n") not in ns: errs.append(f"line {ln}: n")
    if o.get("verdict") not in ("correct", "partly", "wrong"): errs.append(f"line {ln}: verdict")
    if not o.get("note"): errs.append(f"line {ln}: note")
    seen.add(o.get("n"))
if ns - seen: errs.append(f"missing {sorted(ns - seen)[:10]}")
print(len(seen), "cases,", len(errs), "problems"); [print(" ", e) for e in errs[:20]]
