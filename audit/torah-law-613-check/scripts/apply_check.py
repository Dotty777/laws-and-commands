"""Apply the independent accuracy check (round3/check) to the 556-based files and write accuracy-check.json.

Idempotent: running it twice leaves the files as after the first run.
"""
import json, collections
W = "/home/claude/work"; A = f"{W}/audit/torah-laws"; C = f"{W}/round3/check"
key = {k["n"]: k for k in json.load(open(f"{C}/key.json"))}
out = [json.loads(l) for l in open(f"{C}/out.jsonl") if l.strip()]
verd = {o["n"]: o for o in out if "n" in o}
assert len(verd) == len(key) == 62

M = json.load(open(f"{A}/maimonides-613.json")); mby = {r["m"]: r for r in M}
F = json.load(open(f"{A}/findings.json")); CW = json.load(open(f"{A}/count-workings.json")); S = json.load(open(f"{A}/summary.json"))

# ---- 1. corrections to the 613 matching (cases 20, 23, 26)
FIX = {
    "N171": dict(status="torah_law", type="Law", records=["C0655"], labels=["Torah Law"], mislabel=False,
                 add="Accuracy check: C0655 (Leviticus 21:5, Torah Law) states the same mourning-baldness ban, which Maimonides counts once; corrected to torah_law."),
    "P53": dict(status="torah_law", type="Law", records=["C0230"], labels=["Torah Law"], mislabel=False,
                add="Accuracy check: C0230 (Exodus 23:14, 'Observe the three annual pilgrim feasts before God') already required the appearances; corrected to torah_law."),
    "N58": dict(records=["C1091"], labels=["Torah · Historical direction"],
                add="Accuracy check: S116 is a topical study and does not itemize; removed."),
}
for m, fx in FIX.items():
    r = mby[m]
    if fx["add"] in r["note"]: continue
    for k, v in fx.items():
        if k != "add": r[k] = v
    r["note"] = (r["note"].rstrip() + " " + fx["add"]).strip()
    for k in ("category", "why"):
        if m in ("N171", "P53"): r.pop(k, None)
json.dump(M, open(f"{A}/maimonides-613.json", "w"), ensure_ascii=False, indent=1)

F["gaps"] = [g for g in F["gaps"] if g["m"] not in ("N171", "P53")]
F["gap_counts"] = dict(collections.Counter(g["category"] for g in F["gaps"]))
json.dump(F, open(f"{A}/findings.json", "w"), ensure_ascii=False, indent=1)

tm = CW["tl_matched"]
if "N171" not in tm.get("C0655", []): tm.setdefault("C0655", []).append("N171")
if "P53" not in tm.get("C0230", []): tm.setdefault("C0230", []).append("P53")
json.dump(CW, open(f"{A}/count-workings.json", "w"), indent=1)

st = collections.Counter(r["status"] for r in M)
S["maimonides_613"]["status"] = dict(st)
S["maimonides_613"]["torah_law_records_itemizing_any"] = len(tm)
S["maimonides_613"]["torah_law_records_itemizing_none"] = 556 - len(tm)
S["not_stated"] = F["gap_counts"]
S["corrected_after_accuracy_check"] = "N171 and P53 moved to torah_law (C0655, C0230); S116 removed from N58."
json.dump(S, open(f"{A}/summary.json", "w"), ensure_ascii=False, indent=1)

# ---- 2. accuracy-check.json
by_kind = collections.defaultdict(collections.Counter)
for n, k in key.items(): by_kind[k["kind"]][verd[n]["verdict"]] += 1
flat = collections.Counter(verd[n]["verdict"] for n in key)
ACTION = {
    20: "Removed S116 from N58; its status (only a historical direction, C1091) stands.",
    23: "Corrected: N171 is itemized by C0655 at the 556 and now also by S126, which the revision made Torah Law.",
    26: "Corrected: P53 is itemized by C0230 at the 556; the revision has since added Exodus 23:17 to C0230.",
    44: "Regrouped C0800 and C0801 as 'same ban under two labels' beside C0418, which now holds both bans.",
    45: "Kept, with new evidence: the revision has since made the lamps (C0284), incense (C0337) and daily offering (C0333) Torah Law, so the priestly blessing is now the odd one out.",
    61: "Narrowed to C0129 and AUD-02-31-13. The revision keeps the holy-day command and the covenant sign apart on purpose, so this is left as a choice and not counted.",
}
cases = [{"n": n, "kind": key[n]["kind"], "ref": key[n]["ref"], "verdict": verd[n]["verdict"], "note": verd[n]["note"], "action": ACTION.get(n, "")}
         for n in sorted(key) if verd[n]["verdict"] != "correct"]
res = {"sample": len(key), "drawn_from": "40 of the 613 matches, 10 label findings and all 12 duplicate findings of the 556 check",
       "judged_against": "the 556-record catalogue (commit 3d53008)",
       "verdicts": dict(flat), "by_kind": {k: dict(v) for k, v in by_kind.items()}, "cases": cases,
       "summary": (f"{flat['correct']} were correct, {flat['partly']} partly right and {flat['wrong']} wrong. "
                   "The two wrong ones (N171, P53) were commandments the 556 check had treated as held only by topical studies; "
                   "C0655 and C0230 do state them. Both are corrected here, and the partly right ones are narrowed or re-evidenced.")}
json.dump(res, open(f"{A}/accuracy-check.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({"verdicts": res["verdicts"], "by_kind": res["by_kind"], "613_status_556": dict(st), "gaps": F["gap_counts"], "tl_matched": len(tm)}, ensure_ascii=False, indent=1))
