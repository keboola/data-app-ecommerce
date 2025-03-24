import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from keboola_streamlit import KeboolaStreamlit

st.set_page_config(page_title="E-commerce Report", layout="wide")
keboola = KeboolaStreamlit(st.secrets["kbc_url"], st.secrets["kbc_token"])

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

# Segment colors (meaningful progression)
SEGMENT_COLORS = {
    "Champions": '#1E88E5',
    "Loyal Customers": '#90CAF9',
    "Potential Loyalists": '#BBDEFB',
    "Need Attention": '#F44336'
}

# Order status colors (meaningful states)
STATUS_COLORS = {
    'Delivered': '#38a5a4',
    'Shipped': '#1e6996',
    'Processing': '#edad07',
    'Completed': '#73af48',
    'Cancelled': '#cc503e',
    'Refunded': '#e27c03'
}

st.markdown("""
<style>
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

# Load all data files
campaign = pd.read_csv("/data/in/tables/CAMPAIGN.csv")
campaign_event = pd.read_csv("/data/in/tables/CAMPAIGN_EVENT.csv")

channel = pd.read_csv("/data/in/tables/CHANNEL.csv")

content_page = pd.read_csv("/data/in/tables/CONTENT_PAGE.csv")
custom_attribute = pd.read_csv("/data/in/tables/CUSTOM_ATTRIBUTE.csv")
customer = pd.read_csv("/data/in/tables/CUSTOMER.csv")
digital_event = pd.read_csv("/data/in/tables/DIGITAL_EVENT.csv")
digital_site = pd.read_csv("/data/in/tables/DIGITAL_SITE.csv")

facility = pd.read_csv("/data/in/tables/FACILITY.csv")
inventory = pd.read_csv("/data/in/tables/INVENTORY.csv")

## ORDERS, SALES
order_campaign_attribution = pd.read_csv("/data/in/tables/ORDER_CAMPAIGN_ATTRIBUTION.csv")
order_event = pd.read_csv("/data/in/tables/ORDER_EVENT.csv")
order_fact = pd.read_csv("/data/in/tables/ORDER_FACT.csv")
order_fulfillment = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT.csv")
order_fulfillment_line = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT_LINE.csv")
order_line = pd.read_csv("/data/in/tables/ORDER_LINE.csv")
order_status_history = pd.read_csv("/data/in/tables/ORDER_STATUS_HISTORY.csv")

page_performance = pd.read_csv("/data/in/tables/PAGE_PERFORMANCE.csv")

product = pd.read_csv("/data/in/tables/PRODUCT.csv")
product_variant = pd.read_csv("/data/in/tables/PRODUCT_VARIANT.csv")

sales_plan = pd.read_csv("/data/in/tables/SALES_PLAN.csv")

############### NOT USING ###############
company = pd.read_csv("/data/in/tables/COMPANY.csv") 
person = pd.read_csv("/data/in/tables/PERSON.csv") 
############### NOT USING ###############


# Create sidebar filters

with st.sidebar:
    st.subheader("Filters")

    # Add date filter options
    date_filter_option = st.selectbox(
        "Date Filter Type",
        options=["Current Year", "Year to Date", "Custom"],
        index=0
    )

    # Date range filter
    min_date = order_fact['ORDER_DATE'].min()
    today = pd.Timestamp.today()
    
    current_year_start = pd.Timestamp(today.year, 1, 1)
    year_ago = today - pd.DateOffset(years=1)
    
    # Current year from Jan 1st to today
    if date_filter_option == "Current Year":
        date_range = (current_year_start.date(), today.date())
    # Last 365 days
    elif date_filter_option == "Year to Date":
        date_range = (year_ago.date(), today.date())
    # Custom Range
    else:
        date_range = st.date_input(
            "Custom",
            value=(min_date, today.date()),
            min_value=min_date,
            max_value=today.date()
        )
      
    # Product Category
    categories = ['All'] + sorted(product['CATEGORY'].unique().tolist())
    selected_category = st.selectbox('Product Category', categories)

    # Sales Channel
    channels = ['All'] + sorted(channel['CHANNEL_NAME'].unique().tolist())
    selected_channel = st.selectbox('Sales Channel', channels)
    
    # Payment Method
    payment_methods = ['All'] + sorted(order_fact['PAYMENT_METHOD'].unique().tolist())
    selected_payment_method = st.selectbox('Payment Method', payment_methods)
    
    # Order Status
    order_statuses = ['All'] + sorted(order_fact['ORDER_STATUS'].unique().tolist())
    selected_order_status = st.selectbox('Order Status', order_statuses)
        
# Sort dates to ensure start_date is before end_date
sorted_dates = sorted(date_range)
start_date = pd.Timestamp(sorted_dates[0])
end_date = pd.Timestamp(sorted_dates[1])

# Filter orders by date range (using vectorized operations)
order_fact['ORDER_DATE'] = pd.to_datetime(order_fact['ORDER_DATE'])
date_mask = (order_fact['ORDER_DATE'] >= start_date) & (order_fact['ORDER_DATE'] <= end_date)
order_fact = order_fact[date_mask]

# Convert sales plan dates to datetime
sales_plan['PLAN_START_DATE'] = pd.to_datetime(sales_plan['PLAN_START_DATE'])
sales_plan['PLAN_END_DATE'] = pd.to_datetime(sales_plan['PLAN_END_DATE'])

sales_plan = sales_plan[
    ((sales_plan['PLAN_START_DATE'] <= end_date) & 
        (sales_plan['PLAN_END_DATE'] >= start_date))
]

# Filter by channel
if selected_channel != 'All':
    channel_ids = channel[channel['CHANNEL_NAME'] == selected_channel]['CHANNEL_ID'].values
    order_fact = order_fact[order_fact['CHANNEL_ID'].isin(channel_ids)]

# Filter by payment method
if selected_payment_method != 'All':
    order_fact = order_fact[order_fact['PAYMENT_METHOD'] == selected_payment_method]

# Filter by order status
if selected_order_status != 'All':
    order_fact = order_fact[order_fact['ORDER_STATUS'] == selected_order_status]

# Get relevant order IDs (once)
order_ids = order_fact['ORDER_ID'].values

# Filter order lines using the order IDs
order_line = order_line[order_line['ORDER_ID'].isin(order_ids)]

# Filter by product category
if selected_category != 'All':
    # Get product IDs for the selected category
    category_product_ids = product[product['CATEGORY'] == selected_category]['PRODUCT_ID'].values
    
    # Filter order lines by these product IDs
    order_line = order_line[order_line['PRODUCT_ID'].isin(category_product_ids)]
    
    # Filter products
    product = product[product['CATEGORY'] == selected_category]
    
    # Filter inventory
    inventory = inventory[inventory['PRODUCT_ID'].isin(category_product_ids)]
# Get relevant customer IDs
customer_ids = order_fact['CUSTOMER_ID'].unique()

# Filter customer data
customer = customer[customer['CUSTOMER_ID'].isin(customer_ids)]

# Filter digital events by date
digital_event['EVENT_DATE'] = pd.to_datetime(digital_event['EVENT_DATE'])
digital_date_mask = (digital_event['EVENT_DATE'] >= start_date) & (digital_event['EVENT_DATE'] <= end_date)
digital_event = digital_event[digital_date_mask]

# Filter page performance by date
page_performance['DATE'] = pd.to_datetime(page_performance['DATE'])
page_date_mask = (page_performance['DATE'] >= start_date) & (page_performance['DATE'] <= end_date)
page_performance = page_performance[page_date_mask]

# Filter campaigns that overlap with the selected date range
campaign['START_DATE'] = pd.to_datetime(campaign['START_DATE'])
campaign['END_DATE'] = pd.to_datetime(campaign['END_DATE'])
campaign_mask = (campaign['START_DATE'] <= end_date) & (campaign['END_DATE'] >= start_date)
campaign = campaign[campaign_mask]


# Helper function to create metric containers
def create_metric_container(title, value, color=PRIMARY_COLOR):
    """Create a styled metric container"""
    return f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
    </div>
    """

# Create tabs
tab_names = ["Overview", "Sales Analysis", "Product Analysis", "Customer Analysis", "Digital Analysis", "Inventory Analysis", "Campaign Analysis"]
tabs = st.tabs(tab_names)



# Overview tab
with tabs[0]:
    st.markdown(
    """
    <div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 20px; margin-top: 20px;">
        <img src="https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg" alt="Keboola Logo" style="height: 40px;">
    </div>
    """,
    unsafe_allow_html=True
)
    st.markdown("""
    Ecommerce Starter is a **demo project** featuring a fictional eCommerce company designed to showcase how businesses can effortlessly leverage the Keboola platform, including Streamlit dashboards and AI integrations. Discover unified insights into business performance and unlock a path to advanced capabilities such as dynamic pricing, demand forecasting, personalization, and more—all enabled by a single data platform.
    """)
with tabs[1]:
    # Calculate key metrics
    total_revenue = order_fact['TOTAL_AMOUNT'].sum()
    total_orders = len(order_fact)
    total_customers = len(customer)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Create key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_container("Total Customers", f"{total_customers:,.0f}"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container("Total Orders", f"{total_orders:,.0f}"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container("Total Revenue", f"${total_revenue:,.0f}"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container("Avg Order Value", f"${avg_order_value:,.2f}"), unsafe_allow_html=True)
    
    # Create time series with daily orders
    daily_orders = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='D')).agg({
        'ORDER_ID': 'count',
        'TOTAL_AMOUNT': 'sum'
    }).reset_index()
    daily_orders.rename(columns={'ORDER_ID': 'NEW_ORDERS'}, inplace=True)

    # Plot daily orders and revenue
    fig1 = go.Figure()
    # Add bar chart for order count
    fig1.add_trace(go.Bar(
        x=daily_orders['ORDER_DATE'],
        y=daily_orders['NEW_ORDERS'],
        name='Number of Orders',
        marker_color='rgba(128, 128, 128, 0.3)',  # Grey with 70% transparency
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Number of Orders: %{y}<extra></extra>'
    ))
    
    # Add line chart for revenue on secondary y-axis
    fig1.add_trace(go.Scatter(
        x=daily_orders['ORDER_DATE'],
        y=daily_orders['TOTAL_AMOUNT'],
        name='Revenue',
        mode='lines',
        line=dict(color='#1E88E5', width=2),
        yaxis='y2',
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    
    # Update layout for dual y-axis
    fig1.update_layout(
        title='Daily Order Count and Revenue',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title='Number of Orders',
            side='left'
        ),
        yaxis2=dict(
            title='Revenue ($)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig1, use_container_width=True)
    # Group orders by date and status
    status_time = order_fact.groupby([pd.Grouper(key='ORDER_DATE', freq='D'), 'ORDER_STATUS']).size().reset_index(name='COUNT')
    # Create stacked bar chart for status over time (alternative view)
    fig_status_stacked = px.bar(
        status_time,
        x='ORDER_DATE',
        y='COUNT',
        color='ORDER_STATUS',
        title='Order Status Over Time',
        color_discrete_map=STATUS_COLORS,
        labels={
            'ORDER_DATE': 'Date',
            'COUNT': 'Number of Orders',
            'ORDER_STATUS': 'Order Status'
        },
        barmode='stack'  # Stack bars by date
    )
    
    # Customize appearance
    fig_status_stacked.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Orders',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            traceorder='reversed'
        )
    )

    # Customize hover template to show date once at top
    fig_status_stacked.update_traces(
        hovertemplate=
        "Order Status: %{data.name}<br>" +
        "Number of Orders: %{y:,}<extra></extra>"
    )
    
    # Display chart
    st.plotly_chart(fig_status_stacked, use_container_width=True)

    # Revenue by order type and time trend
    type_revenue_time = order_fact.groupby(['ORDER_TYPE', pd.Grouper(key='ORDER_DATE', freq='D')])['TOTAL_AMOUNT'].sum().reset_index()
    
    # Create an area chart for revenue trends
    pivot_revenue = type_revenue_time.pivot_table(
        index='ORDER_DATE', 
        columns='ORDER_TYPE', 
        values='TOTAL_AMOUNT',
        aggfunc='sum'
    ).fillna(0).reset_index()
    
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
        title='Revenue by Order Type',
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={
            'ORDER_DATE': 'Date',
            'TOTAL_AMOUNT': 'Revenue',
            'ORDER_TYPE': 'Order Type'
        }
    )
    
    fig3b.update_layout(
        xaxis_title='',
        yaxis_title='Revenue',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            traceorder='reversed'
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
    
    # Create sales dashboard
    # Add KPI metrics for sales performance

    # Calculate daily actual sales (using efficient groupby)
    daily_actual_sales = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='D')).agg({
        'TOTAL_AMOUNT': 'sum'
    }).reset_index()

    # Filter sales plan to relevant date range
    sales_plan = sales_plan[
        (sales_plan['PLAN_START_DATE'] >= start_date) & 
        (sales_plan['PLAN_START_DATE'] <= end_date)
    ]

    # Create daily plan dataframe from sales_plan data
    daily_plan = sales_plan[['PLAN_START_DATE', 'TARGET_REVENUE']].copy()
    daily_plan.columns = ['ORDER_DATE', 'PLANNED_AMOUNT']

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

    col1, col2, col3 = st.columns(3)

    total_actual = daily_sales['TOTAL_AMOUNT'].sum()
    total_planned = daily_sales['PLANNED_AMOUNT'].sum()
    overall_achievement = (total_actual / total_planned * 100) if total_planned > 0 else 0

    with col1:
        st.markdown(create_metric_container(
            "Total Actual Sales",
            f"${total_actual:,.2f}"
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

    # Create sales vs plan visualization
    sales_plan_fig = go.Figure()

    # Add colored background for each day
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
# Product Analysis tab
with tabs[2]:
    # Merge relevant tables efficiently for product analysis
    product_sales = (order_line.merge(order_fact[['ORDER_ID', 'ORDER_DATE', 'ORDER_STATUS']], on='ORDER_ID')
                    .merge(product[['PRODUCT_ID', 'NAME', 'CATEGORY', 'BRAND', 'PRICE']], on='PRODUCT_ID')
                    .merge(product_variant[['VARIANT_ID', 'PRODUCT_ID', 'VARIANT_NAME', 'INVENTORY_QTY']], on=['PRODUCT_ID', 'VARIANT_ID'], how='left'))
    
    # Calculate product metrics - correctly account for discounts
    product_sales['REVENUE'] = product_sales['LINE_TOTAL']  # LINE_TOTAL already includes discounts
    product_sales['PROFIT_MARGIN'] = ((product_sales['LINE_TOTAL'] - (product_sales['UNIT_PRICE'] * 0.6 * product_sales['QUANTITY'])) / product_sales['LINE_TOTAL']) * 100
    
    # Convert ORDER_DATE to datetime
    product_sales['ORDER_DATE'] = pd.to_datetime(product_sales['ORDER_DATE'])
    
    # Extract year and month for time-based analysis
    product_sales['YEAR'] = product_sales['ORDER_DATE'].dt.year
    product_sales['MONTH'] = product_sales['ORDER_DATE'].dt.month
    product_sales['MONTH_NAME'] = product_sales['ORDER_DATE'].dt.strftime('%b')
    product_sales['YEAR_MONTH'] = product_sales['ORDER_DATE'].dt.strftime('%Y-%m')
    
    # Key metrics
    total_products = len(product)
    active_products = len(product[product['ACTIVE'] == True])
    total_categories = product['CATEGORY'].nunique()
    avg_price = product['PRICE'].mean()
    total_variants = len(product_variant)
    avg_inventory = product_variant['INVENTORY_QTY'].mean()
    
    # Display key metrics in two rows
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Products",
            f"{total_products:,}"
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
            "Avg Product Price",
            f"${avg_price:.2f}"
        ), unsafe_allow_html=True)
        
    

    # Calculate product performance metrics
    product_performance = product_sales.groupby(['PRODUCT_ID', 'NAME', 'CATEGORY', 'BRAND', 'PRICE']).agg({
        'QUANTITY': 'sum',
        'REVENUE': 'sum',
        'ORDER_ID': 'nunique',
        'PROFIT_MARGIN': 'mean'
    }).reset_index()
    
    product_performance['AVG_ORDER_VALUE'] = product_performance['REVENUE'] / product_performance['ORDER_ID']
    product_performance = product_performance.sort_values('REVENUE', ascending=False)
    
    # Top and Bottom Products
        
    # Top products by Revenue
    top_products = product_performance.nlargest(10, 'REVENUE')
    
    fig_top = px.bar(
        top_products,
        x='REVENUE',
        y='NAME',
        color='CATEGORY',
        title='Top 10 Products by Revenue',
        orientation='h',
        color_discrete_sequence=px.colors.qualitative.Prism,
        text='REVENUE'
    )
    
    fig_top.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='inside'
    )
    
    fig_top.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Revenue ($)',
        yaxis_title='',
        showlegend=True,
        legend_title='Category'
    )
    
    st.plotly_chart(fig_top, use_container_width=True)

    # Top products by Profit Margin
    top_margin_products = product_performance.nlargest(10, 'PROFIT_MARGIN')
    
    fig_margin = px.bar(
        top_margin_products,
        x='PROFIT_MARGIN',
        y='NAME',
        color='CATEGORY',
        title='Top 10 Products by Profit Margin (%)',
        orientation='h',
        color_discrete_sequence=px.colors.qualitative.Prism,
        text='PROFIT_MARGIN'
    )
    
    fig_margin.update_traces(
        texttemplate='%{text:.0f}%',
        textposition='outside'
    )
    
    fig_margin.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Profit Margin (%)',
        yaxis_title='',
        showlegend=True,
        legend_title='Category'
    )
    
    st.plotly_chart(fig_margin, use_container_width=True)

    # Brand Performance
    brand_performance = product_sales.groupby('BRAND').agg({
        'REVENUE': 'sum',
        'QUANTITY': 'sum',
        'PRODUCT_ID': 'nunique'
    }).reset_index().sort_values('REVENUE', ascending=False).head(10)
    
    fig_brand = px.bar(
        brand_performance,
        x='BRAND',
        y='REVENUE',
        title='Top 10 Brands by Revenue',
        color='BRAND',
        text='REVENUE',
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    fig_brand.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )
    
    fig_brand.update_layout(
        xaxis_title='Brand',
        yaxis_title='Revenue ($)',
        xaxis={'categoryorder': 'total descending'},
        showlegend=False
    )
    
    st.plotly_chart(fig_brand, use_container_width=True)

    # Product Sales Hierarchy (Sunburst)
    st.markdown("### Product Sales Hierarchy")
    
    # Prepare data for sunburst chart
    product_sales_hierarchy = product_sales.groupby(['CATEGORY', 'BRAND', 'NAME'])['REVENUE'].sum().reset_index()
    
    # Create sunburst chart
    fig_sunburst = px.sunburst(
        product_sales_hierarchy,
        path=['CATEGORY', 'BRAND', 'NAME'], 
        values='REVENUE',
        title='Product Revenue Distribution',
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    fig_sunburst.update_layout(
        height=600
    )
    
    fig_sunburst.update_traces(
        textinfo='label+value+percent parent',
        texttemplate='%{label}<br>$%{value:,.2f}<br>%{percentParent:.1%}'
    )
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # Product Performance Table
    st.markdown("### Detailed Product Performance")
    
    # Format the table data
    product_table = product_performance.copy()
    product_table['REVENUE'] = product_table['REVENUE'].apply(lambda x: f"${x:,.2f}")
    product_table['AVG_ORDER_VALUE'] = product_table['AVG_ORDER_VALUE'].apply(lambda x: f"${x:,.2f}")
    product_table['PRICE'] = product_table['PRICE'].apply(lambda x: f"${x:,.2f}")
    product_table['PROFIT_MARGIN'] = product_table['PROFIT_MARGIN'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        product_table,
        column_config={
            'NAME': 'Product Name',
            'CATEGORY': 'Category',
            'BRAND': 'Brand',
            'PRICE': 'List Price',
            'QUANTITY': 'Units Sold',
            'REVENUE': 'Total Revenue',
            'ORDER_ID': 'Number of Orders',
            'AVG_ORDER_VALUE': 'Avg Order Value',
            'PROFIT_MARGIN': 'Profit Margin'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # PRICING TAB

    st.markdown("### Product Pricing Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price Distribution by Category
        fig_price = px.box(
            product,
            x='CATEGORY',
            y='PRICE',
            title='Price Distribution by Category',
            color='CATEGORY',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        
        fig_price.update_layout(
            xaxis_title='Category',
            yaxis_title='Price ($)',
            showlegend=False
        )
        
        st.plotly_chart(fig_price, use_container_width=True)
    
    with col2:
        # Price vs Revenue Scatterplot
        price_revenue = product_performance.head(100)  # Top 100 products
        
        fig_scatter = px.scatter(
            price_revenue,
            x='PRICE',
            y='REVENUE',
            size='QUANTITY',
            color='CATEGORY',
            hover_name='NAME',
            title='Price vs. Revenue (Top 100 Products)',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        
        fig_scatter.update_layout(
            xaxis_title='Price ($)',
            yaxis_title='Revenue ($)',
            showlegend=True
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)

# Customer Analysis tab
with tabs[3]:

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
    
    # Calculate customer type distribution
    type_dist = customer_metrics.merge(
        customer[['CUSTOMER_ID', 'CUSTOMER_TYPE']], 
        on='CUSTOMER_ID'
    )['CUSTOMER_TYPE'].value_counts().reset_index()
    type_dist.columns = ['Type', 'Count']
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_container(
            "Total Customers",
            f"{len(customer_metrics):,}"
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
        
  #  with col4:
   #     st.markdown(create_metric_container(
    #        "Most Common Type",
     #       f"{type_dist.iloc[0]['Type']}",
      #      PRIMARY_COLOR
       # ), unsafe_allow_html=True)
        
    # Customer Segmentation Analysis
    col1, col2 = st.columns(2)
    with col1:
        # Segment Distribution
        segment_dist = customer_metrics['SEGMENT'].value_counts().reset_index()
        segment_dist.columns = ['Segment', 'Count']
        segment_dist['Percentage'] = (segment_dist['Count'] / len(customer_metrics) * 100).round(1)
        
        # Define color mapping for segments
        segment_colors = {
            'Champions': '#2E7D32',  # Dark green
            'Loyal Customers': '#73af48',  # Green
            'Potential Loyalists': '#edad07',  # Amber
            'At Risk': '#e27c03',  # Orange
            'Lost Customers': '#cc503e'  # Red
        }
        
        fig_segment = px.bar(
            segment_dist,
            x='Segment',
            y='Count',
            text=segment_dist['Percentage'].apply(lambda x: f'{x}%'),
            title='Customer Segment Distribution',
            color='Segment',
            color_discrete_map=segment_colors,
            hover_data={
                'Count': True,
                'Percentage': ':.1f',
                'Segment': False
            },
            custom_data=['Count', 'Percentage']
        )
            
        fig_segment.update_layout(
            xaxis_title='',
            yaxis_title='Number of Customers',
            showlegend=False
        )

        fig_segment.update_traces(
            hovertemplate='Count: %{customdata[0]}<br>Percentage: %{customdata[1]:.1f}%<extra></extra>'
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
            marker_color='#1f6796',  # Darker blue
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ))
        
        fig_metrics.add_trace(go.Bar(
            name='Avg Order Value',
            x=segment_metrics['SEGMENT'],
            y=segment_metrics['AVG_ORDER_VALUE'],
            marker_color='#38a5a5',  # Lighter blue
            hovertemplate='$%{y:,.2f}<extra></extra>'
        ))
        fig_metrics.update_layout(
            title='Average Metrics by Segment',
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
        color_discrete_sequence=[px.colors.qualitative.Prism[0]], # Using first Prism color
        labels={'ORDER_COUNT': 'Number of Orders'},
        text_auto='.0f',  # Format numbers without k suffix
        hover_data=None  # Disable hover
    )
    
    fig_frequency.update_layout(
        xaxis_title='Number of Orders',
        yaxis_title='Number of Customers',
        showlegend=False,
        bargap=0.1,
        margin=dict(t=50),  # Add top margin to prevent text cutoff
        hovermode=False  # Disable hover mode
    )
    
    fig_frequency.update_traces(
        textposition='outside',  # Place numbers above bars
        textangle=0,  # Ensure text is horizontal
        hoverinfo='skip'  # Disable hover info
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
        marker_color='#1f6796',
        hovertemplate='$%{y:.2f}<extra></extra>'
    ))
    
    fig_type_metrics.add_trace(go.Bar(
        name='Avg Order Value',
        x=type_metrics['CUSTOMER_TYPE'],
        y=type_metrics['AVG_ORDER_VALUE'],
        marker_color='#38a5a5',
        hovertemplate='$%{y:.2f}<extra></extra>'
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
    # Calculate key metrics
    total_events = len(digital_event)

    total_visitors = page_performance['UNIQUE_VISITORS'].sum()
    avg_conversion = page_performance['CONVERSION_RATE'].mean() * 100
    avg_bounce = page_performance['BOUNCE_RATE'].mean() * 100
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Events",
            f"{total_events:,}"
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
    col1, col2 = st.columns(2)
    
    with col1:
        # Event Type Distribution
        event_counts = digital_event['EVENT_TYPE'].value_counts().reset_index()
        event_counts.columns = ['EVENT_TYPE', 'COUNT']
        
        # Create color map using Prism colors
        event_types = event_counts['EVENT_TYPE'].unique()
        color_map = dict(zip(event_types, px.colors.qualitative.Prism[:len(event_types)]))
        
        fig_events = px.bar(
            event_counts,
            x='EVENT_TYPE',
            y='COUNT',
            title='Digital Event Distribution',
            color='EVENT_TYPE',
            color_discrete_map=color_map,
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
        device_counts = digital_event['DEVICE_TYPE'].value_counts().reset_index()
        device_counts.columns = ['DEVICE_TYPE', 'COUNT']
        device_counts['PERCENTAGE'] = (device_counts['COUNT'] / device_counts['COUNT'].sum() * 100).round(1)
        
        # Create color map using Prism colors
        device_types = device_counts['DEVICE_TYPE'].unique()
        color_map = dict(zip(device_types, px.colors.qualitative.Prism[:len(device_types)]))
        
        fig_devices = px.pie(
            device_counts,
            values='COUNT', 
            names='DEVICE_TYPE',
            title='Device Type Distribution',
            color='DEVICE_TYPE',
            hover_data=['PERCENTAGE'],
            color_discrete_map=color_map
        )
        
        fig_devices.update_traces(
            textinfo='percent+label',
            textposition='inside'
        )
        st.plotly_chart(fig_devices, use_container_width=True)
    
    # Traffic Analysis Section
    st.markdown("### Traffic Analysis")
    
    # Prepare monthly data
    page_performance['DATE'] = pd.to_datetime(page_performance['DATE'])
    monthly_traffic = page_performance.groupby(pd.Grouper(key='DATE', freq='W')).agg({
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
        title='Weekly Website Traffic',
        xaxis_title='Week',
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
        xaxis_title='Week',
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
    funnel_counts = digital_event[digital_event['EVENT_TYPE'].isin(funnel_events)]['EVENT_TYPE'].value_counts()
    funnel_data = pd.DataFrame({
        'EVENT_TYPE': funnel_events,
        'COUNT': [funnel_counts.get(event, 0) for event in funnel_events]
    })
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_data['EVENT_TYPE'],
        x=funnel_data['COUNT'],
        textinfo="value+percent initial",
        texttemplate="%{value:.2s}<br>(%{percentInitial})"
    ))
    
    fig_funnel.update_layout(
        title='Customer Journey Funnel',
        showlegend=False
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)

# Inventory Analysis tab
with tabs[5]:

    # Function to categorize inventory levels
    def get_inventory_status(qty):
        if qty <= 5:
            return "Critical (0-5)"
        elif qty <= 20:
            return "Low (6-20)"
        elif qty <= 50:
            return "Medium (21-50)"
        else:
            return "High (50+)"
    
    # Add inventory status to product variant data
    product_variant['INVENTORY_STATUS'] = product_variant['INVENTORY_QTY'].apply(get_inventory_status)
    
    # Merge with product data for category information
    inventory_analysis = product_variant.merge(product[['PRODUCT_ID', 'CATEGORY', 'BRAND', 'NAME']], on='PRODUCT_ID')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory Status Distribution
        inventory_status_count = inventory_analysis.groupby('INVENTORY_STATUS').size().reset_index(name='COUNT')
        
        # Custom order for the status
        status_order = ["Critical (0-5)", "Low (6-20)", "Medium (21-50)", "High (50+)"]
        inventory_status_count['INVENTORY_STATUS'] = pd.Categorical(
            inventory_status_count['INVENTORY_STATUS'], 
            categories=status_order, 
            ordered=True
        )
        inventory_status_count = inventory_status_count.sort_values('INVENTORY_STATUS')
        
        # Define colors for each status
        status_colors = {
            "Critical (0-5)": DANGER_COLOR,
            "Low (6-20)": WARNING_COLOR,
            "Medium (21-50)": SECONDARY_COLOR,
            "High (50+)": SUCCESS_COLOR
        }
        
        # Extract the colors in the correct order
        color_sequence = [status_colors[status] for status in inventory_status_count['INVENTORY_STATUS']]
        
        fig_status = px.pie(
            inventory_status_count,
            values='COUNT',
            names='INVENTORY_STATUS',
            title='Inventory Status Distribution',
            color='INVENTORY_STATUS',
            color_discrete_map=status_colors
        )
        
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Inventory by Category
        inventory_by_category = inventory_analysis.groupby('CATEGORY')['INVENTORY_QTY'].agg(['sum', 'mean']).reset_index()
        inventory_by_category.columns = ['CATEGORY', 'TOTAL_INVENTORY', 'AVG_INVENTORY']
        
        # Get unique categories and assign Prism colors
        categories = inventory_by_category['CATEGORY'].unique()
        color_map = dict(zip(categories, px.colors.qualitative.Prism[:len(categories)]))
        
        fig_inv_cat = px.bar(
            inventory_by_category,
            x='CATEGORY',
            y='TOTAL_INVENTORY',
            title='Total Inventory by Category',
            color='CATEGORY',
            text='TOTAL_INVENTORY',
            color_discrete_map=color_map
        )
        
        fig_inv_cat.update_traces(
            texttemplate='%{text:,}',
            textposition='outside'
        )
        fig_inv_cat.update_layout(
            xaxis_title='Category',
            yaxis_title='Total Inventory Quantity',
            showlegend=False
        )
        
        st.plotly_chart(fig_inv_cat, use_container_width=True)
    
    # Out of Stock and Critical Inventory Products
    st.markdown("### Critical Inventory Products")
    
    critical_inventory = inventory_analysis[inventory_analysis['INVENTORY_STATUS'] == "Critical (0-5)"].sort_values('INVENTORY_QTY')
    
    if len(critical_inventory) > 0:
        # Find sales velocity for critical inventory products
        product_velocity = product_sales.groupby('PRODUCT_ID')['QUANTITY'].sum().reset_index()
        product_velocity.columns = ['PRODUCT_ID', 'TOTAL_SOLD']
        
        # Merge with critical inventory
        critical_inventory = critical_inventory.merge(product_velocity, on='PRODUCT_ID', how='left')
        critical_inventory['TOTAL_SOLD'] = critical_inventory['TOTAL_SOLD'].fillna(0)
        
        # Format for display
        critical_table = critical_inventory[['NAME', 'VARIANT_NAME', 'CATEGORY', 'BRAND', 'INVENTORY_QTY', 'TOTAL_SOLD']].copy()
        
        st.dataframe(
            critical_table,
            column_config={
                'NAME': 'Product Name',
                'VARIANT_NAME': 'Variant Name',
                'CATEGORY': 'Category',
                'BRAND': 'Brand',
                'INVENTORY_QTY': 'Current Stock',
                'TOTAL_SOLD': 'Total Units Sold'
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No products with critical inventory levels found.")
    
# Campaign Analysis tab
with tabs[6]:
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
    
    # Convert budget from currency string to numeric
    campaign['BUDGET'] = campaign['BUDGET'].str.replace('$', '').str.replace(',', '').astype(float)
    total_budget = campaign['BUDGET'].sum()
    avg_campaign_budget = total_budget / total_campaigns if total_campaigns > 0 else 0

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_container(
            "Total Campaigns",
            f"{total_campaigns:,}"
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
            f"${avg_campaign_budget:,.2f}"
        ), unsafe_allow_html=True)

    # Campaign Type Analysis
    ""
    st.markdown("#### Campaign Performance by Type")
    
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
        custom_colors = px.colors.qualitative.Prism[:len(campaign_types)]
        color_map = dict(zip(campaign_types, custom_colors))

        # Budget by Campaign Type
        fig_budget = px.pie(
            type_performance,
            values='BUDGET', 
            names='CAMPAIGN_TYPE',
            title='Budget Allocation by Campaign Type',
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
        custom_colors = px.colors.qualitative.Prism[:len(objectives)]
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
        custom_colors = px.colors.qualitative.Prism[:len(segments)]
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