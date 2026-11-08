import json,sys,re,collections,glob
sys.path.insert(0,"/home/claude/work")
from audit_lib import Bible, coverage
import cov2
B=Bible()
recs=json.load(open("/home/claude/repos/laws-and-commands/data/current/commands.json")); byid={r["id"]:r for r in recs}
D=cov2.directive_set(); C=cov2.covered(B,recs); U={i for i in D if i not in C}
cov,prim,_=coverage(B,recs)
r2=set()
for f in sorted(glob.glob("/home/claude/work/round2/batches/R[1-7]*.md")):
    for line in open(f):
        if line.strip().startswith("[ctx]"): continue
        m=re.match(r"\s{3}((?:[1-4] )?[A-Z][A-Za-z ]+?) (\d+):(\d+[a-z]*) ", line)
        if m:
            idx,p=B.expand(f"{m.group(1)} {m.group(2)}:{m.group(3)}"); r2.update(idx)
af={f["key"]:f for f in json.load(open("/home/claude/work/review/all_findings.json"))}
ff=json.load(open("/home/claude/work/audit/findings_final.json"))
final={x.get("key"):k for k in ("new","extend","parallel") for x in ff[k]}
finalobj={x.get("key"):x for k in ("new","extend","parallel") for x in ff[k]}
removed={x["key"]:x["why"] for x in ff["removed"]}
fv=collections.defaultdict(list)
for k,f in af.items():
    for ref in [f.get("reference","")]+([f["additional"]] if f.get("additional") else []):
        if not ref: continue
        idx,p=B.expand(ref)
        for i in idx: fv[i].append(k)
def fate(k):
    f=af[k]
    if k in final: return "final:"+final[k]
    if k in removed: return "removed:"+removed[k].split()[0]
    return "not-recommended:"+str(f.get("confidence"))
if __name__=="__main__":
    cats=collections.Counter(); ex=collections.defaultdict(list)
    for i in U:
        if i in r2: cats["in round-2 review"]+=1; continue
        if i not in fv: cats["read in round 1, no finding"]+=1; continue
        fs=sorted({fate(k) for k in fv[i]})
        key=" + ".join(fs)
        if B.verses[i]["book"] in cov2.LAW and i in cov: key+=" [Law long passage]"
        cats[key]+=1; ex[key].append(f'{B.verses[i]["book"]} {B.verses[i]["ch"]}:{B.verses[i]["v"]}')
    for k,v in cats.most_common(): print(v,k,ex[k][:4])
