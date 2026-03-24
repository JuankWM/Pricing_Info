# Competitor Pricing Analysis Report

## 📊 Descripción
Proyecto de análisis de precios de competidores usando datos de BigQuery. Genera reportes HTML interactivos con visualizaciones de tendencias de precios, variaciones por UPC, detección de cambios y patrones promocionales.

## 🛠️ Tecnologías
- **Python 3.x**
- **BigQuery**: Para consultas de datos de precios
- **HTML + Tailwind CSS**: Para reportes visuales
- **Chart.js**: Para gráficos interactivos

## 📁 Estructura del Proyecto
```
puppy_workspace/
├── generate_pricing_report.py    # Script principal para generar reportes
├── bigquery_results/             # Resultados de consultas BQ (no en git)
├── competitor_pricing_report_2025.html  # Reporte generado (no en git)
└── .gitignore                    # Archivos excluidos de git
```

## 🚀 Instalación y Configuración

### Prerequisitos
1. Python 3.8+
2. Acceso a BigQuery de Walmart
3. Configuración de gcloud CLI con credenciales de Walmart

### Instalación de dependencias
```bash
# Crear ambiente virtual
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias (usar proxy de Walmart)
uv pip install google-cloud-bigquery --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com
```

## 📖 Uso

### Generar reporte de precios
```bash
python generate_pricing_report.py
```

Esto generará:
- Consultas a BigQuery para obtener datos de precios
- Archivo HTML con visualizaciones interactivas
- Resultados en `bigquery_results/` (archivos JSON)

### Abrir el reporte
```bash
# Windows
start competitor_pricing_report_2025.html

# Mac
open competitor_pricing_report_2025.html
```

## 📊 Análisis Incluidos

1. **Tendencias de Precios por País y Competidor**
2. **Variación de Precios por UPC**
3. **Detección de Cambios de Precio**
4. **Patrones Promocionales**
5. **Top Países y Competidores**

## 🔐 Seguridad y Datos

⚠️ **IMPORTANTE**: 
- Los archivos JSON y CSV con datos de BigQuery **NO** están en Git
- Pueden contener información sensible de precios de competidores
- Los reportes HTML generados tampoco están en Git (pueden regenerarse)
- Siempre verifica que no haya PII antes de compartir

## 👤 Autor
**Juan Carlos Catalan Marin** (juan.catalan@walmart.com)

## 📅 Última actualización
Marzo 2026

---

**Nota**: Este proyecto requiere conexión a Walmart VPN o Eagle WiFi para acceder a BigQuery y servicios internos.
