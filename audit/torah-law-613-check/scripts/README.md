# Scripts

These ran in a scratch workspace, with the repository checked out at `/home/claude/repos/laws-and-commands`. The paths in them are as run. They need Python 3.11 and openpyxl, and they import [audit_lib.py](../../scripts/audit_lib.py).

Order of the run:
1. `prep613.py`, `tl_candidates.py`, `prep_dl.py` build the review batches.
2. `validate_613.py` and `validate_dl.py` check the reviewer output in [review-records](../review-records/).
3. `compile_tl.py` and `findings_tl.py` produce the 556-based findings.
4. `validate_check.py` checks the accuracy-check verdicts, and `apply_check.py` applies them.
5. `reconcile_638.py` and `final_638.py` carry the findings forward to the current catalogue.
6. `make_report_tl2.py` writes the README, and `build_xlsx_tl2.py` builds the workbook.
