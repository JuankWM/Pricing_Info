WITH src AS (
  SELECT
    COUNTRY_CODE, UPC_NBR, UPC_DESC, DEPT_CAT_NBR_DESC_COMB, SBU,
    WM_YEAR_WEEK_NBR,
    SUM(WALMART_UNITS)  AS wm_units,
    SUM(MARKET_UNITS)   AS mkt_units,
    SUM(TOTAL_UNITS)    AS tot_units,
    SUM(WALMART_SALES)  AS wm_sales,
    SUM(MARKET_SALES)   AS mkt_sales,
    SUM(TOTAL_SALES)    AS tot_sales
  FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_temp_market_trend`
  WHERE WM_YEAR_WEEK_NBR IN (202501,202502,202503,202504,202505,202506,202507,202508,202509,202510,202511)
  GROUP BY 1,2,3,4,5,6
),
base AS (
  SELECT COUNTRY_CODE, UPC_NBR, UPC_DESC, DEPT_CAT_NBR_DESC_COMB, SBU,
    COUNT(DISTINCT WM_YEAR_WEEK_NBR) AS base_n,
    SUM(wm_units)  AS base_wm_units,
    SUM(mkt_units) AS base_mkt_units,
    SUM(tot_units) AS base_tot_units,
    SUM(wm_sales)  AS base_wm_sales,
    SUM(mkt_sales) AS base_mkt_sales,
    SUM(tot_sales) AS base_tot_sales
  FROM src WHERE WM_YEAR_WEEK_NBR BETWEEN 202501 AND 202509
  GROUP BY 1,2,3,4,5
),
easter AS (
  SELECT COUNTRY_CODE, UPC_NBR, UPC_DESC, DEPT_CAT_NBR_DESC_COMB, SBU,
    SUM(wm_units)  AS e_wm_units,
    SUM(mkt_units) AS e_mkt_units,
    SUM(tot_units) AS e_tot_units,
    SUM(wm_sales)  AS e_wm_sales,
    SUM(mkt_sales) AS e_mkt_sales,
    SUM(tot_sales) AS e_tot_sales
  FROM src WHERE WM_YEAR_WEEK_NBR = 202511
  GROUP BY 1,2,3,4,5
),
lifts AS (
  SELECT
    e.COUNTRY_CODE,
    e.UPC_NBR,
    e.UPC_DESC,
    e.DEPT_CAT_NBR_DESC_COMB AS CATEGORY,
    e.SBU,
    e.e_wm_units    AS easter_wm_units,
    e.e_mkt_units   AS easter_mkt_units,
    e.e_tot_units   AS easter_tot_units,
    e.e_wm_sales    AS easter_wm_sales,
    e.e_mkt_sales   AS easter_mkt_sales,
    e.e_tot_sales   AS easter_tot_sales,
    ROUND(b.base_wm_units  / b.base_n, 2) AS avg_base_wm_units,
    ROUND(b.base_tot_units / b.base_n, 2) AS avg_base_tot_units,
    ROUND(b.base_wm_sales  / b.base_n, 2) AS avg_base_wm_sales,
    ROUND(b.base_mkt_sales / b.base_n, 2) AS avg_base_mkt_sales,
    ROUND(b.base_mkt_units / b.base_n, 2) AS avg_base_mkt_units,
    ROUND(SAFE_DIVIDE(e.e_wm_units,  b.base_wm_units  / b.base_n), 4) AS wm_unit_lift,
    ROUND(SAFE_DIVIDE(e.e_tot_units, b.base_tot_units / b.base_n), 4) AS total_unit_lift,
    ROUND(SAFE_DIVIDE(e.e_mkt_units, b.base_mkt_units / b.base_n), 4) AS mkt_unit_lift,
    ROUND(SAFE_DIVIDE(e.e_wm_units,  e.e_tot_units)  * 100, 2) AS easter_wm_share_pct,
    ROUND(SAFE_DIVIDE(b.base_wm_units / b.base_n, b.base_tot_units / b.base_n) * 100, 2) AS base_wm_share_pct,
    ROUND(SAFE_DIVIDE(e.e_mkt_sales,  e.e_mkt_units),  2)  AS easter_amp,
    ROUND(SAFE_DIVIDE(b.base_mkt_sales / b.base_n, b.base_mkt_units / b.base_n), 2) AS base_amp,
    ROUND(SAFE_DIVIDE(e.e_wm_sales,  e.e_wm_units),  2)   AS easter_wm_price,
    ROUND(SAFE_DIVIDE(b.base_wm_sales / b.base_n, b.base_wm_units / b.base_n), 2) AS base_wm_price
  FROM easter e
  JOIN base b USING (COUNTRY_CODE, UPC_NBR, DEPT_CAT_NBR_DESC_COMB, SBU)
)
SELECT * FROM lifts
WHERE wm_unit_lift >= 1.5 OR total_unit_lift >= 1.5
ORDER BY wm_unit_lift DESC
LIMIT 500