# Scripts

These ran in a scratch workspace beside the repository. The paths in them are as run.

Order of the run:
1. `prep_cat.py` builds the review batches in [method/batches](../method/batches/): each Torah Law record with its Saints Translation verse text, topic, classification, original audience and Maimonides matches.
2. Seven reviewers classified the batches from [the brief](../method/brief.md). `validate_cat.py` checked each output in [review-records](../review-records/).
3. `consistency_cat.py` compared recurring kinds of law across the batches.
4. `compile_cat.py` writes the category layer, `data/current/torah-law-categories.json`.
5. `accuracy_cat.py` compares the blind re-check (`K1`) with the reviewers' answers and writes [accuracy-check.json](../accuracy-check.json).
6. `make_report_cat.py` writes the README, and `build_xlsx_cat.py` builds the workbook.

After that, the repository's own `scripts/build_torah_law_categories.py` normalizes the JSON and writes the CSV, and `scripts/build_browse.py` builds the browse pages.
