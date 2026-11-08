# Reviewer brief: the catalogue's Torah laws against Maimonides' 613 commandments

## Background
The Saints.Bible catalogue of laws, commands, commissions, instructions and wisdom (70-book Bible, 6,416 study records)
labels God-given directions in Exodus–Deuteronomy with a **Mosaic type**:
- **Torah Law** (`{Torah Law}`, record type Law) — 556 records: standing statutes, prohibitions and case laws;
- **Mosaic Instruction** — 417 records: procedures and specifications (sanctuary, offerings, purification steps);
- **Mosaic Command** — 72: direct covenant charges (e.g. love the Lord, do not make idols);
- **Mosaic Wisdom** — 10, **Mosaic Commission** — 9.
Other records have no Mosaic type: historical directions, Genesis "Creation commission"/"Indexed instruction" records,
completeness-review records (ids AUD-…), **passage groups** (ids torah-…, many verses) and **topical studies** (ids S…).
The site states its counts are study records, not a count of distinct commandments.

## Your task
Each item is one of Maimonides' 613 commandments (Sefer HaMitzvot numbering: P1–P248 positive, N1–N365 negative) with its
traditional source verse (Hebrew numbering, already mapped to the Saints text) and the catalogue records on or near that verse.
For each item:
1. State the commandment in at most 12 words, as Maimonides counts it (use the number and the verse; several commandments can
   share one verse, so make sure you state the one this number refers to).
2. Find the record(s) that **itemize** it: the record's own direction is this commandment (or one of at most two or three
   directions it states), and its Scripture includes the source verse or a parallel verse stating the same law. A passage group
   or topical study does not itemize. If several records itemize it (for example one per book), list them all.
3. Choose the status:
   - `torah_law` — itemized by at least one Torah Law record;
   - `other_mosaic` — itemized only by a record of another Mosaic type (give it in `type`);
   - `other_record` — itemized only by a record without a Mosaic type (historical direction, Genesis record, AUD record, an S… study of a few verses);
   - `broad_only` — present only inside a passage group or broad topical study;
   - `partial` — a record holds the verse but states a different part of it, or only part of this commandment;
   - `missing` — no record states it.
4. `mislabel`: true only when the commandment is itemized under a non-Law Mosaic type (or no Mosaic type) although it reads as a
   standing law of the same kind the catalogue labels Torah Law elsewhere (a prohibition or rule binding Israel or a class of people).
   Procedures, one-time charges and exhortations under Instruction or Command are not mislabels.

## Tools
```
python3 -I /home/claude/work/verse.py "Leviticus 19:9-10"            # Saints text
python3 -I /home/claude/work/cat_search.py at "Leviticus 19:9"       # records holding a verse; {braces} = study placement
python3 -I /home/claude/work/cat_search.py words gleanings            # records by words
python3 -I /home/claude/work/cat_search.py book Leviticus 19          # every record in a chapter
```
The candidate list in your batch covers two verses either side; search further (parallels in other books, `words`) before
deciding `missing` or `broad_only`.

## Output
One JSON line per item in `/home/claude/work/round3/out/<BATCH>.jsonl`, written as you go:
`{"m": "N186", "statement": "Do not cook meat with milk", "records": ["C0218"], "status": "torah_law", "type": "Law", "mislabel": false, "confidence": "high|medium|low", "note": "<= 25 words"}`
`records` lists the itemizing records (for `partial`/`broad_only`, the record that holds the verse); `type` is the Mosaic type of the
best itemizing record (`Law`, `Instruction`, `Command`, `Wisdom`, `Commission`) or `none`.
End with `{"batch": "<BATCH>", "done": true}`, then run `python3 -I /home/claude/work/round3/validate_613.py <BATCH>` and fix every problem.
Do not change any other file and do not start other agents.
