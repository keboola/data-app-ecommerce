import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from keboola_streamlit import KeboolaStreamlit


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

# Page Configuration
st.set_page_config(
    page_title="E-commerce Dashboard",
    layout="wide",
    page_icon="🛍️",
)

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

# Load data
campaign = pd.read_csv("/data/in/tables/CAMPAIGN.csv")
campaign_event = pd.read_csv("/data/in/tables/CAMPAIGN_EVENT.csv") #
channel = pd.read_csv("/data/in/tables/CHANNEL.csv")
company = pd.read_csv("/data/in/tables/COMPANY.csv")
content_page = pd.read_csv("/data/in/tables/CONTENT_PAGE.csv") #
custom_attribute = pd.read_csv("/data/in/tables/CUSTOM_ATTRIBUTE.csv") #
customer = pd.read_csv("/data/in/tables/CUSTOMER.csv")
digital_event = pd.read_csv("DIGITAL_EVENT.csv")
digital_site = pd.read_csv("/data/in/tables/DIGITAL_SITE.csv") #
facility = pd.read_csv("/data/in/tables/FACILITY.csv")
inventory = pd.read_csv("/data/in/tables/INVENTORY.csv")
order_campaign_attribution = pd.read_csv("/data/in/tables/ORDER_CAMPAIGN_ATTRIBUTION.csv")
order_event = pd.read_csv("/data/in/tables/ORDER_EVENT.csv") #
order_fact = pd.read_csv("/data/in/tables/ORDER_FACT.csv")
order_fulfillment = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT.csv") #
order_fulfillment_line = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT_LINE.csv") #
order_line = pd.read_csv("/data/in/tables/ORDER_LINE.csv")
order_status_history = pd.read_csv("/data/in/tables/ORDER_STATUS_HISTORY.csv") #
page_performance = pd.read_csv("/data/in/tables/PAGE_PERFORMANCE.csv")
person = pd.read_csv("/data/in/tables/PERSON.csv")
product = pd.read_csv("/data/in/tables/PRODUCT.csv")
product_variant = pd.read_csv("/data/in/tables/PRODUCT_VARIANT.csv") #
sales_plan = pd.read_csv("/data/in/tables/SALES_PLAN.csv")


# Display Keboola logo and title
st.markdown(
    """
    <div style="display: flex; align-items: center; margin-bottom: 30px;">
        <img src="https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg" 
                alt="Keboola Logo" 
                style="height: 55px; margin-right: 15px;">
        <h1 style="margin: 0;">E-commerce Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Create sidebar filters
with st.sidebar:
    st.subheader("Filters")
    
    # Date range filter
    min_date = pd.to_datetime(order_fact['ORDER_DATE']).min()
    max_date = pd.to_datetime(order_fact['ORDER_DATE']).max()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Other filters
    channels = ['All'] + list(channel['CHANNEL_NAME'].unique())
    selected_channel = st.selectbox('Sales Channel', channels)
    
    categories = ['All'] + list(product['CATEGORY'].unique())
    selected_category = st.selectbox('Product Category', categories)
    
    payment_methods = ['All'] + list(order_fact['PAYMENT_METHOD'].unique())
    selected_payment_method = st.selectbox('Payment Method', payment_methods)
    
    order_statuses = ['All'] + list(order_fact['ORDER_STATUS'].unique())
    selected_order_status = st.selectbox('Order Status', order_statuses)
    
    # Show active filters
    active_filters = []
    if len(date_range) == 2:
        active_filters.append(f"Date: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
    if selected_channel != 'All':
        active_filters.append(f"Channel: {selected_channel}")
    if selected_category != 'All':
        active_filters.append(f"Category: {selected_category}")
    if selected_payment_method != 'All':
        active_filters.append(f"Payment Method: {selected_payment_method}")
    if selected_order_status != 'All':
        active_filters.append(f"Order Status: {selected_order_status}")
    
    if active_filters:
        st.markdown("#### Active Filters")
        for filter_text in active_filters:
            st.markdown(f"- {filter_text}")

# Apply filters to data
#iltered_data = data.copy()

# Filter orders by date range
if date_range:  # Check if date_range exists
    try:
        # Sort dates to ensure start_date is before end_date
        sorted_dates = sorted(date_range)
        start_date = sorted_dates[0]
        end_date = sorted_dates[1]
        
        order_fact = order_fact[
            (pd.to_datetime(order_fact['ORDER_DATE']) >= pd.Timestamp(start_date)) &
            (pd.to_datetime(order_fact['ORDER_DATE']) <= pd.Timestamp(end_date))
        ]
    except (IndexError, TypeError):
        st.info("Please select both start and end dates")
        st.stop()  # Stop execution if dates are invalid

# Filter by channel
if selected_channel != 'All':
    channel_ids = channel[channel['CHANNEL_NAME'] == selected_channel]['CHANNEL_ID']
    order_fact = order_fact[order_fact['CHANNEL_ID'].isin(channel_ids)]

# Filter by payment method
if selected_payment_method != 'All':
    order_fact = order_fact[order_fact['PAYMENT_METHOD'] == selected_payment_method]

# Filter by order status
if selected_order_status != 'All':
    order_fact = order_fact[order_fact['ORDER_STATUS'] == selected_order_status]

# Filter order lines and get relevant product IDs
order_line = order_line[
    order_line['ORDER_ID'].isin(order_fact['ORDER_ID'])
]

# Filter by product category
if selected_category != 'All':
    category_product_ids = product[product['CATEGORY'] == selected_category]['PRODUCT_ID']
    order_line = order_line[
        order_line['PRODUCT_ID'].isin(category_product_ids)
    ]
    product = product[product['CATEGORY'] == selected_category]

# Get relevant customer IDs from filtered orders
customer_ids = order_fact['CUSTOMER_ID'].unique()
customer = customer[customer['CUSTOMER_ID'].isin(customer_ids)]

# Filter related tables
person = person[person['CUSTOMER_ID'].isin(customer_ids)]
company = company[company['CUSTOMER_ID'].isin(customer_ids)]

# Filter digital events
digital_event = digital_event[
    (pd.to_datetime(digital_event['EVENT_DATE']) >= pd.Timestamp(date_range[0])) &
    (pd.to_datetime(digital_event['EVENT_DATE']) <= pd.Timestamp(date_range[1]))
]

# Filter page performance
page_performance = page_performance[
    (pd.to_datetime(page_performance['DATE']) >= pd.Timestamp(date_range[0])) &
    (pd.to_datetime(page_performance['DATE']) <= pd.Timestamp(date_range[1]))
]


def create_metric_container(title, value, color=PRIMARY_COLOR):
    """Create a styled metric container"""
    return f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value" style="color: {color}">{value}</div>
    </div>
    """
# Create tabs
tabs = st.tabs(["Sales Overview", "Sales v Plan", "Product Analysis", "Customer Analysis", "Digital Analysis", "Inventory Analysis", "Campaign Analysis"])

# Overview tab
with tabs[0]:

    # Calculate key metrics
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
        st.markdown(create_metric_container("Total Revenue", f"${order_fact['TOTAL_AMOUNT'].sum():,.0f}"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container("Avg Order Value", f"${avg_order_value:,.2f}"), unsafe_allow_html=True)
    
    # Prepare order data
    order_fact['ORDER_DATE'] = pd.to_datetime(order_fact['ORDER_DATE'])
    
    # Create time series with monthly orders
    monthly_orders = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='M')).size().reset_index(name='NEW_ORDERS')
    
    # Plot monthly orders
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=monthly_orders['ORDER_DATE'],
        y=monthly_orders['NEW_ORDERS'],
        name='Monthly Orders',
        mode='lines+markers',
        marker=dict(color='#90CAF9', size=8),
        line=dict(color='#90CAF9', width=2),
        showlegend=False
    ))
    
    fig1.update_layout(
        title='Monthly Sales Trend',
        xaxis_title='Month',
        yaxis_title='Number of Orders',
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Order status distribution
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        # Calculate order status counts
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
    with col2:
        total_orders = len(order_fact)
        delivered = len(order_fact[order_fact['ORDER_STATUS'] == 'Delivered'])
        cancelled = len(order_fact[order_fact['ORDER_STATUS'] == 'Cancelled'])
        failed = len(order_fact[order_fact['ORDER_STATUS'] == 'Failed'])
        returned = len(order_fact[order_fact['ORDER_STATUS'] == 'Returned'])
        refunded = len(order_fact[order_fact['ORDER_STATUS'] == 'Refunded'])
        completed = len(order_fact[order_fact['ORDER_STATUS'] == 'Completed'])
        in_progress = total_orders - delivered - cancelled - failed - returned - refunded - completed
        
        st.markdown(create_metric_container("Completion Rate", f"{completed/total_orders:.1%}", "#4CAF50"), unsafe_allow_html=True)
        st.markdown(create_metric_container("Orders In Progress", f"{in_progress:,.0f}"), unsafe_allow_html=True)
        st.markdown(create_metric_container("Cancellation Rate", f"{cancelled/total_orders:.1%}", "#F44336"), unsafe_allow_html=True)
    
    # Revenue by order type and time trend
    type_revenue_time = order_fact.groupby(['ORDER_TYPE', pd.Grouper(key='ORDER_DATE', freq='M')])['TOTAL_AMOUNT'].sum().reset_index()
    
    # Calculate revenue by order type and status for better visualization
    type_status_revenue = order_fact.groupby(['ORDER_TYPE', 'ORDER_STATUS'])['TOTAL_AMOUNT'].sum().reset_index()
    type_status_revenue = type_status_revenue.sort_values('TOTAL_AMOUNT', ascending=False)
    

    # Create an area chart for revenue trends
    # Calculate cumulative revenue by order type
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
        title='Revenue Trends by Order Type',
        color_discrete_sequence=BASE_PALETTE,
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
        )
    )
    
    st.plotly_chart(fig3b, use_container_width=True)
    

# Sales Analysis tab
with tabs[1]:
# Create sales dashboard
    metrics = st.container()

    # Convert dates to datetime
    order_fact['ORDER_DATE'] = pd.to_datetime(order_fact['ORDER_DATE'])

    # Calculate monthly actual sales
    monthly_actual_sales = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='M')).agg({
        'TOTAL_AMOUNT': 'sum'
    }).reset_index()

    # Process sales plan data
    sales_plan['PLAN_START_DATE'] = pd.to_datetime(sales_plan['PLAN_START_DATE'])
    sales_plan['PLAN_END_DATE'] = pd.to_datetime(sales_plan['PLAN_END_DATE'])

    # Calculate monthly planned sales
    monthly_plan = pd.DataFrame()
    for _, row in sales_plan.iterrows():
        # Create date range for each plan
        date_range = pd.date_range(row['PLAN_START_DATE'], row['PLAN_END_DATE'], freq='M')
        # Distribute target revenue evenly across months
        monthly_revenue = row['TARGET_REVENUE'] / len(date_range)
        temp_df = pd.DataFrame({
            'ORDER_DATE': date_range,
            'PLANNED_AMOUNT': monthly_revenue
        })
        monthly_plan = pd.concat([monthly_plan, temp_df])

    # Aggregate planned sales by month
    monthly_plan = monthly_plan.groupby('ORDER_DATE')['PLANNED_AMOUNT'].sum().reset_index()

    # Merge actual and planned sales
    monthly_sales = pd.merge(
        monthly_actual_sales,
        monthly_plan,
        on='ORDER_DATE',
        how='outer'
    ).fillna(0)

    # Sort by date
    monthly_sales = monthly_sales.sort_values('ORDER_DATE')

    # Calculate achievement rate
    monthly_sales['ACHIEVEMENT_RATE'] = (monthly_sales['TOTAL_AMOUNT'] / monthly_sales['PLANNED_AMOUNT'] * 100).fillna(0)
    # Create sales vs plan visualization
    sales_plan_fig = go.Figure()
    
    # Add actual sales line
    sales_plan_fig.add_trace(go.Scatter(
        x=monthly_sales['ORDER_DATE'],
        y=monthly_sales['TOTAL_AMOUNT'],
        name='Actual Sales',
        line=dict(color=PRIMARY_COLOR, width=3),
        mode='lines+markers'
    ))
    
    # Add planned sales line
    sales_plan_fig.add_trace(go.Scatter(
        x=monthly_sales['ORDER_DATE'],
        y=monthly_sales['PLANNED_AMOUNT'],
        name='Planned Sales',
        line=dict(color=SECONDARY_COLOR, width=3, dash='dash'),
        mode='lines'
    ))
    
    # Add achievement rate as background color only for months with plan data
    for i in range(len(monthly_sales)-1):
        if monthly_sales['PLANNED_AMOUNT'].iloc[i] > 0:  # Only add color if there is plan data
            achievement_rate = monthly_sales['ACHIEVEMENT_RATE'].iloc[i]
            color = SUCCESS_COLOR if achievement_rate >= 100 else WARNING_COLOR if achievement_rate >= 80 else DANGER_COLOR
            opacity = 0.1  # Light background
            
            sales_plan_fig.add_vrect(
                x0=monthly_sales['ORDER_DATE'].iloc[i],
                x1=monthly_sales['ORDER_DATE'].iloc[i+1],
                fillcolor=color,
                opacity=opacity,
                layer="below",
                line_width=0,
                name=f"Achievement {achievement_rate:.1f}%"
            )

    sales_plan_fig.update_layout(
        title='Sales Performance vs Plan',
        xaxis_title='Month',
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

    total_actual = monthly_sales['TOTAL_AMOUNT'].sum()
    total_planned = monthly_sales['PLANNED_AMOUNT'].sum()
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

    
    # Prepare time series data for trend visualization
    order_fact['ORDER_DATE'] = pd.to_datetime(order_fact['ORDER_DATE'])
    monthly_sales = order_fact.groupby(pd.Grouper(key='ORDER_DATE', freq='M')).agg({
        'TOTAL_AMOUNT': 'sum'
    }).reset_index()
    monthly_sales['ORDER_DATE'] = monthly_sales['ORDER_DATE'].astype(str)
    


    # Product Details section
    # st.markdown('#### Product Details')
with tabs[2]:
    st.markdown("## Product Analysis")

    # Merge relevant tables
    product_sales = (order_line.merge(order_fact, on='ORDER_ID')
                    .merge(product, on='PRODUCT_ID'))
    
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
        # Category Distribution
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
    # Prepare data for sunburst chart
    product_hierarchy = product.groupby(['CATEGORY', 'BRAND', 'NAME'])['PRICE'].sum().reset_index()
    
    # Create sunburst chart
    fig_sunburst = px.sunburst(
        product_hierarchy,
        path=['CATEGORY', 'BRAND', 'NAME'],
        values='PRICE',
        title='Product Price Hierarchy',
        #color_discrete_sequence=BASE_PALETTE
    )
    
    fig_sunburst.update_layout(
        width=800,
        height=800
    )
    
    fig_sunburst.update_traces(
        textinfo='label+percent parent'
    )
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
    
    st.markdown("### Top Products Performance")

    # Calculate product performance metrics
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
        color_discrete_sequence=BASE_PALETTE,
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
    
    brand_performance = product_sales.groupby('BRAND').agg({
        'REVENUE': 'sum',
        'QUANTITY': 'sum',
        'ORDER_ID': 'nunique',
        'PRODUCT_ID': 'nunique'
    }).reset_index()
    
    brand_performance = brand_performance.sort_values('REVENUE', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Brand Revenue Share
        fig_brand = px.pie(
            brand_performance,
            values='REVENUE',
            names='BRAND',
            title='Revenue Share by Brand',
            color_discrete_sequence=BASE_PALETTE
        )
        fig_brand.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_brand, use_container_width=True)
    
    with col2:
        # Brand Product Count
        fig_brand_products = px.bar(
            brand_performance,
            x='BRAND',
            y=['PRODUCT_ID', 'ORDER_ID'],
            title='Brand Performance Metrics',
            barmode='group',
            labels={'PRODUCT_ID': 'Number of Products', 'ORDER_ID': 'Number of Orders'},
            color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR]
        )
        fig_brand_products.update_layout(
            xaxis_title='Brand',
            yaxis_title='Count',
            legend_title='Metric',
            xaxis={'tickangle': 45}
        )
        st.plotly_chart(fig_brand_products, use_container_width=True)

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
    total_events = len(digital_event)
    total_visitors = page_performance['UNIQUE_VISITORS'].sum()
    avg_conversion = page_performance['CONVERSION_RATE'].mean() * 100
    avg_bounce = page_performance['BOUNCE_RATE'].mean() * 100
    
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
        event_counts = digital_event['EVENT_TYPE'].value_counts().reset_index()
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
        device_counts = digital_event['DEVICE_TYPE'].value_counts().reset_index()
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
    page_performance['DATE'] = pd.to_datetime(page_performance['DATE'])
    monthly_traffic = page_performance.groupby(pd.Grouper(key='DATE', freq='M')).agg({
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
    
    # User Journey Analysis
    st.markdown("### User Journey Analysis")
    
    # Calculate event sequence metrics
    event_sequence = digital_event.sort_values('EVENT_DATE').groupby('SESSION_ID')['EVENT_TYPE'].agg(list).reset_index()
    
    # Calculate common paths
    def get_journey_path(events):
        return ' → '.join(events[:3])  # Show first 3 events in journey
    
    event_sequence['JOURNEY_PATH'] = event_sequence['EVENT_TYPE'].apply(get_journey_path)
    top_paths = event_sequence['JOURNEY_PATH'].value_counts().head(5).reset_index()
    top_paths.columns = ['Path', 'Count']
    

    fig_paths = px.bar(
        top_paths,
        x='Count',
        y='Path',
        orientation='h',
        title='Most Common User Journeys',
        color='Count',
        color_continuous_scale=[PRIMARY_COLOR, SUCCESS_COLOR]
    )
    
    fig_paths.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Number of Sessions',
        yaxis_title='Journey Path',
        showlegend=False
    )
    
    st.plotly_chart(fig_paths, use_container_width=True)
    # Event Success Analysis
    st.markdown("### Event Success Analysis")
    
    # Filter for conversion events (key actions that indicate user engagement/conversion)
    conversion_events = digital_event[digital_event['EVENT_TYPE'].isin([
        'CHECKOUT_COMPLETE',
        'ACCOUNT_SIGNUP',
        'ADD_TO_CART'
    ])]
    
    # Calculate success rates for these events
    success_rates = conversion_events.groupby('EVENT_TYPE').agg({
        'EVENT_VALUE': lambda x: (x.astype(float) > 0).mean()  # Success if event value > 0
    }).reset_index()
    
    success_rates.columns = ['EVENT_TYPE', 'SUCCESS_RATE']
    success_rates['SUCCESS_RATE'] = (success_rates['SUCCESS_RATE'] * 100).round(1)
    

    fig_success = px.bar(
        success_rates,
        x='EVENT_TYPE',
        y='SUCCESS_RATE',
        title='Success Rates for Key Events',
        color='EVENT_TYPE',
        color_discrete_map={
            'CHECKOUT_COMPLETE': SUCCESS_COLOR,
            'ACCOUNT_SIGNUP': PRIMARY_COLOR,
            'ADD_TO_CART': SECONDARY_COLOR
        },
        text='SUCCESS_RATE'
    )
    
    fig_success.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig_success.update_layout(
        xaxis_title='Event Type',
        yaxis_title='Success Rate (%)',
        showlegend=False
    )
    
    st.plotly_chart(fig_success, use_container_width=True)


    funnel_events = ['PAGE_VIEW', 'PRODUCT_VIEW', 'ADD_TO_CART', 'CHECKOUT_START', 'CHECKOUT_COMPLETE']
    funnel_counts = digital_event[digital_event['EVENT_TYPE'].isin(funnel_events)]['EVENT_TYPE'].value_counts()
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
    st.markdown("## Inventory Analysis")

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
    inventory_analysis = inventory.merge(
        product[['PRODUCT_ID', 'NAME', 'CATEGORY', 'BRAND']], 
        on='PRODUCT_ID'
    ).merge(
        facility[['FACILITY_ID', 'FACILITY_NAME', 'FACILITY_TYPE']], 
        on='FACILITY_ID'
    )

    # Inventory by Category Analysis
    st.markdown("### Inventory by Category")
    col1, col2 = st.columns(2)

    with col1:
        # Category Distribution
        category_inventory = inventory_analysis.groupby('CATEGORY').agg({
            'QUANTITY': 'sum',
            'PRODUCT_ID': 'nunique'
        }).reset_index()

        fig_category = px.pie(
            category_inventory,
            values='QUANTITY',
            names='CATEGORY',
            title='Total Inventory by Category',
            color_discrete_sequence=BASE_PALETTE
        )

        fig_category.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        st.plotly_chart(fig_category, use_container_width=True)

    with col2:
        # Products per Category
        fig_products = px.bar(
            category_inventory,
            x='CATEGORY',
            y='PRODUCT_ID',
            title='Number of Products by Category',
            color='CATEGORY',
            color_discrete_sequence=BASE_PALETTE,
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
            return "Critical Low"
        elif quantity <= 50:
            return "Low"
        elif quantity <= 200:
            return "Medium"
        return "High"

    inventory_analysis['STATUS'] = inventory_analysis['QUANTITY'].apply(get_inventory_status)

    # Create inventory status visualization
    col1, col2 = st.columns(2)

    with col1:
        # Status Distribution
        status_counts = inventory_analysis.groupby('STATUS').size().reset_index(name='COUNT')
        
        fig_status = px.pie(
            status_counts,
            values='COUNT',
            names='STATUS',
            title='Inventory Status Distribution',
            color='STATUS',
            color_discrete_sequence=[DANGER_COLOR, WARNING_COLOR, SECONDARY_COLOR, SUCCESS_COLOR]
        )

        fig_status.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Status by Category
        status_category = inventory_analysis.groupby(['CATEGORY', 'STATUS']).size().reset_index(name='COUNT')
        
        fig_status_category = px.bar(
            status_category,
            x='CATEGORY',
            y='COUNT',
            color='STATUS',
            title='Inventory Status by Category',
            color_discrete_sequence=[DANGER_COLOR, WARNING_COLOR, SECONDARY_COLOR, SUCCESS_COLOR],
            barmode='stack'
        )

        st.plotly_chart(fig_status_category, use_container_width=True)

    # Facility Analysis
    st.markdown("### Facility Analysis")

    # Calculate inventory by facility type
    facility_inventory = inventory_analysis.groupby(['FACILITY_TYPE', 'FACILITY_NAME']).agg({
        'QUANTITY': 'sum',
        'PRODUCT_ID': 'nunique'
    }).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        # Inventory by Facility Type
        facility_type_summary = facility_inventory.groupby('FACILITY_TYPE').agg({
            'QUANTITY': 'sum'
        }).reset_index()

        fig_facility = px.pie(
            facility_type_summary,
            values='QUANTITY',
            names='FACILITY_TYPE',
            title='Inventory Distribution by Facility Type',
            color_discrete_sequence=BASE_PALETTE
        )

        fig_facility.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        st.plotly_chart(fig_facility, use_container_width=True)

    with col2:
        # Top Facilities by Inventory
        fig_top_facilities = px.bar(
            facility_inventory.nlargest(10, 'QUANTITY'),
            x='FACILITY_NAME',
            y='QUANTITY',
            color='FACILITY_TYPE',
            title='Top 10 Facilities by Inventory',
            color_discrete_sequence=BASE_PALETTE
        )

        fig_top_facilities.update_layout(
            xaxis_tickangle=45,
            xaxis_title='Facility',
            yaxis_title='Total Inventory'
        )

        st.plotly_chart(fig_top_facilities, use_container_width=True)

    # Critical Inventory Alerts
    st.markdown("### Critical Inventory Alerts")
    critical_inventory = inventory_analysis[inventory_analysis['STATUS'] == 'Critical Low'].sort_values('QUANTITY')

    if len(critical_inventory) > 0:
        st.warning(f"⚠️ {len(critical_inventory)} products have critically low inventory (10 or fewer units)")
        
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
    st.markdown("## Campaign Analysis")

    # Merge campaign data with attribution and order data
    campaign_performance = (order_campaign_attribution.merge(
        campaign[['CAMPAIGN_ID', 'CAMPAIGN_NAME', 'CAMPAIGN_TYPE', 'OBJECTIVE', 'BUDGET', 'TARGET_SEGMENT', 'START_DATE', 'END_DATE']], 
        on='CAMPAIGN_ID'
    ).merge(
        order_fact[['ORDER_ID', 'TOTAL_AMOUNT']], 
        on='ORDER_ID'
    ))
    
    # Clean budget data - remove '$' and ',' and convert to float
    campaign['BUDGET'] = campaign['BUDGET'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # Calculate attributed revenue
    campaign_performance['ATTRIBUTED_REVENUE'] = campaign_performance['TOTAL_AMOUNT'] * campaign_performance['CONTRIBUTION_PERCENT']

    # Calculate key metrics
    total_campaigns = len(campaign)
    active_campaigns = len(campaign[pd.to_datetime(campaign['END_DATE']) >= pd.Timestamp.now()])
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
        fig_budget = px.pie(
            type_performance,
            values='BUDGET',
            names='CAMPAIGN_TYPE',
            title='Budget Distribution by Campaign Type',
            color_discrete_sequence=BASE_PALETTE
        )
        
        fig_budget.update_traces(
            textposition='inside',
            textinfo='percent+label'
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
            color_discrete_sequence=BASE_PALETTE
        )
        
        fig_count.update_layout(
            xaxis_title='Campaign Type',
            yaxis_title='Number of Campaigns',
            showlegend=False
        )
        
        st.plotly_chart(fig_count, use_container_width=True)

    # Campaign Timeline Analysis
    st.markdown("### Campaign Timeline")
    
    # Prepare timeline data
    campaign['START_DATE'] = pd.to_datetime(campaign['START_DATE'])
    campaign['END_DATE'] = pd.to_datetime(campaign['END_DATE'])
    
    # Create timeline visualization
    fig_timeline = px.timeline(
        campaign,
        x_start='START_DATE',
        x_end='END_DATE',
        y='CAMPAIGN_NAME',
        color='CAMPAIGN_TYPE',
        hover_data=['OBJECTIVE', 'TARGET_SEGMENT', 'BUDGET'],
        title='Campaign Timeline',
        color_discrete_sequence=BASE_PALETTE
    )
    
    fig_timeline.update_layout(
        xaxis_title='Date',
        yaxis_title='Campaign Name',
        height=400
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Campaign Objectives Analysis
    st.markdown("### Campaign Objectives")
    
    objective_counts = campaign.groupby('OBJECTIVE').agg({
        'CAMPAIGN_ID': 'count',
        'BUDGET': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Number of Campaigns by Objective
        fig_objectives = px.bar(
            objective_counts,
            x='OBJECTIVE',
            y='CAMPAIGN_ID',
            title='Number of Campaigns by Objective',
            color='OBJECTIVE',
            labels={'CAMPAIGN_ID': 'Number of Campaigns'},
            color_discrete_sequence=BASE_PALETTE
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
            color_discrete_sequence=BASE_PALETTE
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
        # Campaigns by Target Segment
        fig_segments = px.bar(
            segment_analysis,
            x='TARGET_SEGMENT',
            y='CAMPAIGN_ID',
            title='Number of Campaigns by Target Segment',
            color='TARGET_SEGMENT',
            labels={'CAMPAIGN_ID': 'Number of Campaigns'},
            color_discrete_sequence=BASE_PALETTE
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
            color_discrete_sequence=BASE_PALETTE
        )
        
        fig_segment_budget.update_traces(
            textposition='inside',
            textinfo='percent'
        )
        
        st.plotly_chart(fig_segment_budget, use_container_width=True)

    # Campaign Details Table
    st.markdown("### Campaign Details")
    
    campaign_table = campaign.copy()
    campaign_table['DURATION'] = (campaign_table['END_DATE'] - campaign_table['START_DATE']).dt.days
    campaign_table['STATUS'] = np.where(campaign_table['END_DATE'] >= pd.Timestamp.now(), 'Active', 'Completed')
    
    st.dataframe(
        campaign_table[[
            'CAMPAIGN_NAME', 'CAMPAIGN_TYPE', 'OBJECTIVE', 'TARGET_SEGMENT',
            'START_DATE', 'END_DATE', 'DURATION', 'BUDGET', 'STATUS'
        ]].sort_values('START_DATE', ascending=False),
        column_config={
            'CAMPAIGN_NAME': 'Campaign Name',
            'CAMPAIGN_TYPE': 'Type',
            'OBJECTIVE': 'Objective',
            'TARGET_SEGMENT': 'Target Segment',
            'START_DATE': 'Start Date',
            'END_DATE': 'End Date',
            'DURATION': 'Duration (Days)',
            'BUDGET': st.column_config.NumberColumn('Budget', format="$%.2f"),
            'STATUS': 'Status'
        },
        hide_index=True,
        use_container_width=True
    )

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
            color_discrete_sequence=BASE_PALETTE
        )
        
        fig_attribution.update_layout(
            xaxis_title='Campaign Name',
            yaxis_title='Attributed Revenue ($)',
            xaxis={'tickangle': 45},
            showlegend=True
        )
        
        st.plotly_chart(fig_attribution, use_container_width=True)

