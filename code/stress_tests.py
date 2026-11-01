"""Stress tests for "Wired for Change? How Democratic Diasporas Undermine Autocracies".

Run AFTER the authors' make_all_figures.py (it reads their derived/ panels and data/).
    python stress_tests.py <authors' package folder> <output folder>

Every test re-uses the authors' own sample definitions, controls, standardisation, year FE and
country-clustered SEs, and changes one thing at a time.

  T1  Direction: is |5-yr change| (the "instability" proxy) driven by up-moves or down-moves?
  T2  Placebo / pre-trend: does diaspora democracy at t "predict" the change from t-5 to t?
  T3  Leave-one-region-out and leave-one-country-out for the main diaspora-democracy coefficients.
  T4  What the telecom null can and cannot rule out (95% CI of D x T relative to the main effect),
      plus a within-year standardised telecom measure (removes the 1980s-vs-2000s technology drift).
  T5  Destination-type figure: formal tests of the Wealth vs Democracy hypotheses (b_PD - b_RD, b_RD - b_RA),
      neighbour-democracy control, country FE, region drops.
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
P, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
stars = lambda p: "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
log = open(OUT / "stress_tests_log.txt", "w")
def say(*a):
    s = " ".join(str(x) for x in a); print(s); log.write(s + "\n")

rep = pd.read_csv(P / "derived/diaspora_telecom_panel.csv")
pub = pd.read_csv(P / "derived/diaspora_remittance_vdem_panel.csv").sort_values(["iso3", "year"])

REP_CTRL = ["lgdpcap_1", "growth2_1", "lpop_1", "urban_1", "fueldep_1", "log_durable", "polity_s", "regionpolity_1",
            "communist_1", "geddesmil_1", "geddesparty_1", "violence_domestic_1", "aid2_1"]
PUB_CTRL = ["lgdppc", "growth", "lpop", "urban", "trade", "oilrents", "aid", "v2x_polyarchy", "regdem"]

def ols(df, y, rhs, need, g, fe="C(year)"):
    d = df.dropna(subset=[y] + need + [g, "year"])
    m = smf.ols(f"{y} ~ {rhs} + {fe}", data=d).fit(cov_type="cluster", cov_kwds={"groups": d[g]})
    return m, d

def zscore(df, col):
    r = df[col].dropna(); return (df[col] - r.mean()) / r.std()

# ---------------------------------------------------------------- samples as in fig2 (main spec 3)
R = rep[rep.year.between(1981, 2005) & (rep.autocracy == 1)].copy()
R["D_z"] = zscore(R, "diaspora_dem"); R["SIZE"] = R.diaspora_size
V = pub[pub.year.between(1981, 2010) & (pub.autocracy_vdem == 1)].copy()
V["D_z"] = zscore(V, "diaspora_dem"); V["SIZE"] = V.diaspora_size
RHS_R = "D_z + SIZE + " + " + ".join(REP_CTRL); NEED_R = ["D_z", "SIZE"] + REP_CTRL
RHS_V = "D_z + SIZE + " + " + ".join(PUB_CTRL); NEED_V = ["D_z", "SIZE"] + PUB_CTRL
rows = []

# ================================================================ T1 direction of the volatility effect
say("=" * 90 + "\nT1  Which direction drives |5-yr change|?  (fig2 main spec, V-Dem autocracies 1981-2010)")
# backward-looking lags for T2 are built on the full panel so gaps are respected
g = pub.groupby("iso3")
for var, lab in (("v2x_polyarchy", "vdem"), ("polity_s", "polity")):
    ok = g.year.shift(5) == pub.year - 5
    pub[f"b5_{lab}"] = (pub[var] - g[var].shift(5)).where(ok)
V = V.merge(pub[["iso3", "year", "b5_vdem", "b5_polity"]], on=["iso3", "year"], how="left")
for lab in ("vdem", "polity"):
    V[f"up5_{lab}"] = V[f"d5_{lab}"].clip(lower=0)            # democratising part
    V[f"down5_{lab}"] = (-V[f"d5_{lab}"]).clip(lower=0)       # autocratising part
    thr = 0.10 if lab == "vdem" else 0.15                      # 0.15 on the 0-1 Polity scale = 3 Polity points
    V[f"bigup_{lab}"] = (V[f"d5_{lab}"] >= thr).astype(float).where(V[f"d5_{lab}"].notna())
    V[f"bigdown_{lab}"] = (V[f"d5_{lab}"] <= -thr).astype(float).where(V[f"d5_{lab}"].notna())
for y in ["abs5_vdem", "d5_vdem", "up5_vdem", "down5_vdem", "bigup_vdem", "bigdown_vdem",
          "abs5_polity", "d5_polity", "up5_polity", "down5_polity", "bigup_polity", "bigdown_polity"]:
    m, d = ols(V, y, RHS_V, NEED_V, "iso3")
    rows.append(dict(test="T1 direction", outcome=y, spec="fig2 main spec", coef=m.params.D_z, se=m.bse.D_z,
                     p=m.pvalues.D_z, N=int(m.nobs), mean_y=d[y].mean()))
    say(f"  {y:16s} coef={m.params.D_z:+.4f}{stars(m.pvalues.D_z):3s} se={m.bse.D_z:.4f}  N={int(m.nobs)}  mean={d[y].mean():.3f}")

# ================================================================ T2 placebo: past change
say("=" * 90 + "\nT2  Placebo: diaspora democracy at t vs the change that ALREADY happened (t-5 -> t)")
say("    (controls that are themselves measured at t, e.g. current democracy, are dropped for the placebo)")
PUB_CTRL_NOLEVEL = [c for c in PUB_CTRL if c != "v2x_polyarchy"]
rhs_pl = "D_z + SIZE + " + " + ".join(PUB_CTRL_NOLEVEL); need_pl = ["D_z", "SIZE"] + PUB_CTRL_NOLEVEL
for y in ("d5_vdem", "b5_vdem", "d5_polity", "b5_polity"):
    m, d = ols(V, y, rhs_pl, need_pl, "iso3")
    rows.append(dict(test="T2 placebo", outcome=y, spec="no level control", coef=m.params.D_z, se=m.bse.D_z,
                     p=m.pvalues.D_z, N=int(m.nobs), mean_y=d[y].mean()))
    say(f"  {y:10s} ({'future' if y.startswith('d5') else 'PAST  '}) coef={m.params.D_z:+.4f}{stars(m.pvalues.D_z):3s} "
        f"se={m.bse.D_z:.4f} N={int(m.nobs)}")
# same on the replication file (Polity, 1981-2005)
rg = rep.sort_values(["ccode", "year"]).groupby("ccode")
rep["b5pol_s"] = (rep.polity_s - rg.polity_s.shift(5)).where(rg.year.shift(5) == rep.year - 5)
R = R.merge(rep[["ccode", "year", "b5pol_s"]], on=["ccode", "year"], how="left")
ctrl_nl = [c for c in REP_CTRL if c != "polity_s"]
for y in ("d5pol_s_1", "b5pol_s"):
    m, d = ols(R, y, "D_z + SIZE + " + " + ".join(ctrl_nl), ["D_z", "SIZE"] + ctrl_nl, "ccode")
    rows.append(dict(test="T2 placebo", outcome=y, spec="replication file", coef=m.params.D_z, se=m.bse.D_z,
                     p=m.pvalues.D_z, N=int(m.nobs), mean_y=d[y].mean()))
    say(f"  {y:10s} ({'future' if y.startswith('d5') else 'PAST  '}) coef={m.params.D_z:+.4f}{stars(m.pvalues.D_z):3s} "
        f"se={m.bse.D_z:.4f} N={int(m.nobs)}   [replication file]")

# ================================================================ T3 influence
say("=" * 90 + "\nT3  Leave-one-region-out / leave-one-country-out (fig2 main spec)")
REG = pub[["iso3", "region"]].dropna().drop_duplicates("iso3")
R = R.merge(REG, on="iso3", how="left")
jk = []
for (df, y, rhs, need, gcol) in ((R, "frfailure5_1", RHS_R, NEED_R, "ccode"), (V, "abs5_vdem", RHS_V, NEED_V, "iso3"),
                                (V, "abs5_polity", RHS_V, NEED_V, "iso3"), (R, "d5pol_s_1", RHS_R, NEED_R, "ccode")):
    base, _ = ols(df, y, rhs, need, gcol)
    for reg in sorted(df.region.dropna().unique()):
        m, _ = ols(df[df.region != reg], y, rhs, need, gcol)
        rows.append(dict(test="T3 drop region", outcome=y, spec=f"drop {reg}", coef=m.params.D_z, se=m.bse.D_z,
                         p=m.pvalues.D_z, N=int(m.nobs)))
        say(f"  {y:13s} drop {reg:28s} coef={m.params.D_z:+.4f}{stars(m.pvalues.D_z):3s} (full: {base.params.D_z:+.4f})")
    cs = []
    for c in df[gcol].dropna().unique():
        m, _ = ols(df[df[gcol] != c], y, rhs, need, gcol)
        cs.append((c, m.params.D_z, m.pvalues.D_z))
    cs = pd.DataFrame(cs, columns=["dropped", "coef", "p"])
    say(f"  {y:13s} leave-one-country-out: coef range [{cs.coef.min():+.4f}, {cs.coef.max():+.4f}], "
        f"share p<.05 = {(cs.p < .05).mean():.2f}, share p<.10 = {(cs.p < .10).mean():.2f}; "
        f"most influential: {cs.iloc[(cs.coef - base.params.D_z).abs().argsort()[::-1][:3]].dropped.tolist()}")
    jk.append(cs.assign(outcome=y))
pd.concat(jk).to_csv(OUT / "T3_leave_one_country_out.csv", index=False)

# ================================================================ T4 telecom: what does the null rule out?
say("=" * 90 + "\nT4  Telecom moderation: what the null rules out, and a within-year telecom measure")
win = rep[rep.year.between(1981, 2005)].copy(); base = win[win.autocracy == 1]
z = lambda s, r: (s - r.mean()) / r.std()
win["W_c"] = win.lgdpcap_1 - base.lgdpcap_1.mean()
win["D_z"] = z(win.diaspora_dem, base.diaspora_dem); win["T_z"] = z(win.ict_index, base.ict_index)
# within-year rank of telecom among autocracies (0-1): compares countries only to their contemporaries
win["T_yr"] = np.nan
m_aut = win.autocracy == 1
win.loc[m_aut, "T_yr"] = win[m_aut].groupby("year").ict_index.rank(pct=True)
win["T_yr_z"] = z(win.T_yr, win.loc[m_aut, "T_yr"])
CTL3 = ["growth2_1", "lpop_1", "urban_1", "fueldep_1", "log_durable", "polity_s", "regionpolity_1", "communist_1",
        "geddesmil_1", "geddesparty_1", "violence_domestic_1", "aid2_1", "diaspora_size"]
for y in ("d5pol_s_1", "f5bmr_1", "firreg5_c_1", "frfailure5_1"):
    S = win[win.bmr_1 == 0] if y == "f5bmr_1" else win[win.autocracy == 1]
    for tz, lab in (("T_z", "ICT index (authors)"), ("T_yr_z", "within-year percentile")):
        rhs = f"D_z*{tz} + D_z:W_c + W_c + " + " + ".join(CTL3)
        m, d = ols(S, y, rhs, ["D_z", tz, "W_c"] + CTL3, "ccode")
        k = f"D_z:{tz}"; b, s = m.params[k], m.bse[k]; main_d = m.params.D_z
        lo, hi = b - 1.96 * s, b + 1.96 * s
        rows.append(dict(test="T4 telecom", outcome=y, spec=lab, coef=b, se=s, p=m.pvalues[k], N=int(m.nobs),
                         ci_lo=lo, ci_hi=hi, main_D=main_d))
        say(f"  {y:13s} {lab:24s} DxT={b:+.4f}{stars(m.pvalues[k]):3s} 95% CI [{lo:+.4f}, {hi:+.4f}]  "
            f"| D at mean T = {main_d:+.4f}  -> CI upper bound = {hi / abs(main_d) if main_d else np.nan:.0%} of D per SD of T")

# ================================================================ T5 destination type
say("=" * 90 + "\nT5  Destination type: Wealth vs Democracy hypotheses, formally")
ts = pd.read_csv(P / "data/diaspora_type_shares.csv")
c = pd.read_stata(P / "data/Replication_Migration.dta", convert_categoricals=False).merge(ts, on=["ccode", "year"], how="left")
TY = ["RD", "PD", "RA"]; tot = c[[f"share_{t}" for t in TY + ["PA"]]].sum(axis=1)
for t in TY: c["s_" + t] = c["share_" + t] / tot
c["SZ"] = np.log1p(1000 * tot); c["dpol"] = c.d5pol_s_1 * 20
c["log_durable"], c["polity_s"] = np.log1p(c.durable_1), c.polity_s_1
c = c.merge(rep[["ccode", "year", "iso3"]].drop_duplicates(["ccode", "year"]), on=["ccode", "year"], how="left").merge(REG, on="iso3", how="left")
aut = c[c.year.between(1981, 2005) & (c.polity2_1 <= 5)]
def t5(df, label, ctrl=REP_CTRL, extra="", fe="C(year)", need_extra=()):
    xs = ["s_RD", "s_PD", "s_RA", "SZ"]
    d = df.dropna(subset=["dpol"] + xs + ctrl + list(need_extra))
    m = smf.ols(f"dpol ~ {' + '.join(xs + ctrl)}{extra} + {fe}", data=d).fit(cov_type="cluster", cov_kwds={"groups": d.ccode})
    out = dict(spec=label, N=int(m.nobs))
    for t in TY: out[f"{t} (1/4 shift)"] = .25 * m.params["s_" + t]; out[f"p_{t}"] = m.pvalues["s_" + t]
    out["p(PD = RD)"] = float(m.t_test("s_PD - s_RD = 0").pvalue)
    out["p(RD = RA)  [democracy, holding wealth]"] = float(m.t_test("s_RD - s_RA = 0").pvalue)
    out["p(RD = PD)  [wealth, holding democracy]"] = out["p(PD = RD)"]
    return out
t5rows = [t5(aut, "authors' main"),
          t5(aut, "+ neighbour democracy (nbrpolity_1)", ctrl=REP_CTRL + ["nbrpolity_1"]),
          t5(aut, "+ country FE", fe="C(year) + C(ccode)")]
for reg in sorted(aut.region.dropna().unique()):
    t5rows.append(t5(aut[aut.region != reg], f"drop {reg}"))
t5tab = pd.DataFrame(t5rows)
t5tab.to_csv(OUT / "T5_destination_type_tests.csv", index=False)
say(t5tab.round(3).to_string(index=False))

pd.DataFrame(rows).to_csv(OUT / "stress_tests_results.csv", index=False)
say("\nWrote", OUT / "stress_tests_results.csv")
log.close()
