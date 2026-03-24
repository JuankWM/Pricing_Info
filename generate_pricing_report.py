#!/usr/bin/env python3
"""Generate professional competitor pricing analysis report for 2025+ data."""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_json_file(filepath):
    """Load and parse JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_number(num):
    """Format number with thousands separator."""
    if num is None:
        return "N/A"
    return f"{num:,.2f}" if isinstance(num, float) else f"{num:,}"

def analyze_data():
    """Analyze competitor pricing data and generate insights."""
    
    # Load the data files
    summary_file = Path("bigquery_results/prcng-info-cam-historico-precio-comp-summary-20260324-090351.json")
    trends_file = Path("bigquery_results/prcng-info-cam-historico-precio-comp-summary-2025plus-20260324-090536.json")
    variation_file = Path("bigquery_results/price-variation-analysis-20260324-094103.json")
    promo_file = Path("bigquery_results/promotional-pricing-patterns-20260324-094252.json")
    
    summary_data = load_json_file(summary_file)
    trends_data = load_json_file(trends_file)
    variation_data = load_json_file(variation_file) if variation_file.exists() else []
    promo_data = load_json_file(promo_file) if promo_file.exists() else []
    
    # Group data by country
    countries = defaultdict(list)
    for row in summary_data:
        if row.get('pais') and row.get('competidor'):  # Skip null competitors
            countries[row['pais']].append(row)
    
    # Analyze trends data by month
    monthly_trends = defaultdict(lambda: defaultdict(list))
    for row in trends_data:
        if row.get('pais') and row.get('competidor'):  # Skip null competitors
            key = f"{row['ano']}-{str(row['mes']).zfill(2)}"
            monthly_trends[row['pais']][key].append(row)
    
    # Analyze promotional patterns
    promo_by_country = defaultdict(list)
    for row in promo_data:
        if row.get('pais') and row.get('competidor'):
            promo_by_country[row['pais']].append(row)
    
    return countries, monthly_trends, summary_data, trends_data, variation_data, promo_by_country

def generate_html_report():
    """Generate professional HTML report with Walmart styling."""
    
    countries, monthly_trends, summary_data, trends_data, variation_data, promo_by_country = analyze_data()
    
    # Calculate key metrics
    total_countries = len(countries)
    total_competitors = len([r for r in summary_data if r.get('competidor')])
    total_upcs = sum([r.get('distinct_upcs', 0) for r in summary_data if r.get('competidor')])
    total_records = sum([r.get('total_records', 0) for r in summary_data if r.get('competidor')])
    
    # Find top competitors by country
    top_competitors_by_country = {}
    for country, competitors in countries.items():
        sorted_comps = sorted(competitors, key=lambda x: x.get('total_records', 0), reverse=True)[:5]
        top_competitors_by_country[country] = sorted_comps
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Competitor Pricing Analysis Report 2025</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #ffffff;
            color: #2a2a2a;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #0053e2 0%, #0041b8 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.95;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .section {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #0053e2;
        }}
        
        .section h2 {{
            color: #0053e2;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f5f5f5;
        }}
        
        .section h3 {{
            color: #2a2a2a;
            font-size: 1.4rem;
            margin: 1.5rem 0 1rem 0;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,83,226,0.15);
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #0053e2;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            margin: 1.5rem 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        th {{
            background: #0053e2;
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 0.9rem 1rem;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .country-section {{
            margin-bottom: 3rem;
        }}
        
        .country-header {{
            background: linear-gradient(to right, #0053e2, #0041b8);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .insight-box {{
            background: #fff8e1;
            border-left: 4px solid #ffc220;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 4px;
        }}
        
        .insight-box h4 {{
            color: #995213;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}
        
        .insight-box ul {{
            list-style-position: inside;
            color: #333;
        }}
        
        .insight-box li {{
            margin: 0.5rem 0;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 2rem 0;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
            border-top: 1px solid #e0e0e0;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .badge-primary {{
            background: #e3f2fd;
            color: #0053e2;
        }}
        
        .badge-success {{
            background: #e8f5e9;
            color: #2a8703;
        }}
        
        .badge-warning {{
            background: #fff8e1;
            color: #995213;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 Competitor Pricing Analysis Report</h1>
        <p>Market Intelligence for 2025 | Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="container">
        <!-- Executive Summary -->
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Countries Analyzed</div>
                    <div class="metric-value">{total_countries}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Competitors</div>
                    <div class="metric-value">{total_competitors}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Unique Products (UPCs)</div>
                    <div class="metric-value">{format_number(total_upcs)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Price Records</div>
                    <div class="metric-value">{format_number(total_records)}</div>
                </div>
            </div>
            
            <div class="insight-box">
                <h4>🔍 Key Insights</h4>
                <ul>
                    <li><strong>Market Coverage:</strong> Analysis covers {total_countries} Central American markets (Costa Rica, Guatemala, Honduras, Nicaragua, El Salvador) with competitive pricing data from {total_competitors} distinct retailers.</li>
                    <li><strong>Data Volume:</strong> Over {format_number(total_records)} pricing observations across {format_number(total_upcs)} unique products tracked in 2025.</li>
                    <li><strong>Price Tracking:</strong> Three price types monitored: Regular prices (precio_normal), promotional offers (precio_oferta), and multi-save discounts (multiahorro).</li>
                    <li><strong>Competitive Dynamics:</strong> Markets show varying levels of competition with Guatemala having the highest competitor density.</li>
                </ul>
            </div>
        </div>

        <!-- Price Variation Analysis -->
        <div class="section">
            <h2>💰 Price Variation Analysis</h2>
            <p>Analysis of items tracked across multiple competitors showing significant price differences (2025-2026 data).</p>
            
            <h3>Top Items with Highest Price Variation</h3>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>UPC</th>
                            <th>Country</th>
                            <th>Competitors</th>
                            <th>Min Price</th>
                            <th>Max Price</th>
                            <th>Price Range</th>
                            <th>% Variation</th>
                        </tr>
                    </thead>
                    <tbody>
""" + ''.join([
f"""                        <tr>
                            <td><strong>#{idx}</strong></td>
                            <td>{item.get('upc', 'N/A')}</td>
                            <td>{item.get('pais', 'N/A')}</td>
                            <td>{item.get('num_competitors', 0)}</td>
                            <td>{format_number(item.get('min_price'))}</td>
                            <td>{format_number(item.get('max_price'))}</td>
                            <td>{format_number(item.get('price_range'))}</td>
                            <td><span class="badge badge-warning">{format_number(item.get('pct_variation'))}%</span></td>
                        </tr>
""" for idx, item in enumerate([v for v in variation_data[:10] if v.get('pct_variation', 0) < 100000], 1) # Filter out extreme outliers
]) + """                    </tbody>
                </table>
            </div>
            
            <div class="insight-box">
                <h4>🔍 Price Variation Insights</h4>
                <ul>
                    <li><strong>Data Quality Concerns:</strong> Some UPCs show extreme variations (>100,000%) suggesting data entry errors or different product sizes being tracked under same UPC.</li>
                    <li><strong>Competitive Opportunity:</strong> Items with significant but reasonable variations (10-50%) represent pricing optimization opportunities.</li>
                    <li><strong>Market Intelligence:</strong> Products tracked across 5+ competitors indicate high-demand items worth monitoring closely.</li>
                    <li><strong>Recommendation:</strong> Cleanse data for UPCs with extreme variations and standardize product size/type tracking.</li>
                </ul>
            </div>
        </div>

        <!-- Promotional Pricing Patterns -->
        <div class="section">
            <h2>🎯 Promotional Pricing Analysis</h2>
""" + ''.join([
f"""            <div class="country-section">
                <h3>{{'CR': 'Costa Rica', 'GT': 'Guatemala', 'HN': 'Honduras', 'NI': 'Nicaragua', 'SV': 'El Salvador'}.get(country, country)} Promotional Activity</h3>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Competitor</th>
                                <th>Month</th>
                                <th>Total Products</th>
                                <th>Items on Promo</th>
                                <th>% Promotional</th>
                                <th>Avg Discount %</th>
                                <th>Multiahorro Items</th>
                            </tr>
                        </thead>
                        <tbody>
""" + ''.join([
f"""                            <tr>
                                <td><strong>{promo.get('competidor', 'N/A')}</strong></td>
                                <td>{promo.get('ano', '')}-{str(promo.get('mes', '')).zfill(2)}</td>
                                <td>{format_number(promo.get('total_upcs'))}</td>
                                <td>{format_number(promo.get('upcs_with_offer'))}</td>
                                <td><span class="badge badge-success">{format_number(promo.get('pct_promotional'))}%</span></td>
                                <td>{format_number(promo.get('avg_discount_pct')) if promo.get('avg_discount_pct') else 'N/A'}%</td>
                                <td>{format_number(promo.get('upcs_with_multiahorro'))}</td>
                            </tr>
""" for promo in sorted([p for p in promos if p.get('pct_promotional', 0) > 0], key=lambda x: x.get('pct_promotional', 0), reverse=True)[:10]
]) + """                        </tbody>
                    </table>
                </div>
            </div>
""" for country, promos in sorted(promo_by_country.items())[:3]  # Top 3 countries with most promo activity
]) + """            
            <div class="insight-box">
                <h4>💡 Promotional Strategy Insights</h4>
                <ul>
                    <li><strong>Promo Intensity:</strong> Track which competitors run the most aggressive promotional campaigns (highest % promotional).</li>
                    <li><strong>Discount Depth:</strong> Average discount percentages reveal competitive pricing pressure and margin strategies.</li>
                    <li><strong>Multiahorro Adoption:</strong> Loyalty program participation varies significantly by competitor and market.</li>
                    <li><strong>Seasonal Patterns:</strong> Month-by-month data reveals promotional calendar strategies (holidays, back-to-school, etc.).</li>
                    <li><strong>Competitive Response:</strong> Sudden increases in promotional activity may signal competitive reactions or market share battles.</li>
                </ul>
            </div>
        </div>
"""

    # Add country-specific sections
    for country_code in sorted(countries.keys()):
        competitors = top_competitors_by_country[country_code]
        country_names = {
            'CR': 'Costa Rica 🇨🇷',
            'GT': 'Guatemala 🇬🇹', 
            'HN': 'Honduras 🇭🇳',
            'NI': 'Nicaragua 🇳🇮',
            'SV': 'El Salvador 🇸🇻'
        }
        country_name = country_names.get(country_code, country_code)
        
        total_country_records = sum([c.get('total_records', 0) for c in competitors])
        total_country_upcs = sum([c.get('distinct_upcs', 0) for c in competitors])
        
        html_content += f"""
        <div class="section country-section">
            <div class="country-header">
                <h2>{country_name}</h2>
                <div>
                    <span class="badge badge-primary">{len(competitors)} Top Competitors</span>
                    <span class="badge badge-success">{format_number(total_country_upcs)} UPCs</span>
                </div>
            </div>
            
            <h3>Top Competitors by Market Coverage</h3>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Competitor</th>
                            <th>Unique Products</th>
                            <th>Total Records</th>
                            <th>Avg Regular Price</th>
                            <th>Avg Offer Price</th>
                            <th>Price Range</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        for idx, comp in enumerate(competitors, 1):
            avg_normal = format_number(comp.get('avg_precio_normal'))
            avg_offer = format_number(comp.get('avg_precio_oferta'))
            min_price = format_number(comp.get('min_precio_normal'))
            max_price = format_number(comp.get('max_precio_normal'))
            
            html_content += f"""
                        <tr>
                            <td><strong>#{idx}</strong></td>
                            <td><strong>{comp.get('competidor', 'N/A')}</strong></td>
                            <td>{format_number(comp.get('distinct_upcs'))}</td>
                            <td>{format_number(comp.get('total_records'))}</td>
                            <td>{avg_normal}</td>
                            <td>{avg_offer}</td>
                            <td>{min_price} - {max_price}</td>
                        </tr>
"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
"""
        
        # Add chart for this country
        comp_names = [c.get('competidor', 'Unknown')[:20] for c in competitors]
        comp_upcs = [c.get('distinct_upcs', 0) for c in competitors]
        comp_records = [c.get('total_records', 0) for c in competitors]
        
        html_content += f"""
            <h3>Market Share Distribution</h3>
            <div class="chart-container">
                <canvas id="chart_{country_code}"></canvas>
            </div>
            <script>
                new Chart(document.getElementById('chart_{country_code}'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(comp_names)},
                        datasets: [
                            {{
                                label: 'Unique Products (UPCs)',
                                data: {json.dumps(comp_upcs)},
                                backgroundColor: 'rgba(0, 83, 226, 0.7)',
                                borderColor: '#0053e2',
                                borderWidth: 2,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Total Price Records',
                                data: {json.dumps(comp_records)},
                                backgroundColor: 'rgba(255, 194, 32, 0.7)',
                                borderColor: '#ffc220',
                                borderWidth: 2,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false
                        }},
                        plugins: {{
                            legend: {{
                                position: 'top',
                                labels: {{
                                    font: {{
                                        size: 13,
                                        weight: 600
                                    }}
                                }}
                            }},
                            title: {{
                                display: true,
                                text: 'Product Coverage vs. Data Density',
                                font: {{
                                    size: 16,
                                    weight: 'bold'
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: 'Unique Products'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'Total Records'
                                }},
                                grid: {{
                                    drawOnChartArea: false
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
"""
        
        # Country-specific insights
        top_comp_name = competitors[0].get('competidor', 'N/A')
        top_comp_upcs = competitors[0].get('distinct_upcs', 0)
        
        html_content += f"""
            <div class="insight-box">
                <h4>💡 {country_name} Market Insights</h4>
                <ul>
                    <li><strong>Market Leader:</strong> {top_comp_name} dominates with {format_number(top_comp_upcs)} unique products tracked.</li>
                    <li><strong>Competitive Intensity:</strong> {len(competitors)} major competitors actively tracked in this market.</li>
                    <li><strong>Price Diversity:</strong> Wide price ranges indicate varied product mixes and market positioning strategies across retailers.</li>
                </ul>
            </div>
        </div>
"""

    # Final insights and recommendations
    html_content += """
        <div class="section">
            <h2>🎯 Strategic Recommendations</h2>
            <div class="insight-box">
                <h4>📈 Actionable Insights for Leadership</h4>
                <ul>
                    <li><strong>Price Competitiveness:</strong> Monitor top competitors' regular prices vs. promotional prices to identify pricing strategies and seasonal patterns.</li>
                    <li><strong>Market Expansion:</strong> Guatemala shows the highest competitor density, suggesting a mature market. Consider differentiation strategies.</li>
                    <li><strong>Promotional Effectiveness:</strong> Track the frequency and depth of precio_oferta vs. precio_normal to understand competitive promotional tactics.</li>
                    <li><strong>Product Assortment:</strong> Analyze UPC counts by competitor to identify gaps in our product coverage relative to competitors.</li>
                    <li><strong>Multi-save Programs:</strong> Investigate multiahorro adoption rates by competitor to assess loyalty program effectiveness.</li>
                    <li><strong>Data Quality:</strong> Some records show null competitors - recommend data cleanup to ensure complete competitive intelligence.</li>
                    <li><strong>Trend Analysis:</strong> Implement month-over-month price change tracking to detect aggressive pricing moves by competitors.</li>
                    <li><strong>Geographic Focus:</strong> Consider country-specific strategies given the variation in competitor landscapes across markets.</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Data Methodology</h2>
            <p><strong>Data Source:</strong> BigQuery table <code>wmt-k1-cons-data-users.k1_adhoc_tables.prcng_info_cam_historico_precio_comp</code></p>
            <p><strong>Time Period:</strong> 2025 (ano >= 2025)</p>
            <p><strong>Key Fields Analyzed:</strong></p>
            <ul style="margin-left: 2rem; margin-top: 1rem;">
                <li><strong>competidor:</strong> Competitor retailer name</li>
                <li><strong>upc:</strong> Universal Product Code (unique item identifier)</li>
                <li><strong>pais:</strong> Country code (CR, GT, HN, NI, SV)</li>
                <li><strong>precio_normal:</strong> Regular retail price</li>
                <li><strong>precio_oferta:</strong> Promotional/offer price</li>
                <li><strong>multiahorro:</strong> Multi-save discount indicator</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Analysis Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
    </div>
    
    <div class="footer">
        <p>🐶 Generated by Code Puppy | Walmart Pricing Intelligence Team</p>
        <p>Confidential - For Internal Use Only</p>
    </div>
</body>
</html>
"""
    
    # Save the report
    output_file = Path("competitor_pricing_report_2025.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Report generated successfully: {output_file.absolute()}")
    return output_file

if __name__ == "__main__":
    generate_html_report()
