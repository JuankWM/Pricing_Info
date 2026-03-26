-- Post-Easter Price Analysis — Category Level
-- Pulls week-by-week granular data for all periods:
--   Base     : 202501-202509  (9 weeks pre-Easter baseline)
--   Pre-Easter: 202510
--   Easter   : 202511
--   Post-Easter: 202512-202517  (6 weeks after Easter)
--
-- One row per (COUNTRY_CODE, DEPT_CAT_NBR_DESC_COMB, SBU, WM_YEAR_WEEK_NBR)

SELECT
  COUNTRY_CODE,
  SBU,
  DEPT_CAT_NBR_DESC_COMB                          AS CATEGORY,
  WM_YEAR_WEEK_NBR,

  SUM(WALMART_UNITS)  AS wm_units,
  SUM(MARKET_UNITS)   AS mkt_units,
  SUM(TOTAL_UNITS)    AS tot_units,
  SUM(WALMART_SALES)  AS wm_sales,
  SUM(MARKET_SALES)   AS mkt_sales,
  SUM(TOTAL_SALES)    AS tot_sales,

  -- Derived prices (safe division done in Python)
  ROUND(SAFE_DIVIDE(SUM(WALMART_SALES), SUM(WALMART_UNITS)), 4) AS wm_price,
  ROUND(SAFE_DIVIDE(SUM(MARKET_SALES),  SUM(MARKET_UNITS)),  4) AS mkt_amp

FROM `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_temp_market_trend`
WHERE WM_YEAR_WEEK_NBR IN (
  202501,202502,202503,202504,202505,202506,202507,202508,202509,  -- base
  202510,                                                           -- pre-Easter
  202511,                                                           -- Easter
  202512,202513,202514,202515,202516,202517                         -- post-Easter
)
GROUP BY 1,2,3,4
ORDER BY COUNTRY_CODE, CATEGORY, WM_YEAR_WEEK_NBR
