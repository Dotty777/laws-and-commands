# Independent review of the Round 2 Saints.Bible laws audit

**8 November 2026 · GitHub pull request #2 · merge commit 1845faf**

The draft finds real gaps, but several proposed records misstate the passage or its speaker, and some supporting links repeat the same verses or point to a different direction. Resolve those findings before using the workbook to update the catalogue. The pull request is already merged as a draft. Production and staging continue to serve the 6,416-record catalogue from before this audit. [Pull request #2](https://github.com/Dotty777/laws-and-commands/pull/2) · [Round 2 draft](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/README.md)

The [correction ledger](review-corrections.json) identifies each affected draft row, the editorial decision, and precise replacement fields where available. It covers specific findings from this review. An unlisted draft row has no decision in this ledger.

## Review scope and checks

| Item | Checked | Result |
| --- | ---: | --- |
| Proposed new records | 209 | Read the cited Saints passages and compared nearby catalogue records. All 209 IDs are unique and available. |
| Scripture extensions | 224 | Compared the additional passage with the target record. No original primary verses are dropped. Some additions change the speaker, subject, or directive. |
| Links on existing records | 328 | Compared the added and original passages. Six links overlap other proposed links on the same target. Several others need a related-context label or a different target. |
| Links on proposed records | 40 | Checked their passages and first-verse anchors. Eleven context notes are blank. Some linked accounts differ on details central to the record. |
| Topic changes | 595 | All refer to eligible records and use existing category names. In a stratified 36-record sample, 26 assignments fit, eight had a more specific alternative, and two were clearly mismatched. |
| Workbook | 1 | Compared proposal tabs with the machine-readable files. The shared fields and link lists match. None of the sheets has native hyperlinks. |

All draft Scripture endpoints resolved. The 577 supplied URLs for new records and supporting Scripture use the matching published first-verse anchor. The 1,156 decision IDs are unique. The declined decisions and projected coverage were checked structurally, with the detailed Scripture review focused on the proposals to add or change records. The topic sample was stratified by confidence and category breadth. It does not estimate an error rate for all 595. [Proposal files](https://github.com/Dotty777/laws-and-commands/tree/1845faf/audit/round-2) · [Saints Translation exports](https://github.com/Dotty777/laws-and-commands/tree/1845faf/source/translation)

## New records that need correction

| Proposal | Passage and correction |
| --- | --- |
| AUD-01-44-9 | Genesis 44:9 records the brothers proposing death for the holder of the cup and offering their own enslavement. The steward states different terms in verse 10. Keep their unaccepted proposal as context for the ruling. |
| AUD-06-6-26 | Joshua 6:26 gives an oath-curse concerning whoever rebuilds Jericho. First Kings 16:34 expressly identifies the fulfillment as the Lord’s word through Joshua. Use both passages and title it as the oath-curse or covenant warning. The source gives no separately stated legal prohibition. |
| AUD-10-12-5 | David pronounces a verdict on the man in Nathan’s parable. Label the fictional verdict and its teaching or context. |
| AUD-10-12-25 | The narrative reports the child receiving a name through Nathan. It does not quote a command to give that name. |
| AUD-11-11-37 | First Kings 11:37 promises Jeroboam the kingship. Verse 38 makes the Lord’s support and the promise of a lasting house conditional on obedience. The draft title attaches that condition to the wrong promise. |
| AUD-13-27-1 | First Chronicles 27:1 lists the divisions that served by month. The verse does not report David commissioning them. |
| AUD-14-8-7 | The Saints text in 2 Chronicles 8:7–9 and 1 Kings 10:22b–c says Solomon placed the remaining peoples under tribute and describes the roles of Israelite men. Describe the reported policy as historical context. The draft’s “conscripts” and “enslaves no Israelite” go beyond the primary passage. |
| AUD-14-36-3 | The parallel is real, but the Saints readings give different gold amounts. Second Chronicles 36:3 gives one talent, while 2 Kings 23:33 gives one hundred. Keep the accounts and state the difference in the source note. |
| AUD-15-7-35 and AUD-16-14-31 | Both record Nicanor demanding that Judas be handed over and threatening the temple. Both drafts identify the other account as parallel, but neither includes the link. Use 2 Maccabees 14:31–33 for the explicit order and link 1 Maccabees 7:35 with its distinct wording. |
| AUD-16-7-1 | Second Maccabees 7 describes an attempt to force the family to eat forbidden pork, followed by refusal. Use “tries to force” or “orders them to eat.” |
| AUD-16-8-21 | Second Maccabees 8:22–23 names Simon, Joseph, and Jonathan and explicitly puts Judas over the first company. Preserve their separate roles. |
| AUD-16-12-3 | The common decree is invoked in the invitation to board in 2 Maccabees 12:3–4. The drowning is the narrated outcome. State those roles separately. |
| AUD-16-14-39 | Second Maccabees 14:39 says **more than** five hundred soldiers. The title gives exactly five hundred. |
| AUD-16-15-30 | In 2 Maccabees 15:30–33 Judas orders the head and hand cut off and carried, displays them himself, cuts out the tongue, and orders it fed to the birds. The title treats some of his own acts as orders. |
| AUD-22-30-15 | Proverbs 30:1 in the Saints Greek text does not name Agur. If using that name, label it as the Hebrew attribution. |
| AUD-28-21-12 | The watchman replies to the person calling from Seir. The oracle setting alone does not identify the reply as God’s speech. |
| AUD-28-24-16 | Isaiah reports words from the ends of the earth and a coming woe. A mixed divine and human directive is unsupported. Use Study Context if retaining the passage. |
| AUD-44-4-3 | The source is the tempter, whom Matthew does not present as human. Name the speaker and use the catalogue’s context classification where appropriate. The Luke 4 references promised in the rationale are missing from the compiled record. |
| AUD-44-12-43 | Matthew 12:43–45 is a distinct teaching illustration. Its proposed Luke 11:24–26 parallel appears in the rationale but is missing from the compiled record. |
| AUD-44-26-59 | Matthew records a particular adjuration and verdict. Luke 22:66–71 records a related hearing but no death verdict. Preserve the difference and use historical context for the one-case ruling. |
| AUD-46-1-15 | Gabriel tells Zechariah what John will do. John is the subject of the prediction and Zechariah is its recipient. The title presents an express prohibition addressed to John. |
| AUD-47-18-38 | Pilate explicitly invokes a Passover custom and makes an offer. Use historical context for the custom. The passage does not establish a standing Law. |
| AUD-51-10-1 | Paul appeals to the Corinthians and describes his ministry in the first person. Preserve that appeal and setting. The proposed title turns the description into a general order to wage spiritual warfare. |
| AUD-58-3-14 | First Timothy 3:14–15 gives Paul’s reason for writing. Attach it as context for the existing church-order instructions. The verse does not state a separate conduct rule. |

[New records and their review notes](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/new-records.json)

## Scripture changes that need correction

| Existing record | Draft addition | Review |
| --- | --- | --- |
| C0156 | Deuteronomy 27:24 | The curse concerns striking a neighbor treacherously. The verse does not state that the neighbor died. Use context about violence or leave the murder record’s Scripture as filed. |
| C0485 | Eight Leviticus 13 links | The priest makes examinations throughout the chapter, but the diagnostic signs differ by case. Explain the distinct criteria or itemize separate procedures. |
| ot-joshua-v8-4 | Joshua 8:3 | The preceding verse describes Joshua selecting and sending the soldiers. It can supply context for the quoted ambush order that follows. |
| AUD-06-9-21 | Joshua 9:27 | The labor assignment is the same subject. The leaders speak in verse 21, while Joshua makes the formal appointment in verse 27. Correct the note claiming the same speaker. |
| ot-judges-v17-10 | Judges 17:11–12 | The added text narrates the Levite accepting Micah’s terms and becoming his priest. Identify it as outcome or context rather than additional wording of Micah’s instruction. |
| ot-judges-v19-8 | Judges 19:9 and 19:6–7 | The record’s afternoon invitation differs from an invitation to lodge overnight. Treat the related invitations as distinct or explain the difference. |
| ot-1-samuel-v19-2 | 1 Samuel 19:3 | Jonathan describes his own plan to speak with Saul and report back. Use context for the warning in verse 2. |
| ot-2-kings-v1-2 | 2 Kings 1:4 | Ahaziah orders his messengers to inquire of Baal. The Lord’s separate rebuke and warning in verse 4 belongs with the message retold in ot-2-kings-v1-6. |
| AUD-10-5-8 | 1 Chronicles 11:6 | Chronicles promises command to the first attacker. Samuel gives instructions for the attack. Link the related siege account with a note explaining the different orders. |
| AUD-21-40-2 | Greek Psalm 40:3–4 | These verses ask the Lord to protect and sustain the person. The draft calls the petitions promises from God. |
| AUD-21-82-4 | Greek Psalm 82:13 | The verse’s immediate context invokes earlier rulers, and its stated goal differs from the plot in 82:4–5. Use related context and preserve the uncertainty about the speaker. |
| ot-jeremiah-v28-62 | Jeremiah 28:61 | The added verse contains Jeremiah’s charge to Seraiah to read the words. Retitle the record if expanding it beyond the prayer or acknowledgment in verse 62. |
| K096 | Matthew 15:24 | This says where Jesus Himself was sent. K096 records where Jesus sends the Twelve. Preserve both recipients if using the passage as related context. |
| C1077 | Acts 7:37 | This repeats the prediction of a prophet. Acts 3:22 also quotes the direction to hear him. Only the latter reproduces the direction captured by the target. |
| AUD-50-16-20 | Philippians 4:21 | The greeting does not prescribe a holy kiss. Romans 16:16 is an actual parallel and is already in the record. |
| C0554 | Hebrews 5:3 | The verse describes a priest offering for himself and for the people. It does not repeat the rule specifying a bull and atonement for the priest’s household. |
| X009 and X010 | Revelation 2:1 and 2:8 | Jesus charges John to write. The existing studies concern conduct addressed to the churches. The writing commission can supply letter context with its separate recipient. |

[Scripture extensions](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/extend.json) · [Parallel links](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/parallel.json)

### Six overlapping link pairs

| Existing record | Proposed link | Proposed link it overlaps |
| --- | --- | --- |
| C0771 | Numbers 2:18–23 | Numbers 2:10–15, 18–23, 25–30 |
| C0771 | Numbers 2:25–30 | Numbers 2:10–15, 18–23, 25–30 |
| C0920 | Numbers 34:13 | Numbers 33:54, 34:13 |
| AUD-46-7-24 | Matthew 11:11 | Matthew 11:11–14 |
| AUD-44-15-12 | Luke 6:39 | Luke 6:39–40 |
| AUD-50-9-15 | 2 Corinthians 12:14–15 | 2 Corinthians 12:13–18 |

Choose one citation or split it by distinct teaching, preserving useful notes. For Luke 6:39–40, the blind guides saying matches the target. Verse 40 gives a separate saying about a disciple and teacher. [Parallel proposals](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/parallel.json)

## Topic, anchor, and coverage findings

- **Romans 2:1–11 (AUD-49-2-1)** concerns judging others while doing the same things and God’s impartial judgment. **Judging and Forgiving** fits the record. **Done to Be Seen** describes a different issue in the original topic archive. **Luke 4:43 (AUD-46-4-43)** states Jesus’ mission to announce God’s kingdom elsewhere. **The Sending** fits its stated subject better than **Repent and Believe**, since the verse gives no such appeal. [Topic proposals](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/topic-fixes.json)
- **X012** is a confirmed existing link repair. Revelation 22:8–9 opens at 22:9. Point it to **22:8** so the popup starts with John’s action and then shows the angel’s correction. [Correct Saints Scripture anchor](https://saints.bible/bible/glory/revelation/chapter-22/#v22-8)
- **The coverage percentages are projections.** The per-book totals reconcile, but the coverage code uses the older reference expander, which can count lettered continuations from a bare reference. For example, it can count 1 Kings 2:35a and following under a record explicitly narrowed to 2:35. Use the same exact-verse rules for compilation and coverage. The script also labels 2,617 residual verses as “read in round 1 and judged not to need a record” by default if they do not fall into either other category. That is an inference rather than a verse-by-verse review log. [Coverage code](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/scripts/cov2.py) · [Remaining-verse logic](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/scripts/r2_remaining.py)
- **The workbook needs a separate import step.** Its proposal tables match the JSON, but they have no native Scripture hyperlinks and include 11 blank source notes on new-record links. Generate the final catalogue with verified hyperlinks after correcting source roles, titles, and topics. [Draft workbook](https://github.com/Dotty777/laws-and-commands/blob/1845faf/audit/round-2/Saints-Bible-Associated-Verses-Round-2-2026-11-08.xlsx)

## Supported examples

- **Leviticus 15:9 (AUD-03-15-9)** states a distinct saddle-impurity rule. **Leviticus 24:22 (AUD-03-24-22)** gives equal judicial treatment to resident alien and native.
- **2 Kings 25:22 (AUD-12-25-22)** reports Nebuchadnezzar appointing Gedaliah over the people left in Judah. **Esther 4:5 (AUD-19-4-5)** reports Esther commissioning Achrathaeus to learn what happened to Mordecai.
- **Proverbs 5:8–14** continues the existing warning, while **Proverbs 9:13–18** supplies Folly’s invitation and its consequences.
- **Luke 14:15–24 (AUD-46-14-15)** supports a separate study of the great supper. **Acts 25:6 and 25:17 (AUD-48-25-6)** give Festus’s order and his explicit retelling.
- **Hebrews 7:17** quotes the priesthood appointment in **Greek Psalm 109:4**. **Nehemiah 7:65** repeats the governor’s instruction in **Ezra 2:63**.
