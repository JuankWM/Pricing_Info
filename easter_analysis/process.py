"""Easter Week Seasonality Analysis Engine.

Loads BQ query results, applies all analytical flags, and emits
the processed data as JSON for the HTML report.
"""
import json
import math
from pathlib import Path

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
    """Percentage change from old to new."""
    if not old_val or old_val == 0:
        return None
    return (new_val - old_val) / abs(old_val) * 100


# ---------------------------------------------------------------------------
# Purchase-Role Rules  (keyword matching on CATEGORY string)
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
# Competitive-Behavior logic
# ---------------------------------------------------------------------------

def competitive_behavior(amp_chg_pct, wm_lift):
    """Return competitive behavior label based on AMP change and lift."""
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
    """Classify WM vs Market growth dynamic."""
    wm_growing = wm_lift >= 1.1
    mkt_growing = (mkt_lift is not None) and (mkt_lift >= 1.1)
    wm_shrinking = wm_lift < 0.95
    mkt_shrinking = (mkt_lift is not None) and (mkt_lift < 0.95)

    if wm_growing and mkt_growing:
        return "Market-Wide Growth"
    if wm_growing and not mkt_growing:
        return "Walmart Share Gain"
    if wm_shrinking and mkt_growing:
        return "Walmart Share Loss"
    if wm_shrinking and mkt_shrinking:
        return "Market Contraction"
    return "Flat / Mixed"


# ---------------------------------------------------------------------------
# Process records
# ---------------------------------------------------------------------------

def process_records(records):
    """Enrich a list of category or UPC records with all analysis flags."""

    # Step 1 – compute per-country p75 of wm_unit_lift
    by_country = {}
    for r in records:
        c = r.get("COUNTRY_CODE", "")
        lift = safe_float(r.get("wm_unit_lift", 0))
        by_country.setdefault(c, []).append(lift)

    p75_by_country = {}
    for c, lifts in by_country.items():
        lifts_sorted = sorted(lifts)
        idx = int(len(lifts_sorted) * 0.75)
        p75_by_country[c] = lifts_sorted[min(idx, len(lifts_sorted) - 1)]

    # Step 2 – enrich each record
    enriched = []
    for r in records:
        country = r.get("COUNTRY_CODE", "")
        category = r.get("CATEGORY", "")
        wm_lift = safe_float(r.get("wm_unit_lift", 0))
        tot_lift = safe_float(r.get("total_unit_lift", 0))
        mkt_lift_raw = r.get("mkt_unit_lift")
        mkt_lift = safe_float(mkt_lift_raw, 0) if mkt_lift_raw not in (None, "", "null") else None

        easter_amp = safe_float(r.get("easter_amp", 0))
        base_amp = safe_float(r.get("base_amp", 0))
        amp_chg = pct_change(easter_amp, base_amp)

        easter_wm_share = safe_float(r.get("easter_wm_share_pct", 0))
        base_wm_share = safe_float(r.get("base_wm_share_pct", 0))
        share_delta = easter_wm_share - base_wm_share

        easter_wm_price = safe_float(r.get("easter_wm_price", 0))
        base_wm_price = safe_float(r.get("base_wm_price", 0))
        wm_price_chg = pct_change(easter_wm_price, base_wm_price)

        p75 = p75_by_country.get(country, 1.5)
        is_seasonal = "Yes" if (wm_lift >= 1.5 or wm_lift >= p75) else "No"

        role = assign_role(category)
        comp = competitive_behavior(amp_chg, wm_lift)
        matrix = market_matrix(wm_lift, mkt_lift)

        enriched.append({
            **r,
            "wm_unit_lift": round(wm_lift, 4),
            "total_unit_lift": round(tot_lift, 4),
            "mkt_unit_lift": round(mkt_lift, 4) if mkt_lift is not None else None,
            "easter_amp": round(easter_amp, 2),
            "base_amp": round(base_amp, 2),
            "amp_chg_pct": round(amp_chg, 2) if amp_chg is not None else None,
            "easter_wm_share_pct": round(easter_wm_share, 2),
            "base_wm_share_pct": round(base_wm_share, 2),
            "share_delta_pp": round(share_delta, 2),
            "wm_price_chg_pct": round(wm_price_chg, 2) if wm_price_chg is not None else None,
            "p75_country_lift": round(p75, 4),
            "IS_EASTER_SEASONAL": is_seasonal,
            "PURCHASE_ROLE": role,
            "COMPETITIVE_BEHAVIOR": comp,
            "MARKET_MATRIX": matrix,
        })

    return enriched, p75_by_country


# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------

def compute_summary(cat_data):
    seasonal = [r for r in cat_data if r["IS_EASTER_SEASONAL"] == "Yes"]
    by_role = {}
    by_matrix = {}
    by_behavior = {}
    by_country = {}

    for r in cat_data:
        for d, key in [(by_role, "PURCHASE_ROLE"), (by_matrix, "MARKET_MATRIX"), (by_behavior, "COMPETITIVE_BEHAVIOR")]:
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
            by_country[c]["top_cat"] = r["CATEGORY"]

    return {
        "total_categories": len(cat_data),
        "seasonal_count": len(seasonal),
        "seasonal_pct": round(len(seasonal) / len(cat_data) * 100, 1) if cat_data else 0,
        "avg_wm_lift_seasonal": round(sum(r["wm_unit_lift"] for r in seasonal) / len(seasonal), 3) if seasonal else 0,
        "by_role": by_role,
        "by_matrix": by_matrix,
        "by_behavior": by_behavior,
        "by_country": by_country,
        "price_wars": [r for r in cat_data if "Price War" in r["COMPETITIVE_BEHAVIOR"]],
        "top_10_lift": sorted(cat_data, key=lambda x: -x["wm_unit_lift"])[:10],
        "top_destinations": sorted(
            [r for r in cat_data if r["PURCHASE_ROLE"] == "Destination" and r["IS_EASTER_SEASONAL"] == "Yes"],
            key=lambda x: -x["wm_unit_lift"]
        )[:15],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base_dir = Path(__file__).parent

    with open(base_dir / "category_easter.json", encoding="utf-8") as f:
        cat_raw = json.load(f)
    with open(base_dir / "upc_easter.json", encoding="utf-8") as f:
        upc_raw = json.load(f)

    cat_data, p75_map = process_records(cat_raw)
    upc_data, _ = process_records(upc_raw)
    summary = compute_summary(cat_data)

    # Dump processed outputs
    with open(base_dir / "cat_processed.json", "w", encoding="utf-8") as f:
        json.dump(cat_data, f, ensure_ascii=False, indent=2)
    with open(base_dir / "upc_processed.json", "w", encoding="utf-8") as f:
        json.dump(upc_data, f, ensure_ascii=False, indent=2)
    with open(base_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Categories processed : {len(cat_data)}")
    print(f"UPCs processed       : {len(upc_data)}")
    print(f"Seasonal categories  : {summary['seasonal_count']} ({summary['seasonal_pct']}%)")
    print(f"P75 lift by country  : {p75_map}")
    print(f"\nTop 5 categories by WM Lift:")
    for r in summary["top_10_lift"][:5]:
        print(f"  [{r['COUNTRY_CODE']}] {r['CATEGORY'][:50]:50s}  lift={r['wm_unit_lift']:.2f}  seasonal={r['IS_EASTER_SEASONAL']}  role={r['PURCHASE_ROLE']}")


if __name__ == "__main__":
    main()