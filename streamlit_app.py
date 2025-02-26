import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from keboola_streamlit import KeboolaStreamlit

url = st.secrets["kbc_url"]
token = st.secrets["kbc_token"]
keboola = KeboolaStreamlit(url, token)
# 1. SET PAGE CONFIG
st.set_page_config(
    page_title="E-commerce Dashboard",
    layout="wide",
    page_icon="🛍️",
)

def load_data():
    for table_name in [
        "CAMPAIGN", 
        "CAMPAIGN_EVENT",
        "CHANNEL",  
        "COMPANY", 
        "CONTENT_PAGE", 
        "CUSTOM_ATTRIBUTE",
        "CUSTOMER", 
        "DIGITAL_EVENT", 
        "DIGITAL_SITE", 
        "FACILITY", 
        "INVENTORY", 
        "ORDER_CAMPAIGN_ATTRIBUTION", 
        "ORDER_EVENT",
        "ORDER_FACT", 
        "ORDER_FULFILLMENT", 
        "ORDER_FULFILLMENT_LINE", 
        "ORDER_LINE", 
        "ORDER_STATUS_HISTORY", 
        "PAGE_PERFORMANCE", 
        "PERSON", 
        "PRODUCT", 
        "PRODUCT_VARIANT",
        "SALES_PLAN"]:
        bucket_id = "out.c-BDM"
        table_id = f"{bucket_id}.{table_name}"
        table_data = keboola.read_table(table_id)
        st.session_state[table_name] = table_data

# Define chart configuration function
def configure_chart(chart, height=300):
    return chart.configure_view(
        strokeWidth=0
    ).configure_axis(
        gridColor='#f0f0f0'
    ).configure_legend(
        labelFontSize=12
    ).properties(
        height=height
    )
#load_data()
# Custom CSS for styling

# 2. LOAD DATA
# Generate data using the data generator
df_customer = pd.read_csv("/data/in/tables/CUSTOMER.csv")
df_person = pd.read_csv("/data/in/tables/PERSON.csv")
df_company = pd.read_csv("/data/in/tables/COMPANY.csv")
df_channel = pd.read_csv("/data/in/tables/CHANNEL.csv")
df_facility = pd.read_csv("/data/in/tables/FACILITY.csv")
df_product = pd.read_csv("/data/in/tables/PRODUCT.csv")
df_product_variant = pd.read_csv("/data/in/tables/PRODUCT_VARIANT.csv")
df_inventory = pd.read_csv("/data/in/tables/INVENTORY.csv")
df_order_fact = pd.read_csv("/data/in/tables/ORDER_FACT.csv")
df_order_line = pd.read_csv("/data/in/tables/ORDER_LINE.csv")
df_order_status_history = pd.read_csv("/data/in/tables/ORDER_STATUS_HISTORY.csv")
df_order_campaign_attribution = pd.read_csv("/data/in/tables/ORDER_CAMPAIGN_ATTRIBUTION.csv")
df_campaign = pd.read_csv("/data/in/tables/CAMPAIGN.csv")
df_campaign_event = pd.read_csv("/data/in/tables/CAMPAIGN_EVENT.csv")
df_digital_event = pd.read_csv("/data/in/tables/DIGITAL_EVENT.csv")
df_digital_site = pd.read_csv("/data/in/tables/DIGITAL_SITE.csv")
df_page_performance = pd.read_csv("/data/in/tables/PAGE_PERFORMANCE.csv")
df_content_page = pd.read_csv("/data/in/tables/CONTENT_PAGE.csv")
df_order_fulfillment = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT.csv")

# 3. CREATE VISUALIZATIONS
# Add title with new styling
st.markdown('<h1 class="main-header">E-commerce Analytics Dashboard</h1>', unsafe_allow_html=True)

# Define color scheme for all visualizations
COLOR_SCHEME = ['#1e3d59', '#ff6e40', '#ffc13b', '#12c998', '#5b6c7d', '#4a90e2', '#9013fe', '#50e3c2', '#f5a623', '#4a4a4a']

# Add filters in an expander
with st.sidebar:
    st.write("Filters")
    # Date Range Filter
    min_date = pd.to_datetime(df_order_fact['ORDER_DATE']).min()
    max_date = pd.to_datetime(df_order_fact['ORDER_DATE']).max()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Customer Type Filter
    customer_types = ['All'] + list(df_customer['CUSTOMER_TYPE'].unique())
    selected_customer_type = st.selectbox('Customer Type', customer_types)


    # Channel Filter
    channels = ['All'] + list(df_channel['CHANNEL_NAME'].unique())
    selected_channel = st.selectbox('Sales Channel', channels)
    
    # Product Category Filter
    categories = ['All'] + list(df_product['CATEGORY'].unique())
    selected_category = st.selectbox('Product Category', categories)

    # Payment Method Filter
    payment_methods = ['All'] + list(df_order_fact['PAYMENT_METHOD'].unique())
    selected_payment_method = st.selectbox('Payment Method', payment_methods)
    
    # Order Status Filter
    order_statuses = ['All'] + list(df_order_fact['ORDER_STATUS'].unique())
    selected_order_status = st.selectbox('Order Status', order_statuses)

    # Show active filters
    active_filters = []
    if len(date_range) == 2:
        active_filters.append(f"Date: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
    if selected_customer_type != 'All':
        active_filters.append(f"Customer Type: {selected_customer_type}")
    if selected_channel != 'All':
        active_filters.append(f"Channel: {selected_channel}")
    if selected_category != 'All':
        active_filters.append(f"Category: {selected_category}")
    if selected_payment_method != 'All':
        active_filters.append(f"Payment Method: {selected_payment_method}")
    if selected_order_status != 'All':
        active_filters.append(f"Order Status: {selected_order_status}")
    
    if active_filters:
        st.markdown("---")
        st.markdown('<div class="filter-summary">Active Filters: ' + ' | '.join(active_filters) + '</div>', unsafe_allow_html=True)

# Apply filters to the main dataframe
filtered_orders = df_order_fact.copy()

# Date filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_orders = filtered_orders[
        (pd.to_datetime(filtered_orders['ORDER_DATE']).dt.date >= start_date) &
        (pd.to_datetime(filtered_orders['ORDER_DATE']).dt.date <= end_date)
    ]

# Customer type filter
if selected_customer_type != 'All':
    customer_ids = df_customer[df_customer['CUSTOMER_TYPE'] == selected_customer_type]['CUSTOMER_ID']
    filtered_orders = filtered_orders[filtered_orders['CUSTOMER_ID'].isin(customer_ids)]

# Channel filter
if selected_channel != 'All':
    channel_id = df_channel[df_channel['CHANNEL_NAME'] == selected_channel]['CHANNEL_ID'].iloc[0]
    filtered_orders = filtered_orders[filtered_orders['CHANNEL_ID'] == channel_id]

# Payment method filter
if selected_payment_method != 'All':
    filtered_orders = filtered_orders[filtered_orders['PAYMENT_METHOD'] == selected_payment_method]

# Order status filter
if selected_order_status != 'All':
    filtered_orders = filtered_orders[filtered_orders['ORDER_STATUS'] == selected_order_status]

# Product category filter
if selected_category != 'All':
    # Get order_ids for orders containing products in the selected category
    category_products = df_product[df_product['CATEGORY'] == selected_category]['PRODUCT_ID']
    category_order_lines = df_order_line[df_order_line['PRODUCT_ID'].isin(category_products)]
    filtered_orders = filtered_orders[filtered_orders['ORDER_ID'].isin(category_order_lines['ORDER_ID'])]

# Add some spacing
st.markdown("---")

# Sales Analytics with new styling
st.markdown('<h2 class="sub-header">Sales Analytics</h2>', unsafe_allow_html=True)

# Add key metrics with new styling
st.markdown('<h2 class="sub-header">KPIs</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_orders['TOTAL_AMOUNT'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}", "")

with col2:
    total_orders = len(filtered_orders)
    st.metric("Total Orders", f"{total_orders:,}", "")

with col3:
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    st.metric("Average Order Value", f"${avg_order_value:,.2f}", "")

with col4:
    total_customers = filtered_orders['CUSTOMER_ID'].nunique()
    st.metric("Unique Customers", f"{total_customers:,}", "")


# Create tabs for different analysis views
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Overview", "🏪 Channel Performance", "📦 Product Analytics", "👥 Customer Insights"])

# Update all chart configurations
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Sales Trend
        daily_sales = filtered_orders.groupby('ORDER_DATE')['TOTAL_AMOUNT'].sum().reset_index()
        
        chart_daily_sales = alt.Chart(daily_sales).mark_line(
            point=True
        ).encode(
            x=alt.X('ORDER_DATE:T', title='Date'),
            y=alt.Y('TOTAL_AMOUNT:Q', title='Total Sales ($)'),
            tooltip=['ORDER_DATE', alt.Tooltip('TOTAL_AMOUNT:Q', format='$,.2f')]
        ).properties(
            title='Daily Sales Trend'
        )
        
        st.altair_chart(configure_chart(chart_daily_sales.configure_line(
            color=COLOR_SCHEME[0],
            strokeWidth=3
        ).configure_point(
            color=COLOR_SCHEME[0],
            size=100
        )), use_container_width=True)
    
    with col2:
        # Sales by Payment Method
        payment_sales = filtered_orders.groupby('PAYMENT_METHOD')['TOTAL_AMOUNT'].sum().reset_index()
        
        chart_payment = alt.Chart(payment_sales).mark_bar().encode(
            x=alt.X('PAYMENT_METHOD:N', title='Payment Method'),
            y=alt.Y('TOTAL_AMOUNT:Q', title='Total Sales ($)'),
            color=alt.Color('PAYMENT_METHOD:N', scale=alt.Scale(range=COLOR_SCHEME)),
            tooltip=[
                'PAYMENT_METHOD',
                alt.Tooltip('TOTAL_AMOUNT:Q', format='$,.2f')
            ]
        ).properties(
            title='Sales by Payment Method'
        )
        
        st.altair_chart(configure_chart(chart_payment.configure_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        )), use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Channel
        channel_sales = pd.merge(
            filtered_orders,
            df_channel[['CHANNEL_ID', 'CHANNEL_NAME']],
            on='CHANNEL_ID'
        ).groupby('CHANNEL_NAME')['TOTAL_AMOUNT'].sum().reset_index()
        
        chart_channel = alt.Chart(channel_sales).mark_bar().encode(
            x=alt.X('CHANNEL_NAME:N', title='Channel'),
            y=alt.Y('TOTAL_AMOUNT:Q', title='Total Sales ($)'),
            color=alt.Color('CHANNEL_NAME:N', scale=alt.Scale(range=COLOR_SCHEME)),
            tooltip=[
                'CHANNEL_NAME',
                alt.Tooltip('TOTAL_AMOUNT:Q', format='$,.2f')
            ]
        ).properties(
            title='Sales by Channel'
        )
        
        st.altair_chart(configure_chart(chart_channel.configure_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        )), use_container_width=True)
    
    with col2:
        # Channel Order Count
        channel_orders = pd.merge(
            filtered_orders,
            df_channel[['CHANNEL_ID', 'CHANNEL_NAME']],
            on='CHANNEL_ID'
        ).groupby('CHANNEL_NAME').size().reset_index(name='ORDER_COUNT')
        
        chart_channel_orders = alt.Chart(channel_orders).mark_bar().encode(
            x=alt.X('CHANNEL_NAME:N', title='Channel'),
            y=alt.Y('ORDER_COUNT:Q', title='Number of Orders'),
            color=alt.Color('CHANNEL_NAME:N', scale=alt.Scale(range=COLOR_SCHEME)),
            tooltip=['CHANNEL_NAME', 'ORDER_COUNT']
        ).properties(
            title='Number of Orders by Channel'
        )
        
        st.altair_chart(configure_chart(chart_channel_orders.configure_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        )), use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Products by Revenue
        # First join order lines with filtered orders
        product_sales = pd.merge(
            df_order_line,
            filtered_orders[['ORDER_ID']],
            on='ORDER_ID'
        )
        # Then join with products
        product_sales = pd.merge(
            product_sales,
            df_product[['PRODUCT_ID', 'NAME', 'CATEGORY']],
            on='PRODUCT_ID'
        )
        # Calculate revenue
        product_sales['REVENUE'] = product_sales['QUANTITY'] * product_sales['UNIT_PRICE']
        top_products = product_sales.groupby(['NAME', 'CATEGORY'])['REVENUE'].sum().reset_index().sort_values('REVENUE', ascending=False).head(10)
        
        chart_products = alt.Chart(top_products).mark_bar().encode(
            y=alt.Y('NAME:N', sort='-x', title='Product Name'),
            x=alt.X('REVENUE:Q', title='Revenue ($)'),
            color=alt.Color('CATEGORY:N', scale=alt.Scale(range=COLOR_SCHEME)),
            tooltip=[
                'NAME',
                'CATEGORY',
                alt.Tooltip('REVENUE:Q', format='$,.2f')
            ]
        ).properties(
            title='Top 10 Products by Revenue'
        )
        
        st.altair_chart(configure_chart(chart_products.configure_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        )), use_container_width=True)
    
    with col2:
        # Sales by Category
        category_sales = product_sales.groupby('CATEGORY')['REVENUE'].sum().reset_index()
        
        chart_category = alt.Chart(category_sales).mark_arc(innerRadius=50).encode(
            theta='REVENUE:Q',
            color=alt.Color('CATEGORY:N', scale=alt.Scale(range=COLOR_SCHEME)),
            tooltip=[
                'CATEGORY',
                alt.Tooltip('REVENUE:Q', format='$,.2f')
            ]
        ).properties(
            title='Sales Distribution by Category'
        )
        
        st.altair_chart(configure_chart(chart_category), use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Type Distribution
        customer_type_dist = df_customer.groupby('CUSTOMER_TYPE').size().reset_index(name='COUNT')
        
        chart_customer_type = alt.Chart(customer_type_dist).mark_arc().encode(
            theta='COUNT:Q',
            color='CUSTOMER_TYPE:N',
            tooltip=['CUSTOMER_TYPE', 'COUNT']
        ).properties(
            title='Customer Type Distribution',
            height=300
        )
        
        st.altair_chart(chart_customer_type, use_container_width=True)
    
    with col2:
        # Top Customers by Revenue
        customer_revenue = filtered_orders.groupby('CUSTOMER_ID')['TOTAL_AMOUNT'].sum().reset_index()
        top_customers = pd.merge(
            customer_revenue,
            df_customer[['CUSTOMER_ID', 'NAME']],
            on='CUSTOMER_ID'
        ).sort_values('TOTAL_AMOUNT', ascending=False).head(10)
        
        chart_top_customers = alt.Chart(top_customers).mark_bar().encode(
            y=alt.Y('NAME:N', sort='-x'),
            x='TOTAL_AMOUNT:Q',
            tooltip=['NAME', 'TOTAL_AMOUNT']
        ).properties(
            title='Top 10 Customers by Revenue',
            height=300
        )
        
        st.altair_chart(chart_top_customers, use_container_width=True)
st.markdown("---")
# Marketing and Campaign Analytics
st.markdown('<h2 class="sub-header">Marketing & Campaign Performance</h2>', unsafe_allow_html=True)

st.subheader("KPIs")
col1, col2, col3, col4 = st.columns(4)

with col1:
    filtered_campaigns = df_campaign[df_campaign['CAMPAIGN_ID'].isin(
        df_order_campaign_attribution[
            df_order_campaign_attribution['ORDER_ID'].isin(filtered_orders['ORDER_ID'])
        ]['CAMPAIGN_ID']
    )]
    total_campaigns = len(filtered_campaigns)
    st.metric("Active Campaigns", f"{total_campaigns}")

with col2:
    campaign_revenue = pd.merge(
        df_order_campaign_attribution,
        filtered_orders[['ORDER_ID', 'TOTAL_AMOUNT']],
        on='ORDER_ID'
    )
    total_attributed_revenue = (campaign_revenue['TOTAL_AMOUNT'] * campaign_revenue['CONTRIBUTION_PERCENT']).sum()
    st.metric("Attributed Revenue", f"${total_attributed_revenue:,.2f}")

with col3:
    filtered_events = df_digital_event[
        df_digital_event['CUSTOMER_ID'].isin(filtered_orders['CUSTOMER_ID'])
    ]
    total_digital_events = len(filtered_events)
    st.metric("Digital Events", f"{total_digital_events:,}")

with col4:
    filtered_pages = df_page_performance[
        df_page_performance['PAGE_ID'].isin(
            df_content_page[
                df_content_page['DIGITAL_SITE_ID'].isin(filtered_events['DIGITAL_SITE_ID'])
            ]['PAGE_ID']
        )
    ]
    avg_conversion = filtered_pages['CONVERSION_RATE'].mean()
    st.metric("Avg. Conversion Rate", f"{avg_conversion:.2%}")

tab1, tab2 = st.tabs(["📊 Campaign Performance", "📱 Digital Analytics"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Campaign Revenue Attribution
        campaign_revenue = pd.merge(
            df_order_campaign_attribution,
            df_campaign[['CAMPAIGN_ID', 'CAMPAIGN_NAME', 'CAMPAIGN_TYPE']],
            on='CAMPAIGN_ID'
        )
        campaign_revenue = pd.merge(
            campaign_revenue,
            filtered_orders[['ORDER_ID', 'TOTAL_AMOUNT']],
            on='ORDER_ID'
        )
        campaign_revenue['ATTRIBUTED_REVENUE'] = campaign_revenue['TOTAL_AMOUNT'] * campaign_revenue['CONTRIBUTION_PERCENT']
        campaign_performance = campaign_revenue.groupby(['CAMPAIGN_NAME', 'CAMPAIGN_TYPE'])['ATTRIBUTED_REVENUE'].sum().reset_index()
        
        chart_campaign = alt.Chart(campaign_performance).mark_bar().encode(
            y=alt.Y('CAMPAIGN_NAME:N', sort='-x'),
            x='ATTRIBUTED_REVENUE:Q',
            color='CAMPAIGN_TYPE:N',
            tooltip=['CAMPAIGN_NAME', 'CAMPAIGN_TYPE', 'ATTRIBUTED_REVENUE']
        ).properties(
            title='Campaign Revenue Attribution',
            height=300
        )
        
        st.altair_chart(configure_chart(chart_campaign), use_container_width=True)
    
    with col2:
        # Campaign Events Analysis
        campaign_events = pd.merge(
            df_campaign_event,
            df_campaign[['CAMPAIGN_ID', 'CAMPAIGN_NAME']],
            on='CAMPAIGN_ID'
        )
        event_metrics = campaign_events.groupby(['CAMPAIGN_NAME', 'EVENT_TYPE'])['METRIC_VALUE'].sum().reset_index()
        
        chart_events = alt.Chart(event_metrics).mark_bar().encode(
            x='CAMPAIGN_NAME:N',
            y='METRIC_VALUE:Q',
            color='EVENT_TYPE:N',
            tooltip=['CAMPAIGN_NAME', 'EVENT_TYPE', 'METRIC_VALUE']
        ).properties(
            title='Campaign Events Performance',
            height=300
        )
        
        st.altair_chart(configure_chart(chart_events), use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Digital Event Analysis
        digital_events = pd.merge(
            df_digital_event,
            df_digital_site[['DIGITAL_SITE_ID', 'SITE_NAME']],
            on='DIGITAL_SITE_ID'
        )
        event_summary = digital_events.groupby(['SITE_NAME', 'EVENT_TYPE'])['EVENT_VALUE'].agg(['count', 'sum']).reset_index()
        
        chart_digital = alt.Chart(event_summary).mark_bar().encode(
            x='SITE_NAME:N',
            y='count:Q',
            color='EVENT_TYPE:N',
            tooltip=[
                'SITE_NAME', 
                'EVENT_TYPE', 
                alt.Tooltip('count:Q', title='Event Count'),
                alt.Tooltip('sum:Q', title='Total Value', format='$,.2f')
            ]
        ).properties(
            title='Digital Events by Site',
            height=300
        )
        
        st.altair_chart(configure_chart(chart_digital), use_container_width=True)
    
    with col2:
        # Page Performance Analysis
        page_perf = pd.merge(
            df_page_performance,
            df_content_page[['PAGE_ID', 'PAGE_TITLE', 'IS_LANDING_PAGE']],
            on='PAGE_ID'
        )
        top_pages = page_perf.groupby(['PAGE_TITLE', 'IS_LANDING_PAGE'])['VIEWS'].sum().reset_index().sort_values('VIEWS', ascending=False).head(10)
        
        chart_pages = alt.Chart(top_pages).mark_bar().encode(
            y=alt.Y('PAGE_TITLE:N', sort='-x'),
            x='VIEWS:Q',
            color='IS_LANDING_PAGE:N',
            tooltip=['PAGE_TITLE', 'VIEWS', 'IS_LANDING_PAGE']
        ).properties(
            title='Top 10 Pages by Views',
            height=300
        )
        
        st.altair_chart(configure_chart(chart_pages), use_container_width=True)

    # Update the Marketing KPIs section

# Update Inventory section
filtered_inventory = df_inventory.copy()
if selected_category != 'All':
    category_products = df_product[df_product['CATEGORY'] == selected_category]['PRODUCT_ID']
    filtered_inventory = filtered_inventory[filtered_inventory['PRODUCT_ID'].isin(category_products)]

# Update the inventory metrics
total_inventory = filtered_inventory['QUANTITY'].sum()
low_stock = filtered_inventory[filtered_inventory['QUANTITY'] < 10]
low_stock_count = len(low_stock)

# Update fulfillment section
filtered_fulfillment = df_order_fulfillment[
    df_order_fulfillment['ORDER_ID'].isin(filtered_orders['ORDER_ID'])
]

# Convert date columns to datetime
filtered_fulfillment['FULFILLMENT_DATE'] = pd.to_datetime(filtered_fulfillment['FULFILLMENT_DATE'])
filtered_fulfillment['CREATED_AT'] = pd.to_datetime(filtered_fulfillment['CREATED_AT'])

# Calculate fulfillment time in hours
filtered_fulfillment['FULFILLMENT_TIME'] = (filtered_fulfillment['FULFILLMENT_DATE'] - filtered_fulfillment['CREATED_AT']).dt.total_seconds() / 3600

fulfilled_orders = len(filtered_fulfillment[filtered_fulfillment['FULFILLMENT_STATUS'] == 'success'])
total_fulfillment_orders = len(filtered_fulfillment)
fulfillment_rate = fulfilled_orders / total_fulfillment_orders if total_fulfillment_orders > 0 else 0

st.markdown("---")
# Update Inventory and Fulfillment KPIs
st.subheader("Inventory & Fulfillment KPIs")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Inventory", f"{total_inventory:,}")

with col2:
    st.metric("Low Stock Products", f"{low_stock_count}")

with col3:
    st.metric("Fulfillment Rate", f"{fulfillment_rate:.2%}")

with col4:
    avg_fulfillment_time = filtered_fulfillment['FULFILLMENT_TIME'].mean()
    st.metric("Avg Fulfillment Time", f"{avg_fulfillment_time:.1f} hours")