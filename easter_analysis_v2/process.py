"""Easter Analysis v2 — Process Engine.

Same logic as v1 (Unit Lift, Seasonal, Purchase Role, Competitive Behavior,
Market Matrix) + new post-Easter price variation fields.
Reads from CSV (BQ export) instead of JSON.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# FX Rates (local currency → USD)
# ---------------------------------------------------------------------------
FX_RATES = {"CR": 507.0, "GT": 7.55, "HN": 24.68, "NI": 36.63}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def safe_float(v, default=0.0):
    try:
        f = float(v)
        return f if math.isfinite(f) else default
    except (TypeError, ValueError):
        return default


def pct_change(new_val, old_val):
    if not old_val or old_val == 0:
        return None
    return (new_val - old_val) / abs(old_val) * 100


def _sdiv(a, b, decimals=4):
    try:
        return round(a / b, decimals) if b else None
    except (TypeError, ZeroDivisionError):
        return None


def load_csv(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Purchase-Role Rules
# ---------------------------------------------------------------------------
DESTINATION_KW = [
    "seafood", "fish", "shellfish", "mariscos", "pescado",
    "sun care", "beer", "spirits", "wine", "licor", "liqueur",
    "alcohol", "beverage alcohol", "cocktail",
]
IMPULSE_KW = [
    "chips", "crisps", "snack", "cookie", "cracker", "candy",
    "carbonated", "juices", "juice", "flavored", "bebidas",
    "beverages -", "water", "hydrate", "energy", "tea",
    "noodles", "infant", "infant formula",
]
COMPLEMENTARY_KW = [
    "condiment", "sauce", "marin", "disposable", "tableware",
    "trash", "bag", "laundry", "bleach", "cleaner", "floor",
    "insect", "pesticide", "air fresh", "deodor",
    "coal", "charcoal", "ice", "lime",
]


def assign_role(category: str) -> str:
    cat = category.lower()
    if any(k in cat for k in DESTINATION_KW):
        return "Destination"
    if any(k in cat for k in IMPULSE_KW):
        return "Impulse / Convenience"
    if any(k in cat for k in COMPLEMENTARY_KW):
        return "Complementary"
    return "Other"


# ---------------------------------------------------------------------------
# Competitive Behavior
# ---------------------------------------------------------------------------
def competitive_behavior(amp_chg_pct, wm_lift):
    if amp_chg_pct is None:
        return "Insufficient Data"
    if amp_chg_pct < -10 and wm_lift >= 1.5:
        return "Price War / Loss Leader"
    if -5 <= amp_chg_pct <= 5 and wm_lift >= 1.5:
        return "Convenience-Driven (Low Price Sensitivity)"
    if amp_chg_pct < -10:
        return "Aggressive Pricing (Low Volume)"
    if amp_chg_pct > 10:
        return "Price Inflation"
    return "Stable / Mixed"


# ---------------------------------------------------------------------------
# Market Relevance Matrix
# ---------------------------------------------------------------------------
def market_matrix(wm_lift, mkt_lift):
    wm_growing   = wm_lift >= 1.1
    mkt_growing  = (mkt_lift is not None) and (mkt_lift >= 1.1)
    wm_shrinking = wm_lift < 0.95
    mkt_shrinking = (mkt_lift is not None) and (mkt_lift < 0.95)
    if wm_growing and mkt_growing:   return "Market-Wide Growth"
    if wm_growing and not mkt_growing: return "Walmart Share Gain"
    if wm_shrinking and mkt_growing: return "Walmart Share Loss"
    if wm_shrinking and mkt_shrinking: return "Market Contraction"
    return "Flat / Mixed"


# ---------------------------------------------------------------------------
# Post-Easter price behavior label
# ---------------------------------------------------------------------------
def post_price_label(post_vs_easter_pct, post_vs_base_pct):
    """Classify how prices behaved in the 6 post-Easter weeks."""
    if post_vs_easter_pct is None:
        return "No Post Data"
    if post_vs_easter_pct < -3:
        if post_vs_base_pct is not None and post_vs_base_pct <= 3:
            return "Recovers to Base"
        return "Price Drop"
    if post_vs_easter_pct > 3:
        return "Stays Elevated"
    return "Stable Post-Easter"


# ---------------------------------------------------------------------------
# CAM Aggregation (categories)
# ---------------------------------------------------------------------------
def aggregate_cam_categories(raw_records: list) -> list:
    acc = defaultdict(lambda: {
        "sbu": "",
        "ewu": 0.0, "emu": 0.0, "etu": 0.0,
        "ews": 0.0, "ems": 0.0, "ets": 0.0,
        "bwu": 0.0, "bmu": 0.0, "btu": 0.0,
        "bws": 0.0, "bms": 0.0, "bts": 0.0,
        "post_wm_units": 0.0, "post_mkt_units": 0.0,
        "post_wm_sales": 0.0, "post_mkt_sales": 0.0,
    })
    for r in raw_records:
        fx  = FX_RATES.get(r.get("COUNTRY_CODE", ""), 1.0)
        key = (r.get("CATEGORY", ""), r.get("SBU", ""))
        g   = acc[key]
        g["sbu"] = r.get("SBU", "")
        g["ewu"] += safe_float(r.get("easter_wm_units",  0))
        g["emu"] += safe_float(r.get("easter_mkt_units", 0))
        g["etu"] += safe_float(r.get("easter_tot_units", 0))
        g["ews"] += safe_float(r.get("easter_wm_sales",  0)) / fx
        g["ems"] += safe_float(r.get("easter_mkt_sales", 0)) / fx
        g["ets"] += safe_float(r.get("easter_tot_sales", 0)) / fx
        g["bwu"] += safe_float(r.get("avg_base_wm_units",  0))
        g["bmu"] += safe_float(r.get("avg_base_mkt_units", 0))
        g["btu"] += safe_float(r.get("avg_base_tot_units", 0))
        g["bws"] += safe_float(r.get("avg_base_wm_sales",  0)) / fx
        g["bms"] += safe_float(r.get("avg_base_mkt_sales", 0)) / fx
        g["bts"] += safe_float(r.get("avg_base_tot_sales", 0)) / fx
        # Post-Easter (already averaged per week by SQL)
        g["post_wm_units"]  += safe_float(r.get("avg_post_wm_units",  0))
        g["post_mkt_units"] += safe_float(r.get("avg_post_mkt_units", 0))
        g["post_wm_sales"]  += safe_float(r.get("avg_post_wm_price",  0)) * safe_float(r.get("avg_post_wm_units",  0)) / fx
        g["post_mkt_sales"] += safe_float(r.get("avg_post_mkt_amp",   0)) * safe_float(r.get("avg_post_mkt_units", 0)) / fx

    records = []
    for (cat, sbu), g in acc.items():
        e_wm_sh = _sdiv(g["ewu"], g["etu"], 4)
        b_wm_sh = _sdiv(g["bwu"], g["btu"], 4)
        avg_post_wm_price  = _sdiv(g["post_wm_sales"],  g["post_wm_units"],  4)
        avg_post_mkt_amp   = _sdiv(g["post_mkt_sales"], g["post_mkt_units"], 4)
        records.append({
            "COUNTRY_CODE"         : "CAM",
            "SBU"                  : sbu,
            "CATEGORY"             : cat,
            "easter_wm_units"      : round(g["ewu"], 2),
            "easter_mkt_units"     : round(g["emu"], 2),
            "easter_tot_units"     : round(g["etu"], 2),
            "easter_wm_sales"      : round(g["ews"], 2),
            "easter_mkt_sales"     : round(g["ems"], 2),
            "easter_tot_sales"     : round(g["ets"], 2),
            "avg_base_wm_units"    : round(g["bwu"], 2),
            "avg_base_mkt_units"   : round(g["bmu"], 2),
            "avg_base_tot_units"   : round(g["btu"], 2),
            "avg_base_wm_sales"    : round(g["bws"], 2),
            "avg_base_mkt_sales"   : round(g["bms"], 2),
            "avg_base_tot_sales"   : round(g["bts"], 2),
            "wm_unit_lift"         : _sdiv(g["ewu"], g["bwu"]),
            "total_unit_lift"      : _sdiv(g["etu"], g["btu"]),
            "mkt_unit_lift"        : _sdiv(g["emu"], g["bmu"]),
            "easter_wm_share_pct"  : round(e_wm_sh * 100, 2) if e_wm_sh else None,
            "base_wm_share_pct"    : round(b_wm_sh * 100, 2) if b_wm_sh else None,
            "easter_amp"           : _sdiv(g["ems"], g["emu"], 2),
            "base_amp"             : _sdiv(g["bms"], g["bmu"], 2),
            "easter_wm_price"      : _sdiv(g["ews"], g["ewu"], 2),
            "base_wm_price"        : _sdiv(g["bws"], g["bwu"], 2),
            "preweek_wm_units"     : None,
            "preweek_tot_units"    : None,
            "avg_post_wm_price"    : avg_post_wm_price,
            "avg_post_mkt_amp"     : avg_post_mkt_amp,
        })
    return records


# ---------------------------------------------------------------------------
# CAM Aggregation (UPCs)
# ---------------------------------------------------------------------------
def aggregate_cam_upcs(raw_records: list) -> list:
    acc = defaultdict(lambda: {
        "sbu": "", "desc": "",
        "ewu": 0.0, "emu": 0.0, "etu": 0.0,
        "ews": 0.0, "ems": 0.0,
        "bwu": 0.0, "bmu": 0.0, "btu": 0.0,
        "bws": 0.0, "bms": 0.0,
        "post_wm_units": 0.0, "post_wm_sales": 0.0,
    })
    for r in raw_records:
        fx  = FX_RATES.get(r.get("COUNTRY_CODE", ""), 1.0)
        key = (r.get("UPC_NBR", ""), r.get("CATEGORY", ""), r.get("SBU", ""))
        g   = acc[key]
        if not g["sbu"]:  g["sbu"]  = r.get("SBU", "")
        if not g["desc"]: g["desc"] = r.get("UPC_DESC", "")
        g["ewu"] += safe_float(r.get("easter_wm_units",  0))
        g["emu"] += safe_float(r.get("easter_mkt_units", 0))
        g["etu"] += safe_float(r.get("easter_tot_units", 0))
        g["ews"] += safe_float(r.get("easter_wm_sales",  0)) / fx
        g["ems"] += safe_float(r.get("easter_mkt_sales", 0)) / fx
        g["bwu"] += safe_float(r.get("avg_base_wm_units",  0))
        g["bmu"] += safe_float(r.get("avg_base_mkt_units", 0))
        g["btu"] += safe_float(r.get("avg_base_tot_units", 0))
        g["bws"] += safe_float(r.get("avg_base_wm_sales",  0)) / fx
        g["bms"] += safe_float(r.get("avg_base_mkt_sales", 0)) / fx
        g["post_wm_units"] += safe_float(r.get("avg_post_wm_units", 0))
        g["post_wm_sales"] += safe_float(r.get("avg_post_wm_price", 0)) * safe_float(r.get("avg_post_wm_units", 0)) / fx

    records = []
    for (upc, cat, sbu), g in acc.items():
        e_wm_sh = _sdiv(g["ewu"], g["etu"], 4)
        b_wm_sh = _sdiv(g["bwu"], g["btu"], 4)
        records.append({
            "COUNTRY_CODE"      : "CAM",
            "SBU"               : sbu,
            "CATEGORY"          : cat,
            "UPC_NBR"           : upc,
            "UPC_DESC"          : g["desc"],
            "easter_wm_units"   : round(g["ewu"], 2),
            "easter_mkt_units"  : round(g["emu"], 2),
            "easter_tot_units"  : round(g["etu"], 2),
            "easter_wm_sales"   : round(g["ews"], 2),
            "easter_mkt_sales"  : round(g["ems"], 2),
            "easter_tot_sales"  : round(g["etu"], 2),
            "avg_base_wm_units" : round(g["bwu"], 2),
            "avg_base_mkt_units": round(g["bmu"], 2),
            "avg_base_tot_units": round(g["btu"], 2),
            "avg_base_wm_sales" : round(g["bws"], 2),
            "avg_base_mkt_sales": round(g["bms"], 2),
            "avg_base_tot_sales": round(g["bws"] + g["bms"], 2),
            "wm_unit_lift"      : _sdiv(g["ewu"], g["bwu"]),
            "total_unit_lift"   : _sdiv(g["etu"], g["btu"]),
            "mkt_unit_lift"     : _sdiv(g["emu"], g["bmu"]),
            "easter_wm_share_pct": round(e_wm_sh * 100, 2) if e_wm_sh else None,
            "base_wm_share_pct" : round(b_wm_sh * 100, 2) if b_wm_sh else None,
            "easter_amp"        : _sdiv(g["ems"], g["emu"], 2),
            "base_amp"          : _sdiv(g["bms"], g["bmu"], 2),
            "easter_wm_price"   : _sdiv(g["ews"], g["ewu"], 2),
            "base_wm_price"     : _sdiv(g["bws"], g["bwu"], 2),
            "avg_post_wm_price" : _sdiv(g["post_wm_sales"], g["post_wm_units"], 4),
        })
    return records


# ---------------------------------------------------------------------------
# Enrich records (original logic + post-Easter fields)
# ---------------------------------------------------------------------------
def process_records(records: list) -> tuple:
    # P75 per country
    by_country = {}
    for r in records:
        c    = r.get("COUNTRY_CODE", "")
        lift = safe_float(r.get("wm_unit_lift", 0))
        by_country.setdefault(c, []).append(lift)

    p75_by_country = {}
    for c, lifts in by_country.items():
        ls  = sorted(lifts)
        idx = int(len(ls) * 0.75)
        p75_by_country[c] = ls[min(idx, len(ls) - 1)]

    enriched = []
    for r in records:
        country  = r.get("COUNTRY_CODE", "")
        category = r.get("CATEGORY", "")
        wm_lift  = safe_float(r.get("wm_unit_lift", 0))
        tot_lift = safe_float(r.get("total_unit_lift", 0))
        mkt_raw  = r.get("mkt_unit_lift")
        mkt_lift = safe_float(mkt_raw, 0) if mkt_raw not in (None, "", "null") else None

        easter_amp   = safe_float(r.get("easter_amp", 0))
        base_amp     = safe_float(r.get("base_amp",   0))
        amp_chg      = pct_change(easter_amp, base_amp)

        easter_wm_share = safe_float(r.get("easter_wm_share_pct", 0))
        base_wm_share   = safe_float(r.get("base_wm_share_pct",   0))
        share_delta     = easter_wm_share - base_wm_share

        easter_wm_price = safe_float(r.get("easter_wm_price", 0))
        base_wm_price   = safe_float(r.get("base_wm_price",   0))
        wm_price_chg    = pct_change(easter_wm_price, base_wm_price)

        # --- NEW: post-Easter price fields ---
        avg_post_wm_price  = safe_float(r.get("avg_post_wm_price", 0)) or None
        avg_post_mkt_amp   = safe_float(r.get("avg_post_mkt_amp",  0)) or None
        # Keep None if field missing or zero
        if avg_post_wm_price == 0.0: avg_post_wm_price = None
        if avg_post_mkt_amp  == 0.0: avg_post_mkt_amp  = None

        post_wm_vs_easter  = pct_change(avg_post_wm_price, easter_wm_price) if avg_post_wm_price and easter_wm_price else None
        post_amp_vs_easter = pct_change(avg_post_mkt_amp,  easter_amp)       if avg_post_mkt_amp  and easter_amp      else None
        post_wm_vs_base    = pct_change(avg_post_wm_price, base_wm_price)    if avg_post_wm_price and base_wm_price   else None
        post_label         = post_price_label(post_wm_vs_easter, post_wm_vs_base)
        # ---------------------------------------

        p75         = p75_by_country.get(country, 1.5)
        is_seasonal = "Yes" if (wm_lift >= 1.5 or wm_lift >= p75) else "No"
        role        = assign_role(category)
        comp        = competitive_behavior(amp_chg, wm_lift)
        matrix      = market_matrix(wm_lift, mkt_lift)

        enriched.append({
            **r,
            "wm_unit_lift"            : round(wm_lift,  4),
            "total_unit_lift"         : round(tot_lift, 4),
            "mkt_unit_lift"           : round(mkt_lift, 4) if mkt_lift is not None else None,
            "easter_amp"              : round(easter_amp,       2),
            "base_amp"                : round(base_amp,         2),
            "amp_chg_pct"             : round(amp_chg,          2) if amp_chg is not None else None,
            "easter_wm_share_pct"     : round(easter_wm_share,  2),
            "base_wm_share_pct"       : round(base_wm_share,    2),
            "share_delta_pp"          : round(share_delta,      2),
            "wm_price_chg_pct"        : round(wm_price_chg,     2) if wm_price_chg is not None else None,
            "p75_country_lift"         : round(p75,              4),
            "IS_EASTER_SEASONAL"      : is_seasonal,
            "PURCHASE_ROLE"           : role,
            "COMPETITIVE_BEHAVIOR"    : comp,
            "MARKET_MATRIX"           : matrix,
            # New post-Easter fields
            "avg_post_wm_price"       : round(avg_post_wm_price, 4) if avg_post_wm_price else None,
            "avg_post_mkt_amp"        : round(avg_post_mkt_amp,  4) if avg_post_mkt_amp  else None,
            "post_wm_price_vs_easter" : round(post_wm_vs_easter,  2) if post_wm_vs_easter  is not None else None,
            "post_amp_vs_easter"      : round(post_amp_vs_easter, 2) if post_amp_vs_easter is not None else None,
            "post_wm_price_vs_base"   : round(post_wm_vs_base,   2) if post_wm_vs_base   is not None else None,
            "POST_PRICE_BEHAVIOR"     : post_label,
        })

    return enriched, p75_by_country


# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------
def compute_summary(cat_data: list) -> dict:
    seasonal    = [r for r in cat_data if r["IS_EASTER_SEASONAL"] == "Yes"]
    by_role     = {}
    by_matrix   = {}
    by_behavior = {}
    by_country  = {}
    by_post     = {}

    for r in cat_data:
        for d, key in [
            (by_role,     "PURCHASE_ROLE"),
            (by_matrix,   "MARKET_MATRIX"),
            (by_behavior, "COMPETITIVE_BEHAVIOR"),
            (by_post,     "POST_PRICE_BEHAVIOR"),
        ]:
            k = r[key]
            d.setdefault(k, {"cnt": 0, "seasonal": 0})
            d[k]["cnt"] += 1
            if r["IS_EASTER_SEASONAL"] == "Yes":
                d[k]["seasonal"] += 1

        c = r["COUNTRY_CODE"]
        by_country.setdefault(c, {"cnt": 0, "seasonal": 0, "top_lift": 0, "top_cat": ""})
        by_country[c]["cnt"] += 1
        if r["IS_EASTER_SEASONAL"] == "Yes":
            by_country[c]["seasonal"] += 1
        if r["wm_unit_lift"] > by_country[c]["top_lift"]:
            by_country[c]["top_lift"] = r["wm_unit_lift"]
            by_country[c]["top_cat"]  = r["CATEGORY"]

    return {
        "total_categories"       : len(cat_data),
        "seasonal_count"         : len(seasonal),
        "seasonal_pct"           : round(len(seasonal) / len(cat_data) * 100, 1) if cat_data else 0,
        "avg_wm_lift_seasonal"   : round(sum(r["wm_unit_lift"] for r in seasonal) / len(seasonal), 3) if seasonal else 0,
        "by_role"                : by_role,
        "by_matrix"              : by_matrix,
        "by_behavior"            : by_behavior,
        "by_post"                : by_post,
        "by_country"             : by_country,
        "price_wars"             : [r for r in cat_data if "Price War" in r["COMPETITIVE_BEHAVIOR"]],
        "top_10_lift"            : sorted(cat_data, key=lambda x: -x["wm_unit_lift"])[:10],
        "top_destinations"       : sorted(
            [r for r in cat_data if r["PURCHASE_ROLE"] == "Destination" and r["IS_EASTER_SEASONAL"] == "Yes"],
            key=lambda x: -x["wm_unit_lift"]
        )[:15],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Loading CSVs...")
    cat_raw = load_csv(BASE_DIR / "category_easter.csv")
    upc_raw = load_csv(BASE_DIR / "upc_easter.csv")
    print(f"  Category rows: {len(cat_raw)}")
    print(f"  UPC rows     : {len(upc_raw)}")

    cat_data, p75_map = process_records(cat_raw)
    upc_data, _       = process_records(upc_raw)

    # CAM virtual market
    cam_cat_raw  = aggregate_cam_categories(cat_raw)
    cam_upc_raw  = aggregate_cam_upcs(upc_raw)
    cam_cat_data, cam_p75 = process_records(cam_cat_raw)
    cam_upc_data, _       = process_records(cam_upc_raw)

    cat_data = cat_data + cam_cat_data
    upc_data = upc_data + cam_upc_data

    summary = compute_summary(cat_data)

    print(f"\nCategories: {len(cat_data) - len(cam_cat_data)} country + {len(cam_cat_data)} CAM")
    print(f"UPCs      : {len(upc_data) - len(cam_upc_data)} country + {len(cam_upc_data)} CAM")
    print(f"Seasonal  : {summary['seasonal_count']} ({summary['seasonal_pct']}%)")
    print(f"Post-Easter behavior: {summary['by_post']}")

    with open(BASE_DIR / "cat_processed.json", "w", encoding="utf-8") as f:
        json.dump(cat_data, f, ensure_ascii=False, indent=2)
    with open(BASE_DIR / "upc_processed.json", "w", encoding="utf-8") as f:
        json.dump(upc_data, f, ensure_ascii=False, indent=2)
    with open(BASE_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary,  f, ensure_ascii=False, indent=2)

    print("JSONs written.")


if __name__ == "__main__":
    main()
