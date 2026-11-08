"""Validate a reviewer output file: python3 -I /home/claude/work/validate_out.py B01"""
import sys, json
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible

TOPICS = {t.strip() for t in """Clean and Unclean, and the Tradition of the Elders|Covenant signs, vows and dedications|Creation, personal commissions and Israel’s journeys|Cross-Scripture studies|Do This in Remembrance of Me|Done to Be Seen|Faith, repentance and allegiance|Family, marriage and household|Follow Me|Food, ritual purity and cleansing|Go and Make Disciples|Hear and Keep|Historical commissions, journeys and public life|Holiness, truthfulness and sexual conduct|Human life, injury and care for neighbours|In Secret|Judging and Forgiving|Justice, testimony, government and war|Justice, truth and protection|Knowing, loving and obeying God|Land, harvests and provision for the poor|Major Teachings: The Word of Christ Handed On|Marriage|Marriage, family and care for parents|Mercy, neighbors and the vulnerable|Minor Teachings: The Scriptures Read in Christ|Offerings, sacrifice and atonement|Pray in This Way|Property, honest trade and service|Repent and Believe|Sabbath, appointed times and remembrance|Sanctuary, priesthood and ministry|Serving|Shepherds of the Flock|Supplementary instructions|Temple, Offerings and Tithes|The Commandments and the One Thing Lacking|The Law and the Prophets|The Little Ones and the Poor|The New Commandment|The Sabbath|The Sending|Treasure|Trust|Wages, lending, pledges and inheritance|Watchfulness|Wisdom, speech and conduct|Work, possessions and stewardship|Worship, prayer and holy things|You Heard That It Was Said, but I Tell You""".split("|")}
TYPES = {"Law", "Command", "Commission", "Instruction", "Wisdom"}
ORIG = {"Heavenly (God-given)", "Earthly (Man-made)", "Mixed origins"}
AUD = {"General", "Personal"}
VERD = {"new", "extend", "parallel"}
CONF = {"high", "medium", "low"}

batch = sys.argv[1]
index = {x["batch"]: x for x in json.load(open("/home/claude/work/review/index.json"))}
pids = set(index[batch]["pids"])
ids = {r["id"] for r in json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))}
B = Bible()
errs, n, done = [], 0, False
for ln, line in enumerate(open(f"/home/claude/work/review/out/{batch}.jsonl"), 1):
    line = line.strip()
    if not line:
        continue
    try:
        o = json.loads(line)
    except Exception as e:
        errs.append(f"line {ln}: not JSON ({e})"); continue
    if o.get("done"):
        done = True; continue
    n += 1
    for k in ("pid", "verdict", "reference", "record_type", "title", "speaker", "recipient", "origin", "audience", "topic", "confidence", "existing_id", "note"):
        if k not in o:
            errs.append(f"line {ln}: missing field {k}")
    if o.get("pid") not in pids: errs.append(f"line {ln}: pid {o.get('pid')} not in this batch")
    if o.get("verdict") not in VERD: errs.append(f"line {ln}: verdict {o.get('verdict')!r}")
    if o.get("record_type") not in TYPES: errs.append(f"line {ln}: record_type {o.get('record_type')!r}")
    if o.get("origin") not in ORIG: errs.append(f"line {ln}: origin {o.get('origin')!r}")
    if o.get("audience") not in AUD: errs.append(f"line {ln}: audience {o.get('audience')!r}")
    if o.get("topic") not in TOPICS: errs.append(f"line {ln}: topic {o.get('topic')!r} is not one of the 50")
    if o.get("confidence") not in CONF: errs.append(f"line {ln}: confidence {o.get('confidence')!r}")
    if o.get("verdict") in ("extend", "parallel") and o.get("existing_id") not in ids:
        errs.append(f"line {ln}: existing_id {o.get('existing_id')!r} not a catalogue id")
    idx, prob = B.expand(o.get("reference", ""))
    if not idx or prob: errs.append(f"line {ln}: reference {o.get('reference')!r} does not resolve {prob}")
    if len(o.get("title", "").split()) > 14: errs.append(f"line {ln}: title longer than 12 words")
if not done: errs.append("no final summary line with \"done\": true")
print(f"{batch}: {n} findings, {len(errs)} problems")
for e in errs[:60]: print("  ", e)
