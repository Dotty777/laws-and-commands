"""Tag every verse with directive-language signals.

Signals (a verse may carry several):
  IMP    imperative clause (base-form verb heading a clause with no subject), incl. "do not X"
  JUSS   jussive/hortatory "let ..." (let us / let him / let your heart ...)
  PROH   prohibition: "do not", "you shall not", "no one shall", "let no one", "never"
  SHALL  deontic modal with a person subject: "you shall", "he shall", "must", "ought", "is to be"
  CASU   casuistic law opening: "if a man/anyone/someone ...", "when a man ...", "whoever ... shall"
  LAWNOUN statute vocabulary: "statute", "ordinance", "it is lawful/unlawful", "commanded"
  COMM   commission language: send/appoint/anoint/ordain/set apart/make you/be my witnesses/go and tell
  WISD   wisdom forms: better..than, blessed/happy is, woe to, "son," vocative, the fear of the Lord,
         gnomic "he who/whoever/the one who ... " + present, wise/fool/righteous/wicked/lazy contrasts
Output: signals.json  {idx: {"sig": [...], "imp_verbs": [...]}}
"""
import sys, json, re
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
import spacy

nlp = spacy.load("en_core_web_sm", disable=["ner"])
B = Bible()

VOCATIVE_WORDS = {"son", "sons", "my son", "children", "brothers", "brethren", "sisters", "beloved", "israel",
                  "jacob", "judah", "jerusalem", "zion", "lord", "o", "man", "woman", "daughter", "daughters",
                  "friends", "fathers", "young", "elders", "kings", "rulers", "servants", "wives", "husbands",
                  "masters", "slaves", "people", "heavens", "earth", "mountains", "timothy", "titus", "peter",
                  "simon", "martha", "mary", "teacher", "rabbi"}
DISCOURSE = {"behold", "lo"}
PRAYER_TO_GOD = re.compile(r"\b(O Lord|O God|Lord,|my God|O my God|You, O Lord|O Lord of hosts)\b")

re_proh = re.compile(r"\b(do not|don[’']t|you shall not|you must not|shall not|neither shall you|nor shall you|"
                     r"no one shall|let no(?: one|body)?\b|let not|never\b|you may not|must not|is not lawful|"
                     r"you shall in no wise|shall in no wise)", re.I)
re_shall = re.compile(r"\b(you|ye|he|she|they|it|one|everyone|whoever|the man|the woman|the priest|the priests|"
                      r"each|every man|no one|your \w+|his \w+|the \w+)\s+(shall|must|ought to|are to|is to be|"
                      r"are to be|should)\b", re.I)
re_casu = re.compile(r"^(and |but |now )?(if|when|whenever) (a |any |the )?(man|woman|person|soul|anyone|someone|"
                     r"one|ox|priest|brother|stranger|foreigner|resident|slave|servant|your brother|you)\b|"
                     r"\bwhoever\b.*\b(shall|must)\b|\bshall surely be put to death\b|\bshall be put to death\b|"
                     r"\bshall be cut off\b", re.I)
re_lawnoun = re.compile(r"\b(statute|statutes|ordinance|ordinances|judgments and|commandment|commandments|"
                        r"it is lawful|is not lawful|unlawful|law of|perpetual statute|everlasting statute|"
                        r"as the Lord commanded|commanded you|I command you|I charge you|charge you)\b", re.I)
re_comm = re.compile(r"\b(I (?:will |am |have )?(?:send|sent|sending) you|I am sending|I have appointed|I appoint|"
                     r"I have made you|I will make you|I have set you|I have chosen you|anoint him|anoint you|anointed you|"
                     r"you shall anoint|set apart|separate for me|ordain|ordained|appointed (?:you|them|him)|"
                     r"be my witnesses|make disciples|go and (?:tell|say|speak|proclaim|preach|prophesy|show)|"
                     r"go,? (?:speak|say|tell|prophesy|proclaim|preach)|arise,? go|go to (?:Pharaoh|Nineveh|the people)|"
                     r"preach the|proclaim the|watchman|lay (?:your|his) hands? on|laid (?:their|his) hands on|"
                     r"go into all the world|feed my (?:lambs|sheep)|tend my sheep|shepherd the flock|"
                     r"you shall be (?:a|my|king|priest)|I have given you as|whom shall I send|here am I|send me)\b", re.I)
re_wisd = re.compile(r"\b(better (?:is|are|a|an|the|to)?\b.*\bthan\b|blessed (?:is|are) |happy (?:is|are) |"
                     r"woe to|woe unto|the fear of the Lord|fear of God is|my son\b|^son,|, son,|"
                     r"(?:^|\b)(?:he|she) who\b|whoever\b|the one who\b|those who\b|a wise\b|the wise\b|a fool\b|"
                     r"the fool\b|fools\b|the righteous\b|the wicked\b|the impious\b|the lazy\b|the sluggard\b|"
                     r"the diligent\b|the prudent\b|the simple\b|a prudent\b|wisdom\b|discipline\b|understanding\b|"
                     r"like (?:a |an |the )?\w+.*,? so\b|as (?:a |an |the )?\w+.*,? so\b)", re.I)


def imperatives(doc):
    verbs = []
    for t in doc:
        if t.tag_ != "VB" or t.lower_ in DISCOURSE:
            continue
        if t.dep_ not in ("ROOT", "conj", "ccomp", "parataxis", "advcl", "xcomp", "dep"):
            continue
        kids = list(t.children)
        if any(k.dep_ in ("aux", "auxpass") and (k.tag_ in ("MD", "TO") or k.lower_ == "to") for k in kids):
            continue
        if t.dep_ == "xcomp" and t.head.lemma_ not in ("let",):
            continue
        subj = [k for k in kids if k.dep_ in ("nsubj", "nsubjpass", "expl")]
        if subj:
            s = subj[0]
            nxt = doc[s.i + 1] if s.i + 1 < len(doc) else None
            # vocative misparsed as subject: "Son, do not ..." / "Israel, hear ..."
            if not (nxt is not None and nxt.text == "," and s.i < t.i and
                    (s.lower_ in VOCATIVE_WORDS or s.tag_ == "NNP" or s.lower_ in ("you",))):
                continue
        # conj verbs inherit subject from head; skip if head has a subject
        if t.dep_ == "conj":
            h = t.head
            if any(k.dep_ in ("nsubj", "nsubjpass") for k in h.children) and h.tag_ != "VB":
                continue
        # first-person cohortative inside questions etc. -> skip if sentence ends with '?' and verb is 'do'
        sent = t.sent.text.strip()
        if sent.endswith("?") and t.i == t.sent.start:
            continue
        verbs.append(t.lemma_.lower())
    return verbs


def signals(text, doc):
    sig = set()
    imp = imperatives(doc)
    if imp:
        sig.add("IMP")
    if re.search(r"\blet (us|him|her|them|it|your|my|his|their|every|all|no|not|the|this|that|those|each|everyone|"
                 r"any|none|nobody)\b", text, re.I):
        sig.add("JUSS")
    if re_proh.search(text):
        sig.add("PROH")
    if re_shall.search(text):
        sig.add("SHALL")
    if re_casu.search(text):
        sig.add("CASU")
    if re_lawnoun.search(text):
        sig.add("LAWNOUN")
    if re_comm.search(text):
        sig.add("COMM")
    if re_wisd.search(text):
        sig.add("WISD")
    if PRAYER_TO_GOD.search(text):
        sig.add("ADDR_GOD")
    return sorted(sig), imp


out = {}
texts = [v["text"] for v in B.verses]
for i, doc in enumerate(nlp.pipe(texts, batch_size=256)):
    s, imp = signals(texts[i], doc)
    out[i] = {"sig": s, "imp": imp}
    if i % 5000 == 0:
        print("…", i, file=sys.stderr)
json.dump(out, open("/home/claude/work/signals.json", "w"))
print("done", len(out))
