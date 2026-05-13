"""Render Easter Analysis v2 HTML report.

Same structure as v1 + Post-Easter Price Variation column and chart.
Split into html_parts.py (templates) to stay under 600 lines.
"""
import json
from pathlib import Path

from html_parts import head_css, js_block

BASE = Path(__file__).parent
DATA = json.load(open(BASE / "embed_data.json", encoding="utf-8"))
DATA_JS = json.dumps(DATA, ensure_ascii=True, separators=(',', ':'))


def build_html() -> str:
    return f"""{head_css()}
<body class="min-h-screen">

<!-- HEADER -->
<header class="wm-blue text-white px-6 py-4 flex items-center justify-between shadow-xl">
  <div class="flex items-center gap-3">
    <div class="wm-spark w-11 h-11 rounded-full flex items-center justify-center font-black text-gray-900 text-xl">W</div>
    <div>
      <div class="font-bold text-xl">Easter Week Seasonality Analysis v2 &mdash; Pricing Intelligence</div>
      <div class="text-blue-200 text-xs">CAM Region &middot; 2025 &middot; Base: W01&ndash;W09 &middot; Easter: W11 &middot; Post-Easter: W12&ndash;W17</div>
    </div>
  </div>
  <div class="text-right text-sm">
    <div class="text-blue-200">Generated</div>
    <div class="font-semibold">25 Mar 2025</div>
  </div>
</header>

<!-- KPI STRIP -->
<div class="px-6 py-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3" id="kpiStrip"></div>

<!-- EXECUTIVE INSIGHTS -->
<div class="px-6 pb-4">
  <div class="card p-5 border-l-4 border-blue-500">
    <div class="flex gap-3">
      <div class="text-2xl">&#x1F4A1;</div>
      <div class="flex-1">
        <div class="font-bold text-gray-800 mb-2">Executive Insights &mdash; Easter Week 202511</div>
        <div id="insightsList" class="grid grid-cols-1 md:grid-cols-2 gap-1"></div>
      </div>
    </div>
  </div>
</div>

<!-- TABS -->
<div class="px-6 pb-0">
  <div class="flex gap-1 overflow-x-auto">
    <div class="tab active" data-tab="tabCat" onclick="switchTab('tabCat')">Category Analysis</div>
    <div class="tab" data-tab="tabUPC" onclick="switchTab('tabUPC')">UPC Analysis</div>
    <div class="tab" data-tab="tabMatrix" onclick="switchTab('tabMatrix')">Market Matrix &amp; Charts</div>
    <div class="tab" data-tab="tabMethod" onclick="switchTab('tabMethod')">Methodology</div>
  </div>
</div>

<!-- TAB: CATEGORIES -->
<div id="tabCat" class="panel active px-6 py-4">
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
    <div class="card p-4 lg:col-span-2">
      <div class="font-bold text-gray-800 mb-1">&#x1F3C6; Top 15 Seasonal Categories &mdash; WM Unit Lift</div>
      <div class="text-xs text-gray-400 mb-2">Lift = Easter WM units &divide; weekly avg base (W01&ndash;W09)</div>
      <div class="chart-box"><canvas id="chartTop15"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F3AD; Purchase Role (Seasonal Only)</div>
      <div class="text-xs text-gray-400 mb-2">Distribution of seasonal categories by role</div>
      <div class="chart-box"><canvas id="chartRole"></canvas></div>
    </div>
  </div>

  <!-- Filters -->
  <div class="card p-4 mb-3">
    <div class="font-bold text-gray-700 mb-2 text-sm">Filters</div>
    <div class="filter-row">
      <select class="fsel" id="fCatCountry" onchange="renderCatTable()"><option value="">All Countries</option><option>CAM</option><option>CR</option><option>GT</option><option>HN</option><option>NI</option></select>
      <select class="fsel" id="fCatSBU" onchange="renderCatTable()"><option value="">All SBUs</option><option>CONSUMABLES</option><option>GROCERIES</option><option>PHARMACY</option></select>
      <select class="fsel" id="fCatRole" onchange="renderCatTable()"><option value="">All Roles</option><option>Destination</option><option>Impulse / Convenience</option><option>Complementary</option><option>Other</option></select>
      <select class="fsel" id="fCatSeas" onchange="renderCatTable()"><option value="">All</option><option value="Yes">Seasonal Only</option><option value="No">Non-Seasonal</option></select>
      <select class="fsel" id="fCatMat" onchange="renderCatTable()"><option value="">All Matrix</option><option>Market-Wide Growth</option><option>Walmart Share Gain</option><option>Walmart Share Loss</option><option>Flat / Mixed</option><option>Market Contraction</option></select>
      <select class="fsel" id="fCatPost" onchange="renderCatTable()">
        <option value="">All Post-Easter</option>
        <option>Recovers to Base</option>
        <option>Stays Elevated</option>
        <option>Stable Post-Easter</option>
        <option>Price Drop</option>
      </select>
      <input class="fsel" id="fCatSearch" placeholder="Search category..." oninput="renderCatTable()" style="width:180px" />
      <span class="text-xs text-gray-400" id="catCount"></span>
      <button class="btn-excel" onclick="downloadCatExcel()">&#x2B07;&#xFE0F; Download Excel</button>
    </div>
  </div>
  <div class="card overflow-auto" style="max-height:520px">
    <table class="w-full text-xs">
      <thead><tr class="text-left text-gray-500">
        <th class="py-2 px-2">Country</th><th class="py-2 px-2">SBU</th>
        <th class="py-2 px-2" style="max-width:200px">Category</th>
        <th class="py-2 px-2 text-right">WM Lift</th><th class="py-2 px-2 text-right">Mkt Lift</th><th class="py-2 px-2 text-right">Tot Lift</th>
        <th class="py-2 px-2 text-center">Seasonal?</th><th class="py-2 px-2 text-center">Role</th>
        <th class="py-2 px-2 text-center">Market Matrix</th>
        <th class="py-2 px-2 text-right">WM Share &Delta;pp</th>
        <th class="py-2 px-2 text-right">AMP &Delta;%</th>
        <th class="py-2 px-2 text-center">Competitive</th>
        <th class="py-2 px-2 text-right" style="background:#eff6ff">Post&nbsp;Price&nbsp;&Delta;%</th>
        <th class="py-2 px-2 text-center" style="background:#eff6ff">Post Behavior</th>
      </tr></thead>
      <tbody id="catTbody"></tbody>
    </table>
  </div>
</div>

<!-- TAB: UPC -->
<div id="tabUPC" class="panel px-6 py-4">
  <div class="card p-4 mb-3">
    <div class="font-bold text-gray-700 mb-2 text-sm">Filters &mdash; UPC Level (Lift &ge; 1.5)</div>
    <div class="filter-row">
      <select class="fsel" id="fUPCCountry" onchange="renderUPCTable()"><option value="">All Countries</option><option>CAM</option><option>CR</option><option>GT</option><option>HN</option><option>NI</option></select>
      <select class="fsel" id="fUPCSBU" onchange="renderUPCTable()"><option value="">All SBUs</option><option>CONSUMABLES</option><option>GROCERIES</option><option>PHARMACY</option></select>
      <select class="fsel" id="fUPCRole" onchange="renderUPCTable()"><option value="">All Roles</option><option>Destination</option><option>Impulse / Convenience</option><option>Complementary</option><option>Other</option></select>
      <select class="fsel" id="fUPCMat" onchange="renderUPCTable()"><option value="">All Matrix</option><option>Market-Wide Growth</option><option>Walmart Share Gain</option><option>Walmart Share Loss</option></select>
      <select class="fsel" id="fUPCPost" onchange="renderUPCTable()">
        <option value="">All Post-Easter</option>
        <option>Recovers to Base</option><option>Stays Elevated</option>
        <option>Stable Post-Easter</option><option>Price Drop</option>
      </select>
      <input class="fsel" id="fUPCSearch" placeholder="Search UPC/desc..." oninput="renderUPCTable()" style="width:180px" />
      <span class="text-xs text-gray-400" id="upcCount"></span>
      <button class="btn-excel" onclick="downloadUPCExcel()">&#x2B07;&#xFE0F; Download Excel</button>
    </div>
  </div>
  <div class="card overflow-auto" style="max-height:600px">
    <table class="w-full text-xs">
      <thead><tr class="text-left text-gray-500">
        <th class="py-2 px-2">Country</th><th class="py-2 px-2">UPC</th><th class="py-2 px-2">Description</th>
        <th class="py-2 px-2" style="max-width:160px">Category</th><th class="py-2 px-2">SBU</th>
        <th class="py-2 px-2 text-right">WM Lift</th><th class="py-2 px-2 text-right">Tot Lift</th>
        <th class="py-2 px-2 text-center">Seasonal?</th><th class="py-2 px-2 text-center">Role</th>
        <th class="py-2 px-2 text-center">Matrix</th>
        <th class="py-2 px-2 text-right">Share &Delta;pp</th>
        <th class="py-2 px-2 text-right">AMP &Delta;%</th>
        <th class="py-2 px-2 text-right">Easter WM Units</th>
        <th class="py-2 px-2 text-right">Easter WM Sales</th>
        <th class="py-2 px-2 text-right" style="background:#eff6ff">Post Price &Delta;%</th>
        <th class="py-2 px-2 text-center" style="background:#eff6ff">Post Behavior</th>
      </tr></thead>
      <tbody id="upcTbody"></tbody>
    </table>
  </div>
</div>

<!-- TAB: CHARTS -->
<div id="tabMatrix" class="panel px-6 py-4">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F5FA;&#xFE0F; Market Relevance Matrix</div>
      <div class="text-xs text-gray-400 mb-2">WM vs Market growth dynamics</div>
      <div class="chart-box"><canvas id="chartMatrix"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x26A1; Competitive Behavior Distribution</div>
      <div class="text-xs text-gray-400 mb-2">Based on AMP change + unit lift thresholds</div>
      <div class="chart-box"><canvas id="chartBehavior"></canvas></div>
    </div>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F4B0; AMP Comparison &mdash; Top Destination Categories</div>
      <div class="text-xs text-gray-400 mb-2">Base avg AMP vs Easter AMP</div>
      <div class="chart-box-lg"><canvas id="chartAMP"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F30D; Seasonal Categories by Country</div>
      <div class="text-xs text-gray-400 mb-2">Seasonal, WM gain and price-war categories</div>
      <div class="chart-box"><canvas id="chartCountry"></canvas></div>
    </div>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1FAE7; WM Lift vs Market Lift (Scatter)</div>
      <div class="text-xs text-gray-400 mb-2">Each dot = one category. Above diagonal = WM outpacing market.</div>
      <div class="chart-box-lg"><canvas id="chartScatter"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F4C8; WM Share Delta (pp) &mdash; Seasonal</div>
      <div class="text-xs text-gray-400 mb-2">Change in WM share during Easter vs base</div>
      <div class="chart-box-lg"><canvas id="chartShareDelta"></canvas></div>
    </div>
  </div>
  <!-- NEW: Post-Easter Price Behavior chart -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F501; Post-Easter Price Behavior (All Categories)</div>
      <div class="text-xs text-gray-400 mb-2">How WM prices behaved on average in W12&ndash;W17 vs Easter week</div>
      <div class="chart-box"><canvas id="chartPostBehavior"></canvas></div>
    </div>
    <div class="card p-4">
      <div class="font-bold text-gray-800 mb-1">&#x1F501; Post-Easter Price Behavior (Seasonal Only)</div>
      <div class="text-xs text-gray-400 mb-2">Same breakdown for categories flagged as Easter Seasonal</div>
      <div class="chart-box"><canvas id="chartPostSeasonal"></canvas></div>
    </div>
  </div>
</div>

<!-- TAB: METHODOLOGY -->
<div id="tabMethod" class="panel px-6 py-4">
  <div class="card p-6 max-w-4xl">
    <div class="text-xl font-bold text-gray-800 mb-4">&#x1F4D6; Analytical Methodology</div>
    <div class="space-y-5 text-sm text-gray-700">
      <div><div class="font-bold text-blue-700 mb-1">1. Seasonality Index (Unit Lift)</div>
        <div class="bg-gray-50 rounded p-3 font-mono text-xs mb-2">WM_Unit_Lift = Easter_WM_Units &divide; (Base_WM_Units &divide; Base_Weeks)</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Easter Week:</strong> WM_YEAR_WEEK_NBR = 202511</li>
          <li><strong>Base Period:</strong> Weeks 202501&ndash;202509 (9 weeks)</li>
          <li><strong>Seasonal Flag:</strong> WM_Unit_Lift &ge; 1.5 OR &ge; P75 within country</li>
        </ul>
      </div>
      <div><div class="font-bold text-blue-700 mb-1">2. Market Relevance Matrix</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Market-Wide Growth:</strong> Both WM and Market lift &ge; 1.1</li>
          <li><strong>Walmart Share Gain:</strong> WM growing, Market flat/declining</li>
          <li><strong>Walmart Share Loss:</strong> Market growing, WM declining</li>
          <li><strong>Market Contraction:</strong> Both declining (&lt;0.95)</li>
        </ul>
      </div>
      <div><div class="font-bold text-blue-700 mb-1">3. Competitive Behavior (AMP)</div>
        <div class="bg-gray-50 rounded p-3 font-mono text-xs mb-2">AMP = Market_Sales_excl_WM &divide; Market_Units_excl_WM</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Price War / Loss Leader:</strong> AMP drops &gt;10% AND WM Lift &ge; 1.5</li>
          <li><strong>Convenience-Driven:</strong> AMP stable (&plusmn;5%) AND WM Lift &ge; 1.5</li>
          <li><strong>Price Inflation:</strong> AMP increases &gt;10%</li>
        </ul>
      </div>
      <div><div class="font-bold text-blue-700 mb-1">4. NEW &mdash; Post-Easter Price Variation (W12&ndash;W17)</div>
        <div class="bg-blue-50 rounded p-3 font-mono text-xs mb-2">Post_Price_&Delta;% = (Avg_Post_WM_Price &minus; Easter_WM_Price) &divide; |Easter_WM_Price| &times; 100</div>
        <ul class="list-disc ml-5 space-y-1">
          <li><strong>Recovers to Base:</strong> Post price drops &gt;3% from Easter AND ends near baseline (&le;3% above base)</li>
          <li><strong>Stays Elevated:</strong> Post price remains &gt;3% above Easter week</li>
          <li><strong>Stable Post-Easter:</strong> Price within &plusmn;3% of Easter week</li>
          <li><strong>Price Drop:</strong> Post price drops &gt;3% from Easter but doesn't fully recover to base</li>
        </ul>
      </div>
      <div class="bg-blue-50 border border-blue-200 rounded p-3">
        <div class="font-bold text-blue-800 mb-1">&#x26A0;&#xFE0F; Caveats</div>
        <ul class="list-disc ml-5 space-y-1 text-xs">
          <li>Very high lifts (&gt;10x) in small-volume categories may reflect near-zero base counts.</li>
          <li>Post-Easter prices use local currency for country-level analysis; USD for CAM virtual market.</li>
          <li>UPC analysis capped at 500 records (lift &ge; 1.5).</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<footer class="px-6 py-4 text-center text-xs text-gray-400 border-t bg-white mt-6">
  Walmart CAM &middot; Pricing Intelligence &middot; Easter Seasonality Analysis v2 2025 &middot; Source: prcng_info_cam_temp_market_trend
</footer>

<script>
{js_block(DATA_JS)}
</script>
</body>
</html>"""


def main():
    html = build_html()
    out  = BASE / "index.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report written: {out}  ({out.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
