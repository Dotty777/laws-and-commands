"""Cross-batch consistency checks on the category pass. Prints outliers to adjudicate."""
import json, re, collections
R4 = "/home/claude/work/round4"
index = json.load(open(f"{R4}/index.json"))
batch_of = {i: n for n, ids in index.items() for i in ids}
rec, out = {}, {}
for n in index:
    for x in json.load(open(f"{R4}/batches/{n}.json")): rec[x["id"]] = x
    for line in open(f"{R4}/out/{n}.jsonl"):
        if line.strip():
            o = json.loads(line)
            if "done" not in o: out[o["id"]] = o


def show(title, ids, want=None):
    print(f"\n== {title}: {len(ids)}")
    dist = collections.Counter((out[i]["form"], out[i]["category"] + ("/" + out[i]["secondary"] if out[i]["secondary"] else ""), out[i]["area"]) for i in ids)
    for k, v in dist.most_common(): print("   ", v, k)
    if want:
        bad = [i for i in ids if not want(out[i])]
        for i in bad:
            o = out[i]; x = rec[i]
            print(f"   ! {i} [{batch_of[i]}] {x['reference']} | {x['title'][:80]} | {o['form']}{' mixed' if o['mixed'] else ''} · {o['category']}{'/' + o['secondary'] if o['secondary'] else ''} · {o['area']} | {o['note'][:120]}")


T = lambda i: rec[i]["title"].lower()
pen = [i for i in rec if re.search(r"\b(execute|put to death|be put to death|stone|cut off|burn|repay|restitution|pay .* fine|flog|lashes)\b", T(i))]
show("Penalty-worded titles (expect Civil, Positive; Moral second if the act is a moral wrong)", pen, lambda o: o["category"] == "Civil" and o["form"] == "Positive")
eat = [i for i in rec if re.search(r"^do not eat|\bnot eat\b", T(i))]
show("'Do not eat' titles (expect Ceremonial: Dietary laws, Negative)", eat, lambda o: o["category"] == "Ceremonial" and o["area"] == "Dietary laws")
may = [i for i in rec if re.search(r"\bmay\b", T(i)) and not re.search(r"\bmay not\b", T(i))]
show("'may' titles (expect Permission)", may, lambda o: o["form"] == "Permission")
perm = [i for i in rec if out[i]["form"] == "Permission"]
show("All Permission", perm)
dec = [i for i in rec if re.match(r"(Exodus 20:([3-9]|1[0-7])|Deuteronomy 5:([7-9]|1\d|2[01]))", rec[i]["reference"])]
show("Ten Commandments records (expect Moral)", dec, lambda o: o["category"] == "Moral")
sab = [i for i in rec if "sabbath" in T(i) and "year" not in T(i)]
show("Sabbath (weekly) titles", sab)
neg_title_pos = [i for i in rec if re.match(r"(do not|no |never|none)", T(i)) and out[i]["form"] != "Negative"]
show("'Do not' titles not Negative", neg_title_pos, lambda o: False)
glean = [i for i in rec if re.search(r"glean|corner|forgotten sheaf|poor", T(i))]
show("Poor and gleaning titles (expect Civil + Moral)", glean, lambda o: o["category"] == "Civil" and o["secondary"] == "Moral")
occ = [i for i in rec if re.search(r"divin|sorcer|medium|necromanc|spirit|omen|charm", T(i))]
show("Occult titles (expect Moral)", occ, lambda o: o["category"] == "Moral")
print("\nper-batch category shares:")
for n, ids in index.items():
    c = collections.Counter(out[i]["category"] for i in ids); f = collections.Counter(out[i]["form"] for i in ids)
    print(" ", n, dict(c), dict(f), "mixed", sum(out[i]["mixed"] for i in ids), "non-high", sum(out[i]["confidence"] != "high" for i in ids))
