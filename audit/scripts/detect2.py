"""Second-pass signals that fix the main recall gaps of detect.py.

LEXIMP  clause-initial base-form verb from an imperative lexicon (catches quoted
        speech after "said," that the parser attaches to the speech verb)
REQ     requests: let me / give me / please / I pray you / grant me / I beg you
SHALL2  any deontic shall/must/ought/"is to be" not limited to first person
VOCIMP  "You who ..., <verb>" / "O ..., <verb>" / "Son, <verb>" patterns
Merges into signals.json as signals2.json.
"""
import sys, json, re, collections
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible

B = Bible()
S = {int(k): v for k, v in json.load(open("/home/claude/work/signals.json")).items()}

# imperative lexicon: lemmas the parser already found as imperatives (>=3 times) + a manual core list
cnt = collections.Counter(l for v in S.values() for l in v["imp"])
LEX = {l for l, c in cnt.items() if c >= 3 and l.isalpha() and len(l) > 1}
LEX |= set("""go come take bring give make let hear listen keep love fear serve praise sing shout remember return
turn seek wash put set stand arise rise sit eat drink write speak say tell call cry ask send depart flee leave
receive honor honour obey follow watch pray bless curse kill slay strike smite burn break build gather count
cut circumcise anoint consecrate sanctify purify cleanse redeem buy sell lend pay repay restore judge rebuke
reprove forgive pardon repent believe trust wait hope rejoice exult extol magnify worship bow kneel fast weep
mourn lament wail howl gird prepare guard observe do walk run hasten hurry stop cease beware consider know
learn teach instruct proclaim preach declare announce testify bear carry lift raise lay throw cast hide open
shut close seal show behave fight destroy devour plunder spare save deliver help visit look see behold mark
note sanctify dedicate offer sacrifice slaughter sprinkle pour fill empty measure weigh number appoint choose
anoint ordain commission charge command forbid permit allow suffer endure abide remain stay dwell inherit
possess drive hold grasp cling cleave hate despise abhor flee resist submit yield humble exalt glorify thank
confess acknowledge greet salute welcome entertain feed clothe heal cure raise loose bind tie untie free
release circumcise wake awake arise sleep rest work labor labour sow reap plant water tend shepherd""".split())
LEX -= {"behold", "lo", "see", "look"}          # attention particles
NOUNY_NEXT = {"is", "was", "are", "were", "of", "’s", "'s", "and", "has", "had", "be", "will", "shall"}

LEAD = r"(?:(?:and|but|now|therefore|so|then|also|again|rather|instead|thus|yes|indeed|only|surely|first|now therefore|"\
       r"but now|and now|o \w+(?: \w+)?|my son|son|children|my children|brothers|beloved|sons of \w+|daughter of \w+|"\
       r"you \w+ of \w+|israel|jerusalem|zion|lord)\s*,?\s+)*"
re_clause = re.compile(r"(?:^|[“‘\"(;:.!?]\s*|,\s*(?=(?:and|but|then|or)\s))" + LEAD + r"([A-Za-z]+)(?:\s+(\S+)|(?=[!.,;:”’]))", re.I)
re_reported = re.compile(r"\b(commanded|commands|ordered|orders|charged|instructed|directed|decreed|enjoined|bade|"
                         r"urged|told|warned|forbade|forbids|appointed|ordained|established|determined|resolved|"
                         r"summoned|sent word|gave orders|gave instructions|gave a command|issued)\b\s+(that|them|him|"
                         r"her|us|you|me|the|all|every|his|their|each|to|those|these|Joab|Moses|Aaron|Israel)\b", re.I)
re_req = re.compile(r"\b(let me|let us|give me|grant me|please|I pray you|I pray thee|I beg you|I beseech you|"
                    r"I urge you|I exhort you|I appeal to you|I implore you|we beg you|we ask you|I ask you)\b", re.I)
re_shall2 = re.compile(r"\b(shall|must|ought|is to be|are to be|is required|are required)\b", re.I)
re_firstonly = re.compile(r"\b(I|we) (shall|must|ought)\b", re.I)
re_voc = re.compile(r"(?:^|[“‘])\s*(?:You|O|Ye) (?:who|that|whom)?[^,]{0,80},\s+([a-z]+)\b|(?:^|[“‘])(?:My )?[Ss]on,\s+([a-z]+)\b")


def leximp(text):
    hits = []
    for m in re_clause.finditer(text):
        w, nxt = m.group(1).lower(), (m.group(2) or "").lower().strip(",.;:!?”’")
        if w in LEX and nxt not in NOUNY_NEXT:
            hits.append(w)
    return hits


out = {}
c = collections.Counter()
for i, v in enumerate(B.verses):
    t = v["text"]
    sig = set(S[i]["sig"])
    li = leximp(t)
    if li:
        sig.add("LEXIMP")
    if re_req.search(t):
        sig.add("REQ")
    if re_reported.search(t):
        sig.add("REPORTED")
    sh = re_shall2.findall(t)
    if sh and not (re_firstonly.search(t) and len(sh) == len(re_firstonly.findall(t))):
        sig.add("SHALL2")
    m = re_voc.search(t)
    if m:
        w = (m.group(1) or m.group(2) or "").lower()
        if w in LEX:
            sig.add("VOCIMP")
    out[i] = {"sig": sorted(sig), "imp": S[i]["imp"], "lex": li}
    for s in sig:
        c[s] += 1
json.dump(out, open("/home/claude/work/signals2.json", "w"))
print(c)
