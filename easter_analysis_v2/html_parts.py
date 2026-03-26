"""HTML/CSS/JS templates for Easter Analysis v2 report."""


def head_css() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0" />
<title>Easter Seasonality Analysis v2 2025 &ndash; Pricing Intelligence CAM</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<style>
body{font-family:'Segoe UI',sans-serif;background:#f0f4f8}
.wm-blue{background:#0053e2}.wm-spark{background:#ffc220}
.card{background:white;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.09)}
.kpi:hover{transform:translateY(-2px);transition:transform .15s}
table thead th{position:sticky;top:0;background:#f1f5f9;z-index:2}
.tab{cursor:pointer;padding:8px 18px;border-radius:8px 8px 0 0;font-weight:600;font-size:13px;white-space:nowrap}
.tab.active{background:#0053e2;color:white}
.tab:not(.active){background:#e2e8f0;color:#475569}
.tab:not(.active):hover{background:#cbd5e1}
.panel{display:none}.panel.active{display:block}
.badge{display:inline-block;padding:1px 7px;border-radius:9999px;font-size:11px;font-weight:700}
.bg-dest{background:#dbeafe;color:#1e40af}.bg-imp{background:#dcfce7;color:#166534}
.bg-comp{background:#fef9c3;color:#854d0e}.bg-other{background:#f3f4f6;color:#4b5563}
.bg-sea{background:#d1fae5;color:#065f46}.bg-no{background:#fee2e2;color:#991b1b}
.bg-pw{background:#fca5a5;color:#7f1d1d}.bg-conv{background:#bfdbfe;color:#1e40af}
.bg-stab{background:#e5e7eb;color:#374151}.bg-mwg{background:#a7f3d0;color:#065f46}
.bg-wmg{background:#bfdbfe;color:#1e40af}.bg-wml{background:#fecaca;color:#991b1b}
.bg-flat{background:#e5e7eb;color:#374151}.bg-mc{background:#fed7aa;color:#92400e}
.bg-rec{background:#bbf7d0;color:#065f46}.bg-elev{background:#fecdd3;color:#9f1239}
.bg-sdrop{background:#e0f2fe;color:#0369a1}.bg-nodat{background:#f3f4f6;color:#6b7280}
.chart-box{position:relative;height:320px}.chart-box-lg{position:relative;height:390px}
.filter-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px}
.fsel{border:1px solid #cbd5e1;border-radius:8px;padding:5px 10px;font-size:13px;background:#f8fafc}
.insight-bullet{padding:6px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#334155}
.insight-bullet:last-child{border:none}
.btn-excel{display:inline-flex;align-items:center;gap:6px;background:#2a8703;color:white;
  border:none;border-radius:8px;padding:6px 14px;font-size:12px;font-weight:700;cursor:pointer}
.btn-excel:hover{background:#1e6402}
</style>
</head>"""


def js_block(data_js: str) -> str:  # noqa: C901
    return f"""const D = {data_js};
const CTRY={{CR:'Costa Rica',GT:'Guatemala',HN:'Honduras',NI:'Nicaragua'}};
const ROLE_COLOR={{'Destination':'#1d4ed8','Impulse / Convenience':'#15803d','Complementary':'#b45309','Other':'#6b7280'}};
const MAT_COLOR={{'Market-Wide Growth':'#059669','Walmart Share Gain':'#2563eb','Walmart Share Loss':'#dc2626','Flat / Mixed':'#9ca3af','Market Contraction':'#d97706'}};
const BEHAVIOR_COLOR={{'Price War / Loss Leader':'#dc2626','Convenience-Driven (Low Price Sensitivity)':'#2563eb','Stable / Mixed':'#9ca3af','Price Inflation':'#d97706','Aggressive Pricing (Low Volume)':'#7c3aed','Insufficient Data':'#e5e7eb'}};
const POST_COLOR={{'Recovers to Base':'#059669','Stays Elevated':'#dc2626','Stable Post-Easter':'#9ca3af','Price Drop':'#2563eb','No Post Data':'#e5e7eb'}};

const charts={{}};
function destroyChart(id){{if(charts[id]){{charts[id].destroy();delete charts[id];}}}}
function fmt(v,d=1){{if(v===null||v===undefined||isNaN(v))return'\u2013';const n=Number(v);if(Math.abs(n)>=1e9)return(n/1e9).toFixed(d)+'B';if(Math.abs(n)>=1e6)return(n/1e6).toFixed(d)+'M';if(Math.abs(n)>=1e3)return(n/1e3).toFixed(d)+'K';return n.toFixed(d);}}
function fmtLift(v){{return v===null||v===undefined?'\u2013':Number(v).toFixed(2)+'x';}}
function fmtPct(v){{return v===null||v===undefined?'\u2013':(Number(v)>=0?'+':'')+Number(v).toFixed(1)+'pp';}}
function fmtAmpChg(v){{return v===null||v===undefined?'\u2013':(Number(v)>=0?'+':'')+Number(v).toFixed(1)+'%';}}
function fmtPostPct(v){{
  if(v===null||v===undefined)return'<span class="text-gray-300">\u2013</span>';
  const n=Number(v);
  const cls=n<-3?'color:#059669;font-weight:700':n>3?'color:#dc2626;font-weight:700':'color:#6b7280';
  return `<span style="${{cls}}">${{n>=0?'+':''}}${{n.toFixed(1)}}%</span>`;
}}

// ---- KPI Strip ----
function buildKPIs(){{
  const cs=D.country_summary;
  const CTRY_FULL={{CAM:'CAM (Mercado Total)',CR:'Costa Rica',GT:'Guatemala',HN:'Honduras',NI:'Nicaragua'}};
  const FLAG={{CAM:'\uD83C\uDF0E',CR:'\uD83C\uDDE8\uD83C\uDDF7',GT:'\uD83C\uDDEC\uD83C\uDDF9',HN:'\uD83C\uDDED\uD83C\uDDF3',NI:'\uD83C\uDDF3\uD83C\uDDEE'}};
  const topByCtr={{}};
  D.cat.forEach(r=>{{if(r.seas==='Yes'&&(!topByCtr[r.c]||r.wl>topByCtr[r.c].wl))topByCtr[r.c]=r;}});
  document.getElementById('kpiStrip').innerHTML=Object.entries(cs).map(([c,v])=>{{
    const isCAM=c==='CAM';
    const pct=(v.seasonal/v.total*100).toFixed(1);
    const top=topByCtr[c];
    const topLabel=top?top.cat.replace(/^\\d+\\s*-\\s*/,'').slice(0,28):'\u2014';
    const topLift=top?top.wl.toFixed(1)+'x':'';
    const border=isCAM?'border-blue-600':'border-yellow-400';
    const numClr=isCAM?'text-blue-700':'text-gray-800';
    const subNote=isCAM?'<div class="text-xs text-blue-300 mt-0.5">USD \u00b7 agregado</div>':'';
    return `<div class="card kpi p-3 border-t-4 ${{border}}">
      <div class="text-xs text-gray-400 font-bold uppercase tracking-wide">${{FLAG[c]}} ${{CTRY_FULL[c]}}</div>
      ${{subNote}}
      <div class="flex items-baseline gap-2 mt-0.5">
        <span class="text-xl font-black ${{numClr}}">${{v.total}}</span>
        <span class="text-xs text-gray-400">categor\u00edas</span>
      </div>
      <div class="mt-1">
        <span class="font-bold text-green-700">${{v.seasonal}}</span>
        <span class="text-gray-500 text-xs"> estacionales</span>
        <span class="ml-1 text-xs font-bold bg-green-100 text-green-800 px-1.5 py-0.5 rounded-full">${{pct}}%</span>
      </div>
      <div class="text-xs text-gray-400 mt-1">${{v.wm_gain}} WM Gain \u00b7 ${{v.price_war}} Price War</div>
      <div class="text-xs text-blue-600 font-semibold mt-1 truncate" title="${{top?.cat}}">\uD83C\uDFC6 ${{topLabel}} ${{topLift}}</div>
    </div>`;
  }}).join('');
}}

// ---- Insights ----
function buildInsights(){{
  const s=D.stats;const cs=D.country_summary;
  const CTRY_FULL={{CAM:'CAM (Mercado Total)',CR:'Costa Rica',GT:'Guatemala',HN:'Honduras',NI:'Nicaragua'}};
  const FLAG={{CAM:'\uD83C\uDF0E',CR:'\uD83C\uDDE8\uD83C\uDDF7',GT:'\uD83C\uDDEC\uD83C\uDDF9',HN:'\uD83C\uDDED\uD83C\uDDF3',NI:'\uD83C\uDDF3\uD83C\uDDEE'}};
  const tableRows=Object.entries(cs).map(([c,v])=>{{
    const pct=(v.seasonal/v.total*100).toFixed(1);
    const bar=Math.round(parseFloat(pct));
    const isCAM=c==='CAM';
    const rowCls=isCAM?'bg-blue-50 font-semibold border-t-2 border-blue-200':'border-b border-gray-100';
    const pwCell=v.price_war>0?`<span class="${{isCAM?'text-red-700 font-bold':'text-red-600'}}">${{v.price_war}}</span>`:`<span class="text-gray-300">\u2014</span>`;
    return `<tr class="${{rowCls}}">
      <td class="py-1.5 px-2 font-bold">${{FLAG[c]}} ${{CTRY_FULL[c]}}</td>
      <td class="py-1.5 px-2 text-center text-gray-700">${{v.total}}</td>
      <td class="py-1.5 px-2 text-center font-bold text-green-700">${{v.seasonal}}</td>
      <td class="py-1.5 px-2">
        <div class="flex items-center gap-2">
          <div class="flex-1 bg-gray-100 rounded-full h-2" style="min-width:80px">
            <div class="${{isCAM?'bg-blue-500':'bg-green-500'}} h-2 rounded-full" style="width:${{bar}}%"></div>
          </div>
          <span class="text-xs font-bold ${{isCAM?'text-blue-700':'text-green-700'}} w-10">${{pct}}%</span>
        </div>
      </td>
      <td class="py-1.5 px-2 text-center text-blue-700 font-semibold">${{v.wm_gain}}</td>
      <td class="py-1.5 px-2 text-center">${{pwCell}}</td>
    </tr>`;
  }}).join('');

  const summaryTable=`<div class="col-span-2 mb-2"><table class="w-full text-sm">
    <thead><tr class="text-xs text-gray-400 uppercase tracking-wide border-b-2 border-gray-200">
      <th class="py-1 px-2 text-left">Pa\u00eds</th><th class="py-1 px-2 text-center">Total Cats</th>
      <th class="py-1 px-2 text-center">Estacionales</th><th class="py-1 px-2 text-left">% Estacional</th>
      <th class="py-1 px-2 text-center">WM Gain</th><th class="py-1 px-2 text-center">Price Wars</th>
    </tr></thead><tbody>${{tableRows}}</tbody>
  </table></div>`;

  const pw=D.cat.filter(r=>/Price War/.test(r.comp));
  const topDest=D.cat.filter(r=>r.role==='Destination'&&r.seas==='Yes').sort((a,b)=>b.wl-a.wl).slice(0,3);
  const convDriven=D.cat.filter(r=>/Convenience/.test(r.comp)&&r.seas==='Yes').length;
  const elevPct=s.total_cat>0?((s.post_elevated/s.total_cat)*100).toFixed(1):0;
  const recPct=s.total_cat>0?((s.post_recovers/s.total_cat)*100).toFixed(1):0;

  const bullets=[
    `\uD83D\uDC1F Top Destination: ${{topDest.map(r=>`<strong>[${{r.c}}] ${{r.cat.replace(/^\\d+\\s*-\\s*/,'').slice(0,30)}} (${{r.wl.toFixed(1)}}x)</strong>`).join(' \u00b7 ')}}.`,
    `\uD83D\uDDFA\uFE0F <strong>${{s.mkt_wide}} categor\u00edas</strong> con crecimiento total de mercado. <strong>${{s.wm_gain}}</strong> con ganancia de share exclusiva de Walmart.`,
    `\u26A1 <strong>${{s.price_wars}} Price Wars</strong> detectados (AMP baja >10% + lift alto).`,
    `\uD83C\uDFAF <strong>${{convDriven}} categor\u00edas Convenience-Driven</strong> (AMP estable + lift alto) — oportunidades de margen positivo.`,
    `\uD83D\uDD01 Post-Easter: <strong>${{s.post_elevated}} cats (${{elevPct}}%)</strong> mantienen precio elevado vs Easter. Solo <strong>${{s.post_recovers}} (${{recPct}}%)</strong> regresan al baseline.`,
    `\uD83D\uDCA1 Monitorear categor\u00edas con <em>Stays Elevated</em> y <em>Seasonal=Yes</em>: precio alto post-Easter puede comprometer competitividad en las semanas siguientes.`,
  ];

  document.getElementById('insightsList').innerHTML=summaryTable+bullets.map(i=>`<div class="insight-bullet">${{i}}</div>`).join('');
}}

// ---- Badges ----
function roleBadge(r){{const cls={{Destination:'bg-dest','Impulse / Convenience':'bg-imp',Complementary:'bg-comp',Other:'bg-other'}};return `<span class="badge ${{cls[r]||'bg-other'}}">${{r}}</span>`;}}
function seaB(s){{return `<span class="badge ${{s==='Yes'?'bg-sea':'bg-no'}}">${{s}}</span>`;}}
function matBadge(m){{const cls={{'Market-Wide Growth':'bg-mwg','Walmart Share Gain':'bg-wmg','Walmart Share Loss':'bg-wml','Flat / Mixed':'bg-flat','Market Contraction':'bg-mc'}};const abbr={{'Market-Wide Growth':'Mkt-Wide\u2191','Walmart Share Gain':'WM Gain','Walmart Share Loss':'WM Loss','Flat / Mixed':'Flat','Market Contraction':'Contraction'}};return `<span class="badge ${{cls[m]||'bg-flat'}}">${{abbr[m]||m}}</span>`;}}
function compBadge(c){{if(/Price War/.test(c))return`<span class="badge bg-pw">\uD83D\uDCA5 Price War</span>`;if(/Convenience/.test(c))return`<span class="badge bg-conv">\uD83C\uDFAF Convenience</span>`;if(/Inflation/.test(c))return`<span class="badge" style="background:#fde68a;color:#92400e">\uD83D\uDCC8 Inflation</span>`;if(/Aggressive/.test(c))return`<span class="badge" style="background:#ede9fe;color:#5b21b6">\uD83D\uDFE3 Aggressive</span>`;return`<span class="badge bg-stab">Stable</span>`;}}
function postBadge(b){{const MAP={{'Recovers to Base':'bg-rec \u2193 Recovers','Stays Elevated':'bg-elev \u2191 Elevated','Stable Post-Easter':'bg-stab = Stable','Price Drop':'bg-sdrop \u2193 Drop','No Post Data':'bg-nodat \u2014'}};const v=MAP[b]||'bg-nodat \u2014';const[cls,...words]=v.split(' ');return `<span class="badge ${{cls}}">${{words.join(' ')}}</span>`;}}

// ---- Tab switch ----
function switchTab(id){{
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  const labels={{tabCat:'\uD83D\uDCCA Category Analysis',tabUPC:'\uD83C\uDFF7\uFE0F UPC Analysis',tabMatrix:'\uD83D\uDDFA\uFE0F Market Matrix & Charts',tabMethod:'\uD83D\uDCD6 Methodology'}};
  document.querySelectorAll('.tab').forEach(t=>{{if(t.textContent.trim()===labels[id].replace(/&#x[0-9A-F]+;/gi,''))t.classList.add('active');}});
  if(id==='tabMatrix')buildMatrixCharts();
}}

// ---- Category Table ----
function catFiltered(){{
  const country=document.getElementById('fCatCountry').value;
  const sbu=document.getElementById('fCatSBU').value;
  const role=document.getElementById('fCatRole').value;
  const seas=document.getElementById('fCatSeas').value;
  const mat=document.getElementById('fCatMat').value;
  const post=document.getElementById('fCatPost').value;
  const q=document.getElementById('fCatSearch').value.toLowerCase();
  return D.cat.filter(r=>{{
    if(country&&r.c!==country)return false;
    if(sbu&&r.sbu!==sbu)return false;
    if(role&&r.role!==role)return false;
    if(seas&&r.seas!==seas)return false;
    if(mat&&r.mat!==mat)return false;
    if(post&&r.ppbeh!==post)return false;
    if(q&&!r.cat.toLowerCase().includes(q))return false;
    return true;
  }});
}}
function renderCatTable(){{
  const rows=catFiltered();
  document.getElementById('catCount').textContent=`${{rows.length}} categories`;
  document.getElementById('catTbody').innerHTML=rows.map(r=>`<tr class="border-b border-gray-50 hover:bg-blue-50">
    <td class="py-1 px-2 font-bold">${{r.c}}</td>
    <td class="py-1 px-2 text-gray-500">${{r.sbu}}</td>
    <td class="py-1 px-2 max-w-xs truncate" title="${{r.cat}}">${{r.cat}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtLift(r.wl)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtLift(r.ml)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtLift(r.tl)}}</td>
    <td class="py-1 px-2 text-center">${{seaB(r.seas)}}</td>
    <td class="py-1 px-2 text-center">${{roleBadge(r.role)}}</td>
    <td class="py-1 px-2 text-center">${{matBadge(r.mat)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtPct(r.spd)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtAmpChg(r.ac)}}</td>
    <td class="py-1 px-2 text-center">${{compBadge(r.comp)}}</td>
    <td class="py-1 px-2 text-right" style="background:#f8faff">${{fmtPostPct(r.ppve)}}</td>
    <td class="py-1 px-2 text-center" style="background:#f8faff">${{postBadge(r.ppbeh)}}</td>
  </tr>`).join('');
}}

// ---- UPC Table ----
function upcFiltered(){{
  const country=document.getElementById('fUPCCountry').value;
  const sbu=document.getElementById('fUPCSBU').value;
  const role=document.getElementById('fUPCRole').value;
  const mat=document.getElementById('fUPCMat').value;
  const post=document.getElementById('fUPCPost').value;
  const q=document.getElementById('fUPCSearch').value.toLowerCase();
  return D.upc.filter(r=>{{
    if(country&&r.c!==country)return false;
    if(sbu&&r.sbu!==sbu)return false;
    if(role&&r.role!==role)return false;
    if(mat&&r.mat!==mat)return false;
    if(post&&r.ppbeh!==post)return false;
    if(q&&!(r.upc+'').toLowerCase().includes(q)&&!r.desc.toLowerCase().includes(q)&&!r.cat.toLowerCase().includes(q))return false;
    return true;
  }});
}}
function renderUPCTable(){{
  const rows=upcFiltered();
  document.getElementById('upcCount').textContent=`${{rows.length}} UPCs`;
  document.getElementById('upcTbody').innerHTML=rows.slice(0,300).map(r=>`<tr class="border-b border-gray-50 hover:bg-blue-50">
    <td class="py-1 px-2 font-bold">${{r.c}}</td>
    <td class="py-1 px-2 font-mono text-xs">${{r.upc}}</td>
    <td class="py-1 px-2 max-w-xs truncate" title="${{r.desc}}">${{r.desc}}</td>
    <td class="py-1 px-2 max-w-xs truncate text-xs" title="${{r.cat}}">${{r.cat}}</td>
    <td class="py-1 px-2 text-gray-500">${{r.sbu}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtLift(r.wl)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtLift(r.tl)}}</td>
    <td class="py-1 px-2 text-center">${{seaB(r.seas)}}</td>
    <td class="py-1 px-2 text-center">${{roleBadge(r.role)}}</td>
    <td class="py-1 px-2 text-center">${{matBadge(r.mat)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtPct(r.spd)}}</td>
    <td class="py-1 px-2 text-right font-mono">${{fmtAmpChg(r.ac)}}</td>
    <td class="py-1 px-2 text-right">${{fmt(r.ewu)}}</td>
    <td class="py-1 px-2 text-right">${{fmt(r.ews)}}</td>
    <td class="py-1 px-2 text-right" style="background:#f8faff">${{fmtPostPct(r.ppve)}}</td>
    <td class="py-1 px-2 text-center" style="background:#f8faff">${{postBadge(r.ppbeh)}}</td>
  </tr>`).join('');
}}

// ---- Top15 chart ----
function buildTop15(){{
  const rows=D.top15;
  charts.top15=new Chart(document.getElementById('chartTop15'),{{
    type:'bar',
    data:{{labels:rows.map(r=>`[${{r.c}}] ${{r.cat.replace(/^\\d+\\s*-\\s*/,'').slice(0,28)}}`),
      datasets:[{{label:'WM Unit Lift',data:rows.map(r=>r.wl),backgroundColor:rows.map(r=>ROLE_COLOR[r.role]||'#6b7280'),borderRadius:4}}]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`${{c.parsed.x.toFixed(2)}}x — ${{rows[c.dataIndex].role}}`}}}}}},
      scales:{{x:{{title:{{display:true,text:'WM Unit Lift'}}}}}}}}
  }});
}}

// ---- Role donut ----
function buildRoleDonut(){{
  const rd=D.role_dist;
  charts.role=new Chart(document.getElementById('chartRole'),{{
    type:'doughnut',
    data:{{labels:Object.keys(rd),datasets:[{{data:Object.values(rd),
      backgroundColor:Object.keys(rd).map(k=>ROLE_COLOR[k]||'#9ca3af'),borderWidth:2}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom'}}}}}}
  }});
}}

// ---- Matrix charts (lazy) ----
let matrixBuilt=false;
function buildMatrixCharts(){{
  if(matrixBuilt)return; matrixBuilt=true;
  const md=D.matrix_dist;
  charts.matrix=new Chart(document.getElementById('chartMatrix'),{{
    type:'doughnut',
    data:{{labels:Object.keys(md),datasets:[{{data:Object.values(md),backgroundColor:Object.keys(md).map(k=>MAT_COLOR[k]||'#9ca3af'),borderWidth:2}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom'}}}}}}
  }});
  const bd=D.behavior_dist;
  charts.behavior=new Chart(document.getElementById('chartBehavior'),{{
    type:'doughnut',
    data:{{labels:Object.keys(bd),datasets:[{{data:Object.values(bd),backgroundColor:Object.keys(bd).map(k=>BEHAVIOR_COLOR[k]||'#9ca3af'),borderWidth:2}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom'}}}}}}
  }});
  const amp=D.amp_comparison;
  charts.amp=new Chart(document.getElementById('chartAMP'),{{
    type:'bar',
    data:{{labels:amp.map(a=>a.label),datasets:[
      {{label:'Base AMP',data:amp.map(a=>a.base_amp),backgroundColor:'#93c5fd',borderRadius:3}},
      {{label:'Easter AMP',data:amp.map(a=>a.easter_amp),backgroundColor:'#1d4ed8',borderRadius:3}}
    ]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      scales:{{x:{{title:{{display:true,text:'AMP (local currency)'}}}}}},
      plugins:{{legend:{{position:'bottom'}}}}}}
  }});
  const cs=D.country_summary;
  const cKeys=Object.keys(cs).filter(k=>k!=='CAM');
  charts.country=new Chart(document.getElementById('chartCountry'),{{
    type:'bar',
    data:{{labels:cKeys,datasets:[
      {{label:'Seasonal',data:cKeys.map(k=>cs[k].seasonal),backgroundColor:'#16a34a',borderRadius:3}},
      {{label:'WM Gain',data:cKeys.map(k=>cs[k].wm_gain),backgroundColor:'#2563eb',borderRadius:3}},
      {{label:'Price War',data:cKeys.map(k=>cs[k].price_war),backgroundColor:'#dc2626',borderRadius:3}}
    ]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom'}}}},scales:{{x:{{stacked:true}},y:{{stacked:true}}}}}}
  }});
  const sc=D.scatter;
  charts.scatter=new Chart(document.getElementById('chartScatter'),{{
    type:'scatter',
    data:{{datasets:[{{data:sc.map(r=>{{return{{x:r.x,y:r.y,cat:r.cat,c:r.c,role:r.role,seas:r.seas}}}}),
      backgroundColor:sc.map(r=>ROLE_COLOR[r.role]||'#6b7280')+'aa',pointRadius:4,pointHoverRadius:6}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>`[${{c.raw.c}}] ${{c.raw.cat}} | WM:${{c.parsed.y.toFixed(1)}}x Mkt:${{c.parsed.x.toFixed(1)}}x`}}}}}},
      scales:{{x:{{title:{{display:true,text:'Market Lift'}}}},y:{{title:{{display:true,text:'WM Lift'}}}}}}}}
  }});
  const seasonal=D.cat.filter(r=>r.seas==='Yes').sort((a,b)=>b.spd-a.spd).slice(0,20);
  charts.share=new Chart(document.getElementById('chartShareDelta'),{{
    type:'bar',
    data:{{labels:seasonal.map(r=>`[${{r.c}}] ${{r.cat.slice(0,25)}}`),
      datasets:[{{label:'Share \u0394pp',data:seasonal.map(r=>r.spd),
        backgroundColor:seasonal.map(r=>r.spd>=0?'#16a34a':'#dc2626'),borderRadius:3}}]}},
    options:{{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}}}},scales:{{x:{{title:{{display:true,text:'\u0394pp'}}}}}}}}
  }});
  // NEW: Post-Easter behavior charts
  const pd=D.post_dist;
  const pdColors=Object.keys(pd).map(k=>POST_COLOR[k]||'#9ca3af');
  charts.postBeh=new Chart(document.getElementById('chartPostBehavior'),{{
    type:'doughnut',
    data:{{labels:Object.keys(pd),datasets:[{{data:Object.values(pd),backgroundColor:pdColors,borderWidth:2}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom'}},title:{{display:false}}}}}}
  }});
  // Post-Easter behavior for seasonal only
  const seaCats=D.cat.filter(r=>r.seas==='Yes');
  const pdSea={{}};
  seaCats.forEach(r=>{{pdSea[r.ppbeh]=(pdSea[r.ppbeh]||0)+1;}});
  charts.postSea=new Chart(document.getElementById('chartPostSeasonal'),{{
    type:'doughnut',
    data:{{labels:Object.keys(pdSea),datasets:[{{data:Object.values(pdSea),backgroundColor:Object.keys(pdSea).map(k=>POST_COLOR[k]||'#9ca3af'),borderWidth:2}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom'}}}}}}
  }});
}}

// ---- Excel downloads ----
function downloadCatExcel(){{
  const rows=catFiltered();
  const ws=XLSX.utils.json_to_sheet(rows.map(r=>({{Country:r.c,SBU:r.sbu,Category:r.cat,
    WM_Lift:r.wl,Mkt_Lift:r.ml,Tot_Lift:r.tl,Seasonal:r.seas,Role:r.role,Matrix:r.mat,
    Share_Delta_pp:r.spd,AMP_Chg_pct:r.ac,Competitive:r.comp,
    Post_WM_Price_vs_Easter_pct:r.ppve,Post_MKT_AMP_vs_Easter_pct:r.ppame,
    Post_WM_Price_vs_Base_pct:r.ppvb,Post_Behavior:r.ppbeh
  }})));
  const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,ws,'Categories');
  XLSX.writeFile(wb,'easter_analysis_v2_categories.xlsx');
}}
function downloadUPCExcel(){{
  const rows=upcFiltered();
  const ws=XLSX.utils.json_to_sheet(rows.map(r=>({{Country:r.c,UPC:r.upc,Desc:r.desc,
    Category:r.cat,SBU:r.sbu,WM_Lift:r.wl,Tot_Lift:r.tl,Seasonal:r.seas,Role:r.role,
    Matrix:r.mat,Share_Delta_pp:r.spd,AMP_Chg_pct:r.ac,
    Easter_WM_Units:r.ewu,Easter_WM_Sales:r.ews,
    Post_WM_Price_vs_Easter_pct:r.ppve,Post_Behavior:r.ppbeh
  }})));
  const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,ws,'UPCs');
  XLSX.writeFile(wb,'easter_analysis_v2_upcs.xlsx');
}}

// ---- INIT ----
buildKPIs();
buildInsights();
buildTop15();
buildRoleDonut();
renderCatTable();
renderUPCTable();
"""
