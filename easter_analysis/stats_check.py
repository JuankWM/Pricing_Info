import json
cat = json.load(open('cat_processed.json'))
upc = json.load(open('upc_processed.json'))
seasonal = [r for r in cat if r['IS_EASTER_SEASONAL']=='Yes']
dest = [r for r in cat if r['PURCHASE_ROLE']=='Destination' and r['IS_EASTER_SEASONAL']=='Yes']
pw = [r for r in cat if 'Price War' in r['COMPETITIVE_BEHAVIOR']]
wm_gain = [r for r in cat if r['MARKET_MATRIX']=='Walmart Share Gain']
mkt_wide = [r for r in cat if r['MARKET_MATRIX']=='Market-Wide Growth']
print('TOTAL_CAT:', len(cat))
print('SEASONAL:', len(seasonal))
print('DESTINATION:', len(dest))
print('PRICE_WARS:', len(pw))
print('WM_GAIN:', len(wm_gain))
print('MKT_WIDE:', len(mkt_wide))
print('TOP5:')
top5 = sorted(cat, key=lambda x: -x['wm_unit_lift'])[:5]
for r in top5:
    print(' ', r['COUNTRY_CODE'], r['CATEGORY'][:45], r['wm_unit_lift'], r['IS_EASTER_SEASONAL'], r['PURCHASE_ROLE'])
print('TOP_DEST:')
for r in sorted(dest, key=lambda x: -x['wm_unit_lift'])[:8]:
    print(' ', r['COUNTRY_CODE'], r['CATEGORY'][:45], r['wm_unit_lift'], r['COMPETITIVE_BEHAVIOR'][:25], r['amp_chg_pct'])
print('PRICE_WARS:')
for r in pw[:8]:
    print(' ', r['COUNTRY_CODE'], r['CATEGORY'][:45], r['wm_unit_lift'], r['amp_chg_pct'])
print('UPC TOP10:')
for r in sorted(upc, key=lambda x: -float(x['wm_unit_lift']))[:10]:
    print(' ', r['COUNTRY_CODE'], r.get('UPC_DESC','')[:20], r['CATEGORY'][:30], r['wm_unit_lift'], r['IS_EASTER_SEASONAL'], r['PURCHASE_ROLE'])