"""Coverage of screened directive verses, with the Law-book itemization rule (entries of <= 8 verses)."""
import json, sys, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
STRONG = {"IMP","JUSS","PROH","SHALL","CASU","COMM","LEXIMP","REQ","SHALL2","VOCIMP","REPORTED"}
LAW = {"Genesis","Exodus","Leviticus","Numbers","Deuteronomy"}
def directive_set():
    s2 = json.load(open("/home/claude/work/signals2.json"))
    return {int(k) for k, v in s2.items() if STRONG & set(v["sig"])}
def covered(B, recs):
    """entries: (record id, reference). Returns set of covered verse indices under the rule."""
    out = collections.defaultdict(set)
    for r in recs:
        refs = [r["reference"]] + [(a.get("reference") if isinstance(a, dict) else str(a)) for a in (r.get("additional_scripture") or [])]
        for ref in refs:
            idx, p = B.expand(ref)
            if not idx: continue
            small = len(idx) <= 8
            for i in idx:
                if B.verses[i]["book"] in LAW and not small: continue
                out[i].add(r["id"])
    return out
def stats(B, recs, D=None):
    D = D or directive_set(); c = covered(B, recs)
    hit = [i for i in D if i in c]
    by = collections.defaultdict(lambda: [0, 0])
    for i in D:
        bk = B.verses[i]["book"]; by[bk][0] += 1; by[bk][1] += (i in c)
    return len(D), len(hit), by, c
if __name__ == "__main__":
    B = Bible(); recs = json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json"))
    n, h, by, c = stats(B, recs)
    print(n, h, round(100*h/n, 1))
