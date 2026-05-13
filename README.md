# Pricing Info — Walmart Centroamérica

Repositorio de análisis de precios e inteligencia de mercado para CR, GT, HN y NI.

**Stack**: Python · BigQuery · HTML + Tailwind CSS · Chart.js

---

## 📦 Proyectos

### ⚡ PG InMarket — OBW vs COMP MB
Reporte interactivo de Price Gap comparando la canasta propia de Walmart (OBW) contra la canasta de competidores (COMP MB).

| Archivo | Descripción |
|---|---|
| `build_pricing_inmarket.py` | Pipeline Python: CSV de BQ → HTML self-contained |
| `pricing_inmarket_tpl.html` | Template HTML/JS del reporte |
| `pricing_inmarket_report.html` | Reporte generado — abrir directo en browser |

**Cómo regenerar:**
```bash
# 1. Exportar desde BQ la tabla:
#    wmt-k1-cons-data-users.k1_adhoc_tables.prcng_OBW_inMKT_26_COMP
# 2. Guardar como prcng_OBW_inMKT_26_COMP_results.csv en esta carpeta
python build_pricing_inmarket.py
```

**Tabs del reporte:**
1. **Canasto vs No Canasto** — split de UPCs y unidades por segmento y rango de PG
2. **Análisis por Rango** — drill-down por País / División / Categoría / UPC
3. **Persistencia Semanal** — UPCs con N semanas consecutivas en un rango crítico

**Período**: Semanas 213–226 (Ene–Abr 2026) · 24,223 UPCs · 4 países

---

### 🐣 Easter Analysis
Análisis de variación de precios en semana santa y post-Semana Santa (W12–W17).

### 📊 Competitor Pricing Report
Análisis de tendencias de precios de competidores, variación por UPC y patrones promocionales.

---

## 🔐 Seguridad

- CSVs y JSONs con datos de BQ están en `.gitignore` — regenerables, no se commitean
- No compartir reportes con PII sin revisión previa
- Requiere **Walmart VPN o Eagle WiFi** para acceder a BigQuery

## 👤 Autor
**Juan Carlos Catalan Marin** · juan.catalan@walmart.com
