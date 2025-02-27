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