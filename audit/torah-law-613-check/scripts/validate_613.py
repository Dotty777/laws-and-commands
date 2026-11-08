"""python3 -I /home/claude/work/round3/validate_613.py M1"""
import sys, json
b = sys.argv[1]
ix = json.load(open("/home/claude/work/round3/index.json"))[b]
recs = {r["id"]: r for r in json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))}
ST = {"torah_law", "other_mosaic", "other_record", "broad_only", "partial", "missing"}
TY = {"Law", "Instruction", "Command", "Wisdom", "Commission", "none"}
errs, seen, done = [], set(), False
for ln, line in enumerate(open(f"/home/claude/work/round3/out/{b}.jsonl"), 1):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except Exception as e: errs.append(f"line {ln}: not JSON"); continue
    if o.get("done"): done = True; continue
    m = o.get("m")
    if m not in ix: errs.append(f"line {ln}: {m!r} not in batch")
    if m in seen: errs.append(f"line {ln}: {m} twice")
    seen.add(m)
    if not o.get("statement") or len(o["statement"].split()) > 16: errs.append(f"line {ln}: statement missing or too long")
    rs = o.get("records")
    if not isinstance(rs, list): errs.append(f"line {ln}: records must be a list"); rs = []
    for rid in rs:
        if rid not in recs: errs.append(f"line {ln}: record {rid!r} not in the catalogue")
    st, ty = o.get("status"), o.get("type")
    if st not in ST: errs.append(f"line {ln}: status {st!r}")
    if ty not in TY: errs.append(f"line {ln}: type {ty!r}")
    if not isinstance(o.get("mislabel"), bool): errs.append(f"line {ln}: mislabel must be true/false")
    if o.get("confidence") not in ("high", "medium", "low"): errs.append(f"line {ln}: confidence")
    if "note" not in o: errs.append(f"line {ln}: note missing")
    mts = {recs[r]["mosaic_type"] for r in rs if r in recs}
    if st == "torah_law" and "Law" not in mts: errs.append(f"line {ln}: torah_law but no listed record is a Torah Law record")
    if st == "other_mosaic" and (not rs or "Law" in mts or not (mts - {""})): errs.append(f"line {ln}: other_mosaic needs Mosaic records and none of type Law")
    if st == "other_record" and (not rs or (mts - {""})): errs.append(f"line {ln}: other_record needs records without a Mosaic type")
    if st in ("broad_only", "partial") and not rs: errs.append(f"line {ln}: {st} needs the record that holds the verse")
    if st == "missing" and rs: errs.append(f"line {ln}: missing but records listed")
miss = [m for m in ix if m not in seen]
if miss: errs.append(f"{len(miss)} items undecided, e.g. {miss[:5]}")
if not done: errs.append("no done line")
print(f"{b}: {len(seen)} decided, {len(errs)} problems"); [print("  ", e) for e in errs[:40]]
