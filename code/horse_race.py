"""T6  Wealth vs Democracy hypotheses with the replication file's own continuous measures:
diaspora-weighted host democracy (q2meanpol_lasflowsout) vs diaspora-weighted host log GDP pc (q2meanlgdp_lasflowsout),
both built from the same gravity-predicted flows. Also host civil-liberty measures (freedom of movement, speech, assembly).
Fig-3/Fig-2 main sample & controls (Polity autocracies 1981-2005, year FE, country-clustered SEs).
Usage: python horse_race.py <authors' package folder> <output folder>"""
import sys, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
P, OUT = sys.argv[1], sys.argv[2]
r = pd.read_csv(f"{P}/derived/diaspora_telecom_panel.csv")
R = r[r.year.between(1981, 2005) & (r.autocracy == 1)].copy()
z = lambda s: (s - s.mean()) / s.std()
X = {"DEM": "diaspora_dem", "WEALTH": "q2meanlgdp_lasflowsout", "FREEMOVE": "q2meanfor_lasflowsout",
     "SPEECH": "q2meanspeech_lasflowsout", "ASSN": "q2meanassn_lasflowsout"}
for k, v in X.items(): R[k] = z(R[v])
print("corr(DEM, WEALTH) in sample:", round(R[["DEM", "WEALTH"]].corr().iloc[0, 1], 3))
CTRL = ["lgdpcap_1", "growth2_1", "lpop_1", "urban_1", "fueldep_1", "log_durable", "polity_s", "regionpolity_1",
        "communist_1", "geddesmil_1", "geddesparty_1", "violence_domestic_1", "aid2_1", "diaspora_size"]
rows = []
for y in ("d5pol_s_1", "f5bmr_1", "frfailure5_1", "firreg5_c_1"):
    S = r[r.year.between(1981, 2005) & (r.bmr_1 == 0)].copy() if y == "f5bmr_1" else R
    if y == "f5bmr_1":
        for k, v in X.items(): S[k] = (S[v] - R[v].mean()) / R[v].std()
    for lab, xs in (("DEM alone", ["DEM"]), ("WEALTH alone", ["WEALTH"]), ("DEM + WEALTH", ["DEM", "WEALTH"]),
                    ("SPEECH + WEALTH", ["SPEECH", "WEALTH"]), ("ASSN + WEALTH", ["ASSN", "WEALTH"])):
        d = S.dropna(subset=[y] + xs + CTRL + ["DEM", "WEALTH"])          # common sample across columns
        m = smf.ols(f"{y} ~ {' + '.join(xs + CTRL)} + C(year)", data=d).fit(cov_type="cluster", cov_kwds={"groups": d.ccode})
        for x in xs:
            rows.append(dict(outcome=y, model=lab, term=x, coef=m.params[x], se=m.bse[x], p=m.pvalues[x], N=int(m.nobs)))
t = pd.DataFrame(rows); t.to_csv(f"{OUT}/T6_wealth_vs_democracy_horse_race.csv", index=False)
st = lambda p: "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""
t["cell"] = t.apply(lambda q: f"{q.coef:+.3f}{st(q.p)} ({q.se:.3f})", axis=1)
print(t.pivot_table(index=["model", "term"], columns="outcome", values="cell", aggfunc="first").to_string())
