import sys, json
b = sys.argv[1]
ix = json.load(open("/home/claude/work/round3/index.json"))[b]
LAB = {"Torah Law", "Mosaic Instruction", "Mosaic Command", "Mosaic Wisdom", "Mosaic Commission", "No Mosaic type"}
recs = {r["id"] for r in json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))}
errs, seen, done = [], set(), False
for ln, line in enumerate(open(f"/home/claude/work/round3/out/{b}.jsonl"), 1):
    line = line.strip()
    if not line: continue
    try: o = json.loads(line)
    except Exception: errs.append(f"line {ln}: not JSON"); continue
    if o.get("done"): done = True; continue
    i = o.get("id")
    if i not in ix: errs.append(f"line {ln}: id {i!r} not in batch")
    if i in seen: errs.append(f"line {ln}: {i} twice")
    seen.add(i)
    if o.get("confidence") not in ("high", "medium", "low"): errs.append(f"line {ln}: confidence")
    if not o.get("note"): errs.append(f"line {ln}: note missing")
    if b == "D1":
        if o.get("verdict") not in ("duplicate", "overlap", "split"): errs.append(f"line {ln}: verdict")
    if b == "D2":
        if o.get("verdict") not in ("restatement", "related", "distinct"): errs.append(f"line {ln}: verdict")
    if b in ("D1", "D2"):
        if o.get("keep") != "both" and o.get("keep") not in recs: errs.append(f"line {ln}: keep must be a record id or both")
        if not isinstance(o.get("label_conflict"), bool): errs.append(f"line {ln}: label_conflict must be true/false")
    if b == "L1":
        if o.get("verdict") not in ("keep", "relabel"): errs.append(f"line {ln}: verdict")
        if o.get("suggest") not in LAB: errs.append(f"line {ln}: suggest {o.get('suggest')!r}")
        if not isinstance(o.get("is_law"), bool): errs.append(f"line {ln}: is_law must be true/false")
miss = [i for i in ix if i not in seen]
if miss: errs.append(f"{len(miss)} undecided, e.g. {miss[:5]}")
if not done: errs.append("no done line")
print(f"{b}: {len(seen)} decided, {len(errs)} problems"); [print("  ", e) for e in errs[:40]]
