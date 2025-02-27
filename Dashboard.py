import streamlit as st
import pandas as pd
import altair as alt
from keboola_streamlit import KeboolaStreamlit
import plotly.express as px

st.set_page_config(
    page_title="E-commerce Dashboard",
    layout="wide",
    page_icon="🛍️",
)

url = st.secrets["kbc_url"]
token = st.secrets["kbc_token"]
keboola = KeboolaStreamlit(url, token)

df_campaign = pd.read_csv("/data/in/tables/CAMPAIGN.csv")
df_campaign_event = pd.read_csv("/data/in/tables/CAMPAIGN_EVENT.csv") 
df_campaign_performance_metrics = pd.read_csv("/data/in/tables/CAMPAIGN_PERFORMANCE_METRICS.csv")
df_channel = pd.read_csv("/data/in/tables/CHANNEL.csv")
df_company = pd.read_csv("/data/in/tables/COMPANY.csv")
df_content_page = pd.read_csv("/data/in/tables/CONTENT_PAGE.csv")
df_coupon = pd.read_csv("/data/in/tables/COUPON.csv")
df_coupon_redemption = pd.read_csv("/data/in/tables/COUPON_REDEMPTION.csv")
df_custom_attribute = pd.read_csv("/data/in/tables/CUSTOM_ATTRIBUTE.csv")
df_customer = pd.read_csv("/data/in/tables/CUSTOMER.csv")
df_customer_journey = pd.read_csv("/data/in/tables/CUSTOMER_JOURNEY.csv")
df_digital_event = pd.read_csv("/data/in/tables/DIGITAL_EVENT.csv")
df_digital_site = pd.read_csv("/data/in/tables/DIGITAL_SITE.csv")
df_facility = pd.read_csv("/data/in/tables/FACILITY.csv")
df_inventory = pd.read_csv("/data/in/tables/INVENTORY.csv")
df_marketing_funnel_stage = pd.read_csv("/data/in/tables/MARKETING_FUNNEL_STAGE.csv")
df_order_campaign_attribution = pd.read_csv("/data/in/tables/ORDER_CAMPAIGN_ATTRIBUTION.csv")
df_order_event = pd.read_csv("/data/in/tables/ORDER_EVENT.csv")
df_order_fact = pd.read_csv("/data/in/tables/ORDER_FACT.csv")
df_order_fulfillment = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT.csv")
df_order_fulfillment_line = pd.read_csv("/data/in/tables/ORDER_FULFILLMENT_LINE.csv")
df_order_line = pd.read_csv("/data/in/tables/ORDER_LINE.csv")
df_order_status_history = pd.read_csv("/data/in/tables/ORDER_STATUS_HISTORY.csv")
df_page_performance = pd.read_csv("/data/in/tables/PAGE_PERFORMANCE.csv")
df_person = pd.read_csv("/data/in/tables/PERSON.csv")
df_product = pd.read_csv("/data/in/tables/PRODUCT.csv")
df_product_variant = pd.read_csv("/data/in/tables/PRODUCT_VARIANT.csv")
df_sales_plan = pd.read_csv("/data/in/tables/SALES_PLAN.csv")

# Define a consistent color palette at the top of the file after imports
BLUE_PALETTE = ['#1e3d59', '#2b5d8b', '#3ca0ff', '#75c2ff', '#a8d5ff', '#cce4ff']
BLUE_SEQUENTIAL = ['#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594']

# Update the title to include the Keboola logo
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg" alt="Keboola Logo" style="height: 55px; margin-right: 15px;">
        <h1 style="margin: 0;">E-commerce Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.subheader("Filters")
    min_date = pd.to_datetime(df_order_fact['ORDER_DATE']).min()
    max_date = pd.to_datetime(df_order_fact['ORDER_DATE']).max()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    customer_types = ['All'] + list(df_customer['CUSTOMER_TYPE'].unique())
    selected_customer_type = st.selectbox('Customer Type', customer_types)

    channels = ['All'] + list(df_channel['CHANNEL_NAME'].unique())
    selected_channel = st.selectbox('Sales Channel', channels)
    
    categories = ['All'] + list(df_product['CATEGORY'].unique())
    selected_category = st.selectbox('Product Category', categories)

    payment_methods = ['All'] + list(df_order_fact['PAYMENT_METHOD'].unique())
    selected_payment_method = st.selectbox('Payment Method', payment_methods)
    
    order_statuses = ['All'] + list(df_order_fact['ORDER_STATUS'].unique())
    selected_order_status = st.selectbox('Order Status', order_statuses)

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
    


# Apply filters to the main dataframe
filtered_orders = df_order_fact.copy()

# Ensure ORDER_DATE is in datetime format
filtered_orders['ORDER_DATE'] = pd.to_datetime(filtered_orders['ORDER_DATE'])

# Sort by ORDER_DATE
filtered_orders = filtered_orders.sort_values(by='ORDER_DATE')

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
st.header('Sales Analytics')

# Update metric styling
st.markdown(
    """
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        transition: transform 0.2s;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .metric-container:hover {
        transform: scale(1.05);
    }
    .metric-title {
        font-size: 20px;
        font-weight: bold;
    }
    .metric-value {
        font-size: 30px;
        font-weight: normal;
        color: #1e3d59;
    }
    </style>
    """,
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)
""
""
with col1:
    total_revenue = filtered_orders['TOTAL_AMOUNT'].sum()
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">${total_revenue:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    total_orders = len(filtered_orders)
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Average Order Value</div>
            <div class="metric-value">${avg_order_value:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    total_customers = filtered_orders['CUSTOMER_ID'].nunique()
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Unique Customers</div>
            <div class="metric-value">{total_customers:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Create tabs for different analysis views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Sales Overview", "🏪 Channel Performance", "📦 Product Analytics", "👥 Customer Insights", "🔄 Customer Journey"])

# Update all chart configurations
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Sales Trend using Plotly
        
        # Ensure ORDER_DATE is in datetime format
        filtered_orders['ORDER_DATE'] = pd.to_datetime(filtered_orders['ORDER_DATE'])

        # Group by date only
        daily_sales = filtered_orders.groupby(filtered_orders['ORDER_DATE'].dt.date)['TOTAL_AMOUNT'].sum().reset_index()

        fig = px.line(
            daily_sales,
            x='ORDER_DATE',
            y='TOTAL_AMOUNT',
            title='Daily Sales Trend',
            labels={'ORDER_DATE': 'Date', 'TOTAL_AMOUNT': 'Total Sales ($)'},
            markers=True
        )

        fig.update_traces(
            line=dict(color='#1e3d59', width=3), 
            marker=dict(size=10, color='#1e3d59'),
            hovertemplate='Total Sales: $%{y:,.0f}<extra></extra>'
        )
        fig.update_layout(
            yaxis_tickprefix='$',
            margin=dict(t=50),
            yaxis_tickformat=',.0f'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales by Payment Method using Plotly
        payment_sales = filtered_orders.groupby('PAYMENT_METHOD')['TOTAL_AMOUNT'].sum().reset_index()
        
        fig = px.bar(
            payment_sales,
            x='PAYMENT_METHOD',
            y='TOTAL_AMOUNT',
            title='Sales by Payment Method',
            labels={'PAYMENT_METHOD': 'Payment Method', 'TOTAL_AMOUNT': 'Total Sales ($)'},
            color_discrete_sequence=BLUE_PALETTE,
            text='TOTAL_AMOUNT'
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.0f}', 
            textposition='outside',
            hovertemplate='Total Sales: $%{y:,.0f}<extra></extra>'
        )

        fig.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            yaxis_tickprefix='$',  # Add dollar sign to y-axis labels
            yaxis_tickformat=',.0f',  # Format with commas and two decimal places
            showlegend=False,
            margin=dict(t=50),  # Increase top margin
            yaxis=dict(automargin=True)  # Ensure y-axis has enough space
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by Channel using Plotly
        channel_sales = pd.merge(
            filtered_orders,
            df_channel[['CHANNEL_ID', 'CHANNEL_NAME']],
            on='CHANNEL_ID'
        ).groupby('CHANNEL_NAME')['TOTAL_AMOUNT'].sum().reset_index()
        
        fig = px.bar(
            channel_sales,
            x='CHANNEL_NAME',
            y='TOTAL_AMOUNT',
            title='Sales by Channel',
            labels={'CHANNEL_NAME': 'Channel', 'TOTAL_AMOUNT': 'Total Sales ($)'},
            color_discrete_sequence=BLUE_PALETTE,
            text='TOTAL_AMOUNT'
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.0f}', 
            textposition='outside',
            hovertemplate='Total Sales: $%{y:,.0f}<extra></extra>'
        )
        fig.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            yaxis_tickprefix='$',  # Add dollar sign to y-axis labels
            yaxis_tickformat=',.0f',  # Format with commas and two decimal places
            showlegend=True,  # Show legend
            margin=dict(t=50),  # Increase top margin
            yaxis=dict(automargin=True)  # Ensure y-axis has enough space
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Channel Order Count using Plotly
        channel_orders = pd.merge(
            filtered_orders,
            df_channel[['CHANNEL_ID', 'CHANNEL_NAME']],
            on='CHANNEL_ID'
        ).groupby('CHANNEL_NAME').size().reset_index(name='ORDER_COUNT')
        
        fig = px.bar(
            channel_orders,
            x='CHANNEL_NAME',
            y='ORDER_COUNT',
            title='Number of Orders by Channel',
            labels={'CHANNEL_NAME': 'Channel', 'ORDER_COUNT': 'Number of Orders'},
            color_discrete_sequence=BLUE_PALETTE,
            text='ORDER_COUNT'
        )
        
        fig.update_traces(
            texttemplate='%{text}', 
            textposition='outside',
            hovertemplate='Number of Orders: %{y}<extra></extra>'
        )
        fig.update_layout(
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            showlegend=False,
            margin=dict(t=50),  # Increase top margin
            yaxis=dict(automargin=True)  # Ensure y-axis has enough space
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        # Top Products by Revenue using Plotly

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
        
        # Apply category filter at the product level
        if selected_category != 'All':
            product_sales = product_sales[product_sales['CATEGORY'] == selected_category]
        
        # Calculate revenue
        product_sales['REVENUE'] = product_sales['QUANTITY'] * product_sales['UNIT_PRICE']
        top_products = product_sales.groupby(['NAME', 'CATEGORY'])['REVENUE'].sum().reset_index()
        
        # Sort by revenue and get top 10
        top_products = top_products.sort_values('REVENUE', ascending=False).head(10)
        fig = px.bar(
            top_products,
            x='REVENUE',
            y='NAME',
            color='CATEGORY',
            title='Top 10 Products by Revenue',
            labels={'REVENUE': 'Revenue ($)', 'NAME': 'Product Name'},
            text='REVENUE',
            orientation='h',
            color_discrete_sequence=BLUE_PALETTE
        )
        
        fig.update_traces(
            texttemplate='$%{x:,.0f}',  # Display revenue value
            textposition='inside',
            insidetextanchor='start',
            hovertemplate='Product: %{y}<br>Revenue: $%{x:,.0f}<extra></extra>'
        )
        fig.update_layout(
            yaxis=dict(
                categoryorder='total ascending',  # Sort by revenue
                title=None  # Remove y-axis title
            ),
            margin=dict(t=50, l=10),  # Adjust margins
            xaxis_tickprefix='$',
            xaxis_tickformat=',.2f',
            showlegend=True,  # Show category legend
            legend_title='Category',
            height=400  # Fixed height for better readability
        )
        
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Sales by Category - using the already filtered product_sales
        category_sales = product_sales.groupby('CATEGORY')['REVENUE'].sum().reset_index()
        
        # Sort categories by revenue
        category_sales = category_sales.sort_values('REVENUE', ascending=False)

        fig = px.pie(
            category_sales,
            values='REVENUE',
            names='CATEGORY',
            title='Sales Distribution by Category',
            color_discrete_sequence=BLUE_PALETTE
        )

        fig.update_traces(
            textinfo='label+percent',  # Show label and percentage inside the pie chart
            texttemplate='%{label}: $%{value:,.0f}',  # Add dollar sign and round to whole number
            hovertemplate='%{label}: $%{value:,.0f} (%{percent})<extra></extra>'  # Add dollar sign and round to whole number
        )
        fig.update_layout(
            margin=dict(t=50, b=50, l=20, r=20),
            height=400,
            showlegend=False  # Hide legend since labels are shown in pie
        )

        # Update layout to position the legend below the chart
        fig.update_layout(
            margin=dict(t=50, b=50, l=50, r=50),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.2,  # Position below the chart
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Type Distribution using Plotly
        customer_type_dist = df_customer.groupby('CUSTOMER_TYPE').size().reset_index(name='COUNT')
        
        fig = px.pie(
            customer_type_dist,
            values='COUNT',
            names='CUSTOMER_TYPE',
            title='Customer Type Distribution',
            height=400,
            hole=0.3,  # Optional: to create a donut chart
            color_discrete_sequence=BLUE_PALETTE
        )
        
        fig.update_traces(
            textinfo='value',  # Show label and value inside the pie chart
            hovertemplate='%{label}: %{value} (%{percent})<extra></extra>'
        )
        
        # Update layout to position the legend below the chart
        fig.update_layout(
            margin=dict(t=50, b=50, l=50, r=50),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.2,  # Position below the chart
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top Customers by Revenue using Plotly
        customer_revenue = filtered_orders.groupby('CUSTOMER_ID')['TOTAL_AMOUNT'].sum().reset_index()
        top_customers = pd.merge(
            customer_revenue,
            df_customer[['CUSTOMER_ID', 'NAME']],
            on='CUSTOMER_ID'
        ).sort_values('TOTAL_AMOUNT', ascending=False).head(10)
        
        fig = px.bar(
            top_customers,
            x='TOTAL_AMOUNT',
            y='NAME',
            orientation='h',  # Horizontal bar chart
            title='Top 10 Customers by Revenue',
            labels={'TOTAL_AMOUNT': 'Revenue ($)', 'NAME': 'Customer Name'},
            text='TOTAL_AMOUNT',
            color_discrete_sequence=[BLUE_PALETTE[0]]
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.0f}',  # Format text with dollar sign and two decimal places
            insidetextanchor='start',
            textposition='inside'  # Position text inside the bar
        )
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),  # Sort by revenue
            margin=dict(t=50),  # Increase top margin
            xaxis_tickprefix='$',  # Add dollar sign to x-axis labels
            xaxis_tickformat=',.2f',  # Format with commas and two decimal places
            showlegend=False  # Remove the legend
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab5:

    # Customer Purchase Frequency
    purchase_frequency = filtered_orders.groupby('CUSTOMER_ID').size().value_counts().reset_index()
    purchase_frequency.columns = ['Orders_Made', 'Customer_Count']
    
    fig = px.bar(
        purchase_frequency,
        x='Orders_Made',
        y='Customer_Count',
        title='Customer Purchase Frequency Distribution',
        labels={'Orders_Made': 'Number of Orders', 'Customer_Count': 'Number of Customers'},
        text='Customer_Count',
        color='Orders_Made',
        color_continuous_scale=BLUE_SEQUENTIAL
    )
    
    fig.update_traces(
        textposition='outside',
        hovertemplate='Number of Customers: %{y}<br>Number of Orders: %{x}<extra></extra>'
    )
    fig.update_layout(
        yaxis=dict(title='Number of Customers'),
        xaxis=dict(
            title='Number of Orders',
            dtick=1  # Set tick interval to 1 to show every number
        ),
        margin=dict(t=50)  # Adjust top margin
    )
    
    st.plotly_chart(fig, use_container_width=True)


st.markdown("---")
# Marketing and Campaign Analytics
st.header("Marketing & Campaign Performance")

col1, col2, col3, col4 = st.columns(4)
""
""

with col1:
    total_campaigns = df_campaign['CAMPAIGN_ID'].nunique()
    st.markdown(
    f"""
    <div class="metric-container">
        <div class="metric-title">Active Campaigns</div>
        <div class="metric-value">{total_campaigns}</div>
    </div>
    """,
    unsafe_allow_html=True
)

with col2:
    campaign_revenue = pd.merge(
        df_order_campaign_attribution,
        filtered_orders[['ORDER_ID', 'TOTAL_AMOUNT']],
        on='ORDER_ID'
    )
    total_attributed_revenue = (campaign_revenue['TOTAL_AMOUNT'] * campaign_revenue['CONTRIBUTION_PERCENT']).sum()
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Attributed Revenue</div>
            <div class="metric-value">${total_attributed_revenue:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    filtered_events = df_digital_event[
        df_digital_event['CUSTOMER_ID'].isin(filtered_orders['CUSTOMER_ID'])
    ]
    total_digital_events = len(filtered_events)
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Digital Events</div>
            <div class="metric-value">{total_digital_events:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    filtered_pages = df_page_performance[
        df_page_performance['PAGE_ID'].isin(
            df_content_page[
                df_content_page['DIGITAL_SITE_ID'].isin(filtered_events['DIGITAL_SITE_ID'])
            ]['PAGE_ID']
        )
    ]
    avg_conversion = filtered_pages['CONVERSION_RATE'].mean()
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-title">Avg. Conversion Rate</div>
            <div class="metric-value">{avg_conversion:.2%}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
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
        
        fig = px.bar(
            campaign_performance,
            x='CAMPAIGN_NAME',
            y='ATTRIBUTED_REVENUE',
            color='CAMPAIGN_TYPE',
            title='Campaign Revenue Attribution',
            labels={'CAMPAIGN_NAME': 'Campaign', 'ATTRIBUTED_REVENUE': 'Revenue ($)'},
            text='ATTRIBUTED_REVENUE',
            color_discrete_sequence=BLUE_PALETTE
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.2f}',  # Format text with dollar sign and two decimal places
            textposition='outside'  # Position text outside the bar
        )
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),  # Sort by revenue
            margin=dict(t=50),  # Increase top margin
            xaxis_tickprefix='$',  # Add dollar sign to x-axis labels
            xaxis_tickformat=',.2f',  # Format with commas and two decimal places
            showlegend=False  # Remove the legend
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Campaign Events Analysis
        campaign_events = pd.merge(
            df_campaign_event,
            df_campaign[['CAMPAIGN_ID', 'CAMPAIGN_NAME']],
            on='CAMPAIGN_ID'
        )
        event_metrics = campaign_events.groupby(['CAMPAIGN_NAME', 'EVENT_TYPE'])['METRIC_VALUE'].sum().reset_index()
        
        fig = px.bar(
            event_metrics,
            x='CAMPAIGN_NAME',
            y='METRIC_VALUE',
            color='EVENT_TYPE',
            title='Campaign Events Performance',
            labels={'CAMPAIGN_NAME': 'Campaign', 'METRIC_VALUE': 'Metric Value'},
            text='METRIC_VALUE',
            color_discrete_sequence=BLUE_PALETTE
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.2f}',  # Format text with dollar sign and two decimal places
            textposition='outside'  # Position text outside the bar
        )
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),  # Sort by revenue
            margin=dict(t=50),  # Increase top margin
            xaxis_tickprefix='$',  # Add dollar sign to x-axis labels
            xaxis_tickformat=',.2f',  # Format with commas and two decimal places
            showlegend=False  # Remove the legend
        )
        
        st.plotly_chart(fig, use_container_width=True)

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
        
        fig = px.bar(
            event_summary,
            x='SITE_NAME',
            y='count',
            color='EVENT_TYPE',
            title='Digital Events by Site',
            labels={'SITE_NAME': 'Site', 'count': 'Event Count'},
            text='count',
            color_discrete_sequence=BLUE_PALETTE
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.2f}',  # Format text with dollar sign and two decimal places
            textposition='outside'  # Position text outside the bar
        )
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),  # Sort by revenue
            margin=dict(t=50),  # Increase top margin
            xaxis_tickprefix='$',  # Add dollar sign to x-axis labels
            xaxis_tickformat=',.2f',  # Format with commas and two decimal places
            showlegend=False  # Remove the legend
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Page Performance Analysis
        page_perf = pd.merge(
            df_page_performance,
            df_content_page[['PAGE_ID', 'PAGE_TITLE', 'IS_LANDING_PAGE']],
            on='PAGE_ID'
        )
        top_pages = page_perf.groupby(['PAGE_TITLE', 'IS_LANDING_PAGE'])['VIEWS'].sum().reset_index().sort_values('VIEWS', ascending=False).head(10)
        
        fig = px.bar(
            top_pages,
            x='PAGE_TITLE',
            y='VIEWS',
            color='IS_LANDING_PAGE',
            title='Top 10 Pages by Views',
            labels={'PAGE_TITLE': 'Page Title', 'VIEWS': 'Views'},
            text='VIEWS',
            color_discrete_sequence=[BLUE_PALETTE[0], BLUE_PALETTE[2]]
        )
        
        fig.update_traces(
            texttemplate='%{text:$,.2f}',  # Format text with dollar sign and two decimal places
            textposition='outside'  # Position text outside the bar
        )
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending'),  # Sort by revenue
            margin=dict(t=50),  # Increase top margin
            xaxis_tickprefix='$',  # Add dollar sign to x-axis labels
            xaxis_tickformat=',.2f',  # Format with commas and two decimal places
            showlegend=False  # Remove the legend
        )
        
        st.plotly_chart(fig, use_container_width=True)


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64



# Apply custom styling with blue color scheme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0D47A1;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1565C0;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #E3F2FD;
        border-radius: 5px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-title {
        font-size: 1rem;
        color: #1976D2;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0D47A1;
    }
    .card {
        border-radius: 5px;
        background-color: #E3F2FD;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1565C0;
    }
    /* Custom CSS for metrics rows */
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #BBDEFB;
        border-radius: 4px 4px 0 0;
        color: #0D47A1;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976D2 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)
    # Define a consistent color mapping for categories

# Function to set consistent blue-themed Plotly styling
def set_blue_theme_plotly(fig):
    """Apply a consistent blue theme to Plotly figures"""
    fig.update_layout(
        plot_bgcolor='#F5F9FF',
        paper_bgcolor='#F5F9FF',
        font_color='#0D47A1',
        title_font_color='#0D47A1',
        legend_title_font_color='#0D47A1',
        colorway=['#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#2196F3', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB'],
    )
    fig.update_xaxes(gridcolor='#BBDEFB', zerolinecolor='#BBDEFB')
    fig.update_yaxes(gridcolor='#BBDEFB', zerolinecolor='#BBDEFB')
    return fig


category_colors = {
    'Electronics': px.colors.qualitative.Bold[2],  # Darker blue
    'Clothing': px.colors.qualitative.Bold[3],     # Medium dark blue
    'Home': px.colors.qualitative.Bold[4],         # Medium blue
    'Beauty': px.colors.qualitative.Bold[5],       # Light blue
    'Food': px.colors.qualitative.Bold[6]          # Very light blue
}
    
@st.cache_data
def load_data():
    """Load all tables from the database"""
    try:
        # In a real scenario, you would connect to your database
        # Here we're simulating the data load
        
        # Create sample data for demonstration
        # CUSTOMER table
        customers = pd.DataFrame({
            'customer_id': [f'C{i}' for i in range(1, 101)],
            'customer_type': np.random.choice(['person', 'company'], 100),
            'name': [f'Customer {i}' for i in range(1, 101)],
            'created_at': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        })
        
        # PERSON table
        person_indices = customers[customers['customer_type'] == 'person'].index
        persons = pd.DataFrame({
            'customer_id': customers.loc[person_indices, 'customer_id'].values,
            'first_name': [f'First{i}' for i in range(len(person_indices))],
            'last_name': [f'Last{i}' for i in range(len(person_indices))],
            'gender': np.random.choice(['M', 'F', 'Other'], len(person_indices)),
        })
        
        # COMPANY table
        company_indices = customers[customers['customer_type'] == 'company'].index
        companies = pd.DataFrame({
            'customer_id': customers.loc[company_indices, 'customer_id'].values,
            'company_name': [f'Company {i}' for i in range(len(company_indices))],
            'tax_id': [f'TAX{i}' for i in range(len(company_indices))],
        })
        
        # PRODUCT table
        products = pd.DataFrame({
            'product_id': [f'P{i}' for i in range(1, 51)],
            'name': [f'Product {i}' for i in range(1, 51)],
            'category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Beauty', 'Food'], 50),
            'price': np.random.uniform(10, 1000, 50).round(2),
            'active': np.random.choice([True, False], 50, p=[0.9, 0.1]),
        })
        
        # CHANNEL table
        channels = pd.DataFrame({
            'channel_id': [f'CH{i}' for i in range(1, 6)],
            'channel_name': ['Web Store', 'Mobile App', 'Physical Store', 'Partner', 'Marketplace'],
            'channel_type': ['Digital', 'Digital', 'Physical', 'Partner', 'Digital'],
        })
        
        # FACILITY table
        facilities = pd.DataFrame({
            'facility_id': [f'F{i}' for i in range(1, 11)],
            'facility_name': [f'Facility {i}' for i in range(1, 11)],
            'facility_type': np.random.choice(['Warehouse', 'Store', 'Distribution Center'], 10),
            'country': np.random.choice(['USA', 'Canada', 'UK', 'Germany', 'France'], 10),
            'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], 10),
        })
        
        # ORDER_FACT table
        order_dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        num_orders = 538
        orders = pd.DataFrame({
            'order_id': [f'O{i}' for i in range(1, num_orders + 1)],
            'order_date': np.random.choice(order_dates, num_orders),
            'customer_id': np.random.choice(customers['customer_id'], num_orders),
            'channel_id': np.random.choice(channels['channel_id'], num_orders),
            'facility_id': np.random.choice(facilities['facility_id'], num_orders),
            'total_amount': np.random.uniform(50, 5000, num_orders).round(2),
            'currency': 'USD',
            'order_status': np.random.choice(['Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled'], num_orders),
            'order_type': np.random.choice(['Standard', 'Express', 'Gift', 'Return'], num_orders, p=[0.7, 0.2, 0.05, 0.05]),
        })
        
        # ORDER_LINE table
        num_order_lines = 1500
        order_lines = pd.DataFrame({
            'order_line_id': [f'OL{i}' for i in range(1, num_order_lines + 1)],
            'order_id': np.random.choice(orders['order_id'], num_order_lines),
            'product_id': np.random.choice(products['product_id'], num_order_lines),
            'quantity': np.random.randint(1, 10, num_order_lines),
            'unit_price': np.random.uniform(10, 500, num_order_lines).round(2),
            'discount_amount': np.random.uniform(0, 50, num_order_lines).round(2),
        })
        
        # CAMPAIGN table
        campaigns = pd.DataFrame({
            'campaign_id': [f'CAM{i}' for i in range(1, 21)],
            'campaign_name': [f'Campaign {i}' for i in range(1, 21)],
            'campaign_type': np.random.choice(['Email', 'Social', 'Display', 'Search', 'TV'], 20),
            'start_date': pd.date_range(start='2023-01-01', periods=20, freq='15D'),
            'end_date': pd.date_range(start='2023-01-15', periods=20, freq='15D'),
            'budget': np.random.uniform(5000, 50000, 20).round(2),
        })
        
        # ORDER_CAMPAIGN_ATTRIBUTION table
        num_attributions = 400
        attributions = pd.DataFrame({
            'attribution_id': [f'ATT{i}' for i in range(1, num_attributions + 1)],
            'order_id': np.random.choice(orders['order_id'], num_attributions),
            'campaign_id': np.random.choice(campaigns['campaign_id'], num_attributions),
            'attribution_model': np.random.choice(['Last Click', 'First Click', 'Linear', 'Time Decay'], num_attributions),
            'contribution_percent': np.random.uniform(0.1, 1.0, num_attributions).round(2),
        })
        
        # DIGITAL_SITE table
        digital_sites = pd.DataFrame({
            'digital_site_id': [f'DS{i}' for i in range(1, 6)],
            'site_name': ['Main Website', 'Mobile Site', 'Partner Portal', 'Affiliate Site', 'Landing Pages'],
            'domain': ['example.com', 'm.example.com', 'partners.example.com', 'deals.example.com', 'promo.example.com'],
            'platform_type': ['Web', 'Mobile Web', 'Web', 'Web', 'Web'],
        })
        
        # DIGITAL_EVENT table
        num_events = 2000
        event_types = ['PageView', 'AddToCart', 'Purchase', 'Search', 'ProductView', 'Login', 'Registration']
        digital_events = pd.DataFrame({
            'event_id': [f'EV{i}' for i in range(1, num_events + 1)],
            'event_date': pd.date_range(start='2023-01-01', end='2023-12-31', periods=num_events),
            'customer_id': np.random.choice(list(customers['customer_id']) + [None] * 200, num_events),
            'digital_site_id': np.random.choice(digital_sites['digital_site_id'], num_events),
            'event_type': np.random.choice(event_types, num_events, 
                                          p=[0.4, 0.2, 0.1, 0.1, 0.1, 0.05, 0.05]),
            'device_type': np.random.choice(['Desktop', 'Mobile', 'Tablet'], num_events, p=[0.5, 0.4, 0.1]),
        })
        
        # INVENTORY table
        inventory = pd.DataFrame({
            'inventory_id': [f'INV{i}' for i in range(1, 101)],
            'product_id': np.random.choice(products['product_id'], 100),
            'facility_id': np.random.choice(facilities['facility_id'], 100),
            'quantity': np.random.randint(0, 1000, 100),
            'last_updated': pd.date_range(start='2023-01-01', periods=100, freq='3D'),
        })
        
        # PAGE_PERFORMANCE table
        num_page_performances = 500
        page_performance = pd.DataFrame({
            'performance_id': [f'PP{i}' for i in range(1, num_page_performances + 1)],
            'page_id': [f'PG{i}' for i in range(1, 21)] * 25,
            'date': np.sort(np.random.choice(pd.date_range(start='2023-01-01', end='2023-12-31'), num_page_performances)),
            'views': np.random.randint(10, 5000, num_page_performances),
            'unique_visitors': np.random.randint(5, 3000, num_page_performances),
            'bounce_rate': np.random.uniform(0.1, 0.9, num_page_performances).round(2),
            'avg_time_on_site': np.random.uniform(10, 300, num_page_performances).round(2),
            'conversion_rate': np.random.uniform(0.01, 0.2, num_page_performances).round(3),
        })
        
        return {
            'customers': customers,
            'persons': persons,
            'companies': companies,
            'products': products,
            'orders': orders,
            'order_lines': order_lines,
            'channels': channels,
            'facilities': facilities,
            'campaigns': campaigns,
            'attributions': attributions,
            'digital_sites': digital_sites,
            'digital_events': digital_events,
            'inventory': inventory,
            'page_performance': page_performance
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

# Function to create a data model visualization
def create_data_model_diagram():
    """Create a visualization of the entity-relationship diagram"""
    G = nx.DiGraph()
    
    # Add nodes for each entity
    entities = [
        "CUSTOMER", "PERSON", "COMPANY", "ORDER_FACT", "ORDER_LINE", "PRODUCT", 
        "PRODUCT_VARIANT", "INVENTORY", "CHANNEL", "FACILITY", "DIGITAL_SITE", 
        "DIGITAL_EVENT", "CAMPAIGN", "ORDER_CAMPAIGN_ATTRIBUTION"
    ]
    
    # Define node colors - various shades of blue
    node_colors = {
        "CUSTOMER": "#1565C0",      # Darker blue
        "PERSON": "#1976D2",
        "COMPANY": "#1976D2",
        "ORDER_FACT": "#1E88E5",    # Medium blue
        "ORDER_LINE": "#1E88E5",
        "PRODUCT": "#42A5F5",       # Lighter blue
        "PRODUCT_VARIANT": "#42A5F5",
        "INVENTORY": "#42A5F5",
        "CHANNEL": "#64B5F6",       # Pale blue
        "FACILITY": "#64B5F6",
        "DIGITAL_SITE": "#64B5F6",
        "DIGITAL_EVENT": "#64B5F6",
        "CAMPAIGN": "#90CAF9",      # Very light blue
        "ORDER_CAMPAIGN_ATTRIBUTION": "#90CAF9"
    }
    
    # Add nodes for each entity with appropriate colors
    for entity in entities:
        G.add_node(entity, color=node_colors[entity])
    
    # Add edges for relationships
    relationships = [
        ("CUSTOMER", "PERSON", "is a"),
        ("CUSTOMER", "COMPANY", "is a"),
        ("CUSTOMER", "ORDER_FACT", "places"),
        ("ORDER_FACT", "ORDER_LINE", "contains"),
        ("PRODUCT", "ORDER_LINE", "sold in"),
        ("PRODUCT", "PRODUCT_VARIANT", "has variants"),
        ("CHANNEL", "ORDER_FACT", "channel"),
        ("FACILITY", "ORDER_FACT", "fulfills"),
        ("INVENTORY", "PRODUCT", "for"),
        ("INVENTORY", "FACILITY", "at"),
        ("CAMPAIGN", "ORDER_CAMPAIGN_ATTRIBUTION", "drives"),
        ("DIGITAL_SITE", "DIGITAL_EVENT", "occurs on"),
    ]
    
    for src, tgt, label in relationships:
        G.add_edge(src, tgt, label=label)
    
    # Create the plot
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes with their designated colors
    node_colors_list = [node_colors[node] for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=node_colors_list, alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, arrows=True, arrowsize=20, edge_color="#0D47A1")
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", font_color="white")
    
    # Draw edge labels
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color="#0D47A1")
    
    plt.axis("off")
    plt.tight_layout()
    
    # Set background color for the figure to a very light blue
    plt.gcf().set_facecolor('#F5F9FF')
    
    # Save figure to BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor='#F5F9FF')
    plt.close()
    buf.seek(0)
    
    # Encode the image to base64 for display in Streamlit
    img_str = base64.b64encode(buf.read()).decode()
    return img_str

# Function to create sales analysis
def create_sales_dashboard(orders, order_lines, products, channels):
    

    """Create a sales dashboard with key metrics and visualizations"""
    # Calculate key metrics
    total_revenue = orders['total_amount'].sum()
    total_orders = len(orders)
    avg_order_value = total_revenue / total_orders
    
    # Merge orders with order lines for product-level analysis
    sales_data = order_lines.merge(orders, on='order_id')
    sales_data = sales_data.merge(products[['product_id', 'name', 'category']], on='product_id')
    
    # Add revenue calculation
    sales_data['revenue'] = sales_data['quantity'] * sales_data['unit_price'] - sales_data['discount_amount']
    
    # Sales by channel
    channel_sales = sales_data.merge(channels, on='channel_id')
    channel_sales = channel_sales.groupby(['channel_name', 'channel_type'])['revenue'].sum().reset_index()
    
    # Sales by category
    category_sales = sales_data.groupby('category')['revenue'].sum().reset_index()
    
    # Sales trend over time
    sales_data['order_date'] = pd.to_datetime(sales_data['order_date'])
    sales_data['month'] = sales_data['order_date'].dt.to_period('M')
    monthly_sales = sales_data.groupby('month')['revenue'].sum().reset_index()
    monthly_sales['month'] = monthly_sales['month'].astype(str)
    
    # Create visualizations
    
    # Channel sales chart
    channel_fig = px.bar(
        channel_sales, 
        x='channel_name', 
        y='revenue', 
        color='channel_type',
        title='Revenue by Channel',
        #color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Category sales chart
    category_fig = px.pie(
        category_sales, 
        values='revenue', 
        names='category',
        title='Revenue by Product Category',
        hole=0.4,
        color_discrete_map=category_colors  # Apply category styling
    )
    
    # Monthly sales trend
    trend_fig = px.line(
        monthly_sales, 
        x='month', 
        y='revenue',
        title='Monthly Sales Trend', 
        markers=True,
        line_shape="spline"
    )
    trend_fig.update_xaxes(tickangle=45)
    
    return {
        'metrics': {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value
        },
        'charts': {
            'channel_fig': channel_fig,
            'category_fig': category_fig,
            'trend_fig': trend_fig
        }
    }

# Function to create customer analysis
def create_customer_analysis(customers, orders, persons, companies):
    """Create customer analysis visualizations"""
    # Merge orders with customers
    customer_orders = orders.merge(customers, on='customer_id')
    
    # Customer type distribution
    customer_type_counts = customers['customer_type'].value_counts().reset_index()
    customer_type_counts.columns = ['customer_type', 'count']
    
    # Customer acquisition over time
    customers['created_at'] = pd.to_datetime(customers['created_at'])
    customers['month'] = customers['created_at'].dt.to_period('M')
    monthly_acquisition = customers.groupby(['month', 'customer_type']).size().reset_index(name='count')
    monthly_acquisition['month'] = monthly_acquisition['month'].astype(str)
    
    # Customer spending analysis
    customer_spending = customer_orders.groupby('customer_id')['total_amount'].agg(['sum', 'count']).reset_index()
    customer_spending.columns = ['customer_id', 'total_spent', 'order_count']
    customer_spending['avg_order_value'] = customer_spending['total_spent'] / customer_spending['order_count']
    
    # Merge with customer type
    customer_spending = customer_spending.merge(customers[['customer_id', 'customer_type']], on='customer_id')
    
    # Create visualizations
    
    # Customer type distribution
    type_fig = px.pie(
        customer_type_counts, 
        values='count', 
        names='customer_type',
        title='Customer Type Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Customer acquisition trend
    acquisition_fig = px.bar(
        monthly_acquisition, 
        x='month', 
        y='count', 
        color='customer_type',
        title='Monthly Customer Acquisition',
        barmode='group'
    )
    acquisition_fig.update_xaxes(tickangle=45)
    
    # Customer spending by type
    spending_fig = px.scatter(
        customer_spending, 
        x='total_spent', 
        y='avg_order_value', 
        color='customer_type',
        size='order_count',
        opacity=0.7,
        hover_data=['customer_id'],
        title='Customer Spending Analysis'
    )
    
    return {
        'charts': {
            'type_fig': type_fig,
            'acquisition_fig': acquisition_fig,
            'spending_fig': spending_fig
        }
    }

# Function to create digital analysis dashboard
def create_digital_analysis(digital_events, digital_sites, page_performance):
    """Create digital analytics dashboard"""
    # Event analysis
    event_counts = digital_events['event_type'].value_counts().reset_index()
    event_counts.columns = ['event_type', 'count']
    
    # Device analysis
    device_counts = digital_events['device_type'].value_counts().reset_index()
    device_counts.columns = ['device_type', 'count']
    
    # Page performance trend
    page_performance['date'] = pd.to_datetime(page_performance['date'])
    page_performance['month'] = page_performance['date'].dt.to_period('M')
    monthly_performance = page_performance.groupby('month').agg({
        'views': 'sum',
        'unique_visitors': 'sum',
        'bounce_rate': 'mean',
        'conversion_rate': 'mean'
    }).reset_index()
    monthly_performance['month'] = monthly_performance['month'].astype(str)
    
    # Create visualizations
    
    # Event distribution
    event_fig = px.bar(
        event_counts, 
        x='event_type', 
        y='count', 
        title='Digital Event Distribution',
        color='event_type',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Device distribution
    device_fig = px.pie(
        device_counts, 
        values='count', 
        names='device_type',
        title='Device Type Distribution',
        #color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    
    # Performance trend
    performance_fig = go.Figure()
    performance_fig.add_trace(go.Scatter(
        x=monthly_performance['month'], 
        y=monthly_performance['views'], 
        mode='lines+markers',
        name='Views'
    ))
    performance_fig.add_trace(go.Scatter(
        x=monthly_performance['month'], 
        y=monthly_performance['unique_visitors'], 
        mode='lines+markers',
        name='Unique Visitors'
    ))
    performance_fig.update_layout(
        title='Monthly Website Traffic',
        xaxis_title='Month',
        yaxis_title='Count',
        legend_title='Metric'
    )
    
    # Conversion trend
    conversion_fig = go.Figure()
    conversion_fig.add_trace(go.Scatter(
        x=monthly_performance['month'], 
        y=monthly_performance['conversion_rate'] * 100, 
        mode='lines+markers',
        name='Conversion Rate (%)',
        line=dict(color='green')
    ))
    conversion_fig.add_trace(go.Scatter(
        x=monthly_performance['month'], 
        y=monthly_performance['bounce_rate'] * 100, 
        mode='lines+markers',
        name='Bounce Rate (%)',
        line=dict(color='red')
    ))
    conversion_fig.update_layout(
        title='Conversion and Bounce Rate Trends',
        xaxis_title='Month',
        yaxis_title='Rate (%)',
        legend_title='Metric'
    )
    
    return {
        'charts': {
            'event_fig': event_fig,
            'device_fig': device_fig,
            'performance_fig': performance_fig,
            'conversion_fig': conversion_fig
        }
    }

# Function to create inventory analysis
def create_inventory_analysis(inventory, products, facilities):
    """Create inventory analysis visualizations"""
    # Merge inventory with products and facilities
    inventory_data = inventory.merge(products[['product_id', 'name', 'category']], on='product_id')
    inventory_data = inventory_data.merge(facilities[['facility_id', 'facility_name', 'facility_type', 'region']], on='facility_id')
    
    # Inventory by facility type
    facility_inventory = inventory_data.groupby(['facility_type', 'region'])['quantity'].sum().reset_index()
    
    # Inventory by product category
    category_inventory = inventory_data.groupby('category')['quantity'].sum().reset_index()
    
    # Top products by inventory
    product_inventory = inventory_data.groupby(['name', 'category'])['quantity'].sum().reset_index().sort_values('quantity', ascending=False).head(10)
    
    # Create visualizations
    

    
    # Facility inventory
    facility_fig = px.bar(
        facility_inventory, 
        x='facility_type', 
        y='quantity', 
        color='region',
        title='Inventory by Facility Type and Region',
        barmode='group'
    )
    
    # Category inventory
    category_fig = px.pie(
        category_inventory, 
        values='quantity', 
        names='category',
        title='Inventory by Product Category',
        color='category',
        color_discrete_map=category_colors
    )
    
    # Top products inventory
    product_fig = px.bar(
        product_inventory, 
        x='name', 
        y='quantity', 
        color='category',
        title='Top 10 Products by Inventory Quantity',
        color_discrete_map=category_colors
    )
    product_fig.update_layout(xaxis={'categoryorder':'total descending'})
    
    return {
        'charts': {
            'facility_fig': facility_fig,
            'category_fig': category_fig,
            'product_fig': product_fig
        }
    }

# Function to create campaign analysis
def create_campaign_analysis(campaigns, attributions, orders):
    """Create campaign analysis visualizations"""
    # Merge attributions with campaigns and orders
    campaign_data = attributions.merge(campaigns[['campaign_id', 'campaign_name', 'campaign_type', 'budget']], on='campaign_id')
    campaign_data = campaign_data.merge(orders[['order_id', 'total_amount']], on='order_id')
    
    # Calculate attributed revenue
    campaign_data['attributed_revenue'] = campaign_data['total_amount'] * campaign_data['contribution_percent']
    
    # Campaign performance by type
    type_performance = campaign_data.groupby('campaign_type').agg({
        'attributed_revenue': 'sum',
        'budget': 'sum'
    }).reset_index()
    type_performance['roi'] = (type_performance['attributed_revenue'] / type_performance['budget']).round(2)
    
    # Campaign performance
    campaign_performance = campaign_data.groupby(['campaign_id', 'campaign_name', 'campaign_type']).agg({
        'attributed_revenue': 'sum',
        'budget': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    campaign_performance.columns = ['campaign_id', 'campaign_name', 'campaign_type', 'attributed_revenue', 'budget', 'orders']
    campaign_performance['roi'] = (campaign_performance['attributed_revenue'] / campaign_performance['budget']).round(2)
    campaign_performance = campaign_performance.sort_values('attributed_revenue', ascending=False)
    
    # Attribution model analysis
    model_performance = campaign_data.groupby('attribution_model')['attributed_revenue'].sum().reset_index()
    
    # Create visualizations
    
    # Campaign type performance
    type_fig = px.bar(
        type_performance, 
        x='campaign_type', 
        y=['attributed_revenue', 'budget'],
        title='Campaign Performance by Type',
        barmode='group'
    )
    
    # Add ROI as line
    roi_fig = px.line(
        type_performance, 
        x='campaign_type', 
        y='roi', 
        title='ROI by Campaign Type'
    )
    roi_fig.update_traces(yaxis="y2")
    
    # Create a combined figure
    combined_fig = go.Figure(data=type_fig.data + roi_fig.data)
    combined_fig.update_layout(
        yaxis2=dict(
            title="ROI",
            overlaying="y",
            side="right"
        ),
        title='Campaign Performance and ROI by Type'
    )
    
    # Top campaigns
    campaign_fig = px.bar(
        campaign_performance.head(10), 
        x='campaign_name', 
        y='attributed_revenue', 
        color='campaign_type',
        hover_data=['roi', 'orders'],
        title='Top 10 Campaigns by Attributed Revenue',
        #color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Attribution model comparison
    model_fig = px.pie(
        model_performance, 
        values='attributed_revenue', 
        names='attribution_model',
        title='Revenue by Attribution Model',
        
    )
    
    return {
        'charts': {
            'combined_fig': combined_fig,
            'campaign_fig': campaign_fig,
            'model_fig': model_fig
        }
    }

# Main application
def main():
    st.title("Dashboard v2")
    ""
    # Load the data
    data = load_data()
    
    if not data:
        st.error("Failed to load data. Please check your database connection.")
        return
    
    # Create tabs for different sections
    tabs = st.tabs(["Overview", "Sales Analysis", "Customer Analysis", "Digital Analysis", "Inventory Analysis", "Campaign Analysis", "Data Model"])
    
    # Overview tab
    with tabs[0]:
        st.markdown('<h2 class="sub-header">Business Overview</h2>', unsafe_allow_html=True)
        
        # Create key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Total Customers</div>
                    <div class="metric-value">{len(data['customers']):,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Total Orders</div>
                    <div class="metric-value">{len(data['orders']):,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Total Revenue</div>
                    <div class="metric-value">${data['orders']['total_amount'].sum():,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col4:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Products Available</div>
                    <div class="metric-value">{len(data['products']):,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Create a summary visualization
        st.markdown('<h3 class="sub-header">Sales Overview</h3>', unsafe_allow_html=True)
        
        # Group orders by date and status
        orders = data['orders'].copy()
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        orders['month'] = orders['order_date'].dt.to_period('M')
        monthly_orders = orders.groupby(['month', 'order_status']).size().reset_index(name='count')
        monthly_orders['month'] = monthly_orders['month'].astype(str)
        
        # For order status, use the most recent status for each order in each month
        # Let's use the order_status_history table for this (in a real scenario)
        # For the demo, we'll use a different approach with the available data
        
        # For visualization purpose, let's create an order creation date by month
        orders['creation_month'] = orders['order_date'].dt.to_period('M')
        creation_by_month = orders.groupby('creation_month').size().reset_index(name='new_orders')
        creation_by_month['creation_month'] = creation_by_month['creation_month'].astype(str)
        
        # Current status distribution (as of the most recent data)
        current_status = orders.groupby('order_status').size().reset_index(name='count')
        
        # Create two separate visualizations for better clarity
        
        # 1. New orders by month (orders created in each month)
        fig1 = px.line(
            creation_by_month,
            x='creation_month',
            y='new_orders',
            title='New Orders Created by Month',
            markers=True,
            line_shape='linear',
            color_discrete_sequence=['#1976D2']
        )
        fig1.update_layout(xaxis_tickangle=-45)
        # Apply blue theme
#        fig1 = set_blue_theme_plotly(fig1)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 2. Current order status distribution
        fig2 = px.pie(
            current_status,
            values='count',
            names='order_status',
            title='Current Order Status Distribution',
            color_discrete_sequence=['#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#2196F3']
        )
        # Apply blue theme
        #fig2 = set_blue_theme_plotly(fig2)
        
        # Place status distribution and some additional metrics side by side
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.plotly_chart(fig2, use_container_width=True)
            
        with col2:
            # Calculate some additional metrics
            total_orders = len(orders)
            delivered = len(orders[orders['order_status'] == 'Delivered'])
            cancelled = len(orders[orders['order_status'] == 'Cancelled'])
            in_progress = total_orders - delivered - cancelled
            
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Delivery Rate</div>
                    <div class="metric-value">{delivered/total_orders:.1%}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Cancellation Rate</div>
                    <div class="metric-value">{cancelled/total_orders:.1%}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Orders In Progress</div>
                    <div class="metric-value">{in_progress}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Revenue by channel and order type
        col1, col2 = st.columns(2)
        
        with col1:
            channel_data = orders.merge(data['channels'], on='channel_id')
            channel_revenue = channel_data.groupby('channel_name')['total_amount'].sum().reset_index()
            fig2 = px.pie(channel_revenue, values='total_amount', names='channel_name', 
                          title='Revenue by Channel')
            st.plotly_chart(fig2, use_container_width=True)
            
        with col2:
            type_revenue = orders.groupby('order_type')['total_amount'].sum().reset_index()
            fig3 = px.pie(type_revenue, values='total_amount', names='order_type', 
                          title='Revenue by Order Type')
            st.plotly_chart(fig3, use_container_width=True)
    
    # Sales Analysis tab
    with tabs[1]:
        st.markdown('<h2 class="sub-header">Sales Analysis</h2>', unsafe_allow_html=True)
        
        # Create sales dashboard
        sales_dashboard = create_sales_dashboard(
            data['orders'], data['order_lines'], data['products'], data['channels']
        )
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Total Revenue</div>
                    <div class="metric-value">${sales_dashboard['metrics']['total_revenue']:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Total Orders</div>
                    <div class="metric-value">{sales_dashboard['metrics']['total_orders']:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Average Order Value</div>
                    <div class="metric-value">${sales_dashboard['metrics']['avg_order_value']:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Display charts
        st.plotly_chart(sales_dashboard['charts']['trend_fig'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(sales_dashboard['charts']['channel_fig'], use_container_width=True)
            
        with col2:
            st.plotly_chart(sales_dashboard['charts']['category_fig'], use_container_width=True)
            
        # Add interactive filters
        st.markdown('<h3 class="sub-header">Sales Details</h3>', unsafe_allow_html=True)
        
        # Merge data for detailed view
        sales_details = data['order_lines'].merge(data['orders'], on='order_id')
        sales_details = sales_details.merge(
            data['products'][['product_id', 'name', 'category']], 
            on='product_id', 
            suffixes=('_line', '_product')
        )
        
        # Create filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categories = ['All'] + list(sales_details['category'].unique())
            selected_category = st.selectbox('Filter by Category', categories)
            
        with col2:
            statuses = ['All'] + list(sales_details['order_status'].unique())
            selected_status = st.selectbox('Filter by Order Status', statuses)
            
        with col3:
            date_range = st.date_input(
                'Date Range',
                [
                    sales_details['order_date'].min(),
                    sales_details['order_date'].max()
                ]
            )
        
        # Apply filters
        filtered_sales = sales_details.copy()
        
        if selected_category != 'All':
            filtered_sales = filtered_sales[filtered_sales['category'] == selected_category]
            
        if selected_status != 'All':
            filtered_sales = filtered_sales[filtered_sales['order_status'] == selected_status]
            
        filtered_sales = filtered_sales[
            (filtered_sales['order_date'] >= pd.Timestamp(date_range[0])) & 
            (filtered_sales['order_date'] <= pd.Timestamp(date_range[1]))
        ]
        
        # Display filtered data
        if len(filtered_sales) > 0:
            # Calculate metrics
            total_filtered_revenue = (filtered_sales['quantity'] * filtered_sales['unit_price']).sum()
            avg_filtered_order = total_filtered_revenue / filtered_sales['order_id'].nunique()
            
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-title">Filtered Revenue</div>
                    <div class="metric-value">${total_filtered_revenue:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show product performance in this filter
            product_performance = filtered_sales.groupby(['name', 'category'])[['quantity', 'unit_price']].agg({
                'quantity': 'sum',
                'unit_price': 'mean'
            }).reset_index()
            product_performance['revenue'] = product_performance['quantity'] * product_performance['unit_price']
            product_performance = product_performance.sort_values('revenue', ascending=False).head(10)
            
            fig = px.bar(
                product_performance,
                x='name',
                y='revenue',
                color='category',
                title='Top Products by Revenue (Filtered)',
                color_discrete_map=category_colors
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data matches the selected filters.")
    
    # Customer Analysis tab
    with tabs[2]:
        st.markdown('<h2 class="sub-header">Customer Analysis</h2>', unsafe_allow_html=True)
        
        # Create customer analysis
        customer_analysis = create_customer_analysis(
            data['customers'], data['orders'], data['persons'], data['companies']
        )
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(customer_analysis['charts']['type_fig'], use_container_width=True)
            
        with col2:
            st.plotly_chart(customer_analysis['charts']['acquisition_fig'], use_container_width=True)
        
        st.plotly_chart(customer_analysis['charts']['spending_fig'], use_container_width=True)
        
        # Customer segmentation
        st.markdown('<h3 class="sub-header">Customer Segmentation</h3>', unsafe_allow_html=True)
        
        # Calculate metrics for each customer
        customer_metrics = data['orders'].groupby('customer_id').agg({
            'order_id': 'count',
            'total_amount': 'sum',
            'order_date': ['min', 'max']
        })
        customer_metrics.columns = ['order_count', 'total_spent', 'first_order', 'last_order']
        
        # Add recency and frequency metrics
        last_date = data['orders']['order_date'].max()
        customer_metrics['recency'] = (last_date - customer_metrics['last_order']).dt.days
        customer_metrics['frequency'] = customer_metrics['order_count'] 
        customer_metrics['monetary'] = customer_metrics['total_spent']
        
        # Add RFM score (simple version)
        customer_metrics['r_score'] = pd.qcut(customer_metrics['recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
        customer_metrics['f_score'] = pd.qcut(customer_metrics['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        customer_metrics['m_score'] = pd.qcut(customer_metrics['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        customer_metrics['rfm_score'] = customer_metrics['r_score'] + customer_metrics['f_score'] + customer_metrics['m_score']
        
        # Define segments
        def segment_customer(score):
            if score >= 13:
                return "Champions"
            elif score >= 10:
                return "Loyal Customers"
            elif score >= 7:
                return "Potential Loyalists"
            elif score >= 5:
                return "At Risk"
            else:
                return "Need Attention"
                
        customer_metrics['segment'] = customer_metrics['rfm_score'].apply(segment_customer)
        customer_metrics = customer_metrics.reset_index()
        
        # Add customer type
        customer_metrics = customer_metrics.merge(data['customers'][['customer_id', 'customer_type']], on='customer_id')
        
        # Visualize segments
        segment_counts = customer_metrics['segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']
        
        segment_spending = customer_metrics.groupby(['segment', 'customer_type'])['total_spent'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                segment_counts, 
                x='segment', 
                y='count',
                title='Customer Segments',
                color='segment',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            fig2 = px.bar(
                segment_spending, 
                x='segment', 
                y='total_spent', 
                color='customer_type',
                title='Segment Spending by Customer Type',
                barmode='group'
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Digital Analysis tab
    with tabs[3]:
        st.markdown('<h2 class="sub-header">Digital Analysis</h2>', unsafe_allow_html=True)
        
        # Create digital analysis
        digital_analysis = create_digital_analysis(
            data['digital_events'], data['digital_sites'], data['page_performance']
        )
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(digital_analysis['charts']['event_fig'], use_container_width=True)
            
        with col2:
            st.plotly_chart(digital_analysis['charts']['device_fig'], use_container_width=True)
        
        st.plotly_chart(digital_analysis['charts']['performance_fig'], use_container_width=True)
        st.plotly_chart(digital_analysis['charts']['conversion_fig'], use_container_width=True)
        
        # Digital customer journey
        st.markdown('<h3 class="sub-header">Digital Customer Journey</h3>', unsafe_allow_html=True)
        
        # Create funnel visualization
        funnel_events = ['PageView', 'ProductView', 'AddToCart', 'Purchase']
        funnel_counts = []
        
        for event in funnel_events:
            count = len(data['digital_events'][data['digital_events']['event_type'] == event])
            funnel_counts.append(count)
        
        funnel_data = pd.DataFrame({
            'stage': funnel_events,
            'count': funnel_counts
        })
        
        funnel_fig = px.funnel(
            funnel_data,
            x='count',
            y='stage',
            title='Customer Journey Funnel'
        )
        st.plotly_chart(funnel_fig, use_container_width=True)
    
    # Inventory Analysis tab
    with tabs[4]:
        st.markdown('<h2 class="sub-header">Inventory Analysis</h2>', unsafe_allow_html=True)
        
        # Create inventory analysis
        inventory_analysis = create_inventory_analysis(
            data['inventory'], data['products'], data['facilities']
        )
        
        # Display charts
        st.plotly_chart(inventory_analysis['charts']['facility_fig'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(inventory_analysis['charts']['category_fig'], use_container_width=True)
            
        with col2:
            st.plotly_chart(inventory_analysis['charts']['product_fig'], use_container_width=True)
        
        # Inventory insights
        st.markdown('<h3 class="sub-header">Inventory Insights</h3>', unsafe_allow_html=True)
        
        # Create a simple inventory status summary
        inventory_data = data['inventory'].merge(
            data['products'][['product_id', 'name', 'category']], 
            on='product_id'
        )
        
        # Define inventory status
        def inventory_status(qty):
            if qty <= 10:
                return "Critical Low"
            elif qty <= 50:
                return "Low"
            elif qty <= 200:
                return "Medium"
            else:
                return "High"
                
        inventory_data['status'] = inventory_data['quantity'].apply(inventory_status)
        
        # Inventory status counts
        status_counts = inventory_data['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        # Status by category
        category_status = inventory_data.groupby(['category', 'status']).size().reset_index(name='count')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.pie(
                status_counts, 
                values='count', 
                names='status',
                title='Inventory Status Distribution',
                color='status'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            fig2 = px.bar(
                category_status, 
                x='category', 
                y='count', 
                color='status',
                title='Inventory Status by Category',
                barmode='group'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        # Show items with critical low inventory
        critical_items = inventory_data[inventory_data['status'] == 'Critical Low']
        
        if len(critical_items) > 0:
            st.warning(f"There are {len(critical_items)} items with critically low inventory!")
            st.dataframe(
                critical_items[['name', 'category', 'quantity']].sort_values('quantity'),
                use_container_width=True
            )
    
    # Campaign Analysis tab
    with tabs[5]:
        st.markdown('<h2 class="sub-header">Campaign Analysis</h2>', unsafe_allow_html=True)
        
        # Create campaign analysis
        campaign_analysis = create_campaign_analysis(
            data['campaigns'], data['attributions'], data['orders']
        )
        
        # Display charts
        st.plotly_chart(campaign_analysis['charts']['combined_fig'], use_container_width=True)
        st.plotly_chart(campaign_analysis['charts']['campaign_fig'], use_container_width=True)
        
        st.markdown('<h3 class="sub-header">Attribution Analysis</h3>', unsafe_allow_html=True)
        st.plotly_chart(campaign_analysis['charts']['model_fig'], use_container_width=True)
    
    # Data Model tab
    with tabs[6]:
        st.markdown('<h2 class="sub-header">Data Model</h2>', unsafe_allow_html=True)
        
        # Create data model diagram
        img_str = create_data_model_diagram()
        st.markdown(f'<img src="data:image/png;base64,{img_str}" width="100%">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="padding: 20px;">
        <h3>Entity-Relationship Diagram</h3>
        <p>This diagram shows the relationships between the main entities in the data model:</p>
        <ul>
            <li><strong>CUSTOMER</strong> - Can be either a PERSON or a COMPANY</li>
            <li><strong>ORDER_FACT</strong> - Contains order header information</li>
            <li><strong>ORDER_LINE</strong> - Contains order line item details</li>
            <li><strong>PRODUCT</strong> - Product information with variants</li>
            <li><strong>INVENTORY</strong> - Stock levels by product and facility</li>
            <li><strong>CHANNEL</strong> - Sales channel information</li>
            <li><strong>FACILITY</strong> - Warehouses, stores, and distribution centers</li>
            <li><strong>CAMPAIGN</strong> - Marketing campaign information</li>
            <li><strong>DIGITAL_EVENT</strong> - Website and app interactions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()