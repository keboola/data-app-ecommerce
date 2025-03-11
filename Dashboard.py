import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

from keboola_streamlit import KeboolaStreamlit

st.set_page_config(page_title="E-commerce Report", layout="wide")
# Constants
# Simplified color palette
PRIMARY_COLOR = '#1E88E5'  # Main blue
SECONDARY_COLOR = '#FFC107'  # Amber for emphasis
SUCCESS_COLOR = '#4CAF50'  # Green for positive metrics
WARNING_COLOR = '#FF9800'  # Orange for warnings
DANGER_COLOR = '#F44336'  # Red for negative metrics

# Base palette for sequential data
BASE_PALETTE = [
    '#1E88E5',  # Primary blue
    '#42A5F5',  # Lighter blue
    '#90CAF9',  # Even lighter blue
    '#BBDEFB',  # Lightest blue
    '#E3F2FD'   # Almost white blue
]

# Accent palette for categorical data
ACCENT_PALETTE = [
    '#1E88E5',  # Blue
    '#FFC107',  # Amber
    '#4CAF50',  # Green
    '#FF9800',  # Orange
    '#F44336'   # Red
]

# Category colors (simplified)
CATEGORY_COLORS = {
    'Electronics': '#1E88E5',
    'Clothing': '#42A5F5',
    'Home': '#90CAF9',
    'Beauty': '#BBDEFB',
    'Food': '#E3F2FD'
}

# Segment colors (meaningful progression)
SEGMENT_COLORS = {
    "Champions": '#1E88E5',
    "Loyal Customers": '#90CAF9',
    "Potential Loyalists": '#BBDEFB',
    "Need Attention": '#F44336'
}

# Order status colors (meaningful states)
STATUS_COLORS = {
    'Delivered': '#4CAF50',
    'Shipped': '#1E88E5',
    'Processing': '#FFC107',
    'Created': '#90CAF9',
    'Cancelled': '#F44336'
}

# Device type colors (simplified)
DEVICE_COLORS = {
    'Desktop': '#1E88E5',
    'Mobile': '#42A5F5',
    'Tablet': '#90CAF9'
}

# Event type colors (simplified)
EVENT_COLORS = {
    'PageView': '#1E88E5',
    'AddToCart': '#42A5F5',
    'Purchase': '#4CAF50',
    'Search': '#90CAF9',
    'ProductView': '#BBDEFB',
    'Login': '#FFC107',
    'Registration': '#FF9800'
}

# Campaign type colors (simplified)
CAMPAIGN_COLORS = {
    'Email': '#1E88E5',
    'Social': '#42A5F5',
    'Display': '#90CAF9',
    'Search': '#BBDEFB',
    'TV': '#E3F2FD'
}


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #F5F5F5;
        border-radius: 5px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-title {
        font-size: 1.2rem;
        color: #424242;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .card {
        border-radius: 5px;
        background-color: #F5F5F5;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1E88E5;
    }
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F5F5F5;
        border-radius: 4px 4px 0 0;
        color: #1E88E5;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

data = {}
# Load all data files
data['campaign'] = pd.read_csv("data/in/tables/CAMPAIGN.csv")
data['campaign_event'] = pd.read_csv("data/in/tables/CAMPAIGN_EVENT.csv")
data['channel'] = pd.read_csv("data/in/tables/CHANNEL.csv")
data['company'] = pd.read_csv("data/in/tables/COMPANY.csv")
data['content_page'] = pd.read_csv("data/in/tables/CONTENT_PAGE.csv")
data['custom_attribute'] = pd.read_csv("data/in/tables/CUSTOM_ATTRIBUTE.csv")
data['customer'] = pd.read_csv("data/in/tables/CUSTOMER.csv")
data['digital_event'] = pd.read_csv("data/in/tables/DIGITAL_EVENT.csv")
data['digital_site'] = pd.read_csv("data/in/tables/DIGITAL_SITE.csv")
data['facility'] = pd.read_csv("data/in/tables/FACILITY.csv")
data['inventory'] = pd.read_csv("data/in/tables/INVENTORY.csv")
data['order_campaign_attribution'] = pd.read_csv("data/in/tables/ORDER_CAMPAIGN_ATTRIBUTION.csv")
data['order_event'] = pd.read_csv("data/in/tables/ORDER_EVENT.csv")
data['order_fact'] = pd.read_csv("data/in/tables/ORDER_FACT.csv")
data['order_fulfillment'] = pd.read_csv("data/in/tables/ORDER_FULFILLMENT.csv")
data['order_fulfillment_line'] = pd.read_csv("data/in/tables/ORDER_FULFILLMENT_LINE.csv")
data['order_line'] = pd.read_csv("data/in/tables/ORDER_LINE.csv")
data['order_status_history'] = pd.read_csv("data/in/tables/ORDER_STATUS_HISTORY.csv")
data['page_performance'] = pd.read_csv("data/in/tables/PAGE_PERFORMANCE.csv")
data['person'] = pd.read_csv("data/in/tables/PERSON.csv")
data['product'] = pd.read_csv("data/in/tables/PRODUCT.csv")
data['product_variant'] = pd.read_csv("data/in/tables/PRODUCT_VARIANT.csv")
data['sales_plan'] = pd.read_csv("data/in/tables/SALES_PLAN.csv")

# Preprocess date columns to improve filtering performance
data['order_fact']['ORDER_DATE'] = pd.to_datetime(data['order_fact']['ORDER_DATE'])
data['digital_event']['EVENT_DATE'] = pd.to_datetime(data['digital_event']['EVENT_DATE'])
data['page_performance']['DATE'] = pd.to_datetime(data['page_performance']['DATE'])
data['campaign']['START_DATE'] = pd.to_datetime(data['campaign']['START_DATE'])
data['campaign']['END_DATE'] = pd.to_datetime(data['campaign']['END_DATE'])
data['sales_plan']['PLAN_START_DATE'] = pd.to_datetime(data['sales_plan']['PLAN_START_DATE'])
data['sales_plan']['PLAN_END_DATE'] = pd.to_datetime(data['sales_plan']['PLAN_END_DATE'])

# Clean budget data
data['campaign']['BUDGET'] = data['campaign']['BUDGET'].str.replace('$', '').str.replace(',', '').astype(float)

# Display title and Keboola logo in a row
st.markdown(
f'''
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 40px;">
        <h1 style="margin: 0;">E-commerce Report</h1>
        <img src="https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg" alt="Logo" width="200">
    </div>
''',
unsafe_allow_html=True)


# Create sidebar filters

with st.sidebar:
    st.subheader("Filters")
    
    # Date range filter
    min_date = data['order_fact']['ORDER_DATE'].min()
    max_date = pd.Timestamp.today()
    
    # Add date filter options
    date_filter_option = st.selectbox(
        "Date Filter Type",
        options=["Current Year", "Year to Date", "Custom"],
        index=0
    )
    
    # Calculate date ranges based on selection
    today = pd.Timestamp.today()
    current_year_start = pd.Timestamp(today.year, 1, 1)
    year_ago = today - pd.DateOffset(years=1)
    
    if date_filter_option == "Current Year":
        # Current year from Jan 1st to today
        date_range = (current_year_start.date(), today.date())
    elif date_filter_option == "Year to Date":
        # Last 365 days
        date_range = (year_ago.date(), today.date())
    else:  # Custom Range
        date_range = st.date_input(
            "Custom",
            value=(min_date, today.date()),
            min_value=min_date,
            max_value=today.date()
        )
    
    # Other filters
    channels = ['All'] + sorted(data['channel']['CHANNEL_NAME'].unique().tolist())
    selected_channel = st.selectbox('Sales Channel', channels)
    
    categories = ['All'] + sorted(data['product']['CATEGORY'].unique().tolist())
    selected_category = st.selectbox('Product Category', categories)
    
    payment_methods = ['All'] + sorted(data['order_fact']['PAYMENT_METHOD'].unique().tolist())
    selected_payment_method = st.selectbox('Payment Method', payment_methods)
    
    order_statuses = ['All'] + sorted(data['order_fact']['ORDER_STATUS'].unique().tolist())
    selected_order_status = st.selectbox('Order Status', order_statuses)
    

filtered_data = {
        'order_fact': data['order_fact'].copy(),
        'order_line': data['order_line'].copy(),
        'customer': data['customer'].copy(),
        'product': data['product'].copy(),
        'digital_event': data['digital_event'].copy(),
        'page_performance': data['page_performance'].copy(),
        'campaign': data['campaign'].copy(),
        'inventory': data['inventory'].copy(),
        'facility': data['facility'].copy(),
        'person': data['person'].copy(),
        'company': data['company'].copy(),
        'order_campaign_attribution': data['order_campaign_attribution'].copy()
    }
    
# Sort dates to ensure start_date is before end_date
sorted_dates = sorted(date_range)
start_date = pd.Timestamp(sorted_dates[0])
end_date = pd.Timestamp(sorted_dates[1])

# Filter orders by date range (using vectorized operations)
date_mask = (filtered_data['order_fact']['ORDER_DATE'] >= start_date) & (filtered_data['order_fact']['ORDER_DATE'] <= end_date)
filtered_data['order_fact'] = filtered_data['order_fact'][date_mask]

# Filter by channel
if selected_channel != 'All':
    channel_ids = data['channel'][data['channel']['CHANNEL_NAME'] == selected_channel]['CHANNEL_ID'].values
    filtered_data['order_fact'] = filtered_data['order_fact'][filtered_data['order_fact']['CHANNEL_ID'].isin(channel_ids)]

# Filter by payment method
if selected_payment_method != 'All':
    filtered_data['order_fact'] = filtered_data['order_fact'][filtered_data['order_fact']['PAYMENT_METHOD'] == selected_payment_method]

# Filter by order status
if selected_order_status != 'All':
    filtered_data['order_fact'] = filtered_data['order_fact'][filtered_data['order_fact']['ORDER_STATUS'] == selected_order_status]

# Get relevant order IDs (once)
order_ids = filtered_data['order_fact']['ORDER_ID'].values

# Filter order lines using the order IDs
filtered_data['order_line'] = filtered_data['order_line'][filtered_data['order_line']['ORDER_ID'].isin(order_ids)]

# Filter by product category
if selected_category != 'All':
    # Get product IDs for the selected category
    category_product_ids = filtered_data['product'][filtered_data['product']['CATEGORY'] == selected_category]['PRODUCT_ID'].values
    
    # Filter order lines by these product IDs
    filtered_data['order_line'] = filtered_data['order_line'][filtered_data['order_line']['PRODUCT_ID'].isin(category_product_ids)]
    
    # Filter products
    filtered_data['product'] = filtered_data['product'][filtered_data['product']['CATEGORY'] == selected_category]
    
    # Filter inventory
    filtered_data['inventory'] = filtered_data['inventory'][filtered_data['inventory']['PRODUCT_ID'].isin(category_product_ids)]

# Get relevant customer IDs
customer_ids = filtered_data['order_fact']['CUSTOMER_ID'].unique()

# Filter customer data
filtered_data['customer'] = filtered_data['customer'][filtered_data['customer']['CUSTOMER_ID'].isin(customer_ids)]

# Filter digital events by date
digital_date_mask = (filtered_data['digital_event']['EVENT_DATE'] >= start_date) & (filtered_data['digital_event']['EVENT_DATE'] <= end_date)
filtered_data['digital_event'] = filtered_data['digital_event'][digital_date_mask]

# Filter page performance by date
page_date_mask = (filtered_data['page_performance']['DATE'] >= start_date) & (filtered_data['page_performance']['DATE'] <= end_date)
filtered_data['page_performance'] = filtered_data['page_performance'][page_date_mask]

# Filter campaigns that overlap with the selected date range
campaign_mask = (filtered_data['campaign']['START_DATE'] <= end_date) & (filtered_data['campaign']['END_DATE'] >= start_date)
filtered_data['campaign'] = filtered_data['campaign'][campaign_mask]


# Helper function to create metric containers
def create_metric_container(title, value, color=PRIMARY_COLOR):
    """Create a styled metric container"""
    return f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value" style="color: {color}">{value}</div>
    </div>
    """

# Create tabs
tab_names = ["Sales Overview", "Sales vs Plan", "Product Analysis", "Customer Analysis", "Digital Analysis", "Inventory Analysis", "Campaign Analysis"]
tabs = st.tabs(tab_names)

# Track the active tab in session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Overview tab
with tabs[0]:
    # Calculate key metrics
    order_fact = filtered_data['order_fact']
    customer = filtered_data['customer']
    
    total_revenue = order_fact['TOTAL_AMOUNT'].sum()
    total_orders = len(order_fact)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Create key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_container("Total Customers", f"{len(customer):,.0f}"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container("Total Orders", f"{len(order_fact):,.0f}"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container("Total Revenue", f"${total_revenue:,.0f}"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container("Avg Order Value", f"${avg_order_value:,.2f}"), unsafe_allow_html=True)
    
    # Create time series with daily orders (using efficient groupby)
    daily_orders = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='D')).size().reset_index(name='NEW_ORDERS')
    
    # Plot daily orders
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=daily_orders['ORDER_DATE'],
        y=daily_orders['NEW_ORDERS'],
        name='Daily Orders',
        mode='lines+markers',
        marker=dict(color='#90CAF9', size=8),
        line=dict(color='#90CAF9', width=2),
        showlegend=False
    ))
    
    fig1.update_layout(
        title='Daily Order Count',
        xaxis_title='Date',
        yaxis_title='Number of Orders',
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Order status distribution
    # Calculate order status counts (using value_counts for efficiency)
    order_status_counts = order_fact['ORDER_STATUS'].value_counts().reset_index()
    order_status_counts.columns = ['ORDER_STATUS', 'COUNT']

    # Create bar chart
    fig2 = px.bar(
        order_status_counts,
        x='ORDER_STATUS', 
        y='COUNT',
        title='Order Status Distribution',
        color='ORDER_STATUS',
        color_discrete_map=STATUS_COLORS,
        labels={
            'ORDER_STATUS': 'Order Status',
            'COUNT': 'Number of Orders'
        }
    )

    # Customize appearance
    fig2.update_traces(
        texttemplate='%{y}',
        textposition='outside'
    )
    
    fig2.update_layout(
        xaxis_title='Order Status',
        yaxis_title='Number of Orders',
        showlegend=False,
        margin=dict(t=50)
    )

    # Display chart
    st.plotly_chart(fig2, use_container_width=True)
    
    # Revenue by order type and time trend (using efficient groupby)
    type_revenue_time = order_fact.groupby(['ORDER_TYPE', pd.Grouper(key='ORDER_DATE', freq='D')])['TOTAL_AMOUNT'].sum().reset_index()
    
    # Create an area chart for revenue trends
    # Calculate revenue by order type
    pivot_revenue = type_revenue_time.pivot_table(
        index='ORDER_DATE', 
        columns='ORDER_TYPE', 
        values='TOTAL_AMOUNT',
        aggfunc='sum'
    ).fillna(0).reset_index()
    
    # Melt the pivot table for plotting
    melted_revenue = pd.melt(
        pivot_revenue, 
        id_vars=['ORDER_DATE'], 
        var_name='ORDER_TYPE', 
        value_name='TOTAL_AMOUNT'
    )
    
    fig3b = px.area(
        melted_revenue,
        x='ORDER_DATE',
        y='TOTAL_AMOUNT',
        color='ORDER_TYPE',
        title='Daily Revenue Trends by Order Type',
        color_discrete_sequence=ACCENT_PALETTE,
        labels={
            'ORDER_DATE': 'Date',
            'TOTAL_AMOUNT': 'Revenue ($)',
            'ORDER_TYPE': 'Order Type'
        }
    )
    
    fig3b.update_layout(
        xaxis_title='',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        hoverlabel=dict(
            namelength=-1  # Show full label names
        )
    )
    
    # Customize hover template to show date once at the top
    fig3b.update_traces(
        hovertemplate=
        "%{data.name}: $%{y:,.2f}<extra></extra>"
    )
    
    st.plotly_chart(fig3b, use_container_width=True)
    
    # Update active tab
    st.session_state.active_tab = 0

# Sales Analysis tab
with tabs[1]:
    # Check if this tab is active
    if st.session_state.active_tab != 1:
        st.session_state.active_tab = 1
    
    # Create sales dashboard
    metrics = st.container()

    # Get filtered data
    order_fact = filtered_data['order_fact']
    sales_plan = data['sales_plan']  # Use original sales plan data
    
    # Calculate daily actual sales (using efficient groupby)
    daily_actual_sales = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='D')).agg({
        'TOTAL_AMOUNT': 'sum'
    }).reset_index()

    # Get date range for filtering
    sorted_dates = sorted(date_range)
    start_date = pd.Timestamp(sorted_dates[0])
    end_date = pd.Timestamp(sorted_dates[1])
    
    # Filter sales plan data by the selected date range
    filtered_sales_plan = sales_plan[
        ((sales_plan['PLAN_START_DATE'] <= end_date) & 
         (sales_plan['PLAN_END_DATE'] >= start_date))
    ]

    # Calculate daily planned sales more efficiently
    # Create a date range for the filtered period
    date_range_days = pd.date_range(start=start_date, end=end_date, freq='D')
    daily_plan = pd.DataFrame({'ORDER_DATE': date_range_days, 'PLANNED_AMOUNT': 0.0})
    
    # For each plan, distribute the target revenue across its days
    for _, row in filtered_sales_plan.iterrows():
        plan_start = max(row['PLAN_START_DATE'], start_date)
        plan_end = min(row['PLAN_END_DATE'], end_date)
        plan_days = (plan_end - plan_start).days + 1
        
        if plan_days > 0:
            daily_amount = row['TARGET_REVENUE'] / plan_days
            
            # Update the daily plan for days in this plan's range
            mask = (daily_plan['ORDER_DATE'] >= plan_start) & (daily_plan['ORDER_DATE'] <= plan_end)
            daily_plan.loc[mask, 'PLANNED_AMOUNT'] += daily_amount

    # Merge actual and planned sales
    daily_sales = pd.merge(
        daily_actual_sales,
        daily_plan,
        on='ORDER_DATE',
        how='outer'
    ).fillna(0)

    # Sort by date
    daily_sales = daily_sales.sort_values('ORDER_DATE')

    # Calculate achievement rate
    daily_sales['ACHIEVEMENT_RATE'] = (daily_sales['TOTAL_AMOUNT'] / daily_sales['PLANNED_AMOUNT'] * 100).fillna(0)

    # Create sales vs plan visualization
    sales_plan_fig = go.Figure()

    # Add colored background for each day (more efficiently)
    achievement_colors = np.where(
        daily_sales['TOTAL_AMOUNT'] >= daily_sales['PLANNED_AMOUNT'],
        'rgba(0, 255, 0, 0.1)',  # Green for achievement >= 100%
        'rgba(255, 0, 0, 0.1)'   # Red for achievement < 100%
    )
    
    for i in range(len(daily_sales)-1):
        sales_plan_fig.add_vrect(
            x0=daily_sales['ORDER_DATE'].iloc[i],
            x1=daily_sales['ORDER_DATE'].iloc[i+1],
            fillcolor=achievement_colors[i],
            layer='below',
            line_width=0,
        )
    
    # Add last day rectangle if there's data
    if len(daily_sales) > 0:
        sales_plan_fig.add_vrect(
            x0=daily_sales['ORDER_DATE'].iloc[-1],
            x1=daily_sales['ORDER_DATE'].iloc[-1] + pd.Timedelta(days=1),
            fillcolor=achievement_colors[-1],
            layer='below',
            line_width=0,
        )

    # Add actual sales line
    sales_plan_fig.add_trace(go.Scatter(
        x=daily_sales['ORDER_DATE'],
        y=daily_sales['TOTAL_AMOUNT'],
        name='Actual Sales',
        line=dict(color=PRIMARY_COLOR, width=2),
        mode='lines'
    ))

    # Add planned sales line
    sales_plan_fig.add_trace(go.Scatter(
        x=daily_sales['ORDER_DATE'],
        y=daily_sales['PLANNED_AMOUNT'],
        name='Planned Sales',
        line=dict(color=SECONDARY_COLOR, width=2, dash='dash'),
        mode='lines'
    ))

    # Update layout for daily view
    sales_plan_fig.update_layout(
        title='Sales Performance vs Plan',
        xaxis_title='Date',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Display the updated sales vs plan chart
    st.plotly_chart(sales_plan_fig, use_container_width=True)

    # Add KPI metrics for sales performance
    col1, col2, col3 = metrics.columns(3)

    total_actual = daily_sales['TOTAL_AMOUNT'].sum()
    total_planned = daily_sales['PLANNED_AMOUNT'].sum()
    overall_achievement = (total_actual / total_planned * 100) if total_planned > 0 else 0

    with col1:
        st.markdown(create_metric_container(
            "Total Actual Sales",
            f"${total_actual:,.2f}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(create_metric_container(
            "Total Planned Sales",
            f"${total_planned:,.2f}",
            SECONDARY_COLOR
        ), unsafe_allow_html=True)

    with col3:
        achievement_color = SUCCESS_COLOR if overall_achievement >= 100 else WARNING_COLOR if overall_achievement >= 80 else DANGER_COLOR
        st.markdown(create_metric_container(
            "Overall Achievement Rate",
            f"{overall_achievement:.1f}%",
            achievement_color
        ), unsafe_allow_html=True)

# Product Analysis tab
with tabs[2]:
    # Check if this tab is active
    if st.session_state.active_tab != 2:
        st.session_state.active_tab = 2
        
    st.markdown("## Product Analysis")

    # Get filtered data
    product = filtered_data['product']
    order_line = filtered_data['order_line']
    order_fact = filtered_data['order_fact']

    # Merge relevant tables efficiently
    product_sales = (order_line.merge(order_fact[['ORDER_ID', 'ORDER_DATE', 'ORDER_STATUS']], on='ORDER_ID')
                    .merge(product[['PRODUCT_ID', 'NAME', 'CATEGORY', 'BRAND', 'PRICE']], on='PRODUCT_ID'))
    
    # Calculate product metrics
    product_sales['REVENUE'] = product_sales['QUANTITY'] * product_sales['UNIT_PRICE']
    
    # Key metrics
    total_products = len(product)
    active_products = len(product[product['ACTIVE'] == True])
    total_categories = product['CATEGORY'].nunique()
    avg_price = product['PRICE'].mean()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Products",
            f"{total_products:,}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container(
            "Active Products",
            f"{active_products:,}",
            SUCCESS_COLOR
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container(
            "Categories",
            f"{total_categories:,}",
            SECONDARY_COLOR
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container(
            "Avg Price",
            f"${avg_price:.2f}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Category Distribution - use groupby for efficiency
        category_dist = product.groupby('CATEGORY').agg({
            'PRODUCT_ID': 'count',
            'ACTIVE': lambda x: (x == True).sum()
        }).reset_index()
        category_dist.columns = ['CATEGORY', 'TOTAL_PRODUCTS', 'ACTIVE_PRODUCTS']
        
        fig_category = go.Figure()
        fig_category.add_trace(go.Bar(
            name='Active',
            x=category_dist['CATEGORY'],
            y=category_dist['ACTIVE_PRODUCTS'],
            marker_color=SUCCESS_COLOR
        ))
        fig_category.add_trace(go.Bar(
            name='Inactive',
            x=category_dist['CATEGORY'],
            y=category_dist['TOTAL_PRODUCTS'] - category_dist['ACTIVE_PRODUCTS'],
            marker_color=DANGER_COLOR
        ))
        
        fig_category.update_layout(
            title='Products by Category',
            barmode='stack',
            xaxis_title='Category',
            yaxis_title='Number of Products',
            legend_title='Status'
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Price Distribution by Category
        fig_price = px.box(
            product,
            x='CATEGORY',
            y='PRICE',
            title='Price Distribution by Category',
            color='CATEGORY',
            color_discrete_sequence=BASE_PALETTE
        )
        fig_price.update_layout(
            xaxis_title='Category',
            yaxis_title='Price ($)',
            showlegend=False
        )
        st.plotly_chart(fig_price, use_container_width=True)
    
    # Top Products Analysis
    # Prepare data for sunburst chart by calculating sales - use groupby for efficiency
    product_sales_hierarchy = product_sales.groupby(['CATEGORY', 'BRAND', 'NAME'])['REVENUE'].sum().reset_index()
    
    # Create sunburst chart
    fig_sunburst = px.sunburst(
        product_sales_hierarchy,
        path=['CATEGORY', 'BRAND', 'NAME'], 
        values='REVENUE',
        title='Product Sales Distribution',
        #color_discrete_sequence=BASE_PALETTE
    )
    
    fig_sunburst.update_layout(
        width=800,
        height=800
    )
    
    fig_sunburst.update_traces(
        textinfo='label+value+percent parent',
        texttemplate='%{label}<br>$%{value:,.2f}<br>%{percentParent:.1%}'
    )
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    st.markdown("### Top Products Performance")

    # Calculate product performance metrics - use groupby for efficiency
    product_performance = product_sales.groupby(['PRODUCT_ID', 'NAME', 'CATEGORY', 'PRICE']).agg({
        'QUANTITY': 'sum',
        'REVENUE': 'sum',
        'ORDER_ID': 'nunique'
    }).reset_index()
    
    product_performance['AVG_ORDER_VALUE'] = product_performance['REVENUE'] / product_performance['ORDER_ID']
    
    # Sort by revenue and get top 10
    top_products = product_performance.nlargest(10, 'REVENUE')
    
    fig_top = px.bar(
        top_products,
        x='REVENUE',
        y='NAME',
        color='CATEGORY',
        title='Top 10 Products by Revenue',
        orientation='h',
        color_discrete_sequence=ACCENT_PALETTE,
        text='REVENUE'
    )
    
    fig_top.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )
    
    fig_top.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Revenue ($)',
        yaxis_title='',
            showlegend=True,
        legend_title='Category'
    )
    
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Product Performance Table
    st.markdown("### Detailed Product Performance")
    
    # Format the table data
    product_table = product_performance.copy()
    product_table['REVENUE'] = product_table['REVENUE'].apply(lambda x: f"${x:,.2f}")
    product_table['AVG_ORDER_VALUE'] = product_table['AVG_ORDER_VALUE'].apply(lambda x: f"${x:,.2f}")
    product_table['PRICE'] = product_table['PRICE'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(
        product_table.sort_values('REVENUE', ascending=False),
        column_config={
            'NAME': 'Product Name',
            'CATEGORY': 'Category',
            'PRICE': 'List Price',
            'QUANTITY': 'Units Sold',
            'REVENUE': 'Total Revenue',
            'ORDER_ID': 'Number of Orders',
            'AVG_ORDER_VALUE': 'Avg Order Value'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Brand Analysis
    st.markdown("### Brand Performance")
    
    # Use groupby for efficiency
    brand_performance = product_sales.groupby('BRAND').agg({
        'REVENUE': 'sum',
        'QUANTITY': 'sum',
        'ORDER_ID': 'nunique',
        'PRODUCT_ID': 'nunique'
    }).reset_index()
    
    brand_performance = brand_performance.sort_values('REVENUE', ascending=False)
    
    # Brand Revenue Share
    fig_brand = px.pie(
        brand_performance,
        values='REVENUE',
        names='BRAND',
        title='Revenue Share by Brand',
        color_discrete_sequence=ACCENT_PALETTE
    )
    fig_brand.update_traces(textposition='inside', textinfo='percent')
    st.plotly_chart(fig_brand, use_container_width=True)

# Customer Analysis tab
with tabs[3]:
    st.markdown("## Customer Analysis")

    # Merge customer data with orders
    customer_orders = order_fact.merge(customer, on='CUSTOMER_ID', how='left')
    
    # Calculate customer metrics
    customer_metrics = customer_orders.groupby('CUSTOMER_ID').agg({
        'ORDER_ID': 'count',
        'TOTAL_AMOUNT': 'sum',
        'ORDER_DATE': ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = ['CUSTOMER_ID', 'ORDER_COUNT', 'TOTAL_SPENT', 'FIRST_ORDER', 'LAST_ORDER']
    
    # Calculate days since last order and customer lifetime
    current_date = pd.Timestamp.now()
    customer_metrics['DAYS_SINCE_LAST_ORDER'] = (current_date - pd.to_datetime(customer_metrics['LAST_ORDER'])).dt.days
    customer_metrics['CUSTOMER_LIFETIME_DAYS'] = (pd.to_datetime(customer_metrics['LAST_ORDER']) - pd.to_datetime(customer_metrics['FIRST_ORDER'])).dt.days
    
    # Calculate average order value
    customer_metrics['AVG_ORDER_VALUE'] = customer_metrics['TOTAL_SPENT'] / customer_metrics['ORDER_COUNT']
    
    # Calculate RFM scores
    r_labels = range(4, 0, -1)
    f_labels = range(1, 5)
    
    # Calculate recency score (more recent = higher score)
    r_quartiles = pd.qcut(customer_metrics['DAYS_SINCE_LAST_ORDER'], q=4, labels=r_labels)
    
    # For frequency and monetary, handle cases with fewer unique values
    def get_quartile_labels(series, labels):
        """Create quartile labels handling cases with duplicate values and skewed data"""
        unique_values = series.unique()
        n_unique = len(unique_values)
        
        if n_unique == 1:
            # If only one unique value, return the lowest label for all
            return pd.Series(labels[0], index=series.index)
        elif n_unique < 4:
            # For very few unique values, create bins based on unique values
            bins = np.sort(unique_values)
            # Use as many labels as we have intervals (len(bins) - 1)
            return pd.cut(series, bins=bins, labels=labels[:len(bins)-1], include_lowest=True)
        else:
            try:
                # Try to create quartiles with unique bin edges
                percentiles = np.percentile(series.unique(), [0, 25, 50, 75, 100])
                # Remove duplicate bin edges if any
                percentiles = np.unique(percentiles)
                if len(percentiles) < 2:
                    # If we still can't create valid bins, return lowest label
                    return pd.Series(labels[0], index=series.index)
                # Adjust labels to match number of intervals
                n_intervals = len(percentiles) - 1
                return pd.cut(series, bins=percentiles, labels=labels[:n_intervals], include_lowest=True)
            except Exception:
                # Fallback: assign lowest label if all else fails
                return pd.Series(labels[0], index=series.index)
    
    # Calculate frequency and monetary scores
    f_quartiles = get_quartile_labels(customer_metrics['ORDER_COUNT'], f_labels)
    m_quartiles = get_quartile_labels(customer_metrics['TOTAL_SPENT'], f_labels)
    
    # Assign scores
    customer_metrics['R'] = r_quartiles
    customer_metrics['F'] = f_quartiles
    customer_metrics['M'] = m_quartiles
    
    # Fill any NaN values with the lowest score (1)
    customer_metrics[['R', 'F', 'M']] = customer_metrics[['R', 'F', 'M']].fillna(1)
    
    # Calculate RFM Score and Segment
    customer_metrics['RFM_SCORE'] = customer_metrics['R'].astype(str) + customer_metrics['F'].astype(str) + customer_metrics['M'].astype(str)
    
    def get_segment(rfm_score):
        score = int(rfm_score[0]) + int(rfm_score[1]) + int(rfm_score[2])
        if score >= 11:
            return 'Champions'
        elif score >= 9:
            return 'Loyal Customers'
        elif score >= 7:
            return 'Potential Loyalists'
        elif score >= 5:
            return 'At Risk'
        else:
            return 'Lost Customers'
    
    customer_metrics['SEGMENT'] = customer_metrics['RFM_SCORE'].apply(get_segment)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns([0.24, 0.24, 0.28, 0.24])
    
    with col1:
        st.markdown(create_metric_container(
            "Total Customers",
            f"{len(customer_metrics):,}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_container(
            "Avg Customer Value",
            f"${customer_metrics['TOTAL_SPENT'].mean():,.2f}",
            SUCCESS_COLOR
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_container(
            "Avg Orders per Customer",
            f"{customer_metrics['ORDER_COUNT'].mean():.1f}",
            SECONDARY_COLOR
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_container(
            "Avg Order Value",
            f"${customer_metrics['AVG_ORDER_VALUE'].mean():,.2f}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    
    # Customer Segmentation Analysis
    st.markdown("### Customer Segmentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment Distribution
        segment_dist = customer_metrics['SEGMENT'].value_counts().reset_index()
        segment_dist.columns = ['Segment', 'Count']
        segment_dist['Percentage'] = (segment_dist['Count'] / len(customer_metrics) * 100).round(1)
        
        fig_segment = px.bar(
        segment_dist,
            x='Segment',
            y='Count',
            text='Percentage',
            title='Customer Segment Distribution',
            color='Segment',
            color_discrete_sequence=BASE_PALETTE
        )
        
        fig_segment.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
        fig_segment.update_layout(
            xaxis_title='',
            yaxis_title='Number of Customers',
            showlegend=False
        )
        
        st.plotly_chart(fig_segment, use_container_width=True)
    
    with col2:
        # Average metrics by segment
        segment_metrics = customer_metrics.groupby('SEGMENT').agg({
            'TOTAL_SPENT': 'mean',
            'ORDER_COUNT': 'mean',
            'AVG_ORDER_VALUE': 'mean'
    }).reset_index()
    
        fig_metrics = go.Figure()
        
        # Add bars for each metric
        fig_metrics.add_trace(go.Bar(
            name='Avg Total Spent',
            x=segment_metrics['SEGMENT'],
            y=segment_metrics['TOTAL_SPENT'],
            marker_color=PRIMARY_COLOR
        ))
        
        fig_metrics.add_trace(go.Bar(
            name='Avg Order Value',
            x=segment_metrics['SEGMENT'],
            y=segment_metrics['AVG_ORDER_VALUE'],
            marker_color=SECONDARY_COLOR
        ))
        
        fig_metrics.update_layout(
            title='Average Customer Metrics by Segment',
            barmode='group',
            yaxis_title='Amount ($)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_metrics, use_container_width=True)
    

    # Order Frequency Distribution
    fig_frequency = px.histogram(
        customer_metrics,
        x='ORDER_COUNT',
        title='Order Frequency Distribution',
        color_discrete_sequence=[PRIMARY_COLOR],
        labels={'ORDER_COUNT': 'Number of Orders'},
        text_auto=True  # Add count numbers on bars
    )
    
    fig_frequency.update_layout(
        xaxis_title='Number of Orders',
        yaxis_title='Number of Customers',
        showlegend=False,
        bargap=0.1
    )
    
    fig_frequency.update_traces(
        textposition='outside'  # Place numbers above bars
    )
    
    st.plotly_chart(fig_frequency, use_container_width=True)

    
    
    # Top Customers Table
    st.markdown("### Top Customers")
    
    top_customers = customer_metrics.nlargest(10, 'TOTAL_SPENT')
    top_customers = top_customers.merge(customer[['CUSTOMER_ID', 'NAME', 'PRIMARY_EMAIL']], on='CUSTOMER_ID')
    
    st.dataframe(
        top_customers[[
            'NAME', 'PRIMARY_EMAIL', 'TOTAL_SPENT', 'ORDER_COUNT',
            'AVG_ORDER_VALUE', 'SEGMENT', 'LAST_ORDER'
        ]],
        column_config={
            'NAME': 'Customer Name',
            'PRIMARY_EMAIL': 'Email',
            'TOTAL_SPENT': st.column_config.NumberColumn('Total Spent', format="$%.2f"),
            'ORDER_COUNT': 'Number of Orders',
            'AVG_ORDER_VALUE': st.column_config.NumberColumn('Avg Order Value', format="$%.2f"),
            'SEGMENT': 'Segment',
            'LAST_ORDER': 'Last Order Date'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Customer Type Analysis
    if 'CUSTOMER_TYPE' in customer.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer Type Distribution
            type_dist = customer_metrics.merge(
                customer[['CUSTOMER_ID', 'CUSTOMER_TYPE']], 
                on='CUSTOMER_ID'
            )['CUSTOMER_TYPE'].value_counts().reset_index()
            type_dist.columns = ['Type', 'Count']
            
            fig_type = px.pie(
                type_dist,
                values='Count',
                names='Type',
                title='Customer Type Distribution',
                color_discrete_map=BASE_PALETTE
            )
            
            st.plotly_chart(fig_type, use_container_width=True)
        
        with col2:
            # Average metrics by customer type
            type_metrics = customer_metrics.merge(
                customer[['CUSTOMER_ID', 'CUSTOMER_TYPE']], 
                on='CUSTOMER_ID'
            ).groupby('CUSTOMER_TYPE').agg({
                'TOTAL_SPENT': 'mean',
                'ORDER_COUNT': 'mean',
                'AVG_ORDER_VALUE': 'mean'
            }).reset_index()
            
            fig_type_metrics = go.Figure()
            
            fig_type_metrics.add_trace(go.Bar(
                name='Avg Total Spent',
                x=type_metrics['CUSTOMER_TYPE'],
                y=type_metrics['TOTAL_SPENT'],
                marker_color=PRIMARY_COLOR
            ))
            
            fig_type_metrics.add_trace(go.Bar(
                name='Avg Order Value',
                x=type_metrics['CUSTOMER_TYPE'],
                y=type_metrics['AVG_ORDER_VALUE'],
                marker_color=SECONDARY_COLOR
            ))
            
            fig_type_metrics.update_layout(
                title='Average Metrics by Customer Type',
                barmode='group',
                yaxis_title='Amount ($)',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_type_metrics, use_container_width=True)

# Digital Analysis tab
with tabs[4]:
    st.markdown("## Digital Analysis")
    
    # Calculate key metrics
    total_events = len(filtered_data['digital_event'])
    total_visitors = filtered_data['page_performance']['UNIQUE_VISITORS'].sum()
    avg_conversion = filtered_data['page_performance']['CONVERSION_RATE'].mean() * 100
    avg_bounce = filtered_data['page_performance']['BOUNCE_RATE'].mean() * 100
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Events",
            f"{total_events:,}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container(
            "Total Visitors",
            f"{total_visitors:,}",
            SUCCESS_COLOR
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container(
            "Avg Conversion Rate",
            f"{avg_conversion:.1f}%",
            SECONDARY_COLOR
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container(
            "Avg Bounce Rate",
            f"{avg_bounce:.1f}%",
            WARNING_COLOR if avg_bounce > 50 else SUCCESS_COLOR
        ), unsafe_allow_html=True)
    
    # Event Analysis Section
    st.markdown("### Event Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Event Type Distribution
        event_counts = filtered_data['digital_event']['EVENT_TYPE'].value_counts().reset_index()
        event_counts.columns = ['EVENT_TYPE', 'COUNT']
        
        fig_events = px.bar(
            event_counts,
            x='EVENT_TYPE',
            y='COUNT',
            title='Digital Event Distribution',
            color='EVENT_TYPE',
            color_discrete_map=EVENT_COLORS,
            text='COUNT'
        )
        
        fig_events.update_traces(
            texttemplate='%{text:,}',
            textposition='outside'
        )
        
        fig_events.update_layout(
            xaxis_title='Event Type',
            yaxis_title='Number of Events',
            showlegend=False
        )
        
        st.plotly_chart(fig_events, use_container_width=True)
    
    with col2:
        # Device Type Distribution
        device_counts = filtered_data['digital_event']['DEVICE_TYPE'].value_counts().reset_index()
        device_counts.columns = ['DEVICE_TYPE', 'COUNT']
        device_counts['PERCENTAGE'] = (device_counts['COUNT'] / device_counts['COUNT'].sum() * 100).round(1)
        
        fig_devices = px.pie(
            device_counts,
            values='COUNT',
            names='DEVICE_TYPE',
            title='Device Type Distribution',
            color='DEVICE_TYPE',
            color_discrete_map=DEVICE_COLORS,
            hover_data=['PERCENTAGE']
        )
        
        fig_devices.update_traces(
            textinfo='percent+label',
            textposition='inside'
        )
        
        st.plotly_chart(fig_devices, use_container_width=True)
    
    # Traffic Analysis Section
    st.markdown("### Traffic Analysis")
    
    # Prepare monthly data
    filtered_data['page_performance']['DATE'] = pd.to_datetime(filtered_data['page_performance']['DATE'])
    monthly_traffic = filtered_data['page_performance'].groupby(pd.Grouper(key='DATE', freq='M')).agg({
        'VIEWS': 'sum',
        'UNIQUE_VISITORS': 'sum',
        'BOUNCE_RATE': 'mean',
        'CONVERSION_RATE': 'mean'
    }).reset_index()
    
    # Traffic Trends
    fig_traffic = go.Figure()
    
    fig_traffic.add_trace(go.Scatter(
        x=monthly_traffic['DATE'],
        y=monthly_traffic['VIEWS'],
        name='Total Views',
        mode='lines+markers',
        line=dict(color=PRIMARY_COLOR, width=2)
    ))
    
    fig_traffic.add_trace(go.Scatter(
        x=monthly_traffic['DATE'],
        y=monthly_traffic['UNIQUE_VISITORS'],
        name='Unique Visitors',
        mode='lines+markers',
        line=dict(color=SECONDARY_COLOR, width=2)
    ))
    
    fig_traffic.update_layout(
        title='Monthly Website Traffic',
        xaxis_title='Month',
        yaxis_title='Count',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_traffic, use_container_width=True)
    
    # Conversion and Bounce Rate Trends
    fig_rates = go.Figure()
    
    fig_rates.add_trace(go.Scatter(
        x=monthly_traffic['DATE'],
        y=monthly_traffic['CONVERSION_RATE'] * 100,
        name='Conversion Rate',
        mode='lines+markers',
        line=dict(color=SUCCESS_COLOR, width=2)
    ))
    
    fig_rates.add_trace(go.Scatter(
        x=monthly_traffic['DATE'],
        y=monthly_traffic['BOUNCE_RATE'] * 100,
        name='Bounce Rate',
        mode='lines+markers',
        line=dict(color=DANGER_COLOR, width=2)
    ))
    
    fig_rates.update_layout(
        title='Conversion and Bounce Rate Trends',
        xaxis_title='Month',
        yaxis_title='Rate (%)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_rates, use_container_width=True)

    funnel_events = ['PAGE_VIEW', 'PRODUCT_VIEW', 'ADD_TO_CART', 'CHECKOUT_START', 'CHECKOUT_COMPLETE']
    funnel_counts = filtered_data['digital_event'][filtered_data['digital_event']['EVENT_TYPE'].isin(funnel_events)]['EVENT_TYPE'].value_counts()
    funnel_data = pd.DataFrame({
        'EVENT_TYPE': funnel_events,
        'COUNT': [funnel_counts.get(event, 0) for event in funnel_events]
    })
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_data['EVENT_TYPE'],
        x=funnel_data['COUNT'],
        textinfo="value+percent initial"
    ))
    
    fig_funnel.update_layout(
        title='Customer Journey Funnel',
        showlegend=False
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)

# Inventory Analysis tab
with tabs[5]:
    # Check if this tab is active
    if st.session_state.active_tab != 5:
        st.session_state.active_tab = 5
        
    st.markdown("## Inventory Analysis")

    # Get filtered data
    inventory = filtered_data['inventory']
    product = filtered_data['product']
    facility = filtered_data['facility']
    
    # Check if product_variant is available in the filtered data
    has_product_variants = 'product_variant' in filtered_data
    
    # Calculate key metrics
    total_inventory = inventory['QUANTITY'].sum()
    total_products_in_stock = inventory['PRODUCT_ID'].nunique()
    avg_quantity_per_product = total_inventory / total_products_in_stock if total_products_in_stock > 0 else 0
    total_facilities = inventory['FACILITY_ID'].nunique()

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Inventory",
            f"{total_inventory:,}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container(
            "Products in Stock",
            f"{total_products_in_stock:,}",
            SUCCESS_COLOR
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container(
            "Avg Quantity/Product",
            f"{avg_quantity_per_product:.1f}",
            SECONDARY_COLOR
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container(
            "Total Facilities",
            f"{total_facilities:,}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)

    # Merge inventory with product data for analysis
    # Use the filtered product data based on category selection
    inventory_analysis = inventory.merge(
        product[['PRODUCT_ID', 'NAME', 'CATEGORY', 'BRAND']], 
        on='PRODUCT_ID'
    ).merge(
        facility[['FACILITY_ID', 'FACILITY_NAME', 'FACILITY_TYPE']], 
        on='FACILITY_ID'
    )

    # Inventory by Category Analysis
    st.markdown("### Inventory by Category")

        # Category Distribution
    category_inventory = inventory_analysis.groupby('CATEGORY').agg({
        'QUANTITY': 'sum',
        'PRODUCT_ID': 'nunique'
    }).reset_index()

    # Products per Category
    fig_products = px.bar(
        category_inventory,
        x='CATEGORY',
        y='PRODUCT_ID',
        title='Number of Products by Category',
        color='CATEGORY',
        #color_discrete_sequence=BASE_PALETTE,
        labels={'PRODUCT_ID': 'Number of Products'}
    )

    fig_products.update_layout(
        showlegend=False,
        xaxis_title='Category',
        yaxis_title='Number of Products'
    )

    st.plotly_chart(fig_products, use_container_width=True)
    # Inventory Status Analysis
    st.markdown("### Inventory Status Analysis")
    def get_inventory_status(quantity):
        if quantity <= 10:
            return ("Critical Low", "#FF4B4B")  # Soft red
        elif quantity <= 50:
            return ("Low", "#FFA07A")  # Light salmon
        elif quantity <= 200:
            return ("Medium", "#FFD700")  # Gold
        return ("High", "#32CD32")  # Darker lime green

    # Add status and color to inventory analysis
    inventory_analysis[['STATUS', 'STATUS_COLOR']] = pd.DataFrame(inventory_analysis['QUANTITY'].apply(get_inventory_status).tolist(), index=inventory_analysis.index)

    # Create inventory status visualization
    col1, col2 = st.columns(2)

    with col1:
        # Status Distribution
        status_counts = inventory_analysis.groupby(['STATUS', 'STATUS_COLOR']).size().reset_index(name='COUNT')
        
        fig_status = px.pie(
            status_counts,
            values='COUNT', 
            names='STATUS',
            title='Inventory Status Distribution',
            color='STATUS',
            color_discrete_map=dict(zip(status_counts['STATUS'], status_counts['STATUS_COLOR']))
        )

        fig_status.update_traces(
            textposition='inside',
            textinfo='percent'
        )

        st.plotly_chart(fig_status, use_container_width=True)
    with col2:
        # Status by Category
        status_category = inventory_analysis.groupby(['CATEGORY', 'STATUS', 'STATUS_COLOR']).size().reset_index(name='COUNT')
        
        # Create custom category order
        status_order = ['High', 'Medium', 'Low', 'Critical Low']
        
        fig_status_category = px.bar(
            status_category,
            x='CATEGORY',
            y='COUNT', 
            color='STATUS',
            title='Inventory Status by Category',
            color_discrete_map=dict(zip(status_category['STATUS'], status_category['STATUS_COLOR'])),
            barmode='stack',
            category_orders={'STATUS': status_order}
        )

        st.plotly_chart(fig_status_category, use_container_width=True)

    # Critical Inventory Alerts
    st.markdown("### Critical Inventory Alerts")
    
    # Group by product to get total quantity across all facilities
    product_inventory = inventory_analysis.groupby(['PRODUCT_ID', 'NAME', 'CATEGORY']).agg({
        'QUANTITY': 'sum'
    }).reset_index()
    
    # Apply status to aggregated product quantities
    product_inventory['STATUS'] = product_inventory['QUANTITY'].apply(get_inventory_status)
    
    # Get products with critically low inventory
    critical_products = product_inventory[product_inventory['STATUS'] == 'Critical Low'].sort_values('QUANTITY')
    
    # For the detailed view, get all inventory records for these critical products
    critical_inventory = inventory_analysis[
        inventory_analysis['PRODUCT_ID'].isin(critical_products['PRODUCT_ID'])
    ].sort_values(['PRODUCT_ID', 'QUANTITY'])

    # Display critical inventory alerts
    if len(critical_products) > 0:
        st.warning(f"⚠️ {len(critical_products)} products have critically low inventory (10 or fewer units total)")
        
        # Show aggregated product view first
        st.subheader("Critical Products (Aggregated)")
        st.dataframe(
            critical_products[['NAME', 'CATEGORY', 'QUANTITY']],
            column_config={
                'NAME': 'Product Name',
                'CATEGORY': 'Category',
                'QUANTITY': 'Total Quantity'
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Show detailed inventory by facility
        st.subheader("Critical Inventory by Facility")
        st.dataframe(
            critical_inventory[['NAME', 'CATEGORY', 'QUANTITY', 'FACILITY_NAME']],
            column_config={
                'NAME': 'Product Name',
                'CATEGORY': 'Category',
                'QUANTITY': 'Quantity',
                'FACILITY_NAME': 'Facility'
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✅ No products have critically low inventory")

    # Inventory Distribution Analysis
    st.markdown("### Inventory Distribution")

    # Create box plot of quantity distribution by category
    fig_distribution = px.box(
        inventory_analysis,
        x='CATEGORY',
        y='QUANTITY',
        title='Inventory Quantity Distribution by Category',
        color='CATEGORY',
        color_discrete_sequence=BASE_PALETTE
    )

    fig_distribution.update_layout(
        showlegend=False,
        xaxis_title='Category',
        yaxis_title='Quantity'
    )

    st.plotly_chart(fig_distribution, use_container_width=True)

# Campaign Analysis tab
with tabs[6]:
    # Check if this tab is active
    if st.session_state.active_tab != 6:
        st.session_state.active_tab = 6
        
    st.markdown("## Campaign Analysis")

    # Get filtered data
    campaign = data['campaign']
    order_fact = data['order_fact']
    order_campaign_attribution = data['order_campaign_attribution']

    # Merge campaign data with attribution and order data
    campaign_performance = (order_campaign_attribution.merge(
        campaign[['CAMPAIGN_ID', 'CAMPAIGN_NAME', 'CAMPAIGN_TYPE', 'OBJECTIVE', 'BUDGET', 'TARGET_SEGMENT', 'START_DATE', 'END_DATE']], 
        on='CAMPAIGN_ID'
    ).merge(
        order_fact[['ORDER_ID', 'TOTAL_AMOUNT']], 
        on='ORDER_ID'
    ))
    
    # Calculate attributed revenue
    campaign_performance['ATTRIBUTED_REVENUE'] = campaign_performance['TOTAL_AMOUNT'] * campaign_performance['CONTRIBUTION_PERCENT']

    # Calculate key metrics
    total_campaigns = len(campaign)
    active_campaigns = len(campaign[campaign['END_DATE'] >= pd.Timestamp.now()])
    total_budget = campaign['BUDGET'].sum()
    avg_campaign_budget = total_budget / total_campaigns if total_campaigns > 0 else 0

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Campaigns",
            f"{total_campaigns:,}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container(
            "Active Campaigns",
            f"{active_campaigns:,}",
            SUCCESS_COLOR
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container(
            "Total Budget",
            f"${total_budget:,.2f}",
            SECONDARY_COLOR
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container(
            "Avg Campaign Budget",
            f"${avg_campaign_budget:,.2f}",
            PRIMARY_COLOR
        ), unsafe_allow_html=True)

    # Campaign Type Analysis
    st.markdown("### Campaign Performance by Type")
    
    # Calculate performance metrics by campaign type
    type_performance = campaign.groupby('CAMPAIGN_TYPE').agg({
        'CAMPAIGN_ID': 'count',
        'BUDGET': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Budget by Campaign Type
        # Create a color map to ensure consistent colors across both charts
        campaign_types = type_performance['CAMPAIGN_TYPE'].unique()
        # Use a different color palette from plotly express
        custom_colors = px.colors.qualitative.Dark2[:len(campaign_types)]
        color_map = dict(zip(campaign_types, custom_colors))

        # Budget by Campaign Type
        fig_budget = px.pie(
            type_performance,
            values='BUDGET', 
            names='CAMPAIGN_TYPE',
            title='Budget Distribution by Campaign Type',
            color='CAMPAIGN_TYPE',
            color_discrete_map=color_map
        )
        
        fig_budget.update_traces(
            textposition='inside',
            textinfo='percent'
        )
        
        st.plotly_chart(fig_budget, use_container_width=True)
    
    with col2:
        # Campaign Count by Type
        fig_count = px.bar(
            type_performance,
            x='CAMPAIGN_TYPE',
            y='CAMPAIGN_ID',
            title='Number of Campaigns by Type',
            color='CAMPAIGN_TYPE',
            labels={'CAMPAIGN_ID': 'Number of Campaigns'},
            color_discrete_map=color_map
        )
        
        fig_count.update_layout(
            xaxis_title='Campaign Type',
            yaxis_title='Number of Campaigns',
            showlegend=False
        )
        
        st.plotly_chart(fig_count, use_container_width=True)

    # Campaign Objectives Analysis
    st.markdown("### Campaign Objectives")
    
    objective_counts = campaign.groupby('OBJECTIVE').agg({
        'CAMPAIGN_ID': 'count',
        'BUDGET': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create a color map to ensure consistent colors across both charts
        objectives = objective_counts['OBJECTIVE'].unique()
        custom_colors = px.colors.qualitative.Dark2[:len(objectives)]
        color_map = dict(zip(objectives, custom_colors))

        # Number of Campaigns by Objective
        fig_objectives = px.bar(
            objective_counts,
            x='OBJECTIVE',
            y='CAMPAIGN_ID',
            title='Number of Campaigns by Objective',
            color='OBJECTIVE',
            labels={'CAMPAIGN_ID': 'Number of Campaigns'},
            color_discrete_map=color_map
        )
        
        fig_objectives.update_layout(
            xaxis_title='Objective',
            yaxis_title='Number of Campaigns',
            showlegend=False,
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig_objectives, use_container_width=True)
    
    with col2:
        # Budget by Target Segment
        fig_objective_budget = px.pie(
            objective_counts,
            values='BUDGET',
            names='OBJECTIVE',
            title='Budget Allocation by Objective',
            color='OBJECTIVE',
            color_discrete_map=color_map
        )
        
        fig_objective_budget.update_traces(
            textposition='inside',
            textinfo='percent'
        )
        
        st.plotly_chart(fig_objective_budget, use_container_width=True)

    # Target Segment Analysis
    st.markdown("### Target Segment Analysis")
    
    segment_analysis = campaign.groupby('TARGET_SEGMENT').agg({
        'CAMPAIGN_ID': 'count',
        'BUDGET': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create a color map to ensure consistent colors across both charts
        segments = segment_analysis['TARGET_SEGMENT'].unique()
        custom_colors = px.colors.qualitative.Dark2[:len(segments)]
        color_map = dict(zip(segments, custom_colors))

        # Campaigns by Target Segment
        fig_segments = px.bar(
            segment_analysis,
            x='TARGET_SEGMENT',
            y='CAMPAIGN_ID',
            title='Number of Campaigns by Target Segment',
            color='TARGET_SEGMENT',
            labels={'CAMPAIGN_ID': 'Number of Campaigns'},
            color_discrete_map=color_map
        )
        
        fig_segments.update_layout(
            xaxis_title='Target Segment',
            yaxis_title='Number of Campaigns',
            showlegend=False,
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col2:
        # Budget by Target Segment
        fig_segment_budget = px.pie(
            segment_analysis,
            values='BUDGET',
            names='TARGET_SEGMENT',
            title='Budget Allocation by Target Segment',
            color='TARGET_SEGMENT',
            color_discrete_map=color_map
        )
        
        fig_segment_budget.update_traces(
            textposition='inside',
            textinfo='percent'
        )
        
        st.plotly_chart(fig_segment_budget, use_container_width=True)

    # Campaign Attribution Analysis
    if len(campaign_performance) > 0:
        
        # Calculate attribution metrics
        attribution_metrics = campaign_performance.groupby(
            ['CAMPAIGN_ID', 'CAMPAIGN_NAME', 'CAMPAIGN_TYPE']
        ).agg({
            'ATTRIBUTED_REVENUE': 'sum',
            'ORDER_ID': 'nunique',
            'CONTRIBUTION_PERCENT': 'mean'
        }).reset_index()
        
        # Sort by attributed revenue
        top_attribution = attribution_metrics.nlargest(10, 'ATTRIBUTED_REVENUE')
        
        fig_attribution = px.bar(
            top_attribution,
            x='CAMPAIGN_NAME',
            y='ATTRIBUTED_REVENUE',
            color='CAMPAIGN_TYPE',
            title='Top 10 Campaigns by Attributed Revenue',
            text=top_attribution['ATTRIBUTED_REVENUE'].apply(lambda x: f'${x:,.2f}'),
            color_discrete_map=color_map
        )
        
        fig_attribution.update_layout(
            xaxis_title='Campaign Name',
            yaxis_title='Attributed Revenue ($)',
            xaxis={'tickangle': 45},
            showlegend=True
        )
        
        st.plotly_chart(fig_attribution, use_container_width=True)