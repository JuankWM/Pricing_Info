"""Build the Post-Easter Price Analysis HTML report."""
import json
from pathlib import Path

BASE = Path(__file__).parent


def load_embed() -> dict:
    with open(BASE / "embed_data.json", encoding="utf-8") as f:
        return json.load(f)


def build_html(embed: dict) -> str:
    data_js = json.dumps(embed, ensure_ascii=False, separators=(',', ':'))
    s = embed["summary"]

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Post-Easter Price Analysis — CAM 2025</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body{{font-family:'Segoe UI',sans-serif;background:#f0f4f8;}}
  .kpi{{background:#fff;border-radius:12px;padding:20px 24px;box-shadow:0 1px 4px rgba(0,0,0,.08);}}
  .kpi-val{{font-size:2rem;font-weight:700;line-height:1.1;}}
  .kpi-label{{font-size:.8rem;color:#6b7280;margin-top:4px;text-transform:uppercase;letter-spacing:.05em;}}
  .card{{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:24px;}}
  .chart-wrap{{position:relative;height:320px;}}
  .pill{{display:inline-block;padding:2px 8px;border-radius:999px;font-size:.72rem;font-weight:600;}}
  .pill-drop{{background:#dcfce7;color:#15803d;}}
  .pill-spike{{background:#fee2e2;color:#b91c1c;}}
  .pill-stable{{background:#e0f2fe;color:#0369a1;}}
  thead th{{position:sticky;top:0;background:#0053e2;color:#fff;padding:8px 12px;text-align:left;font-size:.78rem;cursor:pointer;white-space:nowrap;}}
  tbody tr:hover{{background:#f0f4ff;}}
  tbody td{{padding:7px 12px;font-size:.8rem;border-bottom:1px solid #e5e7eb;}}
  .tbl-wrap{{max-height:480px;overflow-y:auto;border-radius:8px;border:1px solid #e5e7eb;}}
  select,input{{border:1px solid #d1d5db;border-radius:6px;padding:6px 10px;font-size:.85rem;}}
  .insigkground:#eff6ff;border-left:4px solid #0053e2;padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:16px;}}
</style>
</head>
<body class="p-4 md:p-8">

<!-- Header -->
<div class="mb-6">
  <div class="flex items-center gap-3 mb-1">
    <span style="font-size:2rem">&#x1F430;</span>
    <h1 class="text-2xl font-bold text-gray-800">Post-Easter Price Analysis</h1>
    <span class="pill pill-stable ml-2">CAM 2025</span>
  </div>
  <p class="text-gray-500 text-sm">\u00bfBajan los precios despu\u00e9s de Semana Santa? Semanas W12\u2013W17 vs Easter (W11) y baseline (W01\u2013W09)</p>
</div>

<!-- KPI row -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
  <div class="kpi">
    <div class="kpi-val" style="color:#0053e2">{s["total_categories"]}</div>
    <div class="kpi-label">Categor\u00edas analizadas</div>
  </div>
  <div class="kpi">
    <div class="kpi-val" style="color:#15803d">{s["price_dropped"]} <span style="font-size:1.1rem">({s["drop_pct"]}%)</span></div>
    <div class="kpi-label">Precio BAJ\u00d3 post-Easter</div>
  </div>
  <div class="kpi">
    <div class="kpi-val" style="color:#b91c1c">{s["price_spiked"]} <span style="font-size:1.1rem">({s["spike_pct"]}%)</span></div>
    <div class="kpi-label">Precio SUBI\u00d3 post-Easter</div>
  </div>
  <div class="kpi">
    <div class="kpi-val" style="color:#0369a1">{s["price_stable"]}</div>
    <div class="kpi-label">Precio ESTABLE</div>
  </div>
</div>

<!-- Insights -->
<div class="card">
  <h2 class="font-bold text-gray-800 mb-3 text-lg">&#x1F4A1; Insights Ejecutivos</h2>
  <div class="insight-box">
    <b>Hallazgo principal:</b> S\u00f3lo el <b>{s["drop_pct"]}%</b> de las categor\u00edas muestra una baja de precio post-Easter (&gt;1%). 
    La mayor\u00eda (<b>{s["spike_pct"]}%</b>) mantiene precios elevados o los incrementa, lo que sugiere que los precios altos de Semana Santa 
    <b>no se corrigen autom\u00e1ticamente</b> en las semanas siguientes.
  </div>
  <div class="insight-box" style="border-color:#ffc220;background:#fffbeb">
    <b>Oportunidad de pricing:</b> Las categor\u00edas con precio promedio post-Easter 
    <b>+{s["avg_spike_pct"]}%</b> sobre el nivel de Easter representan un riesgo de p\u00e9rdida de competitividad. 
    Revisar AMP vs competencia en esas semanas.
  </div>
  <div class="insight-box" style="border-color:#15803d;background:#f0fdf4">
    <b>Bajadas promedio:</b> Las categor\u00edas que s\u00ed bajan lo hacen en promedio un <b>{s["avg_drop_pct"]}%</b> respecto al precio de Easter, 
    regresando cerca del baseline pre-estacional.
  </div>
</div>

<!-- Charts row -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
  <div class="card">
    <h2 class="font-semibold text-gray-700 mb-3">Distribuci\u00f3n de Comportamiento de Precio</h2>
    <div class="chart-wrap"><canvas id="donutChart"></canvas></div>
  </div>
  <div class="card">
    <h2 class="font-semibold text-gray-700 mb-3">Por Pa\u00eds: Categor\u00edas que Bajaron vs Subieron</h2>
    <div class="chart-wrap"><canvas id="countryBar"></canvas></div>
  </div>
</div>

<!-- CAM trend chart -->
<div class="card mb-6">
  <h2 class="font-semibold text-gray-700 mb-1">Evoluci\u00f3n de Precio WM Promedio CAM \u2014 17 semanas</h2>
  <p class="text-xs text-gray-400 mb-3">Precio promedio ponderado en USD (todas las categor\u00edas del mercado virtual CAM)</p>
  <div class="chart-wrap" style="height:260px"><canvas id="trendChart"></canvas></div>
</div>

<!-- Category Table -->
<div class="card">
  <div class="flex flex-wrap gap-3 items-end mb-4">
    <div>
      <label class="text-xs text-gray-500 block mb-1">Pa\u00eds</label>
      <select id="filterCountry" onchange="renderTable()">
        <option value="">Todos</option>
        <option>CAM</option><option>CR</option><option>GT</option><option>HN</option><option>NI</option>
      </select>
    </div>
    <div>
      <label class="text-xs text-gray-500 block mb-1">Comportamiento</label>
      <select id="filterBehavior" onchange="renderTable()">
        <option value="">Todos</option>
        <option value="drop">Baj\u00f3</option>
        <option value="spike">Subi\u00f3</option>
        <option value="stable">Estable</option>
      </select>
    </div>
    <div>
      <label class="text-xs text-gray-500 block mb-1">Buscar categor\u00eda</label>
      <input id="filterSearch" oninput="renderTable()" placeholder="ej. seafood..." style="width:200px">
    </div>
    <span id="rowCount" class="text-xs text-gray-400 ml-auto self-end"></span>
  </div>
  <div class="tbl-wrap">
    <table id="mainTable" style="width:100%;border-collapse:collapse">
      <thead>
        <tr>
          <th onclick="sortBy('c')">Pa\u00eds</th>
          <th onclick="sortBy('cat')">Categor\u00eda</th>
          <th onclick="sortBy('bwp')">Precio Base (USD)</th>
          <th onclick="sortBy('ewp')">Precio Easter (USD)</th>
          <th onclick="sortBy('ewpvb')">Easter vs Base</th>
          <th onclick="sortBy('apwp')">Precio Post-Easter (USD)</th>
          <th onclick="sortBy('drop')">Post vs Easter (%)</th>
          <th onclick="sortBy('vsbase')">Post vs Base (%)</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
</div>

<!-- Post-week detail drilldown -->
<div class="card" id="drillCard" style="display:none">
  <h2 class="font-semibold text-gray-700 mb-3" id="drillTitle">Detalle semanas post-Easter</h2>
  <div class="chart-wrap" style="height:240px"><canvas id="drillChart"></canvas></div>
</div>

<script>
const DATA = {data_js};

const WEEKS_ALL = DATA.weeks;
const POST_LABELS = DATA.post_week_labels;
let sortKey = 'drop', sortDir = 1;
let drillChart = null;

// ---------- Donut ----------
const donut = new Chart(document.getElementById('donutChart'), {{
  type: 'doughnut',
  data: {{
    labels: ['Baj\u00f3 (>1%)', 'Subi\u00f3 (>1%)', 'Estable'],
    datasets: [{{
      data: [DATA.summary.price_dropped, DATA.summary.price_spiked, DATA.summary.price_stable],
      backgroundColor: ['#15803d','#b91c1c','#0369a1'],
      borderWidth: 2,
    }}]
  }},
  options: {{
    responsive:true, maintainAspectRatio:false,
    plugins: {{ legend: {{ position:'bottom' }} }}
  }}
}});

// ---------- Country bar ----------
const byC = DATA.summary.by_country;
const cKeys = Object.keys(byC).filter(k=>k!=='CAM');
new Chart(document.getElementById('countryBar'), {{
  type:'bar',
  data: {{
    labels: cKeys,
    datasets: [
      {{ label:'Baj\u00f3',  data: cKeys.map(k=>byC[k].dropped), backgroundColor:'#15803d' }},
      {{ label:'Subi\u00f3', data: cKeys.map(k=>byC[k].spiked),  backgroundColor:'#b91c1c' }},
      {{ label:'Estable', data: cKeys.map(k=>byC[k].stable),  backgroundColor:'#0369a1' }},
    ]
  }},
  options: {{
    responsive:true, maintainAspectRatio:false,
    plugins:{{ legend:{{ position:'bottom' }} }},
    scales:{{ x:{{ stacked:true }}, y:{{ stacked:true }} }}
  }}
}});

// ---------- CAM trend line ----------
const camRecs = DATA.records.filter(r=>r.c==='CAM');
const weekCount = WEEKS_ALL.length;
const weekSums = Array.from({{length:weekCount}}, ()=>({{sales:0,units:0}}));
camRecs.forEach(r => {{
  r.series.forEach((pt,i) => {{
    if(pt.wm_price && pt.wm_units) {{
      weekSums[i].sales += pt.wm_price * pt.wm_units;
      weekSums[i].units += pt.wm_units;
    }}
  }});
}});
const trendPrices = weekSums.map(s => s.units ? +(s.sales/s.units).toFixed(4) : null);
const EASTER_IDX = WEEKS_ALL.indexOf('W11 (Easter)');

const trendBg = WEEKS_ALL.map((l,i) => {{
  if(l.includes('Easter')) return 'rgba(255,194,32,0.35)';
  if(i > EASTER_IDX) return 'rgba(234,17,0,0.07)';
  return 'rgba(0,83,226,0.07)';
}});

new Chart(document.getElementById('trendChart'), {{
  type:'line',
  data:{{
    labels: WEEKS_ALL,
    datasets:[{{
      label:'Precio Prom WM CAM (USD)',
      data: trendPrices,
      borderColor:'#0053e2',
      backgroundColor: ctx => {{
        const chart = ctx.chart;
        const {{ctx:c, chartArea}} = chart;
        if(!chartArea) return 'transparent';
        return 'rgba(0,83,226,0.08)';
      }},
      fill:true,
      tension:0.4,
      pointRadius: WEEKS_ALL.map((l,i)=>l.includes('Easter')?7:3),
      pointBackgroundColor: WEEKS_ALL.map((l,i)=>l.includes('Easter')?'#ffc220':'#0053e2'),
      pointBorderColor: WEEKS_ALL.map((l,i)=>l.includes('Easter')?'#b45309':'#0053e2'),
    }}]
  }},
  options:{{
    responsive:true, maintainAspectRatio:false,
    scales:{{
      y:{{title:{{display:true,text:'USD / unit'}}}},
      x:{{ticks:{{maxRotation:45,font:{{size:10}}}}}}
    }},
    plugins:{{
      legend:{{display:false}},
      tooltip:{{callbacks:{{
        label: ctx => ` ${{ctx.parsed.y?.toFixed(4)}} USD`
      }}}}
    }}
  }}
}});

// ---------- Table ----------
function fmt(v, decimals=4) {{
  if(v==null) return '-';
  return typeof v==='number' ? v.toFixed(decimals) : v;
}}
function fmtPct(v) {{
  if(v==null) return '-';
  const s = v>0?'+':'';
  const cls = v<-1?'color:#15803d':v>1?'color:#b91c1c':'color:#0369a1';
  return `<span style="${{cls}};font-weight:600">${{s}}${{v.toFixed(1)}}%</span>`;
}}
function pill(r) {{
  if(r.fell) return '<span class="pill pill-drop">&#x2193; Baj\u00f3</span>';
  if(r.rose) return '<span class="pill pill-spike">&#x2191; Subi\u00f3</span>';
  return '<span class="pill pill-stable">= Estable</span>';
}}

function sortBy(k) {{
  if(sortKey===k) sortDir*=-1; else {{sortKey=k;sortDir=1;}}
  renderTable();
}}

function renderTable() {{
  const country  = document.getElementById('filterCountry').value;
  const behavior = document.getElementById('filterBehavior').value;
  const search   = document.getElementById('filterSearch').value.toLowerCase();

  let rows = DATA.records.filter(r => {{
    if(country  && r.c !== country) return false;
    if(behavior==='drop'   && !r.fell) return false;
    if(behavior==='spike'  && !r.rose) return false;
    if(behavior==='stable' && (r.fell||r.rose)) return false;
    if(search && !r.cat.toLowerCase().includes(search)) return false;
    return true;
  }});

  rows.sort((a,b) => {{
    const va = a[sortKey]??-Infinity, vb = b[sortKey]??-Infinity;
    return sortDir*(va<vb?-1:va>vb?1:0);
  }});

  document.getElementById('rowCount').textContent = `${{rows.length}} categor\u00edas`;
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = rows.map((r,i) => `
    <tr onclick="showDrill(${{JSON.stringify(r.cat)}}, ${{JSON.stringify(r.c)}})" style="cursor:pointer">
      <td><b>${{r.c}}</b></td>
      <td style="max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${{r.cat}}">${{r.cat}}</td>
      <td>${{fmt(r.bwp)}}</td>
      <td>${{fmt(r.ewp)}}</td>
      <td>${{fmtPct(r.ewpvb)}}</td>
      <td>${{fmt(r.apwp)}}</td>
      <td>${{fmtPct(r.drop)}}</td>
      <td>${{fmtPct(r.vsbase)}}</td>
      <td>${{pill(r)}}</td>
    </tr>`).join('');
}}

function showDrill(cat, country) {{
  const r = DATA.records.find(x=>x.cat===cat && x.c===country);
  if(!r) return;
  document.getElementById('drillCard').style.display='';
  document.getElementById('drillTitle').textContent = `${{country}} — ${{cat}}`;
  const labels = r.post.map(p=>p.label);
  const wm  = r.post.map(p=>p.wm_price);
  const mkt = r.post.map(p=>p.mkt_amp);
  const eWp = r.ewp;
  const bWp = r.bwp;

  if(drillChart) drillChart.destroy();
  drillChart = new Chart(document.getElementById('drillChart'), {{
    type:'bar',
    data:{{
      labels,
      datasets:[
        {{label:'WM Price (USD)', data:wm,  backgroundColor:'#0053e2', borderRadius:4}},
        {{label:'MKT AMP (USD)',  data:mkt, backgroundColor:'#ffc220', borderRadius:4}},
      ]
    }},
    options:{{
      responsive:true, maintainAspectRatio:false,
      plugins:{{
        legend:{{position:'bottom'}},
        annotation:{{}} ,
        tooltip:{{callbacks:{{label:ctx=>` ${{ctx.parsed.y?.toFixed(4)}} USD`}}}}
      }},
      scales:{{y:{{title:{{display:true,text:'USD / unit'}}}}}}
    }}
  }});
  document.getElementById('drillCard').scrollIntoView({{behavior:'smooth'}});
}}

renderTable();
</script>
</body>
</html>
"""


def main():
    embed = load_embed()
    html  = build_html(embed)
    out   = BASE / "index.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report written: {out}  ({out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
