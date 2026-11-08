# Reviewer brief, round 2: decide every open item so all associated verses are recorded

## Where things stand
The Saints.Bible catalogue of laws, commands, commissions, instructions and wisdom (70-book Bible) was updated on
8 November 2026 to **6,416 records**. A first audit proposed missing records; an editorial review then
published 1,417 new records, 427 Scripture extensions and 406 parallel links, and **held the rest**. Most holds were
never decided ("Deferred for source-context and catalogue comparison", "Source change pending individual comparison
with the existing study entry") or were held without a stated reason. Your job is to give **each item in your batch a
final decision**, so that every verse that states, continues, repeats or quotes a direction ends up attached to a record —
and nothing is added that the catalogue's own standard would reject.

## The standard (follow the published review, which was stricter than the first audit)
Record an item only when the Saints text clearly supports it. Do **not** record when the item:
- **repeats existing coverage** — the same direction is already a record (then use `extend` or `parallel` instead, or `no_record` if already linked);
- **lacks an independent teaching or direction** — narration of an act already recorded, someone carrying out an order,
  a speaker's own plan or proposal about what *he* will do (not a direction to someone), a rhetorical question,
  a narrator describing a custom, a conditional promise or threat that directs no one, praise, or doctrine;
- **cannot be verified with sufficient context** — the direction is implied, not stated;
- **misattributes** the speaker or addressee (e.g. an envoy *quoting* a king's alleged order is not the king's order;
  a refusal is not a command to the person refused);
- is an **overlapping or unspecific update** — an extension that would change what an existing record means, or a range
  that sweeps in unrelated verses (split it, or extend only the verses that carry the same direction).
In scope, as the catalogue already does: directions from any speaker (including wicked rulers), requests, reported
orders, appointments and anointings, royal decrees and covenants with stated obligations, calls to worship addressed to
people, and wisdom sayings that teach how to live. Out of scope: prayers addressed to God, curses and predictions that
direct no one, creation speech, narrative, doctrine. Weaker ordinary speech (small talk, offers, greetings) is not recorded
unless the catalogue already records that kind of speech nearby.

## What counts as an associated verse (the catalogue's own practice in 785 Additional Scripture notes)
Link a verse (extend or parallel) when it **restates, repeats, quotes, reports, retells or expressly recalls** the
direction — e.g. "Narrator restates the charge…", "Judah reports Joseph's demand…", "Quotes the Genesis 50:25 charge as
Moses carries the bones". Plain **fulfilment narrative** that only shows the order being carried out is not linked
("35:29 and 36:5–39:23 are fulfilment narrative, not directives") unless it quotes or expressly cites the direction
("by the Lord's command"). Use `record_extend` when the verses belong inside the record's own passage (same speaker,
same occasion, continuing or renewing the direction); use `record_parallel` when they are elsewhere (another occasion,
book, speaker or a quotation). If the verses are already in the record's Scripture or Additional Scripture, use `no_record`
with reason "already linked".

## Tools (the catalogue tools now read the updated 6,416-record catalogue)
```
python3 -I /home/claude/work/verse.py "2 Kings 23:1-4"                 # Saints text (Psalms use Greek numbering)
python3 -I /home/claude/work/cat_search.py at "2 Kings 23:3"           # current records that include a verse
python3 -I /home/claude/work/cat_search.py words covenant Josiah       # current records by words
python3 -I /home/claude/work/cat_search.py book "2 Kings" 23           # every record in a chapter
```
Always check the current catalogue before deciding: some held items were later covered by another record.

## Decisions (one JSON line per item, in `/home/claude/work/round2/out/<BATCH>.jsonl`)
- `record_new` — a new record is needed. Give `reference`, `record_type` (Law, Command, Commission, Instruction, Wisdom),
  `title` (≤ 12 words, catalogue style), `speaker`, `recipient`, `origin` (`Heavenly (God-given)` | `Earthly (Man-made)` |
  `Mixed origins`), `audience` (`General` | `Personal`), `topic` (one of the 50 topics, copied character for character — including curly apostrophes — from
  `/home/claude/work/audit/topics50.json`).
  Correct the draft's reference, wording or type when needed and say so in `reason`.
- `record_extend` — an existing record already states this direction and its Scripture should take in these verses:
  give `existing_id` and `reference` = only the verses to add.
- `record_parallel` — the same direction is recorded elsewhere; link these verses as Additional Scripture on
  `existing_id`; give `reference` = verses to link and `context` (≤ 25 words, like the Scripture Sources sheet:
  what this passage is in relation to the record).
- `no_record` — do not record; `reason` must name which standard applies (≤ 25 words).
The item id is the text after `### ` up to the first ` · ` (for example `E:C0040|Genesis 19:15`, `N:GAP-06-6-26`, `SIM001`, `U3894`).
Every line: `{"item": "<item id from the batch>", "decision": "...", "confidence": "high|medium|low", "reason": "<≤ 25 words>", ...fields}`.
End with `{"batch": "<BATCH>", "done": true, "items": <n>}`. Write as you go. When finished, run
`python3 -I /home/claude/work/round2/validate_r2.py <BATCH>` and fix every problem. Do not change any other file and
do not start other agents. Reply with counts per decision and the most important items you recorded.
