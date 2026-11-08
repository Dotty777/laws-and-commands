"""Validate /home/claude/work/review/merge.jsonl (reconciliation ops)."""
import json
rows = {o["key"]: o for o in json.load(open("/home/claude/work/review/all_findings.json"))}
ids = {r["id"] for r in json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))}
errs, n, used = [], 0, {}
for ln, line in enumerate(open("/home/claude/work/review/merge.jsonl"), 1):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except Exception as e: errs.append(f"line {ln}: not JSON {e}"); continue
    n += 1; op = o.get("op")
    keys = []
    if op == "absorb": keys = [o.get("primary")] + list(o.get("absorb", []))
    elif op == "widen": keys = [o.get("keep")] + list(o.get("drop", []))
    elif op in ("to_parallel", "drop"): keys = [o.get("key")]
    else: errs.append(f"line {ln}: unknown op {op!r}"); continue
    for k in keys:
        if k not in rows: errs.append(f"line {ln}: key {k!r} not a finding")
        elif k in used and op != "absorb": errs.append(f"line {ln}: key {k} already used on line {used[k]}")
        else: used.setdefault(k, ln)
    if op == "to_parallel" and o.get("existing_id") not in ids: errs.append(f"line {ln}: existing_id {o.get('existing_id')!r} not in catalogue")
    if op == "widen" and not o.get("reference"): errs.append(f"line {ln}: widen needs the final reference")
    if not o.get("why"): errs.append(f"line {ln}: missing why")
print(f"{n} ops, {len(errs)} problems"); [print("  ", e) for e in errs[:40]]
