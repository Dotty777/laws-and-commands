# Brief: categorize Torah Law records by form and by category

You are classifying records from the Saints.Bible catalogue of Mosaic Torah Laws (646 records in all, split into batches). Each record states one standing provision from Exodus–Deuteronomy. For every record in your batch you assign:

1. **Form**, following the Jewish mitzvot tradition: Positive, Negative or Permission.
2. **Category**, following the traditional Christian division of the Mosaic law: Moral, Ceremonial or Civil, with an optional second category.
3. **Ceremonial area**, when Ceremonial is the category or the second category.

Read this brief in full before starting. Work from the Saints Translation verse text supplied with each record. The record title is an editorial paraphrase: use it to see what the provision is, but decide the form from the verse.

## Input fields (one JSON object per record)

- `id`, `reference`, `title`: the record and its primary Scripture.
- `verse_text`: the Saints Translation text of the primary reference, verse labels in brackets.
- `topic`: the catalogue's subject group.
- `classification`: the site's own application label (how the law relates to Christians). It is NOT the category you are assigning; see "Notes" below.
- `original_audience`: who the provision addresses (Israel, priests, judges, an offerer, etc.).
- `context_note`: the catalogue's note, if any.
- `maimonides`: commandments from Maimonides' 613 (Sefer HaMitzvot numbering) that this record was matched to. `P` = positive, `N` = negative. Strong evidence for the form, but check it against the verse.

## 1. Form

- **Positive**: the provision requires an action or a procedure, or a legal status or consequence that must be applied. This includes:
  - duties of priests, Levites, judges or the court, including carrying out a penalty (Maimonides counts court penalties as positive commandments);
  - rules that define a status to be applied, such as impurity periods, valuations or inheritance shares (Maimonides counts the impurity laws as positive commandments);
  - restitution and repayment duties.
- **Negative**: the provision forbids an action ("do not", "you shall not", "no one may", "must not", "shall not be eaten").
- **Permission**: the provision allows something without requiring it ("may eat", "may collect", "may be brought", "may again eat").

Rules:
- Judge by the operative words of the verse, not by the wording of the title. A title like "Keep the Sabbath free of work" can rest on a "you shall not do any work" verse.
- If the `maimonides` seeds are all P, the form is usually Positive; all N, usually Negative. If you disagree with the seeds, explain in the note.
- **mixed**: set `true` when the provision as recorded holds both a requirement and a prohibition (for example "remember the Sabbath … you shall not do any work"; P and N seeds together often signal this). Then give the form of the provision's main operative clause as the title defines it, and say in the note what the other clause is.
- `form_basis`: the operative words that decide the form, quoted from the verse (8 words or fewer), with the verse number, e.g. `"you shall not eat their flesh" (11:8)`. For a penalty or status rule you may add a short label, e.g. `court penalty: "shall surely be put to death" (22:18)`.

## 2. Category (traditional Christian division)

This follows the classic division of the Mosaic law into moral, ceremonial and civil (judicial) laws (Thomas Aquinas; Westminster Confession, chapter 19). Assign the one that best describes the provision itself:

- **Moral**: a duty of love toward God or neighbour, stated as right or wrong in itself rather than as a rite of Israel's worship or a rule of Israel's courts. Examples: exclusive worship of God; no idols for worship; no divination, sorcery or consulting the dead; no child sacrifice; no blasphemy or false oaths; honour parents and elders; no murder; the sexual prohibitions (adultery, incest, bestiality and the like); no theft or fraud; honest weights and measures; no false witness or slander; no hatred or vengeance; love of neighbour and stranger; justice and impartiality as personal duties; care for the poor, widow, orphan and stranger as personal duties; no coveting.
- **Ceremonial**: a rite or holiness rule of Israel's worship under the old covenant. Examples: sacrifices and offerings; tithes, firstfruits and firstborn given to God; the priesthood, the Levites and the sanctuary; ritual purity and cleansing; dietary laws; festivals, holy days and Sabbath rites; covenant signs (circumcision, tassels); vows, Nazirites, dedications, valuations and devoted things; separation laws (mixed seed, mixed cloth, mixed yoking).
- **Civil**: a rule for Israel as a nation: its courts, penalties, government, land and economy. Examples: judges, witnesses and court procedure; penalties and their execution; restitution and damages; property and boundaries; lending, interest, pledges and debt release; servants and hired workers; marriage, divorce and inheritance as legal procedures; land tenure, the sabbatical year and Jubilee as land and economic law; gleaning rights; warfare and kingship; cities of refuge; public order and camp hygiene.

Tie-breakers:
- A prohibition of a wrong act is Moral. A penalty or court procedure for that act is Civil, with Moral as the second category when the underlying act is a moral wrong.
- The Ten Commandments are Moral. The weekly Sabbath rest commanded there, and its restatements, is Moral with Ceremonial (Festivals and holy days) as the second category. Detailed Sabbath rites (offerings, the showbread, no kindling of fire) are Ceremonial.
- The sabbatical year and the Jubilee are Civil, with Ceremonial (Festivals and holy days) as the second category when the provision concerns their sacred proclamation or observance.
- Provisions for the poor at harvest (gleaning, corners, forgotten sheaves) are Civil with Moral as the second category.
- Food laws are Ceremonial (Dietary laws) even where the site's classification says the law continues (for example the blood prohibition).
- Kingship, war, and conquest provisions are Civil unless the provision is itself a rite (then Ceremonial) or an idolatry ban (then Moral).

**secondary**: give a second category only when the provision clearly has a second character under these definitions (as in the tie-breakers). Leave it empty otherwise. It must differ from the category.

## 3. Ceremonial area

Required when the category or the second category is Ceremonial; empty otherwise. Use exactly one of:

- `Sacrifice and offerings`: sacrifices, offerings, tithes, firstfruits, firstborn animals for the altar, the priests' and Levites' portions as offerings.
- `Priesthood and sanctuary`: priests' and Levites' qualifications, conduct, garments and duties; the tabernacle, its furnishings and holy things; access to the sanctuary; the high priest.
- `Dietary laws`: clean and unclean animals, blood, fat, carcasses, the kid in its mother's milk, fruit of young trees, and other food prohibitions.
- `Ritual purity`: impurity and cleansing (corpses, skin disease, discharges, childbirth, menstruation), purity of the camp as a holiness rule.
- `Festivals and holy days`: the Sabbath's ceremonial aspects, new moons, Passover, Unleavened Bread, Weeks, Trumpets, the Day of Atonement, Booths, and the sacred aspects of the sabbatical year and Jubilee.
- `Signs, vows and dedications`: circumcision, tassels, mixed-kind separations, vows, Nazirites, valuations, devoted things, redemption of firstborn sons, consecrated items.

## Confidence and notes

- `confidence`: `high` when the provision clearly fits; `medium` when the definitions allow two readings; `low` when you are unsure.
- `note` (30 words or fewer) is REQUIRED when any of these hold, and optional otherwise:
  - `confidence` is not `high`;
  - `mixed` is `true`;
  - you disagree with the `maimonides` seeds;
  - your category departs from the usual pairing with the site's classification: "Israel’s civil and land laws" with Civil; "Covenant-specific instructions" with Ceremonial; "Fulfilled" with Ceremonial; "Everlasting" or "Unchanged" with Moral. Say briefly why.

## Output

Write one JSON object per line (JSONL) to the output path given in your task, in batch order, then a final line `{"done": true, "n": <number of records>}`. Use exactly these keys:

```
{"id": "C0091", "form": "Positive", "mixed": false, "form_basis": "\"it shall be the first month\" (12:2)", "category": "Ceremonial", "secondary": "", "area": "Festivals and holy days", "confidence": "high", "note": ""}
```

Allowed values: `form` ∈ Positive, Negative, Permission · `category` ∈ Moral, Ceremonial, Civil · `secondary` ∈ "", Moral, Ceremonial, Civil · `area` ∈ "" or one of the six areas above · `confidence` ∈ high, medium, low · `mixed` is true or false.

When you finish, run the validator named in your task and fix any problem it reports. Do not edit the batch file or any repository file.
