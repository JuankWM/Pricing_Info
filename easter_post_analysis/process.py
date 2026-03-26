"""Post-Easter Price Analysis Engine.

Loads the weekly BQ CSV, computes base/Easter/post-Easter price metrics,
and emits processed JSON for the HTML report.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_WEEKS   = {202501,202502,202503,202504,202505,202506,202507,202508,202509}
PRE_WEEK     = 202510
EASTER_WEEK  = 202511
POST_WEEKS   = [202512, 202513, 202514, 202515, 202516, 202517]

WEEK_LABELS  = {
    202501: "W01", 202502: "W02", 202503: "W03", 202504: "W04",
    202505: "W05", 202506: "W06", 202507: "W07", 202508: "W08",
    202509: "W09", 202510: "W10 (Pre)", 202511: "W11 (Easter)",
    202512: "W12", 202513: "W13", 202514: "W14",
    202515: "W15", 202516: "W16", 202517: "W17",
}

FX_RATES = {
    "CR": 507.0,
    "GT": 7.55,
    "HN": 24.68,
    "NI": 36.63,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_float(v, default=0.0):
    try:
        f = float(v)
        return f if math.isfinite(f) else default
    except (TypeError, ValueError):
        return default


def sdiv(a, b, decimals=4):
    """Safe division."""
    try:
        return round(a / b, decimals) if b else None
    except (TypeError, ZeroDivisionError):
        return None


def pct_change(new_val, old_val):
    if not old_val:
        return None
    return round((new_val - old_val) / abs(old_val) * 100, 2)


# ---------------------------------------------------------------------------
# Load CSV
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> list:
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Build per-key weekly accumulators
# ---------------------------------------------------------------------------

def build_weekly_buckets(rows: list) -> dict:
    """Group rows by (country, category, sbu) -> week -> metrics (in local currency)."""
    buckets = defaultdict(lambda: defaultdict(lambda: {
        "wm_units": 0.0, "mkt_units": 0.0, "tot_units": 0.0,
        "wm_sales": 0.0, "mkt_sales": 0.0, "tot_sales": 0.0,
    }))
    for row in rows:
        key  = (row["COUNTRY_CODE"], row["CATEGORY"], row["SBU"])
        week = int(row["WM_YEAR_WEEK_NBR"])
        b    = buckets[key][week]
        b["wm_units"]  += safe_float(row["wm_units"])
        b["mkt_units"] += safe_float(row["mkt_units"])
        b["tot_units"] += safe_float(row["tot_units"])
        b["wm_sales"]  += safe_float(row["wm_sales"])
        b["mkt_sales"] += safe_float(row["mkt_sales"])
        b["tot_sales"] += safe_float(row["tot_sales"])
    return buckets


# ---------------------------------------------------------------------------
# Analyse one (country, category, sbu) series
# ---------------------------------------------------------------------------

def analyse_key(country, category, sbu, weeks_data: dict, fx: float) -> dict:
    """Compute base, Easter, and post-Easter price metrics for one key."""

    def price(sales, units):
        return sdiv(sales / fx, units, 4)  # USD/unit

    # Base period
    base_wm_sales  = sum(weeks_data[w]["wm_sales"]  for w in BASE_WEEKS if w in weeks_data)
    base_wm_units  = sum(weeks_data[w]["wm_units"]  for w in BASE_WEEKS if w in weeks_data)
    base_mkt_sales = sum(weeks_data[w]["mkt_sales"] for w in BASE_WEEKS if w in weeks_data)
    base_mkt_units = sum(weeks_data[w]["mkt_units"] for w in BASE_WEEKS if w in weeks_data)
    base_n         = sum(1 for w in BASE_WEEKS if w in weeks_data)

    avg_base_wm_price  = sdiv(sdiv(base_wm_sales, base_n, 6), sdiv(base_wm_units, base_n, 6), 4)
    avg_base_mkt_amp   = sdiv(sdiv(base_mkt_sales, base_n, 6), sdiv(base_mkt_units, base_n, 6), 4)
    # Simpler: use totals
    avg_base_wm_price  = price(base_wm_sales,  base_wm_units)  if base_wm_units  else None
    avg_base_mkt_amp   = price(base_mkt_sales, base_mkt_units) if base_mkt_units else None
    avg_base_wm_units  = sdiv(base_wm_units, base_n, 2) if base_n else None
    avg_base_mkt_units = sdiv(sum(weeks_data[w]["mkt_units"] for w in BASE_WEEKS if w in weeks_data), base_n, 2) if base_n else None

    # Easter week
    edata = weeks_data.get(EASTER_WEEK, {})
    e_wm_price  = price(edata.get("wm_sales",  0), edata.get("wm_units",  0)) if edata.get("wm_units") else None
    e_mkt_amp   = price(edata.get("mkt_sales", 0), edata.get("mkt_units", 0)) if edata.get("mkt_units") else None
    e_wm_units  = edata.get("wm_units",  0)
    e_mkt_units = edata.get("mkt_units", 0)

    # Post-Easter weeks — weekly granular
    post_weeks_detail = []
    for w in POST_WEEKS:
        wd = weeks_data.get(w, {})
        wu  = wd.get("wm_units",  0)
        mu  = wd.get("mkt_units", 0)
        ws  = wd.get("wm_sales",  0)
        ms  = wd.get("mkt_sales", 0)
        wp  = price(ws, wu)  if wu else None
        ma  = price(ms, mu)  if mu else None
        post_weeks_detail.append({
            "week":     w,
            "label":    WEEK_LABELS[w],
            "wm_units": round(wu, 2),
            "mkt_units":round(mu, 2),
            "wm_price": wp,
            "mkt_amp":  ma,
            # Price drop vs Easter
            "wm_price_vs_easter":  pct_change(wp,  e_wm_price)  if (wp  and e_wm_price)  else None,
            "mkt_amp_vs_easter":   pct_change(ma,  e_mkt_amp)   if (ma  and e_mkt_amp)   else None,
            # Price vs base
            "wm_price_vs_base":    pct_change(wp,  avg_base_wm_price) if (wp  and avg_base_wm_price) else None,
            "mkt_amp_vs_base":     pct_change(ma,  avg_base_mkt_amp)  if (ma  and avg_base_mkt_amp)  else None,
        })

    # Aggregate post-Easter summary
    post_wm_prices  = [pw["wm_price"] for pw in post_weeks_detail if pw["wm_price"] is not None]
    post_mkt_amps   = [pw["mkt_amp"]  for pw in post_weeks_detail if pw["mkt_amp"]  is not None]
    avg_post_wm_price = round(sum(post_wm_prices) / len(post_wm_prices), 4) if post_wm_prices else None
    avg_post_mkt_amp  = round(sum(post_mkt_amps)  / len(post_mkt_amps),  4) if post_mkt_amps  else None

    wm_price_drop_from_easter  = pct_change(avg_post_wm_price, e_wm_price)  if (avg_post_wm_price and e_wm_price)  else None
    mkt_drop_from_easter       = pct_change(avg_post_mkt_amp,  e_mkt_amp)   if (avg_post_mkt_amp  and e_mkt_amp)   else None
    wm_price_vs_base           = pct_change(avg_post_wm_price, avg_base_wm_price) if (avg_post_wm_price and avg_base_wm_price) else None

    # Did price actually drop post-Easter?
    price_dropped = (
        wm_price_drop_from_easter is not None and wm_price_drop_from_easter < -1.0
    )
    price_spiked = (
        wm_price_drop_from_easter is not None and wm_price_drop_from_easter > 1.0
    )

    # Full weekly series (all 17 weeks) for trend chart
    all_weeks_series = []
    all_weeks = sorted(BASE_WEEKS) + [PRE_WEEK, EASTER_WEEK] + POST_WEEKS
    for w in all_weeks:
        wd  = weeks_data.get(w, {})
        wu  = wd.get("wm_units",  0)
        mu  = wd.get("mkt_units", 0)
        ws  = wd.get("wm_sales",  0)
        ms  = wd.get("mkt_sales", 0)
        all_weeks_series.append({
            "week":  w,
            "label": WEEK_LABELS[w],
            "wm_price": price(ws, wu) if wu else None,
            "mkt_amp":  price(ms, mu) if mu else None,
            "wm_units": round(wu, 2),
        })

    return {
        "COUNTRY_CODE":           country,
        "CATEGORY":               category,
        "SBU":                    sbu,
        # Base
        "avg_base_wm_price":      avg_base_wm_price,
        "avg_base_mkt_amp":       avg_base_mkt_amp,
        "avg_base_wm_units":      avg_base_wm_units,
        "avg_base_mkt_units":     avg_base_mkt_units,
        # Easter
        "easter_wm_price":        e_wm_price,
        "easter_mkt_amp":         e_mkt_amp,
        "easter_wm_units":        round(e_wm_units, 2),
        "easter_mkt_units":       round(e_mkt_units, 2),
        # Easter lift (price)
        "wm_price_easter_vs_base":  pct_change(e_wm_price, avg_base_wm_price) if (e_wm_price and avg_base_wm_price) else None,
        "mkt_amp_easter_vs_base":   pct_change(e_mkt_amp,  avg_base_mkt_amp)  if (e_mkt_amp  and avg_base_mkt_amp)  else None,
        # Post-Easter summary
        "avg_post_wm_price":       avg_post_wm_price,
        "avg_post_mkt_amp":        avg_post_mkt_amp,
        "wm_price_drop_from_easter": wm_price_drop_from_easter,
        "mkt_drop_from_easter":      mkt_drop_from_easter,
        "wm_price_vs_base":          wm_price_vs_base,
        "price_dropped":             price_dropped,
        "price_spiked":              price_spiked,
        # Granular
        "post_weeks":             post_weeks_detail,
        "all_weeks_series":       all_weeks_series,
    }


# ---------------------------------------------------------------------------
# CAM aggregation (per-week, in USD)
# ---------------------------------------------------------------------------

def aggregate_cam(country_records: list) -> list:
    """Merge all country records into a single CAM virtual market."""
    cam_buckets = defaultdict(lambda: defaultdict(lambda: {
        "wm_units": 0.0, "mkt_units": 0.0, "tot_units": 0.0,
        "wm_sales": 0.0, "mkt_sales": 0.0,
    }))

    for rec in country_records:
        if rec["COUNTRY_CODE"] == "CAM":
            continue
        fx  = FX_RATES.get(rec["COUNTRY_CODE"], 1.0)
        key = (rec["CATEGORY"], rec["SBU"])
        for ws in rec["all_weeks_series"]:
            w   = ws["week"]
            b   = cam_buckets[key][w]
            # Units are additive
            b["wm_units"]  += ws["wm_units"]
            # Sales need original values; re-derive from price * units
            b["wm_sales"]  += (ws["wm_price"] or 0) * ws["wm_units"] * fx / fx  # already USD (price was /fx)
            # We stored price already in USD, so sales_usd = price_usd * units
            b["wm_sales"]  += 0  # prevent double add — reset below

    # Simpler: re-aggregate directly from raw rows stored per country
    # We'll pass raw_rows instead
    return []


def aggregate_cam_from_buckets(all_buckets: dict) -> list:
    """Build CAM records by summing USD-converted values per (category,sbu,week)."""
    cam_acc = defaultdict(lambda: defaultdict(lambda: {
        "wm_units": 0.0, "mkt_units": 0.0, "tot_units": 0.0,
        "wm_sales": 0.0, "mkt_sales": 0.0,
    }))

    for (country, category, sbu), weeks_data in all_buckets.items():
        fx = FX_RATES.get(country, 1.0)
        key = (category, sbu)
        for week, wd in weeks_data.items():
            b = cam_acc[key][week]
            b["wm_units"]  += wd["wm_units"]
            b["mkt_units"] += wd["mkt_units"]
            b["tot_units"] += wd["tot_units"]
            b["wm_sales"]  += wd["wm_sales"]  / fx   # → USD
            b["mkt_sales"] += wd["mkt_sales"] / fx   # → USD

    cam_records = []
    for (category, sbu), weeks_data in cam_acc.items():
        rec = analyse_key("CAM", category, sbu, weeks_data, fx=1.0)  # already in USD
        cam_records.append(rec)
    return cam_records


# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------

def compute_summary(records: list) -> dict:
    valid = [r for r in records if r["wm_price_drop_from_easter"] is not None]
    dropped   = [r for r in valid if r["price_dropped"]]
    spiked    = [r for r in valid if r["price_spiked"]]
    stable    = [r for r in valid if not r["price_dropped"] and not r["price_spiked"]]

    drops_list = [r["wm_price_drop_from_easter"] for r in dropped]
    spikes_list = [r["wm_price_drop_from_easter"] for r in spiked]

    avg_drop  = round(sum(drops_list)  / len(drops_list),  2) if drops_list  else 0
    avg_spike = round(sum(spikes_list) / len(spikes_list), 2) if spikes_list else 0

    by_country = defaultdict(lambda: {"total": 0, "dropped": 0, "spiked": 0, "stable": 0})
    for r in valid:
        c = r["COUNTRY_CODE"]
        by_country[c]["total"] += 1
        if r["price_dropped"]: by_country[c]["dropped"] += 1
        elif r["price_spiked"]: by_country[c]["spiked"]  += 1
        else:                   by_country[c]["stable"]  += 1

    return {
        "total_categories":  len(valid),
        "price_dropped":     len(dropped),
        "price_spiked":      len(spiked),
        "price_stable":      len(stable),
        "drop_pct":          round(len(dropped) / len(valid) * 100, 1) if valid else 0,
        "spike_pct":         round(len(spiked)  / len(valid) * 100, 1) if valid else 0,
        "avg_drop_pct":      avg_drop,
        "avg_spike_pct":     avg_spike,
        "by_country":        dict(by_country),
        "top_drops":         sorted(dropped, key=lambda x: x["wm_price_drop_from_easter"])[:15],
        "top_spikes":        sorted(spiked,  key=lambda x: -x["wm_price_drop_from_easter"])[:15],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    csv_path = BASE_DIR / "weekly_category_raw.csv"
    print(f"Loading {csv_path} ...")
    rows = load_csv(csv_path)
    print(f"  {len(rows):,} rows loaded")

    all_buckets = build_weekly_buckets(rows)
    print(f"  {len(all_buckets):,} unique (country, category, sbu) keys")

    # Analyse each country key
    country_records = []
    for (country, category, sbu), weeks_data in all_buckets.items():
        fx = FX_RATES.get(country, 1.0)
        rec = analyse_key(country, category, sbu, weeks_data, fx)
        country_records.append(rec)

    # CAM virtual market
    cam_records = aggregate_cam_from_buckets(all_buckets)
    print(f"  CAM virtual market: {len(cam_records)} categories")

    all_records = country_records + cam_records

    summary = compute_summary(all_records)
    print(f"\n=== POST-EASTER PRICE ANALYSIS ===")
    print(f"Total categories   : {summary['total_categories']}")
    print(f"Prices DROPPED     : {summary['price_dropped']}  ({summary['drop_pct']}%)  avg {summary['avg_drop_pct']}%")
    print(f"Prices SPIKED      : {summary['price_spiked']}  ({summary['spike_pct']}%)  avg +{summary['avg_spike_pct']}%")
    print(f"Prices STABLE      : {summary['price_stable']}")

    # Compact records for embed (strip heavy all_weeks_series to keep JSON small)
    def compact(r):
        return {
            "c":      r["COUNTRY_CODE"],
            "cat":    r["CATEGORY"],
            "sbu":    r["SBU"],
            "bwp":    r["avg_base_wm_price"],
            "bma":    r["avg_base_mkt_amp"],
            "bwu":    r["avg_base_wm_units"],
            "ewp":    r["easter_wm_price"],
            "ema":    r["easter_mkt_amp"],
            "ewu":    r["easter_wm_units"],
            "apwp":   r["avg_post_wm_price"],
            "apma":   r["avg_post_mkt_amp"],
            "drop":   r["wm_price_drop_from_easter"],
            "mdrop":  r["mkt_drop_from_easter"],
            "vsbase": r["wm_price_vs_base"],
            "fell":   r["price_dropped"],
            "rose":   r["price_spiked"],
            "ewpvb":  r["wm_price_easter_vs_base"],
            "post":   r["post_weeks"],
            "series": r["all_weeks_series"],
        }

    embed = {
        "records": [compact(r) for r in all_records],
        "summary": {
            k: v for k, v in summary.items()
            if k not in ("top_drops", "top_spikes")  # keep summary lean, use records in JS
        },
        "weeks":   [WEEK_LABELS[w] for w in (sorted(BASE_WEEKS) + [PRE_WEEK, EASTER_WEEK] + POST_WEEKS)],
        "post_week_labels": [WEEK_LABELS[w] for w in POST_WEEKS],
        "easter_week": EASTER_WEEK,
        "post_weeks":  POST_WEEKS,
    }

    out_path = BASE_DIR / "embed_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(embed, f, ensure_ascii=False, separators=(',', ':'))
    print(f"\nEmbed JSON written: {out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
