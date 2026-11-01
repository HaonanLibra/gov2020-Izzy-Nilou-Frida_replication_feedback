#!/usr/bin/env bash
# Reproduce every number in memo.md.
#   bash run_all.sh <path to the authors' diaspora_telecom_figures folder>
# Requires: pip install -r requirements.txt  (the REAL country_converter; delete the authors' local country_converter.py shim first)
set -euo pipefail
PKG="$(cd "$1" && pwd)"; HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$HERE/output"
if [ -f "$PKG/country_converter.py" ]; then
  echo "ERROR: $PKG/country_converter.py (offline shim) would shadow the real package. Remove or rename it first." >&2; exit 1
fi
mkdir -p "$OUT/replication" "$OUT/codefix" "$OUT/stress_tests"

echo "1/5  Authors' script, unmodified"
(cd "$PKG" && python make_all_figures.py > "$OUT/replication/run_log.txt" 2>&1)
cp -r "$PKG/results" "$PKG/figures" "$OUT/replication/"
python "$HERE/code/compare_to_expected.py" "$PKG/results" "$PKG/expected_output/results" | tee "$OUT/replication/comparison_vs_expected.txt"

echo "2/5  Country-code fix (ccode 347 -> SRB)"
TMP="$(mktemp -d)"; python "$HERE/code/codefix_rerun.py" "$PKG" "$TMP"
(cd "$TMP" && python make_all_figures_codefix.py > "$OUT/codefix/run_log.txt" 2>&1); cp -r "$TMP/results" "$OUT/codefix/"

echo "3/5  Stress tests T1-T5";  python "$HERE/code/stress_tests.py" "$PKG" "$OUT/stress_tests" > /dev/null
echo "4/5  Horse race T6";       python "$HERE/code/horse_race.py"   "$PKG" "$OUT/stress_tests" > "$OUT/stress_tests/T6_log.txt"
echo "5/5  Fig-5 variants";      python "$HERE/code/fig5_variants.py" "$PKG" > "$OUT/stress_tests/fig5_variants_log.txt"
echo "Done -> $OUT"
