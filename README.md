# 📊 Nassau Candy Distributor — Profitability & Margin Performance Dashboard
End-to-End Business Intelligence Dashboard for Analyzing Product Profitability, Division Performance, and Customer Retention Opportunities.

🚀 **[Launch Live Dashboard →](#)**

---

## 🎯 Problem Statement

Candy distributors operate on razor-thin margins. Without clear visibility into which products, divisions, and customers are driving — or destroying — profitability, leadership teams make pricing and portfolio decisions based on revenue alone.

This project delivers an **interactive, filter-driven analytics dashboard** built on real distributor data that exposes the true profit story behind Nassau Candy's operations — from product-level margin diagnostics to customer-level segmentation and actionable repricing recommendations.

---

## 🚀 Key Highlights

✅ Built a complete analytics pipeline from raw order data to business insights

✅ Engineered 5+ business-driven KPIs beyond raw sales figures

✅ Developed 6 fully interactive dashboard sections covering all profitability dimensions

✅ Implemented Pareto concentration analysis to identify profit dependency risk

✅ Supports real-time filtering across date, division, margin threshold, product, and customer

✅ Generates data-driven repricing and discontinuation recommendations with quantified upside

---

## 🏆 Business Impact

- Identifies which products drive the majority of gross profit (Pareto 80/20 analysis)
- Flags low-margin / high-volume products as repricing candidates with estimated revenue upside
- Reveals underperforming products and customers for portfolio rationalization
- Enables division-level performance benchmarking across the organization
- Surfaces cost anomalies and IQR-based outliers for cost control interventions
- Supports data-driven pricing, inventory, and customer retention decisions

---

## 🛠 Tech Stack

| Category | Tools |
|---|---|
| Language | Python |
| Web App | Streamlit |
| Data Analysis | Pandas, NumPy |
| Visualization | Plotly Express, Plotly Graph Objects |
| Statistical Analysis | NumPy (IQR, percentiles, cumulative distributions) |

---

## 🏗️ System Architecture

```
Raw Order Data (CSV)
        │
        ▼
Data Cleaning & Validation
(date parsing, zero-sales removal, type coercion)
        │
        ▼
KPI Engineering
(Gross Margin %, Profit per Unit, Cost-to-Sales Ratio,
 YearMonth, Quarter, Year)
        │
        ▼
Pre-Computed Aggregations
(product_agg, customer_agg, monthly_trend)
        │
        ▼
Sidebar Filter Application
(Date, Division, Margin Threshold, Product, Customer)
        │
        ▼
Six-Section Interactive Dashboard
        │
        ├── Product Profitability
        ├── Division Performance
        ├── Cost-Margin Diagnostics
        ├── Profit Concentration (Pareto)
        ├── Insights & Recommendations
        └── Customer Profitability
```

---

## 📊 Dashboard Sections

### 1. 📈 Product Profitability
- Top 15 products by gross profit and gross margin %
- Profit contribution pie chart (Top 10 vs. rest)
- Monthly sales & profit trend lines with margin % overlay
- Order volume and units dual-axis chart
- Full product metrics table (expandable)

### 2. 🏭 Division Performance
- Revenue vs. profit grouped bar chart by division
- Gross margin % distribution box plots per division
- Division-level summary metrics table
- Regional performance breakdown (expandable)

### 3. ⚠️ Cost-Margin Diagnostics
- Cost vs. Sales scatter plot with breakeven line
- Risk flag counts: negative, low, moderate, and healthy margins
- IQR-based anomaly detection on profit-per-unit
- Cost efficiency ratio by division
- Products flagged for review — low margin / high cost (expandable)

### 4. 🎯 Profit Concentration (Pareto Analysis)
- Pareto chart: products driving 80% of profit and revenue
- Concentration risk scoring: Low / Moderate / High
- Revenue and profit distribution pie charts by division
- Detailed concentration metrics with cumulative contribution table (expandable)

### 5. 💡 Insights & Recommendations
- Top performers by profit, margin, volume, and revenue
- Profit-volume quadrant analysis (Stars, Cash Cows, Volume Drivers, Underperformers)
- Repricing opportunity table with estimated 2% and 5% revenue upside
- Discontinuation candidates with cost savings estimates
- Division-level strategic recommendations
- Consolidated action items summary

### 6. 👤 Customer Profitability
- Top 20 customers by gross profit (horizontal bar chart)
- Customer profit tier segmentation (Top / Mid / Low / Bottom)
- Revenue vs. profit scatter for top 200 customers
- Customer tier performance summary table
- Bottom 10% customer identification with high-revenue / low-profit flagging
- Customer concentration analysis (80% revenue and profit thresholds)

---

## 📐 Engineered KPIs

| Metric | Formula | Purpose |
|---|---|---|
| Gross Margin % | `(Gross Profit / Sales) × 100` | Core profitability signal |
| Profit per Unit | `Gross Profit / Units` | Unit economics efficiency |
| Cost to Sales Ratio | `Cost / Sales` | Cost pressure indicator |
| Concentration Ratio | `(# products for 80% profit / total) × 100` | Portfolio dependency risk |
| IQR Anomaly Score | `Profit/Unit < Q1 − 1.5×IQR` | Cost outlier detection |

---

## 🎛️ Dashboard Filters

All filters are in the left sidebar and apply globally across every section:

| Filter | Description |
|---|---|
| **Date Range** | Restrict data to a specific order date window |
| **Division** | Multi-select to include one or more divisions |
| **Margin Threshold (%)** | Exclude orders below a minimum gross margin % |
| **Product Search** | Case-insensitive text filter on product name |
| **Customer Search** | Filter by Customer ID |

---

## 📂 Project Structure

```
nassau-candy-dashboard/
├── app.py                          # Main Streamlit application
├── Nassau Candy Distributor.csv    # Source data file (required)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/nassau-candy-dashboard.git
cd nassau-candy-dashboard
pip install -r requirements.txt
```

---

## ▶️ Run

```bash
streamlit run app.py
```

The dashboard launches at `http://localhost:8501`.

---
