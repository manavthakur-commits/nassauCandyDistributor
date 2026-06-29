# 📊 Nassau Candy Distributor — Profitability & Margin Performance Dashboard

A comprehensive, interactive analytics dashboard built with **Streamlit** and **Plotly** to analyze profitability, margin performance, customer segmentation, and strategic opportunities across Nassau Candy's product portfolio and distribution divisions.

---

## 🚀 Features

### 📈 Product Profitability
- Top 15 products ranked by gross profit and gross margin %
- Profit contribution pie chart (Top 10 products vs. rest)
- Monthly sales & profit trend lines with margin % overlay
- Order volume and units dual-axis chart
- Detailed product metrics table (expandable)

### 🏭 Division Performance
- Revenue vs. profit grouped bar chart by division
- Margin distribution box plots per division
- Division-level performance metrics summary table
- Regional performance breakdown (expandable)

### ⚠️ Cost-Margin Diagnostics
- Cost vs. Sales scatter plot with breakeven line
- Margin risk flags: negative, low, moderate, and healthy order counts
- IQR-based anomaly detection on profit-per-unit
- Cost efficiency ratio by division
- Products needing review (low margin / high cost) — expandable

### 🎯 Profit Concentration (Pareto Analysis)
- Pareto chart: products driving 80% of profit and revenue
- Concentration risk level scoring (Low / Moderate / High)
- Revenue and profit distribution pie charts by division
- Detailed concentration metrics table (expandable)

### 💡 Insights & Recommendations
- Top performers by profit, margin, volume, and revenue
- Profit-volume quadrant analysis (Stars, Cash Cows, Volume Drivers, Underperformers)
- Repricing opportunities with estimated 2% and 5% gain scenarios
- Discontinuation candidates with cost trade-off analysis
- Division-level strategic recommendations
- Consolidated action items summary

### 👤 Customer Profitability
- Top 20 customers by gross profit (horizontal bar chart)
- Customer profit tier segmentation (Top / Mid / Low / Bottom)
- Revenue vs. profit scatter for top 200 customers
- Customer tier performance summary table
- Bottom 10% customer identification with high-revenue / low-profit flagging
- Customer concentration analysis (80% revenue and profit thresholds)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io/) |
| Visualizations | [Plotly Express](https://plotly.com/python/plotly-express/) & [Plotly Graph Objects](https://plotly.com/python/) |
| Data Processing | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| Language | Python 3.8+ |

---

## 📁 Project Structure

```
nassau-candy-dashboard/
├── app.py                          # Main Streamlit application
├── Nassau Candy Distributor.csv    # Source data file (required)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/nassau-candy-dashboard.git
cd nassau-candy-dashboard
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the data file

Place the `Nassau Candy Distributor.csv` file in the project root directory. The file must include the following columns:

| Column | Type | Description |
|---|---|---|
| `Order Date` | Date (`DD-MM-YYYY`) | Date the order was placed |
| `Ship Date` | Date (`DD-MM-YYYY`) | Date the order was shipped |
| `Order ID` | String | Unique order identifier |
| `Customer ID` | String | Unique customer identifier |
| `Product Name` | String | Name of the product |
| `Division` | String | Business division |
| `Region` | String | Geographic region |
| `Sales` | Float | Total revenue for the order line |
| `Cost` | Float | Total cost for the order line |
| `Gross Profit` | Float | Sales minus Cost |
| `Units` | Integer | Number of units sold |

### 5. Run the dashboard

```bash
python -m streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## 🎛️ Dashboard Filters

All filters are located in the left sidebar and apply globally across every section:

| Filter | Description |
|---|---|
| **Date Range** | Narrows data to orders placed within the selected period |
| **Division** | Multi-select to include one or more specific divisions |
| **Margin Threshold** | Excludes orders with gross margin % below the selected value |
| **Product Search** | Case-insensitive text filter on product name |
| **Customer Search** | Filter rows by Customer ID |

---

## 📊 Key Metrics Explained

| Metric | Formula |
|---|---|
| Gross Margin % | `(Gross Profit / Sales) × 100` |
| Profit per Unit | `Gross Profit / Units` |
| Cost to Sales Ratio | `Cost / Sales` |
| Concentration Ratio | `(# products for 80% profit / total products) × 100` |

---

## 🗂️ Requirements

Create a `requirements.txt` with the following:

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
```

---

## 🔮 Roadmap

- [ ] Fix filter propagation to pre-computed aggregations in Insights section
- [ ] Add empty-state guard when filters return no data
- [ ] Export filtered data as CSV from each section
- [ ] Year-over-year comparison toggle in trend charts
- [ ] Fulfillment time analysis using Ship Date − Order Date
- [ ] Dynamic repricing simulator with adjustable margin bump slider
- [ ] Seasonality heatmap (month × year margin %)
- [ ] AI-generated narrative insights via LLM integration

---

## 👤 Author

Built for **Nassau Candy Distributor** internal analytics.
For questions or contributions, open an issue or submit a pull request.

---

*Dashboard version: Enhanced Edition — Last updated dynamically at runtime.*