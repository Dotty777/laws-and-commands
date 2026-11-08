# Completeness audit of the 70-book catalogue — 8 November 2026

**Round 2 (8 November 2026):** after the catalogue update, every verse that states, repeats or recalls a direction was checked against the 6,416 published records. See [round-2/README.md](round-2/README.md).

The report below describes the original draft and its 4,999-record baseline. The subsequent [contextual review decisions](verified-completeness.json) list the corrected proposals included in the [current catalogue](../browse/README.md).

This audit checked the Laws, Commands, and Instructions catalogue against every verse of the 70 books. The catalogue held 4,999 records, in the workbook with SHA-256 `801c93948bdcf13f65c54fe54676fd4a04c4a49b71fab8b0a5ab468077e2b098`, the same file on production, staging and in this repository.

**The catalogue is not complete yet.** The audit proposes **1,906 new records**, **642 records whose Scripture should be extended**, and **683 verses to link as parallels**. Of the new records, **1,607 are high or medium confidence**: add those first. Everything here is a draft for review. Nothing was changed on the website or in the catalogue files.

| Record type | Recommended (high or medium) | To consider (low) | All proposed |
| --- | ---: | ---: | ---: |
| Wisdom | 870 | 105 | 975 |
| Command | 448 | 120 | 568 |
| Commission | 147 | 38 | 185 |
| Law | 91 | 17 | 108 |
| Instruction | 51 | 19 | 70 |
| **All types** | **1,607** | **299** | **1,906** |

| Division | Recommended new records | Extend Scripture | Link as parallel |
| --- | ---: | ---: | ---: |
| Law (Genesis–Deuteronomy) | 132 | 92 | 364 |
| Judgement (Joshua–Job) | 392 | 187 | 60 |
| Wisdom (Psalms–Sirach) | 781 | 157 | 41 |
| Providence (Isaiah–Malachi) | 149 | 66 | 21 |
| Salvation (Gospels) | 92 | 65 | 112 |
| Discipleship (Acts–Jude) | 55 | 66 | 82 |
| Glory (Revelation) | 6 | 9 | 3 |

Proverbs (423) and Sirach (217) hold 40% of the recommended additions. The catalogue had itemized the imperative counsel in the wisdom books but rarely their declarative sayings, though its own Wisdom records include them. Per-book figures are in [coverage-by-book.csv](coverage-by-book.csv).

## How the audit was done

1. **Coverage map.** All 5,268 Scripture references (4,999 primary, 269 additional) were resolved to verses, and every one resolves. The map spans 34,518 verses: the 70 exports in `source/translation/books/`, plus Susanna, Bel and the Dragon, and Proverbs 24:23–34, 30:15–33 and 31:10–31, which the exports leave out (taken from Dotty777/Saints-Translation).
2. **Screen.** Every verse was tagged for imperatives, prohibitions, "you shall" law forms, case law, reported orders, requests, commissions and wisdom forms. Tested on the catalogue's own 4,427 directive records, the screen flags 96.7% of them.
3. **Candidates.** Flagged verses without an itemized record became candidates. Proverbs, Ecclesiastes, Sirach, Wisdom of Solomon, the New Testament letters and Revelation were read in full. That gave 8,808 verses in 3,125 passages. In Genesis–Deuteronomy a verse counts as itemized only when a record of 8 verses or fewer covers it, because the catalogue itemizes each Torah requirement apart from its passage groups.
4. **Maimonides' 613.** The traditional source verse of each commandment in Sefer HaMitzvot (verse index at betemunah.org/sederim/cmds613.html) was checked for an itemized record.
5. **Review.** 24 reviewer passes judged every candidate against rules taken from the catalogue's own records ([review-records/BRIEF.md](review-records/BRIEF.md)). In scope: any speaker, including Pharaoh, Haman and Antiochus; requests and reported orders; calls to worship addressed to people; declarative wisdom sayings. Out of scope: prayers addressed to God, curses and predictions that direct no one, creation speech, narrative and doctrine. Each finding was searched against the whole catalogue first and given one of three verdicts: new, extend or parallel.
6. **Second sweep.** 2,012 further uncovered verses with weaker signals were reviewed in 8 more batches, adding 418 findings.
7. **Reconciliation.** Proposals for the same directive from different batches (parallel Gospels, Kings and Chronicles, Ezra and Nehemiah, 1 and 2 Maccabees) were merged into one record each, folding in 131 duplicates ([review-records/merge.jsonl](review-records/merge.jsonl)).
8. **Checks.** An independent checker re-judged 110 random findings. High confidence: 54 of 56 correct, 2 partly right. Medium: 39 of 41 correct, 2 partly. Low: 5 of 13 correct, 3 partly, 5 wrong. A recall check of 45 passed-over passages and 60 never-shown uncovered verses found 4 misses, all minor; scaled up, roughly 150–350 further minor items remain.

## Maimonides' 613 commandments

| Status | Count |
| --- | ---: |
| Itemized at or beside the source verse | 524 |
| Itemized from another verse: link the source verse as a parallel | 50 |
| Existing record needs its Scripture extended | 7 |
| No record of its own: new record proposed | 32 |

The 32 include the sinew of the thigh (Genesis 32:33), no leaven seen within your borders (Exodus 13:7), and not perverting the justice due to the poor (Exodus 23:6). They also include the priests' grain portion never baked with leaven (Leviticus 6:9–10), who may eat the priests' holy food (Leviticus 22:10–13), not oppressing one another (Leviticus 25:14, 17, 53), and the vineyard mixture laws (Deuteronomy 22:9). Further examples are lending at interest to a foreigner (Deuteronomy 23:21), performing vows (23:23–24), the priests' dues (18:3–4), the Feast of Weeks additional offering (Numbers 28:27–31), and the permission to eat any clean bird (Deuteronomy 14:11). Details are in [maimonides-613.csv](maimonides-613.csv).

## Notable gaps by division

- **Law:**
  - Pharaoh's order to the midwives (Exodus 1:15–17).
  - Jacob's burial charge (Genesis 49:29–32) and Abraham's charge to his servant (Genesis 24:3–4, 7). Genesis 39 has no records.
  - Leviticus 18:3–5, quoted in Romans 10:5 and Galatians 3:12.
  - The Sabbath as covenant sign (Exodus 31:13, 16–17), and the death penalty for murder with its tests (Numbers 35:16–21).
- **Judgement:**
  - The covenant renewals of Asa, Jehoiada and Josiah; David's anointings (2 Samuel 2:4; 5:1–3); Saul's oath on the army (1 Samuel 14:24).
  - The priestly courses, singers and gatekeepers (1 Chronicles 24–27 had no records), and 2 Chronicles 7:12–14.
  - The Maccabean charters (1 Maccabees 13:36–39; 15:16–19), Nehemiah's commission (Nehemiah 2:5–6), Esther's petitions, and Job 31.
- **Wisdom:**
  - Proverbs 10–12 had no records and 13–18 only nine; Wisdom's speeches (Proverbs 1:20–33; 8:12–36).
  - Sirach 1:1–27, including "If you desire wisdom, keep the commandments"; Ecclesiastes 1–3 and 6.
  - The entrance psalms (Greek Psalm 14; 23:3–6); "a priest for ever after Melchizedek" (Greek Psalm 109:4).
- **Providence:**
  - Ezekiel's call (2:1–5) and about 18 commissions to prophesy; Cyrus's commission (Isaiah 44:28–45:6, 13); the Servant's commissions (Isaiah 42:1–4; 50:4–5).
  - Jeremiah's renewed commission (15:19–21); Nebuchadnezzar's decree (Daniel 3:95–96); Zechariah 3:6–7.
- **New Testament:**
  - Parables with no record: the great supper, the wicked tenants, the rich man and Lazarus, wheat and darnel, the labourers in the vineyard, the seed growing unseen.
  - The woes on the Pharisees and lawyers, Ananias and Sapphira (Acts 5:1–11), and elders appointed in every church (Acts 14:23).
  - Personal charges in the letter closings, and Revelation 20:6.

Extensions follow a few patterns:

- References that stop mid-sentence or before the "for…" reason clause.
- Titles that already describe verses outside the reference: A050 (Romans 13), A035 and A020 (Ephesians 4:29, 31), A024 (Philippians 2:1–2), A049 (Ephesians 5:31–33).
- Parables recorded only at their application (K049, K069, K076, K077), and partly recorded church letters (X009–X011).
- Two Genesis 32 records that use English verse numbers.

## Housekeeping in the current data

- 559 records, every one in the "70-book audit" collection, have their record type in the Topic field, so they fall under none of the 50 topics.
- 36 Harmony and Supplemental records have an empty Topic. The import notes assign them "Cross-Scripture studies".
- X009 and X012 have Scripture links that point past the first verse.
- The Genesis export has four placeholder rows (35:16a, 35:16b, 35:22a, 35:22b) whose text is "Earlier label … see this chapter's reading text and numbering notes".

## Limits

- Scope follows the catalogue's own practice. If ordinary requests and narrated orders should be left out, many of the 448 recommended Commands fall away.
- About 150–350 minor items, mostly narrative acts, probably remain unfound.
- The text read was the per-book exports of 14–16 October 2026 plus the supplementary blocks. Later text edits are not reflected.
- 48 Greek-only lettered verses (such as 1 Kings 2:35a–o) count as covered through a bare verse or range reference. They were not screened again.
- The published Maimonides index has three slips (N182, P96, P227), which were corrected before checking.

## Files

| File | Contents |
| --- | --- |
| [Saints-Bible-Instructions-Completeness-Audit-2026-11-08.xlsx](Saints-Bible-Instructions-Completeness-Audit-2026-11-08.xlsx) | New records in the Catalogue sheet's 24 columns (IDs prefixed `GAP-`, collection "Completeness audit 2026-11-08"). Also: Extend Scripture, Link as parallel (Scripture Sources columns), Coverage by book, Maimonides 613, Housekeeping |
| [findings.json](findings.json) | Every final finding (`new`, `extend`, `parallel`), plus the removed duplicates and why they were removed |
| [coverage-by-book.csv](coverage-by-book.csv) | Per-book verses, records, verses screened and reviewed, and findings |
| [maimonides-613.csv](maimonides-613.csv) | The 613 cross-check with status and finding |
| [review-records/](review-records/) | The reviewer brief, every batch's raw output (B01–B24, S01–S08), the reconciliation operations and both verification checks |
| [scripts/](scripts/) | Coverage map, screen, candidate builder, compile and workbook scripts, as run for this audit (paths point to the audit workspace) |
