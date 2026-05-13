"""
build_pricing_inmarket.py
Genera el reporte interactivo HTML de PG OBW / InMarket.
"""
import json, math, webbrowser, os
import pandas as pd
from pathlib import Path

CSV   = Path(__file__).parent / "prcng_OBW_inMKT_26_COMP_results.csv"
OUT   = Path(__file__).parent / "pricing_inmarket_report.html"

# ── rangos PG OBW ────────────────────────────────────────────────────────────
def classify(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "unk"
    if v < 0:   return "neg"
    if v < 5:   return "r05"
    if v < 10:  return "r10"
    return "r10p"

RANGE_LABELS = {
    "neg":  "< 0%",
    "r05":  "0% – 5%",
    "r10":  "5% – 10%",
    "r10p": "> 10%",
    "unk":  "Sin dato",
}
RANGE_ORDER = ["neg", "r05", "r10", "r10p", "unk"]

def max_consec(lst, target):
    best = cur = 0
    for v in lst:
        if v == target:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best

# ── carga CSV ────────────────────────────────────────────────────────────────
print("Cargando CSV…")
df = pd.read_csv(CSV, dtype={"UPC_NBR": str})
df["pg_obw_pct"]  = pd.to_numeric(df["pg_obw_pct"],  errors="coerce")
df["pg_comp_pct"] = pd.to_numeric(df["pg_comp_pct"], errors="coerce")
df["total_units_obw"] = pd.to_numeric(df["total_units_obw"], errors="coerce").fillna(0)
df["rng"] = df["pg_obw_pct"].apply(classify)

weeks = sorted(df["ID_SW"].unique().tolist())
week_to_mes = (df[["ID_SW","mes"]].drop_duplicates()
               .set_index("ID_SW")["mes"].to_dict())

KEY_COLS = ["COUNTRY_CODE","DIVISION","CATEGORIA","UPC_NBR","UPC_DESC","canasto_flag"]

# ── agregación por UPC (overall) ─────────────────────────────────────────────
print("Agregando por UPC…")
grp = (df.groupby(KEY_COLS, dropna=False)
         .agg(
             tot_units   = ("total_units_obw", "sum"),
             sum_fw_obw  = ("pg_obw_pct",  lambda x: (x * df.loc[x.index,"total_units_obw"]).sum()),
             sum_fw_comp = ("pg_comp_pct", lambda x: (x * df.loc[x.index,"total_units_obw"]).sum()),
             sum_w_comp  = ("pg_comp_pct", lambda x: df.loc[x.index[x.notna()],"total_units_obw"].sum()),
             n_weeks     = ("ID_SW", "nunique"),
         )
         .reset_index())

grp["pg_obw_overall"]  = grp["sum_fw_obw"]  / grp["tot_units"].replace(0, float("nan"))
grp["pg_comp_overall"] = grp["sum_fw_comp"] / grp["sum_w_comp"].replace(0, float("nan"))
grp["rng_overall"]     = grp["pg_obw_overall"].apply(classify)

# ── pivot semanal de rangos ──────────────────────────────────────────────────
print("Pivot semanal…")
wk_rng = (df[KEY_COLS + ["ID_SW","rng"]]
           .pivot_table(index=KEY_COLS, columns="ID_SW", values="rng", aggfunc="first")
           .reindex(columns=weeks))

# ── construir records ────────────────────────────────────────────────────────
print("Construyendo records…")
records = []
grp_idx = grp.set_index(KEY_COLS)

for key, row in grp_idx.iterrows():
    cc, dv, cat, upc, desc, can = key
    wk_vals = []
    if key in wk_rng.index:
        wk_vals = [v if isinstance(v, str) else None for v in wk_rng.loc[key].tolist()]

    rng_counts = {r: wk_vals.count(r) for r in RANGE_ORDER}
    max_c      = {r: max_consec(wk_vals, r) for r in RANGE_ORDER}

    pg_o = round(row["pg_obw_overall"],  3) if pd.notna(row["pg_obw_overall"])  else None
    pg_c = round(row["pg_comp_overall"], 3) if pd.notna(row["pg_comp_overall"]) else None

    records.append({
        "cc":  cc,  "dv": dv,  "cat": cat,
        "upc": upc, "desc": desc,
        "can": 1 if can == "CANASTO" else 0,
        "u":   round(row["tot_units"]),
        "nw":  int(row["n_weeks"]),
        "po":  pg_o,
        "pc":  pg_c,
        "ro":  row["rng_overall"],
        "wk":  wk_vals,
        "rc":  rng_counts,
        "mc":  max_c,
    })

# ── jerarquía para filtros ───────────────────────────────────────────────────
hier = {}
for _, r in df[["COUNTRY_CODE","DIVISION","CATEGORIA"]].drop_duplicates().iterrows():
    cc, dv, cat = r["COUNTRY_CODE"], r["DIVISION"], r["CATEGORIA"]
    hier.setdefault(cc, {}).setdefault(dv, [])
    if cat not in hier[cc][dv]:
        hier[cc][dv].append(cat)

payload = {
    "weeks":    [int(w) for w in weeks],
    "wkMes":    {str(int(k)): v for k, v in week_to_mes.items()},
    "hier":     hier,
    "records":  records,
    "ranges":   RANGE_ORDER,
    "rLabels":  RANGE_LABELS,
}

print(f"Records: {len(records):,}")

# ── inyectar en HTML ─────────────────────────────────────────────────────────
json_blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

HTML_TEMPLATE = open(Path(__file__).parent / "pricing_inmarket_tpl.html", encoding="utf-8").read()
html_out = HTML_TEMPLATE.replace("/*__DATA__*/", f"const DATA={json_blob};")

OUT.write_text(html_out, encoding="utf-8")
print(f"Reporte generado: {OUT}")
webbrowser.open(OUT.as_uri())
