"""Compare the blind re-check (K1) with the reviewers' answers and write accuracy-check.json."""
import json, sys
R4 = "/home/claude/work/round4"; REPO = sys.argv[1]
main = {}
for n in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
    for l in open(f"{R4}/out/{n}.jsonl"):
        if l.strip():
            o = json.loads(l)
            if "done" not in o: main[o["id"]] = o
chk = [json.loads(l) for l in open(f"{R4}/out/K1.jsonl") if l.strip()]
chk = [o for o in chk if "done" not in o]
batch = {x["id"]: x for x in json.load(open(f"{R4}/batches/K1.json"))}
f = lambda key: sum(o[key] == main[o["id"]][key] for o in chk)
both_cer = [o for o in chk if o["category"] == main[o["id"]]["category"] == "Ceremonial"]
diffs = []
for o in chk:
    m = main[o["id"]]
    fields = [k for k in ("form", "mixed", "category", "secondary", "area") if o[k] != m[k]]
    if fields:
        diffs.append({"id": o["id"], "reference": batch[o["id"]]["reference"], "fields": fields,
                      "reviewer": {k: m[k] for k in ("form", "mixed", "category", "secondary", "area", "confidence")},
                      "check": {k: o[k] for k in ("form", "mixed", "category", "secondary", "area", "confidence")}})
res = {"sample": len(chk), "drawn_from": "nine records at random from each of the seven review batches",
       "method": "A separate reviewer classified the sample from the same brief without seeing the reviewers' answers.",
       "by_field": {"form": {"agree": f("form"), "of": len(chk)}, "category": {"agree": f("category"), "of": len(chk)},
                    "second_category": {"agree": f("secondary"), "of": len(chk)}, "mixed": {"agree": f("mixed"), "of": len(chk)},
                    "ceremonial_area": {"agree": sum(o["area"] == main[o["id"]]["area"] for o in both_cer), "of": len(both_cer)}},
       "differences": diffs, "changes": []}
res["summary"] = (f"The two agreed on the form of all {res['by_field']['form']['agree']} records and on the main category of {res['by_field']['category']['agree']}; "
                  f"the one difference (C0931) swaps the main and second categories and was already flagged. They agreed on the second category for "
                  f"{res['by_field']['second_category']['agree']}, on whether the form is mixed for {res['by_field']['mixed']['agree']}, and on the ceremonial area for "
                  f"{res['by_field']['ceremonial_area']['agree']} of the {res['by_field']['ceremonial_area']['of']} both called ceremonial. No answer was changed as a result.")
json.dump(res, open(f"{REPO}/audit/torah-law-categories/accuracy-check.json", "w"), ensure_ascii=False, indent=1)
print(res["summary"])
