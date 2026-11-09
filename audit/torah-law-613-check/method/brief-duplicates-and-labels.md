# Reviewer brief: duplicates and labels among the catalogue's Torah records

The Saints.Bible catalogue (6,416 study records) gives God-given directions in Exodus–Deuteronomy a **Mosaic type**, shown as
the study placement. How the catalogue uses the labels (judge records against this, not against a theory of your own):
- **Torah Law** (556 records) — a standing rule for ongoing observance by Israel or a class of people (priests, judges, the king,
  owners, households): prohibitions, obligations and case laws, including festival, offering and purity rules stated as rules.
- **Mosaic Instruction** (417) — procedures and specifications: the steps of a rite as performed, how to make or assemble the
  sanctuary and its items, one-occasion setup tasks, usually addressed to Moses, Aaron or the priests.
- **Mosaic Command** (72) — covenant charges and exhortations: all of the Ten Commandments in Exodus 20:3–17 are filed here,
  with love, fear, serve, remember, do not forget, circumcise the heart, walk in his ways.
- **Mosaic Wisdom** (10) and **Mosaic Commission** (9) — reflective counsel; entrusting a role or task.
- **No Mosaic type** (Torah · Historical direction, Personal historical direction, … study) — a one-time direction tied to a
  historical occasion (the first Passover in Egypt, camp moves, battles, a specific person's task).
The site says its records overlap and are not a count of distinct commandments; separate records for separate clauses of one
verse are normal (for example Leviticus 21:7: do not marry a prostitute / a profaned woman / a divorced woman).

Tools:
```
python3 -I /home/claude/work/verse.py "Leviticus 21:7"
python3 -I /home/claude/work/cat_search.py at "Leviticus 21:7"     # {braces} = study placement
python3 -I /home/claude/work/cat_search.py words leaven
```

## Batch D1 — same-passage pairs (ids D###)
Two records share verses and at least one is Torah Law. Verdict:
- `duplicate` — both state the same direction (same action or prohibition); one is redundant;
- `overlap` — one record's direction contains the other's (a partial duplicate; say which to narrow);
- `split` — they state different clauses, actions or cases (legitimate).
`label_conflict`: true when the same direction (duplicate/overlap) carries different labels, or when a split pair of a
prohibition and its matching positive rule are labelled differently in a way the conventions above do not explain.
Line: `{"id": "D001", "verdict": "duplicate|overlap|split", "keep": "<record id>|both", "label_conflict": false, "confidence": "high|medium|low", "note": "<= 25 words"}`

## Batch D2 — cross-passage pairs (ids X###)
Two records in different passages read alike. Verdict:
- `restatement` — the same law stated again in another passage (it could be one record with the other passage as Additional Scripture);
- `related` — same subject but a different law (sabbatical year vs jubilee, a prohibition vs its penalty, different relatives);
- `distinct` — unrelated beyond wording.
`label_conflict`: true for a restatement whose two records carry different labels.
Line: `{"id": "X001", "verdict": "restatement|related|distinct", "keep": "<record id>|both", "label_conflict": false, "confidence": "high|medium|low", "note": "<= 25 words"}`

## Batch L1 — label review (ids = record ids)
Each record was picked by a screen (the heading says why). Decide whether its label fits the conventions above:
`{"id": "C0104", "verdict": "keep|relabel", "suggest": "Torah Law|Mosaic Instruction|Mosaic Command|Mosaic Wisdom|Mosaic Commission|No Mosaic type", "is_law": true, "confidence": "high|medium|low", "note": "<= 25 words"}`
`suggest` repeats the current label when the verdict is keep. `is_law`: does the record state a standing law at all (false for
narrative, promises, one-time directions)? Relabel only when the record clearly fits another label better; borderline cases stay `keep` with a note.

End every batch with `{"batch": "<BATCH>", "done": true}`, then run `python3 -I /home/claude/work/round3/validate_dl.py <BATCH>` and fix every problem.
Do not change any other file and do not start other agents.
