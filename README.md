# PG InMarket — OBW vs COMP MB

Reporte interactivo de Price Gap para Walmart Centroamérica (CR, GT, HN, NI).

## Archivos

| Archivo | Descripción |
|---|---|
| `build_pricing_inmarket.py` | Script Python que lee el CSV de BQ y genera el reporte |
| `pricing_inmarket_tpl.html` | Template HTML/JS del reporte interactivo |
| `pricing_inmarket_report.html` | Reporte generado (self-contained, abrir en browser) |

## Cómo regenerar el reporte

1. Exportar la query de BigQuery a `prcng_OBW_inMKT_26_COMP_results.csv`
   (tabla: `wmt-k1-cons-data-users.k1_adhoc_tables.prcng_OBW_inMKT_26_COMP`)
2. Poner el CSV en la misma carpeta
3. Correr:
   ```
   python build_pricing_inmarket.py
   ```

## Fuentes de datos

- **OBW**: Own Basket Watch — PG de la canasta propia de Walmart
- **COMP MB**: Competitor Market Basket — PG contra canasta de competidores (PG InMarket)
- **Período**: Semanas 213–226 (Enero–Abril 2026)
- **Price Gap**: `SUM(FACTOR) / SUM(PESO)` ponderado por unidades

## Tabs del reporte

1. **Canasto vs No Canasto** — distribución de UPCs y unidades por segmento y rango
2. **Análisis por Rango** — drill-down por País / División / Categoría / UPC
3. **Persistencia Semanal** — UPCs que llevan N semanas consecutivas en un rango crítico
