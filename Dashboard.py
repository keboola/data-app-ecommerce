import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from keboola_streamlit import KeboolaStreamlit

# Constants
BLUE_PALETTE = ['#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#2196F3']
BLUE_SEQUENTIAL = ['#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594']

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
        font-size: 1.2rem;
        color: #31333F;
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
        background-color: #f1f2f6;
        border-radius: 4px 4px 0 0;
        color: #0D47A1;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0D47A1 !important;
        color: #f1f2f6 !important;
    }
</style>
""", unsafe_allow_html=True)

def create_metric_container(title, value, color="#0D47A1"):
    """Create a styled metric container"""
    return f"""
    <div class="metric-container">
        <div class="metric-title">{title}</div>
        <div class="metric-value" style="color: {color}">{value}</div>
    </div>
    """

def segment_customer(score):
    """Determine customer segment based on RFM score"""
    if score >= 13:
        return "Champions"
    elif score >= 10:
        return "Loyal Customers"
    elif score >= 7:
        return "Potential Loyalists"
    elif score >= 5:
        return "At Risk"
    return "Need Attention"

def inventory_status(qty):
    """Determine inventory status based on quantity"""
    if qty <= 10:
        return "Critical Low"
    elif qty <= 50:
        return "Low"
    elif qty <= 200:
        return "Medium"
    return "High"

@st.cache_data
def load_data():
    """Load and prepare all data for the dashboard"""
    try:
        #data = load_csv_files()
        
        # Create sample data for demonstration
        # CUSTOMER table
        customers = pd.DataFrame({
            'customer_id': [f'C{i}' for i in range(1, 343)],
            'customer_type': np.random.choice(['person'], 342),
            'name': [f'Customer {i}' for i in range(1, 343)],
            'created_at': pd.date_range(start='2023-01-01', periods=342, freq='D'),
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
            'product_id': [f'P{i}' for i in range(1, 52)],
            'name': [f'Product {i}' for i in range(1, 52)],
            'category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Beauty', 'Food'], 51),
            'price': np.random.uniform(10, 1000, 51).round(2),
            'active': np.random.choice([True, False], 51, p=[0.9, 0.1]),
        })
        
        # CHANNEL table
        channels = pd.DataFrame({
            'channel_id': [f'CH{i}' for i in range(1, 5)],
            'channel_name': ['Web Store', 'Mobile App', 'Physical Store', 'Partner'],
            'channel_type': ['Digital', 'Digital', 'Physical', 'Partner'],
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
        order_dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        num_orders = 538
        orders = pd.DataFrame({
            'order_id': [f'O{i}' for i in range(1, num_orders + 1)],
            'order_date': np.random.choice(order_dates, num_orders),
            'customer_id': np.random.choice(customers['customer_id'], num_orders),
            'channel_id': np.random.choice(channels['channel_id'], num_orders),
            'facility_id': np.random.choice(facilities['facility_id'], num_orders),
            'total_amount': np.random.uniform(50, 5000, num_orders).round(2),
            'currency': 'USD',
            'order_status': np.random.choice(
                ['Created', 'Processing', 'Shipped', 'Delivered', 'Cancelled'], 
                num_orders,
                p=[0.1, 0.2, 0.3, 0.35, 0.05]
            ),
            'order_type': np.random.choice(
                ['Standard', 'Express', 'Gift', 'Return'], 
                num_orders, 
                p=[0.7, 0.2, 0.05, 0.05]
            ),
            'payment_method': np.random.choice(
                ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash'],
                num_orders,
                p=[0.4, 0.3, 0.2, 0.1]
            )
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
            'event_date': pd.date_range(start='2024-01-01', end='2024-12-31', periods=num_events),
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
            'last_updated': pd.date_range(start='2024-01-01', periods=100, freq='3D'),
        })
        
        # PAGE_PERFORMANCE table
        num_page_performances = 500
        page_performance = pd.DataFrame({
            'performance_id': [f'PP{i}' for i in range(1, num_page_performances + 1)],
            'page_id': [f'PG{i}' for i in range(1, 21)] * 25,
            'date': np.sort(np.random.choice(pd.date_range(start='2024-01-01', end='2024-12-31'), num_page_performances)),
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
        st.error(f"Failed to load data: {e}")
        return {}

def create_sales_dashboard(orders, order_lines, products, channels):
    """Create sales analysis dashboard components"""
    # Calculate key metrics
    total_revenue = orders['total_amount'].sum()
    total_orders = len(orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Merge data for analysis
    sales_data = (order_lines.merge(orders, on='order_id')
                 .merge(products[['product_id', 'name', 'category']], on='product_id'))
    
    # Calculate revenue
    sales_data['revenue'] = sales_data['quantity'] * sales_data['unit_price'] - sales_data['discount_amount']
    
    # Prepare time series data
    sales_data['month'] = pd.to_datetime(sales_data['order_date']).dt.to_period('M')
    monthly_sales = sales_data.groupby('month')['revenue'].sum().reset_index()
    monthly_sales['month'] = monthly_sales['month'].astype(str)
    
    # Create visualizations
    category_sales = sales_data.groupby('category')['revenue'].sum().reset_index()
    
    category_fig = px.pie(
        category_sales,
        values='revenue',
        names='category',
        title='Revenue by Product Category',
        hole=0.4,
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'category': 'Category',
            'revenue': 'Revenue'
        },
        hover_data={'revenue': ':$,.0f'}
    )
    
    trend_fig = px.line(
        monthly_sales,
        x='month',
        y='revenue',
        title='Monthly Sales Trend',
        markers=True,
        line_shape="spline",
        labels={
            'month': 'Time',
            'revenue': 'Revenue'
        }
    )
    trend_fig.update_xaxes(tickangle=45)
    
    return {
        'metrics': {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value
        },
        'charts': {
            'category_fig': category_fig,
            'trend_fig': trend_fig
        }
    }

def create_customer_analysis(customers, orders, persons, companies):
    """Create customer analysis visualizations"""
    # Merge orders with customers
    customer_orders = orders.merge(customers, on='customer_id')
    
    # Customer acquisition over time
    customers['created_at'] = pd.to_datetime(customers['created_at'])
    customers['month'] = customers['created_at'].dt.to_period('M')
    monthly_acquisition = customers.groupby(['month', 'customer_type']).size().reset_index(name='count')
    monthly_acquisition['month'] = monthly_acquisition['month'].astype(str)
    
    # Customer spending analysis
    customer_spending = (customer_orders.groupby('customer_id')['total_amount']
                       .agg(['sum', 'count'])
                       .reset_index()
                       .rename(columns={'sum': 'total_spent', 'count': 'order_count'}))
    customer_spending['avg_order_value'] = customer_spending['total_spent'] / customer_spending['order_count']
    customer_spending = customer_spending.merge(customers[['customer_id', 'customer_type']], on='customer_id')
    
    # Create visualizations
    acquisition_fig = px.bar(
        monthly_acquisition,
        x='month',
        y='count',
        color='customer_type',
        title='Monthly Customer Acquisition',
        barmode='group',
        color_discrete_sequence=BLUE_PALETTE
    )
    acquisition_fig.update_xaxes(tickangle=45)
    
    spending_fig = px.scatter(
        customer_spending,
        x='total_spent',
        y='avg_order_value',
        size='order_count',
        opacity=0.7,
        hover_data=['customer_id'],
        title='Customer Spending',
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'total_spent': 'Total Spent',
            'avg_order_value': 'Avg Order Value',
            'order_count': 'Order Count',
            'customer_id': 'Customer ID'
        }
    )
    
    return {
        'charts': {
            'acquisition_fig': acquisition_fig,
            'spending_fig': spending_fig
        }
    }

def create_digital_analysis(digital_events, digital_sites, page_performance):
    """Create digital analytics dashboard components"""
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
    event_fig = px.bar(
        event_counts,
        x='event_type',
        y='count',
        title='Digital Event Distribution',
        color='event_type',
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'event_type': 'Event Type',
            'count': 'Count'
        }
    )
    
    device_fig = px.pie(
        device_counts,
        values='count',
        names='device_type',
        title='Device Type Distribution',
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'device_type': 'Device Type',
            'count': 'Count'
        }
    )
    
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
        xaxis_title='Time',
        yaxis_title='Count',
        legend_title='Metric'
    )
    
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

def create_inventory_analysis(inventory, products, facilities):
    """Create inventory analysis visualizations"""
    # Merge inventory with products and facilities
    inventory_data = (inventory.merge(products[['product_id', 'name', 'category']], on='product_id')
                     .merge(facilities[['facility_id', 'facility_name', 'facility_type', 'region']], on='facility_id'))
    
    # Inventory by product category
    category_inventory = inventory_data.groupby('category')['quantity'].sum().reset_index()
    
    # Bottom products by inventory
    product_inventory = (inventory_data.groupby(['name', 'category'])['quantity']
                        .sum()
                        .reset_index()
                        .sort_values('quantity', ascending=False)
                        .tail(10))
    
    # Create visualizations
    category_fig = px.pie(
        category_inventory,
        values='quantity',
        names='category',
        title='Inventory by Product Category',
        color='category',
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'category': 'Category',
            'quantity': 'Quantity'
        }
    )
    
    product_fig = px.bar(
        product_inventory,
        x='name',
        y='quantity',
        color='category',
        title='Bottom 10 Products by Inventory Quantity',
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'name': 'Product Name',
            'quantity': 'Quantity',
            'category': 'Category'
        }
    )
    product_fig.update_layout(xaxis={'categoryorder': 'total ascending'})
    
    return {
        'charts': {
            'category_fig': category_fig,
            'product_fig': product_fig
        }
    }

def create_campaign_analysis(campaigns, attributions, orders):
    """Create campaign analysis visualizations"""
    # Merge attributions with campaigns and orders
    campaign_data = (attributions.merge(
        campaigns[['campaign_id', 'campaign_name', 'campaign_type', 'budget']], 
        on='campaign_id'
    ).merge(
        orders[['order_id', 'total_amount']], 
        on='order_id'
    ))
    
    # Calculate attributed revenue
    campaign_data['attributed_revenue'] = campaign_data['total_amount'] * campaign_data['contribution_percent']
    
    # Campaign performance by type
    type_performance = campaign_data.groupby('campaign_type').agg({
        'attributed_revenue': 'sum',
        'budget': 'sum'
    }).reset_index()
    type_performance['roi'] = (type_performance['attributed_revenue'] / type_performance['budget']).round(2)
    
    # Campaign performance
    campaign_performance = campaign_data.groupby(
        ['campaign_id', 'campaign_name', 'campaign_type']
    ).agg({
        'attributed_revenue': 'sum',
        'budget': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    
    campaign_performance['roi'] = (campaign_performance['attributed_revenue'] / campaign_performance['budget']).round(2)
    campaign_performance = campaign_performance.sort_values('attributed_revenue', ascending=False)
    
    # Create visualizations
    type_fig = px.bar(
        type_performance,
        x='campaign_type',
        y=['attributed_revenue', 'budget'],
        title='Campaign Performance by Type',
        barmode='group'
    )
    
    roi_fig = px.line(
        type_performance,
        x='campaign_type',
        y='roi',
        title='ROI by Campaign Type',
        color_discrete_sequence=BLUE_PALETTE
    )
    roi_fig.update_traces(yaxis="y2")
    
    combined_fig = go.Figure(data=type_fig.data + roi_fig.data)
    combined_fig.update_layout(
        yaxis2=dict(
            title="ROI",
            overlaying="y",
            side="right"
        ),
        title='Campaign Performance and ROI by Type'
    )
    
    campaign_fig = px.bar(
        campaign_performance.head(10),
        x='campaign_name',
        y='attributed_revenue',
        color='campaign_type',
        hover_data=['roi', 'order_id'],
        title='Top 10 Campaigns by Attributed Revenue',
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'campaign_name': 'Campaign Name',
            'attributed_revenue': 'Attributed Revenue',
            'campaign_type': 'Campaign Type',
            'roi': 'ROI',
            'order_id': 'Order Count'
        }
    )
    
    return {
        'charts': {
            'combined_fig': combined_fig,
            'campaign_fig': campaign_fig
        }
    }

def display_overview_tab(data):
    """Display overview tab content"""
    # Create key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_container("Total Customers", len(data['customers'])), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container("Total Orders", len(data['orders'])), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container("Total Revenue", f"${data['orders']['total_amount'].sum():,.0f}"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_container("Products Available", len(data['products'])), unsafe_allow_html=True)
    
    # Prepare order data
    orders = data['orders'].copy()
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders['month'] = orders['order_date'].dt.to_period('M')
    orders['creation_month'] = orders['order_date'].dt.to_period('M')
    
    # Create visualizations
    creation_by_month = orders.groupby('creation_month').size().reset_index(name='new_orders')
    creation_by_month['creation_month'] = creation_by_month['creation_month'].astype(str)
    
    current_status = orders.groupby('order_status').size().reset_index(name='count')
    # New orders trend
    fig1 = px.line(
        creation_by_month,
        x='creation_month',
        y='new_orders',
        title='New Orders Created by Month',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['#1976D2'],
        labels={
            'creation_month': 'Time',
            'new_orders': 'Count'
        }
    )
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Order status distribution
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        fig2 = px.bar(
            current_status,
            x='order_status',
            y='count',
            title='Current Order Status Distribution',
            color='order_status',
            color_discrete_map={
                'Shipped': '#4CAF50',
                'Cancelled': '#F44336',
                'Created': '#0D47A1',
                'Processing': '#1565C0',
                'Delivered': '#1976D2'
            },
            labels={
                'order_status': 'Order Status',
                'count': 'Count'
            }
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(
            xaxis_title='Order Status',
            yaxis_title='Count',
            showlegend=False,
            margin=dict(t=50)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        total_orders = len(orders)
        delivered = len(orders[orders['order_status'] == 'Delivered'])
        cancelled = len(orders[orders['order_status'] == 'Cancelled'])
        in_progress = total_orders - delivered - cancelled
        
        st.markdown(create_metric_container("Delivery Rate", f"{delivered/total_orders:.1%}", "#4CAF50"), unsafe_allow_html=True)
        st.markdown(create_metric_container("Orders In Progress", in_progress), unsafe_allow_html=True)
        st.markdown(create_metric_container("Cancellation Rate", f"{cancelled/total_orders:.1%}", "#F44336"), unsafe_allow_html=True)
    
    # Revenue by order type
    type_revenue = orders.groupby('order_type')['total_amount'].sum().reset_index()
    fig3 = px.pie(
        type_revenue, 
        values='total_amount', 
        names='order_type',
        title='Revenue by Order Type', 
        color_discrete_sequence=BLUE_PALETTE,
        labels={
            'order_type': 'Order Type',
            'total_amount': 'Revenue'
        },
        hover_data={'total_amount': ':$,.2f'}
    )
    st.plotly_chart(fig3, use_container_width=True)

def display_sales_tab(data):
    """Display sales analysis tab content"""
    # Create sales dashboard
    sales_dashboard = create_sales_dashboard(data['orders'], data['order_lines'], data['products'], data['channels'])
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(create_metric_container("Total Revenue", f"${sales_dashboard['metrics']['total_revenue']:,.0f}"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_container("Total Orders", sales_dashboard['metrics']['total_orders']), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_container("Average Order Value", f"${sales_dashboard['metrics']['avg_order_value']:,.0f}"), unsafe_allow_html=True)
    
    # Display charts
    st.plotly_chart(sales_dashboard['charts']['trend_fig'], use_container_width=True)
    st.plotly_chart(sales_dashboard['charts']['category_fig'], use_container_width=True)
    
    # Product Details section
   # st.markdown('#### Product Details')
    
    # Prepare data
    sales_details = (data['order_lines'].merge(data['orders'], on='order_id')
                    .merge(data['products'][['product_id', 'name', 'category']], 
                          on='product_id', 
                          suffixes=('_line', '_product')))
        
    if len(sales_details) > 0:
        # Calculate metrics
        #total_filtered_revenue = (sales_details['quantity'] * sales_details['unit_price']).sum()
        
        #st.markdown(create_metric_container("Filtered Revenue", f"${total_filtered_revenue:,.0f}"), unsafe_allow_html=True)
        
        # Product performance
        product_performance = sales_details.groupby(['name', 'category'])[['quantity', 'unit_price']].agg({
            'quantity': 'sum',
            'unit_price': 'mean'
        }).reset_index()
        product_performance['revenue'] = product_performance['quantity'] * product_performance['unit_price']
        product_performance = product_performance.sort_values('revenue', ascending=False).head(10)
        
        fig = px.bar(
            product_performance,
            x='revenue',
            y='name',
            color='category',
            title='Top Products by Revenue (Filtered)',
            labels={'revenue': 'Revenue', 'name': 'Product Name'},
            text='revenue',
            orientation='h',
            color_discrete_sequence=BLUE_PALETTE
        )
        fig.update_traces(
            texttemplate='$%{x:,.0f}',
            textposition='inside',
            insidetextanchor='start',
            hovertemplate='Product=%{y}<br>Revenue=$%{x:,.0f}<extra></extra>'
        )
        fig.update_layout(
            yaxis=dict(categoryorder='total ascending', title=None),
            margin=dict(t=50, l=10),
            xaxis_tickprefix='$',
            xaxis_tickformat=',.0f',
            showlegend=True,
            legend_title='Category',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data matches the selected filters.")

def display_customer_tab(data):
    """Display customer analysis tab content"""
    # Create customer analysis
    customer_analysis = create_customer_analysis(data['customers'], data['orders'], data['persons'], data['companies'])
    st.plotly_chart(customer_analysis['charts']['spending_fig'], use_container_width=True)
    
    # Calculate RFM metrics
    customer_metrics = data['orders'].groupby('customer_id').agg({
        'order_id': 'count',
        'total_amount': 'sum',
        'order_date': ['min', 'max']
    })
    customer_metrics.columns = ['order_count', 'total_spent', 'first_order', 'last_order']
    
    # Add RFM metrics
    last_date = data['orders']['order_date'].max()
    customer_metrics['recency'] = (last_date - customer_metrics['last_order']).dt.days
    customer_metrics['frequency'] = customer_metrics['order_count']
    customer_metrics['monetary'] = customer_metrics['total_spent']
    
    # Calculate RFM scores
    customer_metrics['r_score'] = pd.qcut(customer_metrics['recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    customer_metrics['f_score'] = pd.qcut(customer_metrics['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    customer_metrics['m_score'] = pd.qcut(customer_metrics['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    customer_metrics['rfm_score'] = customer_metrics['r_score'] + customer_metrics['f_score'] + customer_metrics['m_score']
    
    # Add segments and customer type
    customer_metrics['segment'] = customer_metrics['rfm_score'].apply(segment_customer)
    customer_metrics = customer_metrics.reset_index()
    customer_metrics = customer_metrics.merge(data['customers'][['customer_id', 'customer_type']], on='customer_id')
    
    # Revenue by Customers
   # st.markdown('#### Revenue by Customers')
    customer_revenue = (customer_metrics[['customer_id', 'total_spent']]
                       .sort_values(by='total_spent', ascending=False)
                       .head(10)
                       .merge(data['customers'][['customer_id', 'name']], on='customer_id'))
    
    fig = px.bar(
        customer_revenue,
        x='total_spent',
        y='name',
        orientation='h',
        title='Top 10 Customers by Revenue',
        labels={'total_spent': 'Total Revenue ($)', 'name': 'Customer Name'},
        text='total_spent',
        color_discrete_sequence=BLUE_PALETTE
    )
    fig.update_traces(
        texttemplate='$%{x:,.0f}',
        textposition='inside',
        insidetextanchor='start',
        hovertemplate='Customer: %{y}<br>Revenue: $%{x:,.0f}<extra></extra>'
    )
    fig.update_layout(
        yaxis=dict(categoryorder='total ascending', title=None),
        margin=dict(t=50, l=10),
        xaxis_tickprefix='$',
        xaxis_tickformat=',.0f',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def display_digital_tab(data):
    """Display digital analysis tab content"""
    digital_analysis = create_digital_analysis(data['digital_events'], data['digital_sites'], data['page_performance'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(digital_analysis['charts']['event_fig'], use_container_width=True)
    with col2:
        st.plotly_chart(digital_analysis['charts']['device_fig'], use_container_width=True)
    
    st.plotly_chart(digital_analysis['charts']['performance_fig'], use_container_width=True)
    st.plotly_chart(digital_analysis['charts']['conversion_fig'], use_container_width=True)

def display_inventory_tab(data):
    """Display inventory analysis tab content"""
    inventory_analysis = create_inventory_analysis(data['inventory'], data['products'], data['facilities'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(inventory_analysis['charts']['category_fig'], use_container_width=True)
    with col2:
        st.plotly_chart(inventory_analysis['charts']['product_fig'], use_container_width=True)
    
    st.markdown('#### Inventory Insights')
    
    # Prepare inventory data
    inventory_data = data['inventory'].merge(
        data['products'][['product_id', 'name', 'category']], 
        on='product_id'
    )
    inventory_data['status'] = inventory_data['quantity'].apply(inventory_status)
    
    # Status analysis
    status_counts = inventory_data['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    category_status = inventory_data.groupby(['category', 'status']).size().reset_index(name='count')
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(
            status_counts,
            values='count',
            names='status',
            title='Inventory Status Distribution',
            color='status',
            color_discrete_sequence=BLUE_PALETTE,
            labels={
                'status': 'Status',
                'count': 'Count'
            }
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(
            category_status,
            x='category',
            y='count',
            color='status',
            title='Inventory Status by Category',
            barmode='group',
            color_discrete_sequence=BLUE_PALETTE,
            labels={
                'category': 'Category',
                'count': 'Count',
                'status': 'Status'
            }
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Critical items alert
    critical_items = inventory_data[inventory_data['status'] == 'Critical Low']
    if len(critical_items) > 0:
        st.warning(f"There are {len(critical_items)} items with critically low inventory!")
        st.dataframe(
            critical_items[['name', 'category', 'quantity']].sort_values('quantity'),
            use_container_width=True,
            hide_index=True,
            column_config={
                'name': 'Product Name',
                'category': 'Category',
                'quantity': 'Quantity'
            }
        )

def display_campaign_tab(data):
    """Display campaign analysis tab content"""
    campaign_analysis = create_campaign_analysis(data['campaigns'], data['attributions'], data['orders'])
    st.plotly_chart(campaign_analysis['charts']['combined_fig'], use_container_width=True)
    st.plotly_chart(campaign_analysis['charts']['campaign_fig'], use_container_width=True)

def main():
    """Main application entry point"""
    # Load data
    url = st.secrets["kbc_url"]
    token = st.secrets["kbc_token"]
    keboola = KeboolaStreamlit(url, token)

    data = load_data()
    if not data:
        st.error("Failed to load data. Please check your database connection.")
        return
    
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
        min_date = pd.to_datetime(data['orders']['order_date']).min()
        max_date = pd.to_datetime(data['orders']['order_date']).max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Other filters
        channels = ['All'] + list(data['channels']['channel_name'].unique())
        selected_channel = st.selectbox('Sales Channel', channels)
        
        categories = ['All'] + list(data['products']['category'].unique())
        selected_category = st.selectbox('Product Category', categories)
        
        payment_methods = ['All'] + list(data['orders']['payment_method'].unique())
        selected_payment_method = st.selectbox('Payment Method', payment_methods)
        
        order_statuses = ['All'] + list(data['orders']['order_status'].unique())
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
    filtered_data = data.copy()
    
    # Filter orders by date range
    if date_range:  # Check if date_range exists
        try:
            # Sort dates to ensure start_date is before end_date
            sorted_dates = sorted(date_range)
            start_date = sorted_dates[0]
            end_date = sorted_dates[1]
            
            filtered_data['orders'] = data['orders'][
                (pd.to_datetime(data['orders']['order_date']) >= pd.Timestamp(start_date)) &
                (pd.to_datetime(data['orders']['order_date']) <= pd.Timestamp(end_date))
            ]
        except (IndexError, TypeError):
            st.info("Please select both start and end dates")
            st.stop()  # Stop execution if dates are invalid
    
    # Filter by channel
    if selected_channel != 'All':
        channel_ids = data['channels'][data['channels']['channel_name'] == selected_channel]['channel_id']
        filtered_data['orders'] = filtered_data['orders'][filtered_data['orders']['channel_id'].isin(channel_ids)]
    
    # Filter by payment method
    if selected_payment_method != 'All':
        filtered_data['orders'] = filtered_data['orders'][filtered_data['orders']['payment_method'] == selected_payment_method]
    
    # Filter by order status
    if selected_order_status != 'All':
        filtered_data['orders'] = filtered_data['orders'][filtered_data['orders']['order_status'] == selected_order_status]
    
    # Filter order lines and get relevant product IDs
    filtered_data['order_lines'] = data['order_lines'][
        data['order_lines']['order_id'].isin(filtered_data['orders']['order_id'])
    ]
    
    # Filter by product category
    if selected_category != 'All':
        category_product_ids = data['products'][data['products']['category'] == selected_category]['product_id']
        filtered_data['order_lines'] = filtered_data['order_lines'][
            filtered_data['order_lines']['product_id'].isin(category_product_ids)
        ]
        filtered_data['products'] = data['products'][data['products']['category'] == selected_category]
    
    # Get relevant customer IDs from filtered orders
    customer_ids = filtered_data['orders']['customer_id'].unique()
    filtered_data['customers'] = data['customers'][data['customers']['customer_id'].isin(customer_ids)]
    
    # Filter related tables
    filtered_data['persons'] = data['persons'][data['persons']['customer_id'].isin(customer_ids)]
    filtered_data['companies'] = data['companies'][data['companies']['customer_id'].isin(customer_ids)]
    
    # Filter digital events
    filtered_data['digital_events'] = data['digital_events'][
        (pd.to_datetime(data['digital_events']['event_date']) >= pd.Timestamp(date_range[0])) &
        (pd.to_datetime(data['digital_events']['event_date']) <= pd.Timestamp(date_range[1]))
    ]
    
    # Filter page performance
    filtered_data['page_performance'] = data['page_performance'][
        (pd.to_datetime(data['page_performance']['date']) >= pd.Timestamp(date_range[0])) &
        (pd.to_datetime(data['page_performance']['date']) <= pd.Timestamp(date_range[1]))
    ]
    
    # Create tabs
    tabs = st.tabs(["Overview", "Sales Analysis", "Customer Analysis", "Digital Analysis", "Inventory Analysis", "Campaign Analysis"])
    
    # Overview tab
    with tabs[0]:
        display_overview_tab(filtered_data)
    
    # Sales Analysis tab
    with tabs[1]:
        display_sales_tab(filtered_data)
    
    # Customer Analysis tab
    with tabs[2]:
        display_customer_tab(filtered_data)
    
    # Digital Analysis tab
    with tabs[3]:
        display_digital_tab(filtered_data)
    
    # Inventory Analysis tab
    with tabs[4]:
        display_inventory_tab(filtered_data)
    
    # Campaign Analysis tab
    with tabs[5]:
        display_campaign_tab(filtered_data)

if __name__ == "__main__":
    main()