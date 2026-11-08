"""python3 -I /home/claude/work/round2/validate_r2.py R1"""
import sys, json
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
b = sys.argv[1]
ix = json.load(open("/home/claude/work/round2/index.json"))[b]
ids = {r["id"] for r in json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))}
TOP = set(json.load(open("/home/claude/work/audit/topics50.json")))
B = Bible(); errs, seen, done = [], set(), False
for ln, line in enumerate(open(f"/home/claude/work/round2/out/{b}.jsonl"), 1):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except Exception as e: errs.append(f"line {ln}: not JSON {e}"); continue
    if o.get("done"): done = True; continue
    it, d = o.get("item"), o.get("decision")
    if it not in ix: errs.append(f"line {ln}: item {it!r} not in batch")
    seen.add(it)
    if d not in ("record_new", "record_extend", "record_parallel", "no_record"): errs.append(f"line {ln}: decision {d!r}")
    if o.get("confidence") not in ("high", "medium", "low"): errs.append(f"line {ln}: confidence")
    if not o.get("reason"): errs.append(f"line {ln}: reason missing")
    if d in ("record_new", "record_extend", "record_parallel"):
        idx, p = B.expand(o.get("reference", ""))
        if not idx or p: errs.append(f"line {ln}: reference {o.get('reference')!r} does not resolve")
    if d == "record_new":
        for k in ("record_type", "title", "speaker", "recipient", "origin", "audience", "topic"):
            if not o.get(k): errs.append(f"line {ln}: {k} missing")
        if o.get("record_type") not in ("Law", "Command", "Commission", "Instruction", "Wisdom"): errs.append(f"line {ln}: record_type")
        if o.get("origin") not in ("Heavenly (God-given)", "Earthly (Man-made)", "Mixed origins"): errs.append(f"line {ln}: origin")
        if o.get("audience") not in ("General", "Personal"): errs.append(f"line {ln}: audience")
        if o.get("topic") not in TOP: errs.append(f"line {ln}: topic {o.get('topic')!r} not one of the 50")
        if len(o.get("title", "").split()) > 14: errs.append(f"line {ln}: title too long")
    if d in ("record_extend", "record_parallel") and o.get("existing_id") not in ids: errs.append(f"line {ln}: existing_id {o.get('existing_id')!r} not in the current catalogue")
    if d == "record_parallel" and not o.get("context"): errs.append(f"line {ln}: context missing")
missing = [i for i in ix if i not in seen]
if missing: errs.append(f"{len(missing)} batch items have no decision, e.g. {missing[:5]}")
if not done: errs.append("no final done line")
print(f"{b}: {len(seen)} items decided, {len(errs)} problems"); [print("  ", e) for e in errs[:40]]
