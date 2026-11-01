"""Compare a run of make_all_figures.py with the authors expected_output/.
Usage: python compare_to_expected.py <results dir of new run> <expected_output/results>"""
import pandas as pd, numpy as np, sys, glob, os
a, b = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(f"{b}/*.csv")):
    n=os.path.basename(f); x=pd.read_csv(f); y=pd.read_csv(f"{a}/{n}")
    num=x.select_dtypes("number").columns
    if x.shape!=y.shape: print(n,"SHAPE",x.shape,y.shape); continue
    d=(x[num]-y[num]).abs().max().max()
    print(f"{n:45s} max abs diff {d:.2e}")
