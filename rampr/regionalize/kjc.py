from __future__ import annotations
import pandas as pd, numpy as np

def kjc_share(
    make_output: pd.DataFrame,
    emp: pd.DataFrame,
    emp_col: str,
    *,
    geo: str,
    year: int | None = None
) -> pd.DataFrame:

    """Kendrick–Jaycox regional output.
    Returns a DataFrame with columns: industry, output (national), region_output.
    """

    df, df1 = emp.copy(), make_output.copy()

    if year is not None and "year" in df.columns:
      df = df[df["year"] == year]
      if df.empty:
        raise ValueError(
            f"No rows found for year={year}. Available years: {sorted(emp['year'].unique())}"
        )


    e_ir = df[df["geo"] == geo].groupby("industry")[emp_col].sum()  # regional employment for industry i
    
    # check for zero division error
    col = df.iloc[:, 1].tolist()
    for i in range(len(col)):
        if col[i] == 0:
            raise ZeroDivisionError(f"output column has 0 at row {i}")

    e_i = df.groupby("industry")[emp_col].sum()  # national employment for industries i

    if len(df1.columns) == 2:
        x_i = df1.groupby(df1.columns[0])[df1.columns[1]].sum()
    else:
        raise ValueError("df1 must have exactly 2 columns: [industry, output]")

    # align the regional employment industries with national output
   # e_ir = e_ir.reindex(x_i.index)
   # e_i = e_i.reindex(x_i.index)

    share = (e_ir / e_i).reindex(x_i.index)  # find the regional share first
    
    # constraint checking
    neg = share.values < 0
    if np.any(neg):
        result = share.index[neg].tolist()
        raise ValueError(
            f"share < 0, not reasonable; we avoid negative ---> {result}"
        )

    pos = share.values > 1
    if np.any(pos):
        result = share.index[pos].tolist()
        raise ValueError(
            f"share > 1: the region's share is greater than the national total, "
            f"which does not conform to the analysis. "
            f"Problem industries: {result}"
        )

    # computing regional output via Kendrick Jaycox
    x_ir = share * x_i

    # place regional output into dataframe with both industries and national output
    df = pd.DataFrame(make_output, columns=["industry", "output"])
    df["region_output"] = df["industry"].map(x_ir)

    return df
