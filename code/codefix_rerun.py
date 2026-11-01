"""Re-run the authors' make_all_figures.py with one change: the country-code fix.

ccode 347 in Replication_Migration.dta is Yugoslavia / Serbia-Montenegro (1991-2006), not Kosovo.
country_converter maps GW 347 -> XKX, so Serbia's Milosevic-era autocracy-years lose their diaspora
exposure in the V-Dem panel (Figs 2-4) and get no telecom data in Fig 3. Here 347 -> SRB.

Usage:  python codefix_rerun.py <path to authors' package folder> <output folder>
"""
import sys, shutil, re
from pathlib import Path
src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
code = (src / "make_all_figures.py").read_text()
old = 'manual = {255: "DEU",'
assert old in code
code = code.replace(old, 'manual = {347: "SRB", 255: "DEU",')
(out / "make_all_figures_codefix.py").write_text(code)
if not (out / "data").exists():
    (out / "data").symlink_to((src / "data").resolve())
