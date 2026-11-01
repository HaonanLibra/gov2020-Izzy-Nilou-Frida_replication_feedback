# Replication of "Wired for Change? How Democratic Diasporas Undermine Autocracies"

Gov 2020 replication assignment. Haonan Tian, replicating Davis, Lopez-Bravo & Sunby.

* **`memo.md`**: the memo to the authors (start here).
* `code/`: my replication and stress-test scripts (the authors' data and code are not redistributed here).
* `output/`: everything the scripts produce.

## Reproduce

```bash
pip install -r requirements.txt
# use the REAL country_converter: remove the local country_converter.py shim from the authors' folder first
bash run_all.sh /path/to/diaspora_telecom_figures      # < 1 minute
```

Tested with Python 3.13, pandas 3.0.5, numpy 2.5.3, statsmodels 0.15.0, matplotlib 3.11.2, geopandas 1.2.0, country_converter 1.3.2, pycountry 26.2.16.

| Script | What it does | Output |
|---|---|---|
| (authors) `make_all_figures.py` | Unmodified run | `output/replication/` (+ `comparison_vs_expected.txt`: all 8 tables identical, max diff ≈ 1e-13) |
| `code/compare_to_expected.py` | Cell-by-cell comparison with the authors' `expected_output/` | same |
| `code/codefix_rerun.py` | Re-runs the authors' script with ccode 347 → SRB (it is mapped to Kosovo) | `output/codefix/` |
| `code/stress_tests.py` | T1 direction of the volatility effect · T2 pre-trend placebo · T3 leave-one-region/country-out · T4 informativeness of the telecom null + within-year telecom · T5 destination-type formal tests | `output/stress_tests/` |
| `code/horse_race.py` | T6 diaspora democracy vs diaspora host-wealth (and host civil liberties) | `output/stress_tests/T6_*` |
| `code/fig5_variants.py` | Attempts to reproduce the draft's destination-type figure | `output/stress_tests/fig5_variants_log.txt` |
