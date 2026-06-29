import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Nassau Candy - Profitability Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOAD & PROCESS DATA
# ============================================================================
@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    
    # Data cleaning & validation
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d-%m-%Y')
    
    # Calculate key metrics
    df['Gross Margin %'] = (df['Gross Profit'] / df['Sales'] * 100).round(2)
    df['Profit per Unit'] = (df['Gross Profit'] / df['Units']).round(2)
    df['Cost to Sales Ratio'] = (df['Cost'] / df['Sales']).round(3)
    
    # Extract time features
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Month'] = df['Order Date'].dt.month
    df['Quarter'] = df['Order Date'].dt.quarter
    df['Year'] = df['Order Date'].dt.year
    
    # Remove invalid records
    df = df[df['Sales'] > 0].copy()
    df = df[df['Units'] > 0].copy()
    
    return df

df = load_data()

# Pre-compute aggregations for performance
product_agg = df.groupby('Product Name').agg({
    'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
    'Profit per Unit': 'mean', 'Units': 'sum', 'Cost': 'sum', 'Order ID': 'count'
}).round(2).rename(columns={'Order ID': 'Orders'}).sort_values('Gross Profit', ascending=False)

customer_agg = df.groupby('Customer ID').agg({
    'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
    'Units': 'sum', 'Order ID': 'count', 'Cost': 'sum'
}).round(2).rename(columns={'Order ID': 'Orders'}).sort_values('Gross Profit', ascending=False)

monthly_trend = df.groupby('YearMonth').agg({
    'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
    'Units': 'sum', 'Order ID': 'count'
}).round(2).rename(columns={'Order ID': 'Orders'}).sort_index()

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
st.sidebar.title("🎛️ Dashboard Filters")

# Date range selector
date_input = st.sidebar.date_input(
    "📅 Date Range",
    value=(df['Order Date'].min().date(), df['Order Date'].max().date()),
    min_value=df['Order Date'].min().date(),
    max_value=df['Order Date'].max().date()
)

# Handle single-date selection (edge case)
if isinstance(date_input, tuple) and len(date_input) == 2:
    date_range = date_input
else:
    date_range = (date_input, date_input)

# Division filter — selectbox toggle for All vs Specific
div_mode = st.sidebar.selectbox("🏭 Division Filter Mode", ["All Divisions", "Select Specific"])
selected_divisions = []
if div_mode == "Select Specific":
    selected_divisions = st.sidebar.multiselect(
        "🏭 Select Divisions", sorted(df['Division'].unique().tolist()), default=[]
    )
else:
    selected_divisions = ['All']

# Margin threshold slider
margin_threshold = st.sidebar.slider(
    "📊 Margin Threshold (%)", min_value=-100.0, max_value=100.0,
    value=0.0, step=1.0
)

# Product search
product_search = st.sidebar.text_input(
    "🔍 Product Search", placeholder="Search by product name..."
)

# Customer search
customer_search = st.sidebar.text_input(
    "👤 Customer Search (ID)", placeholder="Search by Customer ID..."
)

# ============================================================================
# APPLY FILTERS
# ============================================================================
filtered_df = df.copy()

# Date filter
filtered_df = filtered_df[
    (filtered_df['Order Date'].dt.date >= date_range[0]) &
    (filtered_df['Order Date'].dt.date <= date_range[1])
]

# Division filter
if 'All' not in selected_divisions:
    filtered_df = filtered_df[filtered_df['Division'].isin(selected_divisions)]

# Margin threshold filter
filtered_df = filtered_df[filtered_df['Gross Margin %'] >= margin_threshold]

# Product search filter
if product_search:
    filtered_df = filtered_df[
        filtered_df['Product Name'].str.contains(product_search, case=False, na=False)
    ]

# Customer search filter
if customer_search:
    filtered_df = filtered_df[
        filtered_df['Customer ID'].astype(str).str.contains(customer_search, case=False, na=False)
    ]

# ============================================================================
# COMPUTE DERIVED METRICS
# ============================================================================
# Order fulfillment time (shipping lag)
filtered_df['Fulfillment Days'] = (filtered_df['Ship Date'] - filtered_df['Order Date']).dt.days

# ============================================================================
# EMPTY STATE CHECK
# ============================================================================
if filtered_df.empty:
    st.warning("⚠️ No data matches current filters. Please adjust your selections.")
    st.stop()

# ============================================================================
# DASHBOARD HEADER
# ============================================================================
st.markdown("# 📊 Nassau Candy Distributor")
st.markdown("### Profitability & Margin Performance Analytics — Enhanced Edition")
st.divider()

# ============================================================================
# KEY METRICS & EXECUTIVE SUMMARY
# ============================================================================
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Gross Profit'].sum()
total_units = filtered_df['Units'].sum()
unique_products = filtered_df['Product Name'].nunique()
unique_customers = filtered_df['Customer ID'].nunique()
avg_margin = filtered_df['Gross Margin %'].mean()

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Sales", f"${total_sales:,.0f}", delta=f"{len(filtered_df):,} orders")
with col2:
    margin_val = f"{(total_profit/total_sales*100):.1f}% margin" if total_sales > 0 else "0%"
    st.metric("Total Gross Profit", f"${total_profit:,.0f}", delta=margin_val)
with col3:
    st.metric("Avg Margin %", f"{avg_margin:.2f}%", delta=f"{filtered_df['Gross Margin %'].std():.2f}% std")
with col4:
    st.metric("Total Units", f"{total_units:,.0f}")
with col5:
    st.metric("Products", f"{unique_products}", delta=f"{filtered_df['Division'].nunique()} divisions")
with col6:
    st.metric("Customers", f"{unique_customers:,}")

st.divider()

# --- Executive Insights Banner ---
profit_products = filtered_df.groupby('Product Name')['Gross Profit'].sum().sort_values(ascending=False)
sales_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False)
margin_products = filtered_df.groupby('Product Name')['Gross Margin %'].mean().sort_values(ascending=False)

top_profit_product = profit_products.index[0] if len(profit_products) > 0 else "N/A"
top_margin_product = margin_products.index[0] if len(margin_products) > 0 else "N/A"
top_sales_product = sales_products.index[0] if len(sales_products) > 0 else "N/A"

# Profit/Revenue mismatch detection
if len(profit_products) > 0 and len(sales_products) > 0:
    if profit_products.index[0] != sales_products.index[0]:
        mismatch_flag = "⚠️ **Volume ≠ Profit**: Top revenue product is NOT the top profit product."
    else:
        mismatch_flag = "✅ Top revenue product is also top profit product."
else:
    mismatch_flag = ""

# Low margin warning
low_margin_count = len(filtered_df[filtered_df['Gross Margin %'] < 10])
high_margin_count = len(filtered_df[filtered_df['Gross Margin %'] > 40])

with st.expander("💡 **Quick Executive Insights** (click to expand)", expanded=True):
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    with insight_col1:
        st.markdown(f"**🏆 Top Profit Product:** `{top_profit_product}`")
        st.markdown(f"**📈 Top Margin Product:** `{top_margin_product}`")
    with insight_col2:
        st.markdown(f"**🛒 Top Revenue Product:** `{top_sales_product}`")
        st.markdown(f"**{mismatch_flag}**")
    with insight_col3:
        st.markdown(f"**🟢 High Margin Orders (>40%):** {high_margin_count:,}")
        st.markdown(f"**🟡 Low Margin Orders (<10%):** {low_margin_count:,}")

st.divider()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Section Navigation")

section = st.sidebar.radio(
    "Select a section to view:",
    options=[
        "📈 Product Profitability",
        "🏭 Division Performance",
        "⚠️ Cost-Margin Diagnostics",
        "🎯 Profit Concentration",
        "💡 Insights & Recommendations",
        "👤 Customer Profitability"
    ],
    index=0,
    label_visibility="collapsed"
)

# ============================================================================
# RENDER SELECTED SECTION
# ============================================================================

# --- SECTION 1: PRODUCT PROFITABILITY OVERVIEW + TRENDS ---
if section == "📈 Product Profitability":
    st.subheader("Product-Level Profitability Leaderboard")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("#### Top 15 by Gross Profit")
        product_profit = filtered_df.groupby('Product Name').agg({
            'Gross Profit': 'sum', 'Sales': 'sum', 'Units': 'sum', 'Gross Margin %': 'mean'
        }).round(2).sort_values('Gross Profit', ascending=False).head(15)
        
        fig_profit = px.bar(
            product_profit.reset_index(),
            x='Gross Profit', y='Product Name', orientation='h',
            color='Gross Margin %', color_continuous_scale='RdYlGn',
            hover_data=['Sales', 'Units', 'Gross Margin %'],
            title="Top 15 Products by Gross Profit"
        )
        fig_profit.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_profit, use_container_width=True)
    
    with col_b:
        st.markdown("#### Top 15 by Gross Margin %")
        product_margin = filtered_df.groupby('Product Name').agg({
            'Gross Margin %': 'mean', 'Gross Profit': 'sum', 'Sales': 'sum', 'Units': 'sum'
        }).round(2).sort_values('Gross Margin %', ascending=False).head(15)
        
        fig_margin = px.bar(
            product_margin.reset_index(),
            x='Gross Margin %', y='Product Name', orientation='h',
            color='Gross Profit', color_continuous_scale='Blues',
            hover_data=['Gross Profit', 'Sales', 'Units'],
            title="Top 15 Products by Gross Margin %"
        )
        fig_margin.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_margin, use_container_width=True)
    
    # Profit contribution pie chart
    st.markdown("#### Profit Contribution Distribution")
    product_contribution = filtered_df.groupby('Product Name')['Gross Profit'].sum().sort_values(ascending=False).head(10)
    other_profit = filtered_df.groupby('Product Name')['Gross Profit'].sum().sort_values(ascending=False).iloc[10:].sum()
    
    if other_profit > 0:
        temp_series = pd.Series({'Other Products': other_profit})
        product_contribution = pd.concat([product_contribution, temp_series])
    
    fig_pie = px.pie(
        values=product_contribution.values, names=product_contribution.index,
        title="Profit Contribution by Product (Top 10)", hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # --- TREND ANALYSIS ---
    st.markdown("---")
    st.subheader("📈 Monthly Profitability Trends")
    
    # Compute monthly trends from filtered data
    monthly_data = filtered_df.groupby('YearMonth').agg({
        'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
        'Units': 'sum', 'Order ID': 'count'
    }).round(2).rename(columns={'Order ID': 'Orders'}).sort_index()
    
    # YoY / Period-over-Period comparison toggle
    show_yoy = st.checkbox("📊 Compare to prior period (Month-over-Month % Change)", value=False)
    
    if len(monthly_data) > 1:
        trend_col1, trend_col2 = st.columns([1, 1])
        
        with trend_col1:
            fig_trend_sales = go.Figure()
            fig_trend_sales.add_trace(go.Scatter(
                x=monthly_data.index, y=monthly_data['Sales'],
                mode='lines+markers', name='Sales', marker_color='steelblue',
                line=dict(width=3)
            ))
            fig_trend_sales.add_trace(go.Scatter(
                x=monthly_data.index, y=monthly_data['Gross Profit'],
                mode='lines+markers', name='Gross Profit', marker_color='green',
                line=dict(width=3)
            ))
            
            # Add YoY % change line if toggled
            if show_yoy and len(monthly_data) > 2:
                sales_pct_change = monthly_data['Sales'].pct_change() * 100
                fig_trend_sales.add_trace(go.Scatter(
                    x=monthly_data.index, y=sales_pct_change,
                    mode='lines+markers', name='Sales MoM % Change',
                    marker_color='purple', line=dict(width=2, dash='dot'),
                    yaxis='y2'
                ))
                fig_trend_sales.update_layout(
                    yaxis2=dict(title="MoM % Change", overlaying='y', side='right', showgrid=False)
                )
            
            fig_trend_sales.update_layout(
                title="Monthly Sales & Profit Trend", height=350,
                xaxis_title="Month", yaxis_title="Amount ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig_trend_sales, use_container_width=True)
        
        with trend_col2:
            fig_trend_margin = go.Figure()
            fig_trend_margin.add_trace(go.Scatter(
                x=monthly_data.index, y=monthly_data['Gross Margin %'],
                mode='lines+markers', name='Avg Margin %', marker_color='orange',
                line=dict(width=3), fill='tozeroy'
            ))
            
            # Add margin % change line if toggled
            if show_yoy and len(monthly_data) > 2:
                margin_pct_change = monthly_data['Gross Margin %'].pct_change() * 100
                fig_trend_margin.add_trace(go.Scatter(
                    x=monthly_data.index, y=margin_pct_change,
                    mode='lines+markers', name='Margin MoM Change (pp)',
                    marker_color='purple', line=dict(width=2, dash='dot'),
                    yaxis='y2'
                ))
                fig_trend_margin.update_layout(
                    yaxis2=dict(title="MoM % Change", overlaying='y', side='right', showgrid=False)
                )
            
            fig_trend_margin.add_hline(
                y=monthly_data['Gross Margin %'].mean(), line_dash="dash",
                annotation_text=f"Avg: {monthly_data['Gross Margin %'].mean():.1f}%"
            )
            fig_trend_margin.update_layout(
                title="Monthly Average Margin % Trend", height=350,
                xaxis_title="Month", yaxis_title="Margin %",
                hovermode='x unified'
            )
            st.plotly_chart(fig_trend_margin, use_container_width=True)
        
        # Show a summary table with MoM changes when toggled
        if show_yoy and len(monthly_data) > 2:
            st.markdown("#### Period-over-Period Change Summary")
            mom_summary = monthly_data[['Sales', 'Gross Profit', 'Gross Margin %']].pct_change() * 100
            mom_summary = mom_summary.round(2)
            mom_summary.columns = ['Sales % Change', 'Profit % Change', 'Margin % Change']
            mom_summary = mom_summary.iloc[1:]  # drop first NaN row
            st.dataframe(mom_summary, use_container_width=True)
        
        # Monthly order volume & units
        fig_vol = make_subplots(specs=[[{"secondary_y": True}]])
        fig_vol.add_trace(go.Bar(
            x=monthly_data.index, y=monthly_data['Orders'], name='Orders',
            marker_color='lightblue'
        ), secondary_y=False)
        fig_vol.add_trace(go.Scatter(
            x=monthly_data.index, y=monthly_data['Units'], name='Units',
            mode='lines+markers', marker_color='coral', line=dict(width=2)
        ), secondary_y=True)
        fig_vol.update_layout(title="Monthly Order Volume & Units", height=300, hovermode='x unified')
        fig_vol.update_yaxes(title_text="Orders", secondary_y=False)
        fig_vol.update_yaxes(title_text="Units", secondary_y=True)
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("ℹ️ Need at least 2 months of data to show trends.")
    
    # Detailed product table
    with st.expander("📋 Detailed Product Metrics"):
        product_detail = filtered_df.groupby('Product Name').agg({
            'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
            'Profit per Unit': 'mean', 'Units': 'sum', 'Cost': 'sum'
        }).round(2).sort_values('Gross Profit', ascending=False)
        product_detail.columns = ['Total Sales', 'Gross Profit', 'Avg Margin %', 'Profit/Unit', 'Units', 'Total Cost']
        st.dataframe(product_detail, use_container_width=True)

# --- SECTION 2: DIVISION PERFORMANCE DASHBOARD ---
elif section == "🏭 Division Performance":
    st.subheader("Division-Level Performance Analysis")
    
    # Division aggregation
    division_stats = filtered_df.groupby('Division').agg({
        'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
        'Profit per Unit': 'mean', 'Units': 'sum', 'Order ID': 'count'
    }).round(2)
    
    division_stats.columns = ['Total Sales', 'Total Profit', 'Avg Margin %', 'Profit/Unit', 'Units', 'Orders']
    division_stats = division_stats.sort_values('Total Profit', ascending=False)
    
    col_x, col_y = st.columns([1, 1])
    
    with col_x:
        st.markdown("#### Revenue vs Profit by Division")
        division_comp = division_stats.reset_index()[['Division', 'Total Sales', 'Total Profit']]
        
        fig_div = go.Figure(data=[
            go.Bar(x=division_comp['Division'], y=division_comp['Total Sales'], 
                   name='Revenue', marker_color='lightblue'),
            go.Bar(x=division_comp['Division'], y=division_comp['Total Profit'], 
                   name='Profit', marker_color='darkblue')
        ])
        fig_div.update_layout(
            barmode='group', height=400,
            title="Revenue vs Profit Comparison",
            xaxis_title="Division", yaxis_title="Amount ($)"
        )
        st.plotly_chart(fig_div, use_container_width=True)
    
    with col_y:
        st.markdown("#### Margin Distribution by Division")
        fig_box = go.Figure()
        for division in division_stats.index:
            div_margins = filtered_df[filtered_df['Division'] == division]['Gross Margin %'].values
            fig_box.add_trace(go.Box(y=div_margins, name=division, boxmean='sd'))
        
        fig_box.update_layout(height=400, title="Margin Distribution by Division",
                            yaxis_title="Gross Margin %", showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Division metrics table
    st.markdown("#### Division Performance Metrics")
    st.dataframe(division_stats, use_container_width=True)
    
    # Fulfillment time (shipping lag)
    with st.expander("🚚 Order Fulfillment Time (Shipping Lag)"):
        fulfilment_stats = filtered_df.groupby('Division').agg({
            'Fulfillment Days': 'mean', 'Order ID': 'count'
        }).round(1).rename(columns={'Order ID': 'Orders', 'Fulfillment Days': 'Avg Fulfillment (Days)'})
        fulfilment_stats = fulfilment_stats.sort_values('Avg Fulfillment (Days)', ascending=False)
        
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            fig_fulfill = px.bar(
                fulfilment_stats.reset_index(),
                x='Avg Fulfillment (Days)', y='Division', orientation='h',
                color='Avg Fulfillment (Days)', color_continuous_scale='RdYlGn_r',
                title="Average Fulfillment Time by Division (days)"
            )
            fig_fulfill.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_fulfill, use_container_width=True)
        
        with col_f2:
            st.metric("Overall Avg Fulfillment", f"{filtered_df['Fulfillment Days'].mean():.1f} days",
                     delta=f"{filtered_df['Fulfillment Days'].std():.1f} days std")
            st.dataframe(fulfilment_stats, use_container_width=True)
        
        # Product-level fulfillment
        st.markdown("**Top 10 Slowest-Fulfilling Products**")
        slow_products = filtered_df.groupby('Product Name')['Fulfillment Days'].agg(['mean', 'count', 'std']).round(1)
        slow_products.columns = ['Avg Days', 'Orders', 'Std Dev']
        slow_products = slow_products[slow_products['Orders'] >= 3].sort_values('Avg Days', ascending=False).head(10)
        st.dataframe(slow_products, use_container_width=True)

    # Region performance
    with st.expander("🗺️ Regional Performance"):
        region_stats = filtered_df.groupby('Region').agg({
            'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
            'Units': 'sum', 'Order ID': 'count'
        }).round(2).sort_values('Gross Profit', ascending=False)
        
        region_stats.columns = ['Total Sales', 'Total Profit', 'Avg Margin %', 'Units', 'Orders']
        
        col_r1, col_r2 = st.columns([1, 1])
        
        with col_r1:
            fig_region = px.bar(
                region_stats.reset_index(),
                x='Total Profit', y='Region', orientation='h',
                color='Avg Margin %', color_continuous_scale='Viridis',
                title="Regional Profit Performance"
            )
            fig_region.update_layout(height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_region, use_container_width=True)
        
        with col_r2:
            st.dataframe(region_stats, use_container_width=True)

# --- SECTION 3: COST-MARGIN DIAGNOSTICS ---
elif section == "⚠️ Cost-Margin Diagnostics":
    st.subheader("Cost Structure & Margin Risk Analysis")
    
    col_d1, col_d2 = st.columns([1, 1])
    
    with col_d1:
        st.markdown("#### Cost vs Sales Scatter (by Product)")
        scatter_data = filtered_df.groupby('Product Name').agg({
            'Cost': 'sum', 'Sales': 'sum', 'Gross Profit': 'sum',
            'Gross Margin %': 'mean', 'Units': 'sum'
        }).reset_index()
        
        fig_scatter = px.scatter(
            scatter_data, x='Cost', y='Sales', size='Gross Profit',
            color='Gross Margin %', hover_name='Product Name',
            hover_data=['Units', 'Gross Profit'],
            color_continuous_scale='RdYlGn',
            title="Cost vs Sales Analysis",
            labels={'Cost': 'Total Cost ($)', 'Sales': 'Total Sales ($)'}
        )
        
        max_val = max(scatter_data['Cost'].max(), scatter_data['Sales'].max())
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val], mode='lines',
            name='Breakeven', line=dict(dash='dash', color='gray')
        ))
        
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_d2:
        st.markdown("#### Margin Risk Flags")
        
        # Identify margin risks
        low_margin_threshold = filtered_df['Gross Margin %'].quantile(0.25)
        negative_margin = filtered_df[filtered_df['Gross Margin %'] < 0]
        low_margin = filtered_df[
            (filtered_df['Gross Margin %'] >= 0) & 
            (filtered_df['Gross Margin %'] < low_margin_threshold)
        ]
        risky_margin = filtered_df[filtered_df['Gross Margin %'] < 10]
        
        st.warning(f"⚠️ **Orders Below 10% Margin**: {len(risky_margin)} orders (${risky_margin['Sales'].sum():,.0f} revenue)")
        st.info(f"ℹ️ **Low Margin Orders** (< {low_margin_threshold:.1f}%): {len(low_margin)} orders")
        st.metric("Negative Margin Orders", f"{len(negative_margin)}",
                  delta=f"${negative_margin['Gross Profit'].sum():,.0f} loss" if len(negative_margin) > 0 else "None")
        
        # Risk breakdown
        fig_risk = go.Figure(data=[
            go.Bar(
                x=['Healthy\n(>25%)', 'Moderate\n(10-25%)', 'Low\n(0-10%)', 'Negative\n(<0%)'],
                y=[
                    len(filtered_df[filtered_df['Gross Margin %'] > 25]),
                    len(filtered_df[(filtered_df['Gross Margin %'] >= 10) & (filtered_df['Gross Margin %'] <= 25)]),
                    len(filtered_df[(filtered_df['Gross Margin %'] > 0) & (filtered_df['Gross Margin %'] < 10)]),
                    len(filtered_df[filtered_df['Gross Margin %'] < 0])
                ],
                marker_color=['#2ecc71', '#f39c12', '#e74c3c', '#c0392b']
            )
        ])
        fig_risk.update_layout(
            title="Margin Risk Distribution", xaxis_title="Margin Category",
            yaxis_title="Number of Orders", height=250
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # --- ANOMALY DETECTION ---
    st.markdown("---")
    st.subheader("🔍 Anomaly Detection & Outlier Orders")
    
    anomaly_col1, anomaly_col2 = st.columns([1, 1])
    
    with anomaly_col1:
        st.markdown("#### Outlier Orders by Profit/Unit")
        
        # Detect anomalies using IQR method on Profit per Unit
        q1 = filtered_df['Profit per Unit'].quantile(0.25)
        q3 = filtered_df['Profit per Unit'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        anomalies = filtered_df[
            (filtered_df['Profit per Unit'] < lower_bound) | 
            (filtered_df['Profit per Unit'] > upper_bound)
        ].sort_values('Profit per Unit')
        
        st.metric("Anomalous Orders Detected", f"{len(anomalies)}",
                  delta=f"{(len(anomalies)/len(filtered_df)*100):.1f}% of total")
        
        if len(anomalies) > 0:
            st.markdown("**Anomaly details:**")
            anomaly_summary = anomalies.groupby('Product Name').agg({
                'Sales': 'sum', 'Gross Profit': 'sum', 'Profit per Unit': 'mean',
                'Units': 'sum', 'Order ID': 'count'
            }).round(2).rename(columns={'Order ID': 'Order Count'}).sort_values('Profit per Unit')
            st.dataframe(anomaly_summary, use_container_width=True)
    
    with anomaly_col2:
        st.markdown("#### Profit per Unit Distribution")
        fig_anom = px.histogram(
            filtered_df, x='Profit per Unit', nbins=50,
            color_discrete_sequence=['steelblue'],
            title="Profit per Unit Distribution with Outlier Bounds"
        )
        fig_anom.add_vline(x=lower_bound, line_dash="dash", line_color="red",
                          annotation_text=f"Lower: {lower_bound:.2f}")
        fig_anom.add_vline(x=upper_bound, line_dash="dash", line_color="red",
                          annotation_text=f"Upper: {upper_bound:.2f}")
        fig_anom.update_layout(height=350)
        st.plotly_chart(fig_anom, use_container_width=True)
    
    # Cost efficiency by division
    st.markdown("---")
    st.markdown("#### Cost Efficiency Analysis by Division")
    cost_eff = filtered_df.groupby('Division').agg({
        'Cost': 'sum', 'Sales': 'sum', 'Gross Profit': 'sum'
    }).round(2)
    cost_eff['Cost to Sales Ratio'] = (cost_eff['Cost'] / cost_eff['Sales']).round(3)
    cost_eff['Profit Margin %'] = (cost_eff['Gross Profit'] / cost_eff['Sales'] * 100).round(2)
    
    fig_cost = px.bar(
        cost_eff.reset_index(), x='Division', y=['Cost to Sales Ratio'],
        color='Division', title="Cost Efficiency by Division (Lower is Better)",
        height=350
    )
    st.plotly_chart(fig_cost, use_container_width=True)
    
    # Products needing review
    with st.expander("🔍 Products Needing Review (Low Margin/High Cost)"):
        problem_products = filtered_df.groupby('Product Name').agg({
            'Gross Margin %': 'mean', 'Cost': 'sum', 'Sales': 'sum',
            'Units': 'sum', 'Gross Profit': 'sum'
        }).round(2)
        
        problem_products = problem_products[
            (problem_products['Gross Margin %'] < 15) & 
            (problem_products['Sales'] > 0)
        ].sort_values('Gross Margin %')
        
        if len(problem_products) > 0:
            st.dataframe(problem_products, use_container_width=True)
        else:
            st.info("✅ No problem products identified in current filters!")

# --- SECTION 4: PROFIT CONCENTRATION (PARETO ANALYSIS) ---
elif section == "🎯 Profit Concentration":
    st.subheader("Profit Concentration & Pareto Analysis")
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        st.markdown("#### Pareto: Products Contributing to Profit")
        
        product_profit = filtered_df.groupby('Product Name')['Gross Profit'].sum().sort_values(ascending=False)
        product_revenue = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False)
        
        profit_cumsum = product_profit.cumsum() / product_profit.sum() * 100
        rev_cumsum = product_revenue.cumsum() / product_revenue.sum() * 100
        
        profit_80_count = (profit_cumsum <= 80).sum() + 1
        rev_80_count = (rev_cumsum <= 80).sum() + 1
        
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_pareto.add_trace(
            go.Bar(x=list(range(1, len(product_profit) + 1)), y=product_profit.values,
                   name='Profit', marker_color='steelblue'), secondary_y=False
        )
        fig_pareto.add_trace(
            go.Scatter(x=list(range(1, len(profit_cumsum) + 1)), y=profit_cumsum.values,
                       name='Cumulative %', marker_color='red', mode='lines+markers',
                       line=dict(width=3)), secondary_y=True
        )
        fig_pareto.add_hline(y=80, secondary_y=True, line_dash="dash",
                            annotation_text="80% Threshold", annotation_position="right")
        fig_pareto.add_vline(x=profit_80_count, line_dash="dash",
                            annotation_text=f"{profit_80_count} products", annotation_position="top")
        
        fig_pareto.update_xaxes(title_text="Product Rank")
        fig_pareto.update_yaxes(title_text="Profit ($)", secondary_y=False)
        fig_pareto.update_yaxes(title_text="Cumulative %", secondary_y=True)
        fig_pareto.update_layout(height=400, title="Pareto Chart: Profit Concentration")
        
        st.plotly_chart(fig_pareto, use_container_width=True)
    
    with col_p2:
        st.markdown("#### Pareto Insights")
        
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.metric("Products for 80% Profit", f"{profit_80_count}",
                     delta=f"of {len(product_profit)} total", delta_color="off")
            st.metric("% of Product Line", f"{(profit_80_count/len(product_profit)*100):.1f}%",
                     delta="concentration ratio", delta_color="off")
        
        with col_i2:
            st.metric("Products for 80% Revenue", f"{rev_80_count}",
                     delta=f"of {len(product_revenue)} total", delta_color="off")
            st.metric("Profit/Revenue Mismatch", f"{abs(profit_80_count - rev_80_count)}",
                     delta="products differ", delta_color="off")
        
        # Concentration risk gauge
        concentration_ratio = profit_80_count / len(product_profit) * 100 if len(product_profit) > 0 else 0
        if concentration_ratio <= 30:
            risk_level = "🟢 Low"
            risk_desc = "Well diversified"
        elif concentration_ratio <= 50:
            risk_level = "🟡 Moderate"
            risk_desc = "Some concentration risk"
        else:
            risk_level = "🔴 High"
            risk_desc = "High concentration risk"
        
        st.markdown("---")
        st.markdown(f"**Concentration Risk Level:** {risk_level}")
        st.markdown(f"*{risk_desc}: {profit_80_count} products drive 80% of profit*")
        
        st.markdown("---")
        st.markdown("""
        **Key Insights:**
        - Products with **high profit concentration** suggest dependency risk
        - **Revenue vs Profit mismatch** indicates pricing or cost issues
        - Focus optimization on the **vital few products** driving results
        """)
    
    # Division concentration
    st.markdown("---")
    st.markdown("#### Concentration by Division")
    div_revenue = filtered_df.groupby('Division')['Sales'].sum().sort_values(ascending=False)
    div_profit = filtered_df.groupby('Division')['Gross Profit'].sum().sort_values(ascending=False)
    
    col_d1_p, col_d2_p = st.columns(2)
    
    with col_d1_p:
        fig_div_rev = px.pie(values=div_revenue.values, names=div_revenue.index,
                            title="Revenue Distribution by Division", hole=0.3)
        fig_div_rev.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_div_rev, use_container_width=True)
    
    with col_d2_p:
        fig_div_prof = px.pie(values=div_profit.values, names=div_profit.index,
                             title="Profit Distribution by Division", hole=0.3)
        fig_div_prof.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_div_prof, use_container_width=True)
    
    # Concentration table
    with st.expander("📊 Detailed Concentration Metrics"):
        conc_table = pd.DataFrame({
            'Product': product_profit.index,
            'Profit': product_profit.values,
            'Cumulative %': profit_cumsum.values.round(2),
            'Revenue': product_revenue[product_profit.index].values,
            'Rev Cumulative %': rev_cumsum[product_profit.index].values.round(2)
        })
        st.dataframe(conc_table, use_container_width=True)

# --- SECTION 5: INSIGHTS & RECOMMENDATIONS ---
elif section == "💡 Insights & Recommendations":
    st.subheader("💡 Strategic Insights & Actionable Recommendations")
    st.markdown("Data-driven recommendations based on profitability analysis.")
    st.divider()
    
    # Compute fresh aggregations from filtered data so filters apply correctly
    filtered_product_agg = filtered_df.groupby('Product Name').agg({
        'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
        'Profit per Unit': 'mean', 'Units': 'sum', 'Cost': 'sum', 'Order ID': 'count'
    }).round(2).rename(columns={'Order ID': 'Orders'}).sort_values('Gross Profit', ascending=False)
    
    filtered_customer_agg = filtered_df.groupby('Customer ID').agg({
        'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
        'Units': 'sum', 'Order ID': 'count', 'Cost': 'sum'
    }).round(2).rename(columns={'Order ID': 'Orders'}).sort_values('Gross Profit', ascending=False)
    
    # --- 1. TOP PERFORMERS ---
    st.markdown("### 🏆 Top Performers")
    
    perf_col1, perf_col2 = st.columns(2)
    
    with perf_col1:
        st.markdown("#### Highest Profit Contributors")
        top5_profit = filtered_product_agg.head(5)[['Sales', 'Gross Profit', 'Gross Margin %']]
        top5_profit.columns = ['Sales', 'Gross Profit', 'Margin %']
        st.dataframe(top5_profit, use_container_width=True)
        
        st.markdown("#### Highest Margin Products")
        top5_margin = filtered_product_agg.sort_values('Gross Margin %', ascending=False).head(5)[['Sales', 'Gross Profit', 'Gross Margin %']]
        top5_margin.columns = ['Sales', 'Gross Profit', 'Margin %']
        st.dataframe(top5_margin, use_container_width=True)
    
    with perf_col2:
        st.markdown("#### Highest Volume (Units Sold)")
        top5_volume = filtered_product_agg.sort_values('Units', ascending=False).head(5)[['Sales', 'Gross Profit', 'Units']]
        top5_volume.columns = ['Sales', 'Gross Profit', 'Units']
        st.dataframe(top5_volume, use_container_width=True)
        
        st.markdown("#### Highest Revenue Products")
        top5_revenue = filtered_product_agg.sort_values('Sales', ascending=False).head(5)[['Sales', 'Gross Profit', 'Gross Margin %']]
        top5_revenue.columns = ['Sales', 'Gross Profit', 'Margin %']
        st.dataframe(top5_revenue, use_container_width=True)
    
    st.divider()
    
    # --- 2. PROFIT/VOLUME QUADRANT ANALYSIS ---
    st.markdown("### 📊 Profit-Volume Quadrant Analysis")
    st.markdown("""
    This analysis categorizes products into four quadrants to identify strategic opportunities:
    - **🌟 Stars**: High Profit + High Volume (Core products to protect)
    - **💰 Cash Cows**: High Profit + Low Volume (Niche gems to grow)
    - **📦 Volume Drivers**: Low Profit + High Volume (Repricing candidates)
    - **⚠️ Underperformers**: Low Profit + Low Volume (Discontinuation candidates)
    """)
    
    # Calculate median splits for quadrant analysis from filtered data
    profit_median = filtered_product_agg['Gross Profit'].median() if len(filtered_product_agg) > 0 else 0
    volume_median = filtered_product_agg['Units'].median() if len(filtered_product_agg) > 0 else 0
    
    def assign_quadrant(row):
        if row['Gross Profit'] >= profit_median and row['Units'] >= volume_median:
            return '🌟 Star'
        elif row['Gross Profit'] >= profit_median and row['Units'] < volume_median:
            return '💰 Cash Cow'
        elif row['Gross Profit'] < profit_median and row['Units'] >= volume_median:
            return '📦 Volume Driver'
        else:
            return '⚠️ Underperformer'
    
    quadrant_df = filtered_product_agg.copy()
    quadrant_df['Quadrant'] = quadrant_df.apply(assign_quadrant, axis=1)
    
    # Scatter plot
    fig_quad = px.scatter(
        quadrant_df.reset_index(),
        x='Units', y='Gross Profit', size='Sales',
        color='Quadrant', hover_name='Product Name',
        hover_data=['Sales', 'Gross Margin %'],
        title="Product Quadrant: Profit vs Volume",
        color_discrete_map={
            '🌟 Star': 'gold', '💰 Cash Cow': 'green',
            '📦 Volume Driver': 'orange', '⚠️ Underperformer': 'red'
        }
    )
    fig_quad.add_hline(y=profit_median, line_dash="dash", line_color="gray",
                      annotation_text="Profit Median")
    fig_quad.add_vline(x=volume_median, line_dash="dash", line_color="gray",
                      annotation_text="Volume Median")
    fig_quad.update_layout(height=450)
    st.plotly_chart(fig_quad, use_container_width=True)
    
    # Quadrant breakdown
    quad_counts = quadrant_df['Quadrant'].value_counts()
    quad_cols = st.columns(4)
    quad_emojis = {'🌟 Star': '🌟', '💰 Cash Cow': '💰', '📦 Volume Driver': '📦', '⚠️ Underperformer': '⚠️'}
    for i, (quad, count) in enumerate(quad_counts.items()):
        with quad_cols[i]:
            st.metric(f"{quad}", f"{count} products")
    
    st.divider()
    
    # --- 3. REPRICING OPPORTUNITIES ---
    st.markdown("### 💲 Repricing Opportunities")
    st.markdown("Products with high volume but low margins — potential repricing candidates to improve profitability.")
    
    # Find products with high units but low margin
    unit_median = filtered_product_agg['Units'].median() if len(filtered_product_agg) > 0 else 0
    margin_median = filtered_product_agg['Gross Margin %'].median() if len(filtered_product_agg) > 0 else 0
    
    repricing_candidates = filtered_product_agg[
        (filtered_product_agg['Units'] >= unit_median) & 
        (filtered_product_agg['Gross Margin %'] < margin_median)
    ].sort_values('Units', ascending=False)
    
    if len(repricing_candidates) > 0:
        repricing_candidates['Est. Gain (2% bump)'] = (repricing_candidates['Sales'] * 0.02).round(2)
        repricing_candidates['Est. Gain (5% bump)'] = (repricing_candidates['Sales'] * 0.05).round(2)
        st.dataframe(repricing_candidates[['Sales', 'Gross Profit', 'Gross Margin %', 'Units', 'Est. Gain (2% bump)', 'Est. Gain (5% bump)']], use_container_width=True)
        
        total_2pct = repricing_candidates['Est. Gain (2% bump)'].sum()
        total_5pct = repricing_candidates['Est. Gain (5% bump)'].sum()
        st.success(f"💡 **Estimated Margin Improvement:** **${total_2pct:,.0f}** (2% bump) to **${total_5pct:,.0f}** (5% bump) from repricing these products.")
        
        # Export button for repricing candidates
        csv_repricing = repricing_candidates[['Sales', 'Gross Profit', 'Gross Margin %', 'Units', 'Est. Gain (2% bump)', 'Est. Gain (5% bump)']].to_csv(index=True)
        st.download_button(
            label="📥 Download Repricing Candidates (CSV)",
            data=csv_repricing,
            file_name="repricing_candidates.csv",
            mime="text/csv",
            key="download_repricing"
        )
    else:
        st.info("✅ No clear repricing candidates identified in current filters.")
    
    st.divider()
    
    # --- 4. DISCONTINUATION CANDIDATES ---
    st.markdown("### 🗑️ Rationalization / Discontinuation Candidates")
    st.markdown("Products with low profit contribution and low volume — potential candidates for phase-out.")
    
    disc_candidates = filtered_product_agg[
        (filtered_product_agg['Gross Profit'] < profit_median) & 
        (filtered_product_agg['Units'] < volume_median)
    ].sort_values('Gross Profit')
    
    if len(disc_candidates) > 0:
        st.dataframe(disc_candidates[['Sales', 'Gross Profit', 'Gross Margin %', 'Units', 'Cost']], use_container_width=True)
        
        # Calculate potential savings
        total_cost_saved = disc_candidates['Cost'].sum()
        total_profit_lost = disc_candidates['Gross Profit'].sum()
        net_impact = total_profit_lost - total_cost_saved  # negative means savings
        
        st.warning(f"⚖️ **Trade-off:** Discontinuing would lose **${total_profit_lost:,.0f}** profit but free up **${total_cost_saved:,.0f}** in costs. Net operational impact: **${net_impact:,.0f}**")
        st.info("💡 *Consider resource reallocation to higher-profit products.*")
        
        # Export button for discontinuation candidates
        csv_disc = disc_candidates[['Sales', 'Gross Profit', 'Gross Margin %', 'Units', 'Cost']].to_csv(index=True)
        st.download_button(
            label="📥 Download Discontinuation Candidates (CSV)",
            data=csv_disc,
            file_name="discontinuation_candidates.csv",
            mime="text/csv",
            key="download_disc"
        )
    else:
        st.info("✅ No clear discontinuation candidates in current filters.")
    
    st.divider()
    
    # --- 5. DIVISION-LEVEL STRATEGIC RECOMMENDATIONS ---
    st.markdown("### 🏢 Division-Level Strategic Recommendations")
    
    div_profitability = filtered_df.groupby('Division').agg({
        'Gross Profit': 'sum', 'Sales': 'sum', 'Gross Margin %': 'mean',
        'Cost': 'sum', 'Units': 'sum'
    }).round(2)
    div_profitability['Margin %'] = (div_profitability['Gross Profit'] / div_profitability['Sales'] * 100).round(2)
    div_profitability['Cost Ratio'] = (div_profitability['Cost'] / div_profitability['Sales']).round(3)
    
    div_cols = st.columns(len(div_profitability))
    for i, (div, row) in enumerate(div_profitability.iterrows()):
        with div_cols[i]:
            st.markdown(f"**{div}**")
            st.metric("Profit", f"${row['Gross Profit']:,.0f}", delta=f"{row['Margin %']:.1f}% margin")
            if row['Cost Ratio'] > 0.7:
                st.markdown("⚠️ *High cost ratio*")
            elif row['Cost Ratio'] < 0.5:
                st.markdown("✅ *Efficient operations*")
    
    # Overall recommendations
    st.markdown("---")
    st.markdown("### 📋 Consolidated Action Items")
    
    action_items = []
    
    # 1. Repricing recommendation
    if len(repricing_candidates) > 0:
        action_items.append(f"🔴 **Repricing Priority**: Review pricing for {len(repricing_candidates)} high-volume, low-margin products. Est. upside: ${total_2pct:,.0f}-${total_5pct:,.0f}")
    
    # 2. Discontinuation recommendation
    if len(disc_candidates) > 0:
        action_items.append(f"🟡 **Portfolio Rationalization**: Evaluate {len(disc_candidates)} underperforming products for discontinuation. Frees ${total_cost_saved:,.0f} in costs.")
    
    # 3. Concentration risk (recompute from filtered)
    product_profit_filtered = filtered_df.groupby('Product Name')['Gross Profit'].sum().sort_values(ascending=False)
    concentration_ratio_filtered = (product_profit_filtered.cumsum() <= product_profit_filtered.sum() * 0.8).sum() + 1
    concentration_ratio_filtered = concentration_ratio_filtered / len(product_profit_filtered) * 100 if len(product_profit_filtered) > 0 else 0
    
    if concentration_ratio_filtered > 40:
        action_items.append(f"🔴 **Concentration Risk**: Strong profit concentration detected. Diversify to reduce dependency risk.")
    else:
        action_items.append(f"✅ **Portfolio Diversification**: Good profit distribution across {len(filtered_product_agg)} products.")
    
    # 4. Top performer investment
    if len(top5_profit) > 0:
        top_profit_name = top5_profit.index[0]
        action_items.append(f"🟢 **Invest In Winners**: Top profit product ({top_profit_name}) generates ${top5_profit.iloc[0]['Gross Profit']:,.0f}. Consider increasing inventory/marketing.")
    
    # 5. Customer profitability
    top_customer_profit = filtered_customer_agg.head(1)['Gross Profit'].sum() if len(filtered_customer_agg) > 0 else 0
    action_items.append(f"🔵 **Customer Focus**: Top customer generates ${top_customer_profit:,.0f} profit. Identify and nurture high-value customer segments.")
    
    for item in action_items:
        st.markdown(f"- {item}")
    
    # Consolidated export
    st.markdown("---")
    st.markdown("#### 📥 Export Recommendations")
    st.markdown("Download the full recommendations data for offline analysis.")
    
    # Build a combined recommendations table
    recommendations_data = []
    if len(repricing_candidates) > 0:
        rec_subset = repricing_candidates[['Sales', 'Gross Profit', 'Gross Margin %', 'Units']].head(50).copy()
        rec_subset['Recommendation'] = 'Repricing Candidate'
        recommendations_data.append(rec_subset)
    if len(disc_candidates) > 0:
        disc_subset = disc_candidates[['Sales', 'Gross Profit', 'Gross Margin %', 'Units']].head(50).copy()
        disc_subset['Recommendation'] = 'Discontinuation Candidate'
        recommendations_data.append(disc_subset)
    
    if recommendations_data:
        combined_recs = pd.concat(recommendations_data)
        csv_combined = combined_recs.to_csv(index=True)
        st.download_button(
            label="📥 Download All Recommendations (CSV)",
            data=csv_combined,
            file_name="all_recommendations.csv",
            mime="text/csv",
            key="download_all_recs"
        )

# --- SECTION 6: CUSTOMER PROFITABILITY ---
elif section == "👤 Customer Profitability":
    st.subheader("👤 Customer Profitability Analysis")
    st.markdown("Analyze profitability at the customer level to identify high-value and unprofitable segments.")
    st.divider()
    
    # Compute customer aggregations from filtered data
    cust_agg = filtered_df.groupby('Customer ID').agg({
        'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
        'Units': 'sum', 'Order ID': 'count', 'Cost': 'sum'
    }).round(2).rename(columns={'Order ID': 'Orders'}).sort_values('Gross Profit', ascending=False)
    
    cust_col1, cust_col2 = st.columns([1, 1])
    
    with cust_col1:
        st.markdown("#### Top 20 Customers by Gross Profit")
        top_cust = cust_agg.head(20).reset_index()
        top_cust['Customer ID'] = top_cust['Customer ID'].astype(str)
        
        fig_cust_profit = px.bar(
            top_cust, x='Gross Profit', y='Customer ID', orientation='h',
            color='Gross Margin %', color_continuous_scale='RdYlGn',
            hover_data=['Sales', 'Orders', 'Gross Margin %'],
            title="Top 20 Customers by Profit Contribution"
        )
        fig_cust_profit.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_cust_profit, use_container_width=True)
    
    with cust_col2:
        st.markdown("#### Customer Profit Distribution")
        
        # Segment customers into tiers
        def customer_tier(profit):
            if profit >= cust_agg['Gross Profit'].quantile(0.8):
                return '🌟 Top Tier'
            elif profit >= cust_agg['Gross Profit'].quantile(0.5):
                return '💰 Mid Tier'
            elif profit >= cust_agg['Gross Profit'].quantile(0.2):
                return '📦 Low Tier'
            else:
                return '⚠️ Bottom Tier'
        
        cust_agg['Tier'] = cust_agg['Gross Profit'].apply(customer_tier)
        tier_counts = cust_agg['Tier'].value_counts()
        
        fig_tier = px.pie(
            values=tier_counts.values, names=tier_counts.index,
            title="Customer Distribution by Profit Tier",
            hole=0.3, color_discrete_map={
                '🌟 Top Tier': 'gold', '💰 Mid Tier': 'steelblue',
                '📦 Low Tier': 'orange', '⚠️ Bottom Tier': 'red'
            }
        )
        fig_tier.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_tier, use_container_width=True)
    
    # Customer Revenue vs Profit scatter
    st.markdown("---")
    st.markdown("#### Customer: Revenue vs Profit")
    
    fig_cust_scatter = px.scatter(
        cust_agg.reset_index().head(200),  # Show top 200 for performance
        x='Sales', y='Gross Profit', size='Orders',
        color='Gross Margin %', hover_name='Customer ID',
        hover_data=['Orders', 'Units', 'Gross Margin %'],
        color_continuous_scale='RdYlGn',
        title="Customer Profitability Mapping (Top 200 Customers)",
        labels={'Sales': 'Revenue ($)', 'Gross Profit': 'Gross Profit ($)'}
    )
    fig_cust_scatter.add_hline(y=0, line_dash="dash", line_color="red")
    fig_cust_scatter.update_layout(height=450)
    st.plotly_chart(fig_cust_scatter, use_container_width=True)
    
    # Customer tier metrics
    st.markdown("---")
    st.markdown("#### Customer Tier Performance Summary")
    
    tier_summary = cust_agg.reset_index().groupby('Tier').agg({
        'Sales': 'sum', 'Gross Profit': 'sum', 'Gross Margin %': 'mean',
        'Orders': 'sum', 'Customer ID': 'nunique'
    }).round(2).rename(columns={'Customer ID': 'Customer Count'})
    
    tier_order = ['🌟 Top Tier', '💰 Mid Tier', '📦 Low Tier', '⚠️ Bottom Tier']
    tier_summary = tier_summary.reindex([t for t in tier_order if t in tier_summary.index])
    
    st.dataframe(tier_summary, use_container_width=True)
    
    # Low-value customer identification
    st.markdown("---")
    st.markdown("#### 🟡 Customers Requiring Review (Low Profit / High Service Cost)")
    
    # Find bottom 10% customers by profit
    bottom_cutoff = cust_agg['Gross Profit'].quantile(0.1)
    bottom_customers = cust_agg[cust_agg['Gross Profit'] <= bottom_cutoff].sort_values('Gross Profit')
    
    if len(bottom_customers) > 0:
        st.warning(f"⚠️ **{len(bottom_customers)} customers** are in the bottom 10% by profitability.")
        
        # Check if any have significant revenue (high volume but low profit)
        high_rev_low_profit = bottom_customers[
            bottom_customers['Sales'] > bottom_customers['Sales'].median()
        ].sort_values('Sales', ascending=False)
        
        if len(high_rev_low_profit) > 0:
            st.markdown("**High-revenue but low-profit customers** (potential repricing candidates):")
            st.dataframe(high_rev_low_profit[['Sales', 'Gross Profit', 'Gross Margin %', 'Orders', 'Units']].head(10), use_container_width=True)
        else:
            st.markdown("All low-profit customers have proportionally low revenue.")
        
        with st.expander("📋 Full List of Bottom-Tier Customers"):
            st.dataframe(bottom_customers[['Sales', 'Gross Profit', 'Gross Margin %', 'Orders', 'Units']], use_container_width=True)
    else:
        st.info("✅ No significantly underperforming customers identified.")
    
    # Customer concentration
    st.markdown("---")
    st.markdown("#### 📊 Customer Concentration Analysis")
    
    cust_con_col1, cust_con_col2 = st.columns(2)
    
    with cust_con_col1:
        # Revenue concentration
        cust_rev_cumsum = cust_agg['Sales'].sort_values(ascending=False).cumsum()
        cust_rev_cumsum_pct = cust_rev_cumsum / cust_rev_cumsum.iloc[-1] * 100
        cust_rev_80 = (cust_rev_cumsum_pct <= 80).sum() + 1
        
        st.metric("Customers for 80% Revenue", f"{cust_rev_80} of {len(cust_agg)}",
                 delta=f"{(cust_rev_80/len(cust_agg)*100):.1f}% of customer base")
    
    with cust_con_col2:
        # Profit concentration
        cust_profit_cumsum = cust_agg['Gross Profit'].sort_values(ascending=False).cumsum()
        cust_profit_cumsum_pct = cust_profit_cumsum / cust_profit_cumsum.iloc[-1] * 100
        cust_profit_80 = (cust_profit_cumsum_pct <= 80).sum() + 1
        
        st.metric("Customers for 80% Profit", f"{cust_profit_80} of {len(cust_agg)}",
                 delta=f"{(cust_profit_80/len(cust_agg)*100):.1f}% of customer base")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown(f"""
<div style='text-align: center; color: gray; font-size: 12px; margin-top: 20px;'>
    <p>Nassau Candy Distributor | Profitability & Margin Performance Dashboard — Enhanced Edition</p>
    <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)