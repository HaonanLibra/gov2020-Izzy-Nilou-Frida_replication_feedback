"""Search for the specification behind the draft's destination-type figure (RD +0.9, PD +0.7, RA 0.0;
remittances +23%, +11%, +28%), which the package does not reproduce (it gives +0.1/+0.7/-0.2 and -9/-8/-7%).
Usage: python fig5_variants.py <authors' package folder>"""
import sys, numpy as np, pandas as pd, statsmodels.formula.api as smf
P = sys.argv[1]
ts = pd.read_csv(f"{P}/data/diaspora_type_shares.csv")
c = pd.read_stata(f"{P}/data/Replication_Migration.dta", convert_categoricals=False).merge(ts, on=["ccode","year"], how="left")
T = ["RD","PD","RA"]; tot = c[[f"share_{t}" for t in T+["PA"]]].sum(axis=1)
for t in T: c["s_"+t] = c["share_"+t]/tot
c["SZ"] = np.log1p(1000*tot); c["dpol"] = c.d5pol_s_1*20
c["log_durable"], c["polity_s"] = np.log1p(c.durable_1), c.polity_s_1
iso = pd.read_csv(f"{P}/derived/diaspora_telecom_panel.csv", usecols=["ccode","iso3","year"]).drop_duplicates(["ccode","year"])
R = pd.read_csv(f"{P}/data/ddf--datapoints--bx_trf_pwkr_cd_dt--by--economy--year.csv"); R.columns=["iso3","year","rem"]
R["iso3"]=R.iso3.str.upper(); R=R.sort_values(["iso3","year"]); R["lrem"]=np.log(R.rem)
R["drem"]=R.groupby("iso3").lrem.shift(-5)-R.lrem; R.loc[R.groupby("iso3").year.shift(-5)!=R.year+5,"drem"]=np.nan
c = c.merge(iso,on=["ccode","year"],how="left").merge(R[["iso3","year","drem"]],on=["iso3","year"],how="left")
CTRL=["lgdpcap_1","growth2_1","lpop_1","urban_1","fueldep_1","log_durable","polity_s","regionpolity_1","communist_1","geddesmil_1","geddesparty_1","violence_domestic_1","aid2_1"]
def est(df,y,ctrl,xs,extra="",fe="C(year)"):
    d=df.dropna(subset=[y]+xs+ctrl); m=smf.ols(f"{y} ~ {' + '.join(xs+ctrl)}{extra} + {fe}",data=d).fit(cov_type="cluster",cov_kwds={"groups":d.ccode})
    out=[]
    for x in xs[:3]:
        b=.25*m.params[x]; out.append(round(100*(np.exp(b)-1) if y=="drem" else b,2))
    return out, int(m.nobs)
aut=c[c.year.between(1981,2005)&(c.polity2_1<=5)]
for t in T: c["p_"+t]=100*c["share_"+t]   # population shares in percentage points
aut2=c[c.year.between(1981,2005)&(c.polity2_1<=5)]
rows=[]
for name,df,xs,ctrl in [("package main",aut,["s_RD","s_PD","s_RA","SZ"],CTRL),
                        ("no SZ control",aut,["s_RD","s_PD","s_RA"],CTRL),
                        ("no controls, no SZ",aut,["s_RD","s_PD","s_RA"],[]),
                        ("1981-2010",c[c.year.between(1981,2010)&(c.polity2_1<=5)],["s_RD","s_PD","s_RA","SZ"],CTRL)]:
    for y in ("dpol","drem"):
        e,n=est(df,y,ctrl,xs); rows.append((name,y,e,n))
for r in rows: print(r)
