# Torah Laws: the 556, the revision to 638, and Maimonides' 613 — 8 November 2026

**The catalogue now counts 638 Torah Law records.** It counted 556 when this check began. The contextual Torah Law audit (commit `467e928`) made the change during the check:
- added 21 new records;
- relabelled 80 records as Torah Law, among them all of the Ten Commandments;
- merged 19 Torah Law records into others.

The record type audit that followed (commit `00f33d1`) changed no Torah Law record and no record in the open findings (it did fix one of the editing notes), so the figures below hold for the current catalogue. This report gives that current state first, then what the 556 counted.

**Against Maimonides' 613, in the current catalogue:**
- **475** commandments are itemized by a Torah Law record (up from 419).
- **59** sit only under another Mosaic label: 44 Instruction, 14 Command and 1 Commission.
- **13** sit only in records with no Mosaic type.
- **66** are not stated as Maimonides counts them. In 58 of these his reading goes beyond the plain text, and in 6 the Saints (Greek) wording differs.

**Still to fix in the current catalogue:**
- 2 commandments to add;
- 7 duplicate or overlap cases, 1 of them introduced by the revision;
- 27 records still labelled inconsistently;
- 132 public notes that still read as editing instructions.

Nothing was changed in the catalogue by this check. The review workbook is [Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx](Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx).

## The 613 in the current catalogue

| Status | Now (638) | Before (556) |
| --- | ---: | ---: |
| Itemized by a Torah Law record | 475 | 419 |
| Only under Mosaic Instruction | 44 | 71 |
| Only under Mosaic Command | 14 | 32 |
| Only under Mosaic Commission | 1 | 1 |
| Only in a record with no Mosaic type | 13 | 20 |
| Not stated: the text states it, but no record does | 2 | 6 |
| Not stated: the Saints wording differs | 6 | 6 |
| Not stated: Maimonides' reading goes beyond the text | 58 | 58 |

The counts are not meant to match one to one. The catalogue often splits one commandment into several records. Many Torah Law records are penalties, sub-cases or details that Maimonides counts inside a broader commandment. The revision's own report says its total "is not a reconciliation to a traditional count of mitzvot".

### Commandments to add

- **N133** A non-priest must not eat terumah (holy food): Leviticus 22:10a ('no outsider shall eat the holy thing') still has no record; AUD-03-22-10 states only the lodger and hired-worker clause.
- **P222** Divorce only by giving a written bill of divorce: Deuteronomy 24:1's written bill of divorce has no record; C1166 states the remarriage ban. The bill is part of the case's background.

The 556 check found 10 commandments in this position, after the accuracy check showed that two more (N171 and P53) were already itemized by C0655 and C0230. The revision has since fixed 7 of them: P83 (TL-05-12-05 now itemizes Deuteronomy 12:5–6, 11, 26–27); P85 (TL-05-12-05); P155 (Exodus 20:8 is now Additional Scripture on C0129); N184 (TL-03-17-10 now itemizes Leviticus 17:10–12, 14); P99 (S062 is now Torah Law); P176 (S135 is now Torah Law); N286 (Exodus 23:1 is now Additional Scripture on C0157 (false witness)). It also linked Leviticus 12:3 to the Genesis circumcision record (P215) and keeps that record as the primary, by choice.

## Duplicates still open

| Records | Their labels | What to do | Origin |
| --- | --- | --- | --- |
| C0096, C0097 | Mosaic Instruction; Torah Law | C0096 (Instruction) still contains the not-raw and not-boiled rule now merged into C0097 (Torah Law); narrow C0096 to the positive manner of eating. | found in the 556 check, still open |
| C0883, C0884 | Torah Law; Mosaic Instruction | Both direct the Levites' portion from their tithe; C0884 adds 'best'. Narrow C0883 to 18:26–28 or merge; labels and classifications differ. | found in the 556 check, still open |
| C1024, C1025 | Mosaic Instruction; Torah Law | Both cover the same execution (13:10–11); C1024 only adds who strikes first. Narrow C1025 to the sentence (13:11) or merge; labels differ. | found in the 556 check, still open |
| C0146, C0995 | Torah Law; Torah Law | Deuteronomy 6:14 restates Exodus 20:3; both are now Torah Law. Link Deuteronomy 6:14 to C0146 instead of keeping two records. | found in the 556 check, still open |
| C0445, C0875 | Torah Law; Torah Law | Num 18:9–10 restates the most-holy eating rule (every male, holy place) for guilt, sin and grain offerings; add it to C0445, C0437, C0388. | found in the 556 check, still open |
| C0949, C1054 | Torah Law; Torah Law | Numbers 35:30 and Deuteronomy 17:6 both forbid a death sentence on one witness; one record could carry the other as Additional Scripture. | found in the 556 check, still open |
| C0201, TL-03-20-15 | Torah Law; Torah Law | TL-03-20-15 (Leviticus 20:15–16) states the human death penalty that C0201 (Exodus 22:18) already states. The revision's note names C0651 and C0593 but not C0201. Link Leviticus 20:15–16 to C0201 instead, as the 556 check suggested. | introduced by the revision |

- **Resolved by the revision: C1120, C1122.** The revision merged C1122 into C1120.
- **Resolved by the revision: C0391, C0389, C0390.** The revision retitled C0391 as the firstfruit permission ('Leaven and honey may be brought as firstfruits'). Its reference still includes Leviticus 2:11; narrowing it to 2:12 would finish the fix.
- **Left as a choice: C0129, AUD-02-31-13.** C0129 (keep the Sabbath holy: Exodus 16:23, with 20:8) and AUD-02-31-13 (keep the Sabbath as a sign: Exodus 31:13–17) state the same keeping of the day. The revision keeps the holy-day command and the covenant sign apart on purpose, so this report does not count it. C0152 (the weekly work and rest) is a separate clause.
- **Left as a choice: C0607, C1175.** Leviticus 19:13 (do not hold a worker's wages overnight) and Deuteronomy 24:14–15 (pay them before sunset) are the negative and positive forms of one duty. Maimonides counts both (N238 and P200), and the catalogue keeps positive and negative forms apart elsewhere, so this report does not count it.

Three Additional Scripture links now point at verses the revision gave their own records. The catalogue already does this in about 44 places, so they are not counted as duplicates:
- C0733 (Leviticus 25:41) lists Leviticus 25:54 as Additional Scripture; the revision made 25:54 its own record for the foreign-master case.
- C0212 (Exodus 22:29) lists Leviticus 22:27 as Additional Scripture; the revision also made 22:27 its own record for the eighth-day rule.
- C0019 (Genesis 9:4) and TL-03-17-10 both list Leviticus 3:17, 7:26–27 and Deuteronomy 12:23–25, 15:23 as Additional Scripture.

## Labels still inconsistent

The revision resolved 43 of the 70 label findings: the Ten Commandments, most positive duties beside their negative twins, and the regular offerings. It also re-pointed C0709 from the one-off sentence in Leviticus 24:14 to the standing law in 24:16. Still open:

| Group | Records |
| --- | --- |
| Clear correction (4) | ot-leviticus-v13-32 'The priest reexamines the skin lesion on the seventh day' (Torah · Historical direction study); C1041 'Do not begrudge your gift to the needy' (Mosaic Instruction); C1044 'Do not resent releasing the Hebrew servant after the prescribed service' (Mosaic Instruction); C1091 'Israel: do not fear the enemy in the prescribed war with God's promised presence' (Torah · Historical direction) |
| Positive duty under Instruction, negative twin under Torah Law (2) | C0215 'Dispose of the torn flesh by giving it to dogs' (Mosaic Instruction); C1150 'The man unclean through the stated nocturnal discharge: leave the military camp' (Mosaic Instruction) |
| Same ban under two labels (2) | C0800 'Do not put oil on the jealousy offering' (Mosaic Instruction); C0801 'Do not put frankincense on the jealousy offering' (Mosaic Instruction) |
| Standing observance under Instruction, comparable ones under Torah Law (9) | C0574 'Cover the hunted animal's blood with earth' (Mosaic Instruction); C0685 'Count the seven complete weeks and fifty days to the new grain offering' (Mosaic Instruction); C0702 'Take the prescribed branches and fruit for Booths' (Mosaic Instruction); C0716 'Count seven cycles of seven years for the Jubilee' (Mosaic Instruction); C0717 'Sound the Jubilee proclamation on the appointed Day of Atonement' (Mosaic Instruction); C0743 'Have a non-sacrificial vowed animal valued by the priest' (Mosaic Instruction); C0745 'Have a consecrated house valued by the priest' (Mosaic Instruction); C0827 'Aaron and sons: bless Israel with the appointed words and God's name' (Mosaic Instruction); C1181 'Administer judicial lashes under supervision in proportion to the offense' (Mosaic Instruction) |
| Conquest-era ban still a historical direction while its siblings are now Torah Law (2) | C0997 'Do not spare the peoples placed under the stated conquest judgment' (Torah · Historical direction); C1197 'Carry out the prescribed judgment against Amalek after the stated rest' (Torah · Historical direction) |
| Standing duty still under Mosaic Command (7) | C0616 'Reprove your neighbour' (Mosaic Command); C0636 'Revere God's sanctuary and holy things' (Mosaic Command); C0639 'Rise before the aged' (Mosaic Command); C0640 'Honour the elder' (Mosaic Command); C0768 'Levites: carry the tabernacle and its furnishings in their assigned service' (Mosaic Command); C0772 'Levites: guard the tabernacle and its furnishings' (Mosaic Command); C0774 'Aaron and sons: keep the priestly charge of altar and inner sanctuary' (Mosaic Command) |
| New: same practice under two labels (1) | C0573 'Drain the blood of animals killed for food, as prescribed' (Mosaic Instruction) |

The revision deferred some items on purpose. It keeps love of God and cleaving to him as covenant commands rather than reclassifying them "solely to match Maimonides' count". It also keeps the Deuteronomy 26:14 abstentions inside the tithe declaration. This report does not count those as errors.

## What the count would be

| Step | Change | Torah Law count |
| --- | ---: | ---: |
| Current Torah Law count |  | 638 |
| Clear fixes: fold C0995 into C0146 and TL-03-20-15 into C0201; move 3 in | +1 | 639 |
| Finish the Instruction / Torah Law alignment (14 records) | +14 | 653 |
| Conquest-era bans still historical (2) | +2 | 655 |
| Standing duties still under Mosaic Command (7), if they are to count | +7 | 662 |

Each step adds to the one before. The last step is a choice about the convention, not an error.

## What the 556 counted

The 556 were the records whose study placement was **Torah Law** (Mosaic type Law): God-given rules for a General audience in Exodus–Deuteronomy.
- **By book:** 251 in Leviticus, 140 in Deuteronomy, 106 in Exodus and 59 in Numbers. None were in Genesis.
- **Origin of the records:** 512 were original Torah requirement records and 44 were completeness-review additions.

The 556 left out several groups:
- **The Ten Commandments:** all 14 records were Mosaic Command.
- **Other Mosaic types:** 417 Mosaic Instruction, 10 Wisdom and 9 Commission records, plus the 58 Command records outside Exodus 20.
- **The Genesis laws** on blood, homicide and circumcision.
- **Broad records:** 177 passage groups and 144 topical studies.

Against the 613, the 556 itemized 419 commandments. 104 sat under other Mosaic labels, 20 sat in records with no Mosaic type, and 70 were not stated.

The 556 check also found:
- 1 duplicate, 4 records overlapping others in the same passage, and 5 laws recorded twice (2 of the 5 are now left as choices, as explained above);
- 70 label inconsistencies.

The workbook keeps every original finding, with its status in the current catalogue.

## Accuracy check

A separate reviewer, who had not seen the work, re-checked 62 findings against the 556-record catalogue: 40 of the 613 matches, 10 label findings and all 12 duplicate findings of the 556 check. **56 were correct, 4 partly right and 2 wrong.**

| Findings | Checked | Correct | Partly right | Wrong |
| --- | ---: | ---: | ---: | ---: |
| Commandment matches | 40 | 37 | 1 | 2 |
| Label findings | 10 | 8 | 2 | 0 |
| Duplicate findings | 12 | 11 | 1 | 0 |

What changed as a result:
- **N58** (partly): Removed S116 from N58; its status (only a historical direction, C1091) stands.
- **N171** (wrong): Corrected: N171 is itemized by C0655 at the 556 and now also by S126, which the revision made Torah Law.
- **P53** (wrong): Corrected: P53 is itemized by C0230 at the 556; the revision has since added Exodus 23:17 to C0230.
- **C0800** (partly): Regrouped C0800 and C0801 as 'same ban under two labels' beside C0418, which now holds both bans.
- **C0827** (partly): Kept, with new evidence: the revision has since made the lamps (C0284), incense (C0337) and daily offering (C0333) Torah Law, so the priestly blessing is now the odd one out.
- **C0129, AUD-02-31-13, C0152** (partly): Narrowed to C0129 and AUD-02-31-13. The revision keeps the holy-day command and the covenant sign apart on purpose, so this is left as a choice and not counted.

## Other findings

- **Editing notes in public text.** 132 public notes on 124 records still read as instructions to an editor, such as "extend to 22:9–10", "link as Additional Scripture" and "Rambam P103 is itemized…". Most come from audit notes copied into the catalogue. They are listed in the Edit notes sheet.
- **Errors in the source index.** For 12 commandments the index's source verse, or its mapping to the Saints text, was wrong: P43, P48, P58, P192, N45, N116, N119, N228, N266, N318, and N267 and N268, which are swapped. Each was matched by its number instead.

## How it was done

1. **The 613.** Six reviewers matched each of the 613 against the Saints text and every record on or near its source verse, starting from the 556-record catalogue (commit `3d53008`). The source verses come from the betemunah.org index of Sefer HaMitzvot, mapped to the Saints text.
2. **Duplicates and labels.**
   - All 214 same-passage pairs with a Torah Law record were reviewed, with the 78 closest cross-passage pairs.
   - 159 records picked by screens were reviewed for their labels.
3. **The revision.** Every finding was carried forward to the revised catalogue (commit `467e928`) using its merge index and change ledger, then checked again against the current catalogue (commit `00f33d1`). The revision's additions and new Torah Law records were screened again for duplicates.

## Files

| File | What it holds |
| --- | --- |
| [Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx](Saints-Bible-Torah-Law-Count-Check-2026-11-08.xlsx) | The review workbook, with each finding's status in the current catalogue |
| [findings-638.json](findings-638.json) | Current-state findings: the 613 now, gaps, open duplicates, open labels, count steps |
| [reconcile-638.json](reconcile-638.json), [edit-notes-638.json](edit-notes-638.json) | How each 556 finding was carried forward, and the edit notes in the current catalogue |
| [accuracy-check.json](accuracy-check.json) | The independent check: verdicts by kind and what changed |
| [maimonides-613.json](maimonides-613.json), [findings.json](findings.json) | The 556-based matching and findings |
| [summary.json](summary.json) | The 556-based totals |
| [review-records/](review-records/), [method/](method/), [scripts/](scripts/) | Reviewer output, briefs and scripts |

## Limits

- Matching a commandment to a record is a judgment.
- The label conventions were inferred from the catalogue's own usage and from the revision's stated criteria.
- The current-state statuses were carried forward from the 556 review, not reviewed again from scratch. The revision's new records were matched to the 613 by hand.
- The accuracy check covered a sample. Most label findings and commandment matches were not re-checked one by one.
- The live website was not opened. The catalogue was read from the repository.
