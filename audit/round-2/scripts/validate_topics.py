"""python3 -I /home/claude/work/round2/topics/validate_topics.py T1"""
import sys, json
b = sys.argv[1]; D = "/home/claude/work/round2/topics/"
ids = json.load(open(D + b + ".ids.json"))
TOP = set(json.load(open("/home/claude/work/audit/topics50.json")))
errs, seen, done = [], set(), False
for ln, line in enumerate(open(D + b + ".out.jsonl"), 1):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except Exception as e: errs.append(f"line {ln}: not JSON {e}"); continue
    if o.get("done"): done = True; continue
    if o.get("id") not in ids: errs.append(f"line {ln}: id {o.get('id')!r} not in batch")
    if o.get("id") in seen: errs.append(f"line {ln}: duplicate id {o.get('id')}")
    seen.add(o.get("id"))
    if o.get("topic") not in TOP: errs.append(f"line {ln}: topic {o.get('topic')!r} is not one of the 50 (copy it exactly)")
    if o.get("confidence") not in ("high", "medium", "low"): errs.append(f"line {ln}: confidence")
missing = [i for i in ids if i not in seen]
if missing: errs.append(f"{len(missing)} records have no topic, e.g. {missing[:5]}")
if not done: errs.append("no final done line")
print(f"{b}: {len(seen)} records, {len(errs)} problems"); [print("  ", e) for e in errs[:40]]
