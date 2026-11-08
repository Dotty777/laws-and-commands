# Reviewer brief: Saints.Bible Laws, Commands and Instructions — completeness audit

## Purpose
Saints.Bible keeps a catalogue of **4,999 study records** of the laws, commands, commissions, instructions and
wisdom of its 70-book Bible (`saints.bible/instructions/`). We are auditing it for **completeness**. Each batch
file lists *candidate verses* — verses that contain directive or wisdom language but have **no itemized record**.
Your job: decide which candidates are genuinely in scope and missing, and draft the record that should be added.
Most candidates in narrative and prophecy will turn out *not* to need a record; that is expected.

Work only from the Saints Translation text in the batch file. Do not change any website or repository.

## The catalogue's scope (follow its own practice)
The catalogue is deliberately broad. It records directions from **any speaker** — God, Christ, angels, prophets,
apostles, kings, parents, ordinary people, and even wicked rulers (Pharaoh, Haman, Antiochus) — and keeps the
speaker, recipient and occasion attached. Recording an order does not mean approving it.

**In scope — report if missing:**
- **Law** — a legal requirement, statute, ordinance or ruling with legal force: each Torah requirement
  (the catalogue itemizes them one by one, e.g. "Do not take the mother bird with the young"); royal decrees and
  edicts (Persian, Babylonian, Seleucid); covenant stipulations; communal decrees (e.g. Hanukkah established,
  the Jerusalem council's decree).
- **Command** — a direct order, prohibition or request from one party to another, including **reported** orders
  ("Joseph commanded the embalmers to…"), ordinary **requests** ("Give me a little water"), calls to worship
  addressed to people ("Praise the Lord", "Sing to God", "Come, let us bow down"), and prophetic summonses to
  peoples or cities to act (flee, wail, gather, prepare for battle, return, repent).
- **Commission** — appointing, sending, anointing, ordaining or charging someone to a task or office (prophetic
  calls, kings anointed, priests and Levites assigned, apostles and messengers sent with a charge, authority handed on).
- **Instruction** — practical or procedural direction (how to build, perform a rite, travel, conduct oneself), and
  runs of exhortation in letters and speeches that direct conduct.
- **Wisdom** — proverbs, maxims, counsel, beatitudes and woes, and **declarative sayings that teach how to live**
  (the catalogue's own Wisdom records include "A friend is present in every season" and "A yielding answer can
  turn away wrath"). In Proverbs, Ecclesiastes, Sirach and Wisdom of Solomon, nearly every saying is in scope.

**Out of scope — do not report:**
- Petitions and prayers addressed **to God** ("Hear my prayer, O Lord", "Save me", "Remember me", Job's appeals
  to God), blessings and wishes spoken over people ("The Lord bless you"), doxologies.
- Curses, judgments, predictions and promises that give no one a direction (Genesis 3:14–19; "you shall bear a
  son" as a foretelling). But a foretelling that *tells someone to do something* is in scope ("you shall call his
  name Jesus" → Command).
- Creation speech ("Let there be light"), narrative, genealogies, descriptions, rhetorical questions, laments.
- Poetic apostrophes to nature or personified things ("Hear, O heavens", "Lift up your heads, O gates") unless the
  address is really to people.
- Imperatives inside a parable when the parable as a whole already has a record. (If a parable or teaching of
  Jesus has no record at all, report one Wisdom record for it.)
- Whole-book wisdom reflections that are history or praise rather than counsel (much of Wisdom of Solomon 10–19 is
  a meditation on the Exodus: report only the sayings that teach or direct).

When unsure whether the catalogue would include something, report it with `"confidence": "low"`.

Clarifications from the first review wave:
- Doctrine, Christ hymns, praise of God, and a writer's autobiography are **not** Wisdom unless they state a maxim or
  direct conduct (Paul's "count all things loss" as an example to imitate can be Wisdom; "every knee shall bow" is not).
  If you include a borderline item of this kind, mark it `low`.
- For `parallel` and `extend`, use the existing record's own record type.
- If you notice a clear gap in a verse that is not marked [C] (context verses, or a verse the screen missed), you may
  report it too; say "outside candidate list" in `note`.

## Check for existing coverage before proposing
Each passage shows `Near:` records already in that chapter. Also search the whole catalogue:
```
python3 -I /home/claude/work/cat_search.py words <word> [<word> ...]   # e.g. words wool linen
python3 -I /home/claude/work/cat_search.py at "Deuteronomy 22:11"       # records that include a verse
python3 -I /home/claude/work/cat_search.py book "Mark" 9                 # every record for a chapter
```
Use one of three verdicts:
- `new` — nothing in the catalogue records this directive.
- `extend` — an existing record clearly records this same directive but its Scripture reference stops short of
  these verses (give `existing_id`). E.g. a record titled "…and payment of what is owed" whose reference is only
  Romans 13:1 should be extended to 13:6–7.
- `parallel` — the same directive is already itemized from another passage (a repeated law, a parallel Gospel
  account, a quotation); the verse should be linked as Additional Scripture on that record (give `existing_id`).
  E.g. Deuteronomy 22:11 (wool and linen) parallels the existing Leviticus 19:19 record.
Search for parallels especially for Gospel sayings, repeated Torah laws, and Chronicles/Kings parallels.

Candidates marked `broad-only` sit inside a long passage record (often 20–60 verses) but have no itemized record.
In the Law books (Genesis–Deuteronomy) the catalogue itemizes each requirement and each recorded direction, so a
distinct law or direction covered only by a broad passage record **is a gap** (`new`, or `parallel` if itemized
elsewhere). `Rambam N…/P…` marks a verse that is the traditional source of one of Maimonides' 613 commandments;
say explicitly in `note` whether that commandment is itemized anywhere (give the id) or missing.

## Granularity
One record per distinct directive or tight unit: same speaker, same addressee, same occasion, consecutive verses.
Laws: one record per requirement (a verse with two separate prohibitions can be two records, as the catalogue does).
Proverbs and Sirach: one record per saying, or a cluster of at most 4 consecutive verses that make one point —
never a whole chapter. A long exhortation (e.g. a letter's closing commands) may be one record per distinct command
or per sentence-group; prefer the finer division when the commands are different in kind.

## Output
Write JSON Lines to `/home/claude/work/review/out/<BATCH>.jsonl`: one object per finding, then a final summary
line. Write as you go (e.g. append every 20–30 passages with a short Python snippet) so work is never lost.

```json
{"pid": "P00137", "verdict": "new", "reference": "Genesis 50:2", "record_type": "Command",
 "title": "Joseph orders the embalmers to prepare Jacob for burial", "speaker": "Joseph",
 "recipient": "his servants the embalmers", "origin": "Earthly (Man-made)", "audience": "Personal",
 "topic": "Family, marriage and household", "confidence": "high", "existing_id": "", "note": ""}
```
Final line: `{"batch": "<BATCH>", "done": true, "passages_reviewed": <n>, "findings": <n>, "summary": "<one sentence>"}`

Field rules:
- `reference`: Book chapter:verse, en dash for ranges (`Genesis 49:29–32`). Psalms use the batch's Greek numbering
  written as `Greek Psalm 49:16`; Susanna and Bel as `Susanna 1:22` / `Bel and the Dragon 1:8`. Lettered verses as
  shown (`Proverbs 9:12a`, `Esther 4:17k`). The reference may include context verses when the directive runs into them.
- `record_type`: one of `Law`, `Command`, `Commission`, `Instruction`, `Wisdom`.
- `title`: at most 12 words, catalogue style — imperative for laws and wisdom ("Do not move your neighbour's
  boundary stone"), descriptive for recorded directions ("Pharaoh orders the midwives to kill Hebrew boys").
- `speaker` / `recipient`: who gives it and to whom (e.g. "the Lord through Moses" / "Israel"; "Ben Sira" / "his son, the reader").
- `origin`: `Heavenly (God-given)` when God, Christ, the Spirit or an angel speaks, or a prophet delivers God's word;
  `Earthly (Man-made)` for human speakers — including wisdom teachers, psalmists and apostles' own exhortations, as
  the catalogue does; `Mixed origins` when both.
- `audience`: `Personal` for a direction to a particular person or household on a particular occasion; otherwise `General`.
- `topic`: exactly one of these 50 catalogue topics:
  Clean and Unclean, and the Tradition of the Elders · Covenant signs, vows and dedications · Creation, personal commissions and Israel’s journeys ·
  Cross-Scripture studies · Do This in Remembrance of Me · Done to Be Seen · Faith, repentance and allegiance · Family, marriage and household ·
  Follow Me · Food, ritual purity and cleansing · Go and Make Disciples · Hear and Keep · Historical commissions, journeys and public life ·
  Holiness, truthfulness and sexual conduct · Human life, injury and care for neighbours · In Secret · Judging and Forgiving ·
  Justice, testimony, government and war · Justice, truth and protection · Knowing, loving and obeying God · Land, harvests and provision for the poor ·
  Major Teachings: The Word of Christ Handed On · Marriage · Marriage, family and care for parents · Mercy, neighbors and the vulnerable ·
  Minor Teachings: The Scriptures Read in Christ · Offerings, sacrifice and atonement · Pray in This Way · Property, honest trade and service ·
  Repent and Believe · Sabbath, appointed times and remembrance · Sanctuary, priesthood and ministry · Serving · Shepherds of the Flock ·
  Supplementary instructions · Temple, Offerings and Tithes · The Commandments and the One Thing Lacking · The Law and the Prophets ·
  The Little Ones and the Poor · The New Commandment · The Sabbath · The Sending · Treasure · Trust · Wages, lending, pledges and inheritance ·
  Watchfulness · Wisdom, speech and conduct · Work, possessions and stewardship · Worship, prayer and holy things ·
  You Heard That It Was Said, but I Tell You
- `confidence`: `high`, `medium` or `low`. `existing_id`: required for `extend` and `parallel`, else "".
- `note`: at most 25 words, only when useful (what is missing, why in scope, the Rambam status).

When finished, run `python3 -I /home/claude/work/validate_out.py <BATCH>` and fix every error it reports.
Then reply with: findings by verdict and by record type, and up to five of the most significant gaps you found.

## Second sweep (batches S01–S08)
These batches hold verses the screen did **not** flag, so most need nothing. They were never read in the first pass.
`{inside a long record only}` marks an Old Testament verse whose only coverage is a record spanning many verses:
report it only when it holds a distinct law, direction or saying that the long record's title does not capture
(the catalogue itemizes sayings and directions one by one elsewhere in these books).
The first pass has already proposed about 2,950 findings that are not yet in the catalogue. Before proposing,
also check them, so nothing is proposed twice:
```
python3 -I /home/claude/work/find_search.py at "2 Kings 22:12"      # first-pass findings that include a verse
python3 -I /home/claude/work/find_search.py words Hilkiah            # first-pass findings by words
```
If a first-pass finding already covers it, skip it; if it should be widened, say so in `note` on your own finding.
