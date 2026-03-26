"""Build embed_data.json for the Easter Analysis v2 HTML report.

Same as v1 but includes post-Easter price variation fields.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent

cat_full = json.load(open(BASE / "cat_processed.json", encoding="utf-8"))
upc_full = json.load(open(BASE / "upc_processed.json", encoding="utf-8"))


def compact_cat(r):
    return {
        "c":     r["COUNTRY_CODE"],
        "sbu":   r["SBU"],
        "cat":   r["CATEGORY"],
        "ewu":   r["easter_wm_units"],
        "etu":   r["easter_tot_units"],
        "emu":   r["easter_mkt_units"],
        "ews":   r["easter_wm_sales"],
        "ets":   r["easter_tot_sales"],
        "ems":   r["easter_mkt_sales"],
        "bwu":   r["avg_base_wm_units"],
        "btu":   r["avg_base_tot_units"],
        "bmu":   r["avg_base_mkt_units"],
        "bws":   r["avg_base_wm_sales"],
        "bts":   r["avg_base_tot_sales"],
        "bms":   r["avg_base_mkt_sales"],
        "wl":    r["wm_unit_lift"],
        "tl":    r["total_unit_lift"],
        "ml":    r["mkt_unit_lift"],
        "ews_pct": r["easter_wm_share_pct"],
        "bws_pct": r["base_wm_share_pct"],
        "spd":   r["share_delta_pp"],
        "ea":    r["easter_amp"],
        "ba":    r["base_amp"],
        "ac":    r["amp_chg_pct"],
        "ewp":   r["easter_wm_price"],
        "bwp":   r["base_wm_price"],
        "wpc":   r["wm_price_chg_pct"],
        "seas":  r["IS_EASTER_SEASONAL"],
        "role":  r["PURCHASE_ROLE"],
        "comp":  r["COMPETITIVE_BEHAVIOR"],
        "mat":   r["MARKET_MATRIX"],
        "p75":   r["p75_country_lift"],
        # NEW: post-Easter price variation
        "ppwp":  r["avg_post_wm_price"],       # avg post-Easter WM price
        "ppma":  r["avg_post_mkt_amp"],         # avg post-Easter MKT AMP
        "ppve":  r["post_wm_price_vs_easter"],  # % vs Easter
        "ppame": r["post_amp_vs_easter"],       # AMP % vs Easter
        "ppvb":  r["post_wm_price_vs_base"],    # % vs Base
        "ppbeh": r["POST_PRICE_BEHAVIOR"],      # label
    }


def compact_upc(r):
    return {
        "c":     r["COUNTRY_CODE"],
        "sbu":   r["SBU"],
        "cat":   r["CATEGORY"],
        "upc":   r.get("UPC_NBR", ""),
        "desc":  r.get("UPC_DESC", ""),
        "ewu":   r["easter_wm_units"],
        "etu":   r["easter_tot_units"],
        "emu":   r["easter_mkt_units"],
        "ews":   r["easter_wm_sales"],
        "bwu":   r["avg_base_wm_units"],
        "btu":   r["avg_base_tot_units"],
        "wl":    r["wm_unit_lift"],
        "tl":    r["total_unit_lift"],
        "ml":    r["mkt_unit_lift"],
        "ews_pct": r["easter_wm_share_pct"],
        "bws_pct": r["base_wm_share_pct"],
        "spd":   r["share_delta_pp"],
        "ea":    r["easter_amp"],
        "ba":    r["base_amp"],
        "ac":    r["amp_chg_pct"],
        "ewp":   r["easter_wm_price"],
        "bwp":   r["base_wm_price"],
        "seas":  r["IS_EASTER_SEASONAL"],
        "role":  r["PURCHASE_ROLE"],
        "comp":  r["COMPETITIVE_BEHAVIOR"],
        "mat":   r["MARKET_MATRIX"],
        # NEW
        "ppwp":  r["avg_post_wm_price"],
        "ppve":  r["post_wm_price_vs_easter"],
        "ppvb":  r["post_wm_price_vs_base"],
        "ppbeh": r["POST_PRICE_BEHAVIOR"],
    }


def count_by(data, key):
    out = {}
    for r in data:
        v = r.get(key, "")
        out[v] = out.get(v, 0) + 1
    return out


cat_compact = [compact_cat(r) for r in cat_full]
upc_compact = [compact_upc(r) for r in upc_full]

seasonal_cat = [r for r in cat_compact if r["seas"] == "Yes"]
dest_cat     = [r for r in seasonal_cat if r["role"] == "Destination"]
pw_cat       = [r for r in cat_compact if "Price War" in r["comp"]]
wm_gain_cat  = [r for r in cat_compact if r["mat"] == "Walmart Share Gain"]
mkt_wide_cat = [r for r in cat_compact if r["mat"] == "Market-Wide Growth"]

role_dist     = count_by(seasonal_cat, "role")
matrix_dist   = count_by(cat_compact,  "mat")
behavior_dist = count_by(cat_compact,  "comp")
post_dist     = count_by(cat_compact,  "ppbeh")  # NEW

top15 = sorted(seasonal_cat, key=lambda x: -(x["wl"] or 0))[:15]

# Country summary — same as v1
country_summary = {}
for r in cat_compact:
    c = r["c"]
    if c not in country_summary:
        country_summary[c] = {"total": 0, "seasonal": 0, "wm_gain": 0, "price_war": 0}
    country_summary[c]["total"] += 1
    if r["seas"] == "Yes":              country_summary[c]["seasonal"]  += 1
    if r["mat"] == "Walmart Share Gain": country_summary[c]["wm_gain"]   += 1
    if "Price War" in r["comp"]:         country_summary[c]["price_war"] += 1

_order = ["CAM", "CR", "GT", "HN", "NI"]
country_summary = {k: country_summary[k] for k in _order if k in country_summary}

# AMP comparison chart data
amp_comparison = [{
    "label":       f"[{r['c']}] {r['cat'][:35]}",
    "base_amp":    r["ba"],
    "easter_amp":  r["ea"],
    "chg":         r["ac"],
    "wl":          r["wl"],
    "comp":        r["comp"],
} for r in sorted(dest_cat, key=lambda x: -(x["wl"] or 0))[:12]]

# Scatter
scatter_data = [{
    "x":    min(float(r["tl"] or 0), 10),
    "y":    min(float(r["wl"] or 0), 10),
    "cat":  r["cat"][:40],
    "c":    r["c"],
    "role": r["role"],
    "seas": r["seas"],
} for r in cat_compact]

EMBED = {
    "cat":             cat_compact,
    "upc":             upc_compact,
    "top15":           top15,
    "role_dist":       role_dist,
    "matrix_dist":     matrix_dist,
    "behavior_dist":   behavior_dist,
    "post_dist":       post_dist,    # NEW
    "country_summary": country_summary,
    "amp_comparison":  amp_comparison,
    "scatter":         scatter_data,
    "stats": {
        "total_cat":     len(cat_compact),
        "seasonal_cat":  len(seasonal_cat),
        "seasonal_pct":  round(len(seasonal_cat) / len(cat_compact) * 100, 1),
        "dest_seasonal": len(dest_cat),
        "price_wars":    len(pw_cat),
        "wm_gain":       len(wm_gain_cat),
        "mkt_wide":      len(mkt_wide_cat),
        "total_upc":     len(upc_compact),
        "upc_seasonal":  len([r for r in upc_compact if r["seas"] == "Yes"]),
        # NEW post-Easter summary counts
        "post_recovers": sum(1 for r in cat_compact if r["ppbeh"] == "Recovers to Base"),
        "post_elevated": sum(1 for r in cat_compact if r["ppbeh"] == "Stays Elevated"),
        "post_stable":   sum(1 for r in cat_compact if r["ppbeh"] == "Stable Post-Easter"),
        "post_drop":     sum(1 for r in cat_compact if r["ppbeh"] == "Price Drop"),
    },
}

print("Stats:", json.dumps(EMBED["stats"], indent=2))
print(f"Post behavior dist: {post_dist}")

with open(BASE / "embed_data.json", "w", encoding="utf-8") as f:
    json.dump(EMBED, f, ensure_ascii=False, separators=(',', ':'))

print(f"\nEmbed JSON written: {(BASE / 'embed_data.json').stat().st_size / 1024:.1f} KB")
