"""Render the final Easter Analysis HTML report.

Reads embed_data.json and generates index.html.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent
DATA = json.load(open(BASE / "embed_data.json", encoding="utf-8"))
DATA_JS = json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))

COUNTRY_NAMES = {"CR": "Costa Rica", "GT": "Guatemala", "HN": "Honduras", "NI": "Nicaragua"}

DATA_PLACEHOLDER = DATA_JS
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0" />
<title>Easter Week Seasonality Analysis 2025 – Pricing Intelligence CAM</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
body{{font-family:'Segoe UI',sans-serif;background:#f0f4f8}}
.wm-blue{{background:#0053e2}}
.wm-spark{{background:#ffc220}}
.card{{background:white;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.09)}}
.kpi:hover{{transform:translateY(-2px);transition:transform .15s}}
table thead th{{position:sticky;top:0;background:#f1f5f9;z-index:2}}
.tab{{cursor:pointer;padding:8px 18px;border-radius:8px 8px 0 0;font-weight:600;font-size:13px;white-space:nowrap}}
.tab.active{{background:#0053e2;color:white}}
.tab:not(.active){{background:#e2e8f0;color:#475569}}
.tab:not(.active):hover{{background:#cbd5e1}}
.panel{{display:none}}.panel.active{{display:block}}
.badge{{display:inline-block;padding:1px 7px;border-radius:9999px;font-size:11px;font-weight:700}}
.bg-dest{{background:#dbeafe;color:#1e40af}}
.bg-imp{{background:#dcfce7;color:#166534}}
.bg-comp{{background:#fef9c3;color:#854d0e}}
.bg-other{{background:#f3f4f6;color:#4b5563}}
.bg-sea{{background:#d1fae5;color:#065f46}}
.bg-no{{background:#fee2e2;color:#991b1b}}
.bg-pw{{background:#fca5a5;color:#7f1d1d}}
.bg-conv{{background:#bfdbfe;color:#1e40af}}
.bg-stab{{background:#e5e7eb;color:#374151}}
.bg-mwg{{background:#a7f3d0;color:#065f46}}
.bg-wmg{{background:#bfdbfe;color:#1e40af}}
.bg-wml{{background:#fecaca;color:#991b1b}}
.bg-flat{{background:#e5e7eb;color:#374151}}
.bg-mc{{background:#fed7aa;color:#92400e}}
.chart-box{{position:relative;height:320px}}
.chart-box-lg{{position:relative;height:390px}}
.filter-row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px}}
.fsel{{border:1px solid #cbd5e1;border-radius:8px;padding:5px 10px;font-size:13px;background:#f8fafc}}
.insight-bullet{{padding:6px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#334155}}
.insight-bullet:last-child{{border:none}}
</style>
</head>
<body class="min-h-screen">

<!-- HEADER -->
<header class="wm-blue text-white px-6 py-4 flex items-center justify-between shadow-xl">
  <div class="flex items-center gap-3">
    <div class="wm-spark w-11 h-11 rounded-full flex items-center justify-center font-black text-gray-900 text-xl">W</div>
    <div>
      <div class="font-bold text-xl">Easter Week Seasonality Analysis — Pricing Intelligence</div>
      <div class="text-blue-200 text-xs">CAM Region · 2025 · Base: Weeks 202501–202509 · Easter Week: 202511 · Methodology: Unit Lift + AMP + Market Matrix</div>
    </div>
  </div>
  <div class="text-right text-sm">
    <div class="text-blue-200">Generated</div>
    <div class="font-semibold">25 Mar 2025</div>
  </div>
</header>

<!-- KPI STRIP -->
<div class="px-6 py-4 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3" id="kpiStrip"></div>

<!-- EXECUTIVE INSIGHTS -->
<div class="px-6 pb-4">
  <div class="card p-5 border-l-4 border-blue-500">
    <div class="flex gap-3">
      <div class="text-2xl">💡</div>
      <div class="flex-1">
        <div class="font-bold text-gray-800 mb-2">Executive Insights — Easter Week 202511</div>
        <div id="insightsList" class="grid grid-cols-1 md:grid-cols-2 gap-1"></div>
      </div>
    </div>
  </div>
</div>

<!-- TABS -->
<div class="px-6 pb-0">
  <div class="flex gap-1 overflow-x-auto pb-0">
    <div class="tab active" onclick="switchTab('tabCat')">📊 Category Analysis</div>
    <div class="tab" onclick="switchTab('tabUPC')">🏷️ UPC Analysis</div>
    <div class="tab" onclick="switchTab('tabMatrix')">🗺️ Market Matrix & Charts</div>
    <div class="tab" onclick="switchTab('tabMethod')">📖 Methodology</div>
  </div>
</div>

<!-- ===== TAB: CATEGORIES ===== -->
<div id="tabCat" class="panel active px-6 py-4">
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
    <div class="card p-4 lg:col-span-2">
      <div class="font-bold text-gray-800 mb-1">🏆 Top 15 Seasonal Categories — WM Unit Lift</div>
      <div class="text-xs text-gray-400 mb-2">Lift = Easter WM units ÷ weekly avg during base period (202501–202509)</div>
      <div class="chart-box"><canvas id="chartTop15"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">🎭 Purchase Role (Seasonal Only)</div>
      <div class="text-xs text-gray-400 mb-2">Distribution of seasonal categories by role</div>
      <div class="chart-box"><canvas id="chartRole"></canvas></div>
    </div>
  </div>

  <!-- Filters -->
  <div class="card p-4 mb-3">
    <div class="font-bold text-gray-700 mb-2 text-sm">Filters</div>
    <div class="filter-row">
      <select class="fsel" id="fCatCountry" onchange="renderCatTable()"><option value="">All Countries</option><option>CR</option><option>GT</option><option>HN</option><option>NI</option></select>
      <select class="fsel" id="fCatSBU" onchange="renderCatTable()"><option value="">All SBUs</option><option>CONSUMABLES</option><option>GROCERIES</option><option>PHARMACY</option></select>
      <select class="fsel" id="fCatRole" onchange="renderCatTable()"><option value="">All Roles</option><option>Destination</option><option>Impulse / Convenience</option><option>Complementary</option><option>Other</option></select>
      <select class="fsel" id="fCatSeas" onchange="renderCatTable()"><option value="">All</option><option value="Yes">Seasonal Only</option><option value="No">Non-Seasonal</option></select>
      <select class="fsel" id="fCatMat" onchange="renderCatTable()"><option value="">All Matrix</option><option>Market-Wide Growth</option><option>Walmart Share Gain</option><option>Walmart Share Loss</option><option>Flat / Mixed</option><option>Market Contraction</option></select>
      <input class="fsel" id="fCatSearch" placeholder="Search category..." oninput="renderCatTable()" style="width:180px" />
      <span class="text-xs text-gray-400 ml-auto" id="catCount"></span>
    </div>
  </div>
  <div class="card overflow-auto" style="max-height:520px">
    <table class="w-full text-xs">
      <thead><tr class="text-left text-gray-500">
        <th class="py-2 px-2">Country</th><th class="py-2 px-2">SBU</th><th class="py-2 px-2" style="max-width:220px">Category</th>
        <th class="py-2 px-2 text-right">WM Lift</th><th class="py-2 px-2 text-right">Mkt Lift</th><th class="py-2 px-2 text-right">Tot Lift</th>
        <th class="py-2 px-2 text-center">Seasonal?</th><th class="py-2 px-2 text-center">Role</th>
        <th class="py-2 px-2 text-center">Market Matrix</th>
        <th class="py-2 px-2 text-right">WM Share Δpp</th>
        <th class="py-2 px-2 text-right">AMP Δ%</th>
        <th class="py-2 px-2 text-center">Competitive</th>
      </tr></thead>
      <tbody id="catTbody"></tbody>
    </table>
  </div>
</div>

<!-- ===== TAB: UPC ===== -->
<div id="tabUPC" class="panel px-6 py-4">
  <div class="card p-4 mb-3">
    <div class="font-bold text-gray-700 mb-2 text-sm">Filters — UPC Level (Lift ≥ 1.5)</div>
    <div class="filter-row">
      <select class="fsel" id="fUPCCountry" onchange="renderUPCTable()"><option value="">All Countries</option><option>CR</option><option>GT</option><option>HN</option><option>NI</option></select>
      <select class="fsel" id="fUPCSBU" onchange="renderUPCTable()"><option value="">All SBUs</option><option>CONSUMABLES</option><option>GROCERIES</option><option>PHARMACY</option></select>
      <select class="fsel" id="fUPCRole" onchange="renderUPCTable()"><option value="">All Roles</option><option>Destination</option><option>Impulse / Convenience</option><option>Complementary</option><option>Other</option></select>
      <select class="fsel" id="fUPCMat" onchange="renderUPCTable()"><option value="">All Matrix</option><option>Market-Wide Growth</option><option>Walmart Share Gain</option><option>Walmart Share Loss</option></select>
      <input class="fsel" id="fUPCSearch" placeholder="Search UPC/desc..." oninput="renderUPCTable()" style="width:180px" />
      <span class="text-xs text-gray-400 ml-auto" id="upcCount"></span>
    </div>
  </div>
  <div class="card overflow-auto" style="max-height:600px">
    <table class="w-full text-xs">
      <thead><tr class="text-left text-gray-500">
        <th class="py-2 px-2">Country</th><th class="py-2 px-2">UPC</th><th class="py-2 px-2">Description</th>
        <th class="py-2 px-2" style="max-width:180px">Category</th><th class="py-2 px-2">SBU</th>
        <th class="py-2 px-2 text-right">WM Lift</th><th class="py-2 px-2 text-right">Tot Lift</th>
        <th class="py-2 px-2 text-center">Seasonal?</th><th class="py-2 px-2 text-center">Role</th>
        <th class="py-2 px-2 text-center">Matrix</th>
        <th class="py-2 px-2 text-right">Share Δpp</th>
        <th class="py-2 px-2 text-right">AMP Δ%</th>
        <th class="py-2 px-2 text-right">Easter WM Units</th>
        <th class="py-2 px-2 text-right">Easter WM Sales</th>
      </tr></thead>
      <tbody id="upcTbody"></tbody>
    </table>
  </div>
</div>

<!-- ===== TAB: CHARTS ===== -->
<div id="tabMatrix" class="panel px-6 py-4">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">🗺️ Market Relevance Matrix</div>
      <div class="text-xs text-gray-400 mb-2">Classification of categories by WM vs Market growth dynamics</div>
      <div class="chart-box"><canvas id="chartMatrix"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">⚡ Competitive Behavior Distribution</div>
      <div class="text-xs text-gray-400 mb-2">Based on AMP change + unit lift thresholds</div>
      <div class="chart-box"><canvas id="chartBehavior"></canvas></div>
    </div>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">💰 AMP Comparison — Top Destination Categories</div>
      <div class="text-xs text-gray-400 mb-2">Base period avg AMP vs Easter Week AMP (non-WM market price)</div>
      <div class="chart-box-lg"><canvas id="chartAMP"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">🌍 Seasonal Categories by Country</div>
      <div class="text-xs text-gray-400 mb-2">Breakdown of seasonal, WM gain, and price-war categories per country</div>
      <div class="chart-box"><canvas id="chartCountry"></canvas></div>
    </div>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">🫧 WM Lift vs Market Lift (Category Scatter)</div>
      <div class="text-xs text-gray-400 mb-2">Each dot = one category. Color = Purchase Role. Above diagonal = WM outpacing market.</div>
      <div class="chart-box-lg"><canvas id="chartScatter"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">📈 WM Share Delta (pp) — Seasonal Categories</div>
      <div class="text-xs text-gray-400 mb-2">Change in WM share during Easter vs base (positive = WM gained share)</div>
      <div class="chart-box-lg"><canvas id="chartShareDelta"></canvas></div>
    </div>
  </div>
</div>

<!-- ===== TAB: METHODOLOGY ===== -->
<div id="tabMethod" class="panel px-6 py-4">
  <div class="card p-6 max-w-4xl">
    <div class="text-xl font-bold text-gray-800 mb-4">📖 Analytical Methodology</div>
    <div class="space-y-5 text-sm text-gray-700">
      <div>
        <div class="font-bold text-blue-700 mb-1">1. Seasonality Index (Unit Lift)</div>
        <div class="bg-gray-50 rounded p-3 font-mono text-xs mb-2">WM_Unit_Lift = Easter_WM_Units ÷ (Base_WM_Units ÷ Base_Weeks)</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Easter Week:</strong> WM_YEAR_WEEK_NBR = 202511</li>
          <li><strong>Base Period:</strong> Weeks 202501–202509 (9 weeks) — excludes 202510 (immediate pre-Easter week)</li>
          <li><strong>Seasonal Flag Criteria:</strong> WM_Unit_Lift ≥ 1.5 OR ≥ 75th percentile within country</li>
          <li><strong>P75 by Country:</strong> CR≈1.28 · GT≈1.25 · HN≈1.19 · NI≈1.27</li>
        </ul>
      </div>
      <div>
        <div class="font-bold text-blue-700 mb-1">2. Market Relevance Matrix</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Market-Wide Growth:</strong> Both WM and Market growing (lift ≥ 1.1)</li>
          <li><strong>Walmart Share Gain:</strong> WM growing, Market flat/declining</li>
          <li><strong>Walmart Share Loss:</strong> Market growing, WM declining</li>
          <li><strong>Market Contraction:</strong> Both WM and Market declining</li>
          <li><strong>Flat/Mixed:</strong> Neither clearly growing or declining</li>
        </ul>
      </div>
      <div>
        <div class="font-bold text-blue-700 mb-1">3. Competitive Intensity / Price War Proxy</div>
        <div class="bg-gray-50 rounded p-3 font-mono text-xs mb-2">AMP = Market_Sales_excl_WM ÷ Market_Units_excl_WM</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Price War / Loss Leader:</strong> AMP drops &gt;10% AND WM Unit Lift ≥ 1.5</li>
          <li><strong>Convenience-Driven:</strong> AMP stable (±5%) AND WM Unit Lift ≥ 1.5</li>
          <li><strong>Price Inflation:</strong> AMP increases &gt;10% during Easter</li>
          <li><strong>Stable/Mixed:</strong> All other combinations</li>
        </ul>
      </div>
      <div>
        <div class="font-bold text-blue-700 mb-1">4. Purchase Role Classification</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Destination:</strong> Seafood, fish, shellfish, alcohol (beer/spirits/wine/cocktails/liqueurs), sun care — core seasonal shopping intent</li>
          <li><strong>Impulse / Convenience:</strong> Chips, snacks, cookies, carbonated beverages, juices, flavored drinks, water — driven by proximity and urgency</li>
          <li><strong>Complementary:</strong> Laundry, cleaners, bleach, condiments, sauces, disposable tableware, pest control — basket additions</li>
          <li><strong>Other:</strong> Categories not clearly fitting the above buckets</li>
        </ul>
      </div>
      <div class="bg-blue-50 border border-blue-200 rounded p-3">
        <div class="font-bold text-blue-800 mb-1">⚠️ Important Caveats</div>
        <ul class="list-disc ml-5 space-y-1 text-xs">
          <li>Very high lifts (e.g., &gt;10x) in small-volume categories may reflect near-zero base counts rather than true seasonality — validate with absolute unit volumes.</li>
          <li>AMP comparisons are meaningful only when base market units &gt; 0. Records with null AMP were excluded from competitive behavior classification.</li>
          <li>UPC-level analysis is filtered to items with Lift ≥ 1.5 (500 records max). Full UPC universe requires a separate export.</li>
          <li>Walmart Fiscal Week 202510 (immediate pre-Easter) is intentionally excluded from the base to avoid pre-holiday demand pull contaminating the baseline.</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<footer class="px-6 py-4 text-center text-xs text-gray-400 border-t bg-white mt-6">
  Walmart CAM · Pricing Intelligence · Easter Seasonality Analysis 2025 · Source: prcng_info_cam_temp_market_trend
</footer>

<script>
const D = {DATA_PLACEHOLDER};

const CTRY = {{CR:'Costa Rica',GT:'Guatemala',HN:'Honduras',NI:'Nicaragua'}};
const ROLE_COLOR = {{'Destination':'#1d4ed8','Impulse / Convenience':'#15803d','Complementary':'#b45309','Other':'#6b7280'}};
const MAT_COLOR = {{'Market-Wide Growth':'#059669','Walmart Share Gain':'#2563eb','Walmart Share Loss':'#dc2626','Flat / Mixed':'#9ca3af','Market Contraction':'#d97706'}};
const BEHAVIOR_COLOR = {{'Price War / Loss Leader':'#dc2626','Convenience-Driven (Low Price Sensitivity)':'#2563eb','Stable / Mixed':'#9ca3af','Price Inflation':'#d97706','Aggressive Pricing (Low Volume)':'#7c3aed','Insufficient Data':'#e5e7eb'}};

const charts = {{}};
function destroyChart(id){{ if(charts[id]){{ charts[id].destroy(); delete charts[id]; }} }}
function fmt(v,d=1){{ if(v===null||v===undefined||isNaN(v)) return '–'; const n=Number(v); if(Math.abs(n)>=1e9) return (n/1e9).toFixed(d)+'B'; if(Math.abs(n)>=1e6) return (n/1e6).toFixed(d)+'M'; if(Math.abs(n)>=1e3) return (n/1e3).toFixed(d)+'K'; return n.toFixed(d); }}
function fmtLift(v){{ return v===null||v===undefined ? '–' : Number(v).toFixed(2)+'x'; }}
function fmtPct(v){{ return v===null||v===undefined ? '–' : (Number(v)>=0?'+':'')+Number(v).toFixed(1)+'pp'; }}
function fmtAmpChg(v){{ return v===null||v===undefined ? '–' : (Number(v)>=0?'+':'')+Number(v).toFixed(1)+'%'; }}

// ---- KPI Strip ----
function buildKPIs(){{
  const s=D.stats;
  const kpis=[
    {{label:'Total Categories',val:s.total_cat,sub:'in analysis',color:'text-gray-700'}},
    {{label:'Seasonal (Cat)',val:s.seasonal_cat+' ('+s.seasonal_pct+'%)',sub:'WM Lift ≥1.5 or P75',color:'text-green-700'}},
    {{label:'Destination Seasonal',val:s.dest_seasonal,sub:'core seasonal intent',color:'text-blue-700'}},
    {{label:'Price Wars',val:s.price_wars,sub:'AMP drop >10% + lift',color:'text-red-700'}},
    {{label:'WM Share Gain',val:s.wm_gain,sub:'categories gained share',color:'text-blue-600'}},
    {{label:'Market-Wide Growth',val:s.mkt_wide,sub:'full market expanding',color:'text-emerald-700'}},
    {{label:'Seasonal UPCs',val:s.upc_seasonal,sub:'UPCs with lift ≥1.5',color:'text-purple-700'}},
    {{label:'Countries',val:'4',sub:'CR · GT · HN · NI',color:'text-gray-600'}},
  ];
  document.getElementById('kpiStrip').innerHTML=kpis.map(k=>`
    <div class="card kpi p-3">
      <div class="text-xs text-gray-400 font-semibold uppercase tracking-wide">${{k.label}}</div>
      <div class="text-xl font-black ${{k.color}} mt-0.5">${{k.val}}</div>
      <div class="text-xs text-gray-400">${{k.sub}}</div>
    </div>`).join('');
}}

// ---- Insights ----
function buildInsights(){{
  const s=D.stats;
  const pw=D.cat.filter(r=>/Price War/.test(r.comp));
  const topDest=D.cat.filter(r=>r.role==='Destination'&&r.seas==='Yes').sort((a,b)=>b.wl-a.wl).slice(0,3);
  const insights=[
    `🏆 <strong>${{s.seasonal_cat}} of ${{s.total_cat}} categories (${{s.seasonal_pct}}%)</strong> flagged as Easter seasonal across the CAM region.`,
    `🐟 Top Destination categories: ${{topDest.map(r=>`<strong>[${{r.c}}] ${{r.cat.slice(0,35)}} (${{r.wl.toFixed(1)}}x)</strong>`).join(', ')}}.`,
    `🗺️ <strong>${{s.mkt_wide}} categories</strong> showed Market-Wide Growth — true Easter demand expansion. <strong>${{s.wm_gain}}</strong> showed WM-specific share gain.`,
    `⚡ <strong>${{s.price_wars}} Price War / Loss Leader</strong> situations detected (AMP drop >10% with significant unit lift). Monitor margin impact.`,
    `📊 <strong>18 categories</strong> behaved as Convenience-Driven (AMP stable, high lift) — margin-positive opportunities for planogramming and promo.`,
    `🌍 Honduras shows the highest WM share gain count (${{D.country_summary.HN.wm_gain}} categories) — strong competitive positioning during Easter.`,
    `💡 Alcohol (Cocktails, Mixers, Spirits) and Seafood are universal Destination categories across all 4 countries — prime candidates for aggressive promotional pricing.`,
    `⚠️ Sun Care shows Price War dynamics in CR (AMP -15.7%) — likely loss-leader tactic during beach-season cross-shopping with Easter.`,
  ];
  document.getElementById('insightsList').innerHTML=insights.map(i=>`<div class="insight-bullet">${{i}}</div>`).join('');
}}

// ---- ROLE BADGE ----
function roleBadge(r){{
  const cls={{Destination:'bg-dest','Impulse / Convenience':'bg-imp',Complementary:'bg-comp',Other:'bg-other'}};
  return `<span class="badge ${{cls[r]||'bg-other'}}">${{r}}</span>`;
}}
function seaB(s){{ return `<span class="badge ${{s==='Yes'?'bg-sea':'bg-no'}}">${{s}}</span>`; }}
function matBadge(m){{
  const cls={{'Market-Wide Growth':'bg-mwg','Walmart Share Gain':'bg-wmg','Walmart Share Loss':'bg-wml','Flat / Mixed':'bg-flat','Market Contraction':'bg-mc'}};
  const abbr={{'Market-Wide Growth':'Mkt-Wide↑','Walmart Share Gain':'WM Gain','Walmart Share Loss':'WM Loss','Flat / Mixed':'Flat','Market Contraction':'Contraction'}};
  return `<span class="badge ${{cls[m]||'bg-flat'}}">${{abbr[m]||m}}</span>`;
}}
function compBadge(c){{
  if(/Price War/.test(c)) return `<span class="badge bg-pw">💥 Price War</span>`;
  if(/Convenience/.test(c)) return `<span class="badge bg-conv">🎯 Convenience</span>`;
  if(/Inflation/.test(c)) return `<span class="badge" style="background:#fde68a;color:#92400e">📈 Inflation</span>`;
  if(/Aggressive/.test(c)) return `<span class="badge" style="background:#ede9fe;color:#5b21b6">🟣 Aggressive</span>`;
  return `<span class="badge bg-stab">Stable</span>`;
}}

// ---- TAB SWITCH ----
function switchTab(id){{
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  const labels={{tabCat:'📊 Category Analysis',tabUPC:'🏷️ UPC Analysis',tabMatrix:'🗺️ Market Matrix & Charts',tabMethod:'📖 Methodology'}};
  document.querySelectorAll('.tab').forEach(t=>{{ if(t.textContent===labels[id]) t.classList.add('active'); }});
  if(id==='tabMatrix') buildMatrixCharts();
}}

// ---- CATEGORY TABLE ----
function catFiltered(){{
  const country=document.getElementById('fCatCountry').value;
  const sbu=document.getElementById('fCatSBU').value;
  const role=document.getElementById('fCatRole').value;
  const seas=document.getElementById('fCatSeas').value;
  const mat=document.getElementById('fCatMat').value;
  const q=document.getElementById('fCatSearch').value.toLowerCase();
  return D.cat.filter(r=>
    (!country||r.c===country)&&(!sbu||r.sbu===sbu)&&(!role||r.role===role)&&
    (!seas||r.seas===seas)&&(!mat||r.mat===mat)&&
    (!q||r.cat.toLowerCase().includes(q))
  );
}}
function renderCatTable(){{
  const rows=catFiltered();
  document.getElementById('catCount').textContent=`${{rows.length}} categories`;
  document.getElementById('catTbody').innerHTML=rows.map((r,i)=>
    `<tr class="${{i%2===0?'bg-white':'bg-gray-50'}} hover:bg-blue-50">
      <td class="py-1.5 px-2 font-semibold">${{r.c}}</td>
      <td class="py-1.5 px-2">${{r.sbu}}</td>
      <td class="py-1.5 px-2" style="max-width:220px;word-break:break-word">${{r.cat}}</td>
      <td class="py-1.5 px-2 text-right font-mono font-bold ${{r.wl>=2?'text-green-700':r.wl>=1.5?'text-blue-600':'text-gray-700'}}">${{fmtLift(r.wl)}}</td>
      <td class="py-1.5 px-2 text-right font-mono">${{fmtLift(r.ml)}}</td>
      <td class="py-1.5 px-2 text-right font-mono">${{fmtLift(r.tl)}}</td>
      <td class="py-1.5 px-2 text-center">${{seaB(r.seas)}}</td>
      <td class="py-1.5 px-2 text-center">${{roleBadge(r.role)}}</td>
      <td class="py-1.5 px-2 text-center">${{matBadge(r.mat)}}</td>
      <td class="py-1.5 px-2 text-right ${{r.spd>0?'text-green-700':r.spd<0?'text-red-700':'text-gray-500'}}">${{fmtPct(r.spd)}}</td>
      <td class="py-1.5 px-2 text-right ${{r.ac!==null&&r.ac<-10?'text-red-700 font-bold':r.ac!==null&&r.ac>10?'text-orange-600':''}}">${{fmtAmpChg(r.ac)}}</td>
      <td class="py-1.5 px-2 text-center">${{compBadge(r.comp)}}</td>
    </tr>`
  ).join('');
}}

// ---- UPC TABLE ----
function upcFiltered(){{
  const country=document.getElementById('fUPCCountry').value;
  const sbu=document.getElementById('fUPCSBU').value;
  const role=document.getElementById('fUPCRole').value;
  const mat=document.getElementById('fUPCMat').value;
  const q=document.getElementById('fUPCSearch').value.toLowerCase();
  return D.upc.filter(r=>
    (!country||r.c===country)&&(!sbu||r.sbu===sbu)&&(!role||r.role===role)&&
    (!mat||r.mat===mat)&&
    (!q||r.cat.toLowerCase().includes(q)||r.desc.toLowerCase().includes(q)||r.upc.includes(q))
  );
}}
function renderUPCTable(){{
  const rows=upcFiltered().slice(0,300);
  document.getElementById('upcCount').textContent=`${{upcFiltered().length}} UPCs (showing max 300)`;
  document.getElementById('upcTbody').innerHTML=rows.map((r,i)=>
    `<tr class="${{i%2===0?'bg-white':'bg-gray-50'}} hover:bg-blue-50">
      <td class="py-1.5 px-2 font-semibold">${{r.c}}</td>
      <td class="py-1.5 px-2 font-mono text-gray-500">${{r.upc}}</td>
      <td class="py-1.5 px-2 font-semibold">${{r.desc}}</td>
      <td class="py-1.5 px-2" style="max-width:180px;word-break:break-word">${{r.cat}}</td>
      <td class="py-1.5 px-2">${{r.sbu}}</td>
      <td class="py-1.5 px-2 text-right font-mono font-bold ${{r.wl>=2?'text-green-700':r.wl>=1.5?'text-blue-600':''}}">${{fmtLift(r.wl)}}</td>
      <td class="py-1.5 px-2 text-right font-mono">${{fmtLift(r.tl)}}</td>
      <td class="py-1.5 px-2 text-center">${{seaB(r.seas)}}</td>
      <td class="py-1.5 px-2 text-center">${{roleBadge(r.role)}}</td>
      <td class="py-1.5 px-2 text-center">${{matBadge(r.mat)}}</td>
      <td class="py-1.5 px-2 text-right ${{r.spd>0?'text-green-700':r.spd<0?'text-red-700':''}}">${{fmtPct(r.spd)}}</td>
      <td class="py-1.5 px-2 text-right ${{r.ac!==null&&r.ac<-10?'text-red-700 font-bold':''}}">${{fmtAmpChg(r.ac)}}</td>
      <td class="py-1.5 px-2 text-right font-mono">${{fmt(r.ewu,0)}}</td>
      <td class="py-1.5 px-2 text-right font-mono">${{fmt(r.ews)}}</td>
    </tr>`
  ).join('');
}}

// ---- TOP15 CHART ----
function buildTop15(){{
  destroyChart('chartTop15');
  const ctx=document.getElementById('chartTop15').getContext('2d');
  const rows=D.top15;
  const labels=rows.map(r=>`[${{r.c}}] ${{r.cat.slice(0,35)}}`);
  const wlData=rows.map(r=>Math.min(r.wl||0,12));
  const colors=rows.map(r=>ROLE_COLOR[r.role]||'#6b7280');
  charts['chartTop15']=new Chart(ctx,{{
    type:'bar',
    data:{{labels,datasets:[{{label:'WM Unit Lift',data:wlData,backgroundColor:colors,borderRadius:5}}]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{rows[c.dataIndex].role}} · Lift: ${{rows[c.dataIndex].wl.toFixed(2)}}x · ${{rows[c.dataIndex].comp.slice(0,30)}}`}}}}}},
      scales:{{x:{{min:0,ticks:{{callback:v=>v+'x'}}}},y:{{ticks:{{font:{{size:10}}}}}}}}
    }}
  }});
}}

// ---- ROLE DONUT ----
function buildRoleChart(){{
  destroyChart('chartRole');
  const ctx=document.getElementById('chartRole').getContext('2d');
  const labels=Object.keys(D.role_dist);
  const vals=Object.values(D.role_dist);
  const colors=labels.map(l=>ROLE_COLOR[l]||'#9ca3af');
  charts['chartRole']=new Chart(ctx,{{
    type:'doughnut',
    data:{{labels,datasets:[{{data:vals,backgroundColor:colors,borderWidth:2,borderColor:'white'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right',labels:{{boxWidth:12,font:{{size:11}}}}}}}}}}
  }});
}}

// ---- MATRIX CHARTS (lazy) ----
let matrixBuilt=false;
function buildMatrixCharts(){{
  if(matrixBuilt) return; matrixBuilt=true;

  // Matrix donut
  destroyChart('chartMatrix');
  const ctx1=document.getElementById('chartMatrix').getContext('2d');
  const ml=Object.keys(D.matrix_dist); const mv=Object.values(D.matrix_dist);
  charts['chartMatrix']=new Chart(ctx1,{{
    type:'doughnut',
    data:{{labels:ml,datasets:[{{data:mv,backgroundColor:ml.map(k=>MAT_COLOR[k]||'#9ca3af'),borderWidth:2,borderColor:'white'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right',labels:{{boxWidth:12,font:{{size:11}}}}}}}}}}
  }});

  // Behavior donut
  destroyChart('chartBehavior');
  const ctx2=document.getElementById('chartBehavior').getContext('2d');
  const bl=Object.keys(D.behavior_dist); const bv=Object.values(D.behavior_dist);
  charts['chartBehavior']=new Chart(ctx2,{{
    type:'doughnut',
    data:{{labels:bl,datasets:[{{data:bv,backgroundColor:bl.map(k=>BEHAVIOR_COLOR[k]||'#9ca3af'),borderWidth:2,borderColor:'white'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right',labels:{{boxWidth:12,font:{{size:11}}}}}}}}}}
  }});

  // AMP comparison
  destroyChart('chartAMP');
  const ctx3=document.getElementById('chartAMP').getContext('2d');
  const amp=D.amp_comparison;
  charts['chartAMP']=new Chart(ctx3,{{
    type:'bar',
    data:{{
      labels:amp.map(r=>r.label),
      datasets:[
        {{label:'Base AMP',data:amp.map(r=>r.base_amp),backgroundColor:'rgba(96,165,250,0.7)',borderRadius:4}},
        {{label:'Easter AMP',data:amp.map(r=>r.easter_amp),backgroundColor:'rgba(251,146,60,0.8)',borderRadius:4}}
      ]
    }},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}},tooltip:{{callbacks:{{afterLabel:c=>{{ const r=amp[c.dataIndex]; return `Lift: ${{r.wl.toFixed(2)}}x  AMP Δ: ${{r.chg!==null?r.chg.toFixed(1)+'%':'n/a'}}  [${{r.comp.slice(0,25)}}]`; }}}}}}}},
      scales:{{y:{{ticks:{{font:{{size:10}}}}}}}}
    }}
  }});

  // Country bar
  destroyChart('chartCountry');
  const ctx4=document.getElementById('chartCountry').getContext('2d');
  const cs=D.country_summary; const ctrs=Object.keys(cs);
  charts['chartCountry']=new Chart(ctx4,{{
    type:'bar',
    data:{{
      labels:ctrs.map(c=>CTRY[c]||c),
      datasets:[
        {{label:'Total Categories',data:ctrs.map(c=>cs[c].total),backgroundColor:'rgba(226,232,240,0.8)',borderRadius:4}},
        {{label:'Seasonal',data:ctrs.map(c=>cs[c].seasonal),backgroundColor:'rgba(34,197,94,0.8)',borderRadius:4}},
        {{label:'WM Share Gain',data:ctrs.map(c=>cs[c].wm_gain),backgroundColor:'rgba(59,130,246,0.8)',borderRadius:4}},
        {{label:'Price War',data:ctrs.map(c=>cs[c].price_war),backgroundColor:'rgba(239,68,68,0.8)',borderRadius:4}},
      ]
    }},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'top',labels:{{boxWidth:12,font:{{size:11}}}}}}}},scales:{{y:{{ticks:{{stepSize:10}}}}}}}}
  }});

  // Scatter: WM Lift vs Market Lift
  destroyChart('chartScatter');
  const ctx5=document.getElementById('chartScatter').getContext('2d');
  const roleGroups={{}};
  D.scatter.forEach(r=>{{ if(!roleGroups[r.role]) roleGroups[r.role]=[]; roleGroups[r.role].push({{x:r.x,y:r.y,cat:r.cat,c:r.c}}); }});
  const scatterDatasets=Object.entries(roleGroups).map(([role,pts])=>({{ label:role, data:pts, backgroundColor:(ROLE_COLOR[role]||'#9ca3af')+'99', pointRadius:5, pointHoverRadius:7 }}));
  // Add diagonal reference line
  scatterDatasets.push({{label:'y=x (parity)',data:[{{x:0,y:0}},{{x:10,y:10}}],type:'line',borderColor:'#94a3b8',borderDash:[4,4],pointRadius:0,fill:false,borderWidth:1}});
  charts['chartScatter']=new Chart(ctx5,{{
    type:'scatter',
    data:{{datasets:scatterDatasets}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top',labels:{{boxWidth:10,font:{{size:10}}}}}},
        tooltip:{{callbacks:{{label:c=>{{ const p=c.raw; return `[${{p.c}}] ${{p.cat}} → WM:${{p.y?.toFixed(2)}}x Mkt:${{p.x?.toFixed(2)}}x`; }}}}}}}},
      scales:{{x:{{min:0,max:10,title:{{display:true,text:'Market Total Lift'}}}},y:{{min:0,max:10,title:{{display:true,text:'WM Unit Lift'}}}}}}
    }}
  }});

  // Share Delta chart
  destroyChart('chartShareDelta');
  const ctx6=document.getElementById('chartShareDelta').getContext('2d');
  const sdRows=D.cat.filter(r=>r.seas==='Yes'&&r.spd!==null).sort((a,b)=>b.spd-a.spd).slice(0,20);
  charts['chartShareDelta']=new Chart(ctx6,{{
    type:'bar',
    data:{{
      labels:sdRows.map(r=>`[${{r.c}}] ${{r.cat.slice(0,30)}}`),
      datasets:[{{label:'WM Share Δ (pp)',data:sdRows.map(r=>r.spd),backgroundColor:sdRows.map(r=>r.spd>=0?'rgba(34,197,94,0.75)':'rgba(239,68,68,0.75)'),borderRadius:4}}]
    }},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`Share Δ: ${{c.raw>=0?'+':''}}${{c.raw.toFixed(2)}}pp`}}}}}},
      scales:{{y:{{ticks:{{font:{{size:9}}}}}},x:{{ticks:{{callback:v=>(v>=0?'+':'')+v+'pp'}}}}}}
    }}
  }});
}}

// ---- INIT ----
document.addEventListener('DOMContentLoaded',()=>{{
  buildKPIs();
  buildInsights();
  buildTop15();
  buildRoleChart();
  renderCatTable();
  renderUPCTable();
}});
</script>
</body></html>
"""

# Inject data
html_out = HTML.replace('{DATA_PLACEHOLDER}', DATA_JS)

out_path = BASE / "index.html"
out_path.write_text(html_out, encoding="utf-8")
print(f"Report written: {out_path}")
print(f"File size: {out_path.stat().st_size/1024:.1f} KB")