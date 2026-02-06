"""
E-Commerce Analytical Dashboard
A comprehensive analytics dashboard for e-commerce data visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import sys
import os
import warnings

# Suppress unnecessary warnings
warnings.filterwarnings('ignore')

# Add the current directory to the path to avoid import issues
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from data_generator import generate_ecommerce_data
except ImportError:
    st.error("Error: Could not import data_generator. Please ensure data_generator.py is in the same directory.")
    st.stop()

# Page configuration - Must be first Streamlit command
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Enhanced Custom CSS with modern design
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Header with Gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: -1px;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Metric Cards with Glassmorphism */
    .metric-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Button Styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #2d3748;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Add animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache e-commerce data"""
    return generate_ecommerce_data()

def main():
    # Header with enhanced styling
    st.markdown('<h1 class="main-header fade-in">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box"><p style="text-align: center; margin: 0; color: #4a5568; font-size: 1.1rem;">Comprehensive insights into your e-commerce performance</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load data with progress indicator
    with st.spinner('🔄 Loading e-commerce data...'):
        df = load_data()
    st.success(f'✅ Successfully loaded {len(df):,} transaction records!')
    
    # Sidebar filters with enhanced styling
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: white; margin: 0; font-size: 1.5rem;'>🔍 Filters</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Date range filter
    min_date = df['order_date'].min().date()
    max_date = df['order_date'].max().date()
    
    st.sidebar.markdown("**📅 Date Range**")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Category filter
    st.sidebar.markdown("**📦 Category**")
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox(
        "Select Category",
        categories,
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Region filter
    st.sidebar.markdown("**🌍 Region**")
    regions = ['All'] + sorted(df['region'].unique().tolist())
    selected_region = st.sidebar.selectbox(
        "Select Region",
        regions,
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='color: white; margin: 0; font-size: 0.9rem;'>Total Records</p>
            <h3 style='color: white; margin: 0; font-size: 2rem;'>{len(df):,}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['order_date'].dt.date >= date_range[0]) &
            (filtered_df['order_date'].dt.date <= date_range[1])
        ]
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    # Key Metrics with enhanced styling
    st.markdown('<h2 class="section-header">📈 Key Performance Indicators</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = filtered_df['total_amount'].sum()
    total_orders = len(filtered_df)
    avg_order_value = filtered_df['total_amount'].mean()
    unique_customers = filtered_df['customer_id'].nunique()
    
    # Calculate deltas
    base_revenue = df['total_amount'].sum()
    base_orders = len(df)
    base_avg = df['total_amount'].mean()
    base_customers = df['customer_id'].nunique()
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.2f}",
            delta=f"${total_revenue - base_revenue:,.2f}" if len(filtered_df) != len(df) else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="🛒 Total Orders",
            value=f"{total_orders:,}",
            delta=f"{total_orders - base_orders:,}" if len(filtered_df) != len(df) else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="💵 Average Order Value",
            value=f"${avg_order_value:.2f}",
            delta=f"${avg_order_value - base_avg:.2f}" if len(filtered_df) != len(df) else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="👥 Unique Customers",
            value=f"{unique_customers:,}",
            delta=f"{unique_customers - base_customers:,}" if len(filtered_df) != len(df) else None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Revenue Trends with enhanced charts
    st.markdown('<h2 class="section-header">📊 Revenue Trends</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Revenue
        daily_revenue = filtered_df.groupby(filtered_df['order_date'].dt.date)['total_amount'].sum().reset_index()
        daily_revenue.columns = ['date', 'revenue']
        
        fig_daily = px.line(
            daily_revenue,
            x='date',
            y='revenue',
            title='📈 Daily Revenue Trend',
            labels={'date': 'Date', 'revenue': 'Revenue ($)'},
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#667eea']
        )
        fig_daily.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            hovermode='x unified'
        )
        fig_daily.update_traces(line=dict(width=3), marker=dict(size=6))
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with col2:
        # Monthly Revenue
        monthly_revenue = filtered_df.groupby(
            filtered_df['order_date'].dt.to_period('M').astype(str)
        )['total_amount'].sum().reset_index()
        monthly_revenue.columns = ['month', 'revenue']
        
        fig_monthly = px.bar(
            monthly_revenue,
            x='month',
            y='revenue',
            title='📊 Monthly Revenue',
            labels={'month': 'Month', 'revenue': 'Revenue ($)'},
            color='revenue',
            color_continuous_scale=[[0, '#667eea'], [1, '#764ba2']]
        )
        fig_monthly.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            showlegend=False
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Product Analysis with enhanced charts
    st.markdown('<h2 class="section-header">🛍️ Product Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Products by Revenue
        top_products = filtered_df.groupby('product_name')['total_amount'].sum().nlargest(10).reset_index()
        
        fig_products = px.bar(
            top_products,
            x='total_amount',
            y='product_name',
            orientation='h',
            title='🏆 Top 10 Products by Revenue',
            labels={'total_amount': 'Revenue ($)', 'product_name': 'Product'},
            color='total_amount',
            color_continuous_scale=[[0, '#667eea'], [1, '#764ba2']]
        )
        fig_products.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_products, use_container_width=True)
    
    with col2:
        # Category Distribution
        category_revenue = filtered_df.groupby('category')['total_amount'].sum().reset_index()
        
        fig_category = px.pie(
            category_revenue,
            values='total_amount',
            names='category',
            title='📊 Revenue by Category',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_category.update_layout(
            height=450,
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Customer Analysis with enhanced charts
    st.markdown('<h2 class="section-header">👥 Customer Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Lifetime Value
        customer_ltv = filtered_df.groupby('customer_id')['total_amount'].sum().reset_index()
        customer_ltv_sorted = customer_ltv.nlargest(10, 'total_amount')
        
        fig_customer = px.bar(
            customer_ltv_sorted,
            x='customer_id',
            y='total_amount',
            title='⭐ Top 10 Customers by Lifetime Value',
            labels={'customer_id': 'Customer ID', 'total_amount': 'Total Spent ($)'},
            color='total_amount',
            color_continuous_scale=[[0, '#f093fb'], [1, '#f5576c']]
        )
        fig_customer.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            xaxis={'categoryorder': 'total descending'},
            showlegend=False
        )
        st.plotly_chart(fig_customer, use_container_width=True)
    
    with col2:
        # Orders per Customer Distribution
        orders_per_customer = filtered_df.groupby('customer_id').size().reset_index(name='order_count')
        
        fig_orders = px.histogram(
            orders_per_customer,
            x='order_count',
            title='📊 Distribution of Orders per Customer',
            labels={'order_count': 'Number of Orders', 'count': 'Number of Customers'},
            nbins=20,
            color_discrete_sequence=['#667eea']
        )
        fig_orders.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            showlegend=False
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    # Geographic Analysis with enhanced charts
    st.markdown('<h2 class="section-header">🌍 Geographic Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Region
        region_revenue = filtered_df.groupby('region')['total_amount'].sum().reset_index()
        region_revenue = region_revenue.sort_values('total_amount', ascending=False)
        
        fig_region = px.bar(
            region_revenue,
            x='region',
            y='total_amount',
            title='💰 Revenue by Region',
            labels={'region': 'Region', 'total_amount': 'Revenue ($)'},
            color='total_amount',
            color_continuous_scale=[[0, '#fa709a'], [1, '#fee140']]
        )
        fig_region.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            xaxis={'categoryorder': 'total descending'},
            showlegend=False
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    with col2:
        # Orders by Region
        region_orders = filtered_df.groupby('region').size().reset_index(name='order_count')
        region_orders = region_orders.sort_values('order_count', ascending=False)
        
        fig_region_orders = px.pie(
            region_orders,
            values='order_count',
            names='region',
            title='🌐 Order Distribution by Region',
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_region_orders.update_layout(
            height=450,
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )
        fig_region_orders.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_region_orders, use_container_width=True)
    
    # Time-based Analysis with enhanced charts
    st.markdown('<h2 class="section-header">⏰ Time-based Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Day of Week
        filtered_df['day_of_week'] = filtered_df['order_date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_revenue = filtered_df.groupby('day_of_week')['total_amount'].sum().reindex(day_order).reset_index()
        
        fig_day = px.bar(
            day_revenue,
            x='day_of_week',
            y='total_amount',
            title='📅 Revenue by Day of Week',
            labels={'day_of_week': 'Day', 'total_amount': 'Revenue ($)'},
            color='total_amount',
            color_continuous_scale=[[0, '#4facfe'], [1, '#00f2fe']]
        )
        fig_day.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            showlegend=False
        )
        st.plotly_chart(fig_day, use_container_width=True)
    
    with col2:
        # Revenue by Hour of Day
        filtered_df['hour'] = filtered_df['order_date'].dt.hour
        hour_revenue = filtered_df.groupby('hour')['total_amount'].sum().reset_index()
        
        fig_hour = px.line(
            hour_revenue,
            x='hour',
            y='total_amount',
            title='🕐 Revenue by Hour of Day',
            labels={'hour': 'Hour', 'total_amount': 'Revenue ($)'},
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#fa709a']
        )
        fig_hour.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins", size=12),
            title_font=dict(size=18, color='#2d3748'),
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            hovermode='x unified'
        )
        fig_hour.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_hour, use_container_width=True)
    
    # Sales Performance Table with enhanced styling
    st.markdown('<h2 class="section-header">📋 Detailed Sales Performance</h2>', unsafe_allow_html=True)
    
    # Summary statistics
    summary_stats = filtered_df.groupby('product_name').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    }).reset_index()
    summary_stats.columns = ['Product', 'Total Revenue', 'Avg Order Value', 'Order Count', 'Total Quantity']
    summary_stats = summary_stats.sort_values('Total Revenue', ascending=False)
    
    # Format the dataframe for better display
    summary_stats_display = summary_stats.copy()
    summary_stats_display['Total Revenue'] = summary_stats_display['Total Revenue'].apply(lambda x: f"${x:,.2f}")
    summary_stats_display['Avg Order Value'] = summary_stats_display['Avg Order Value'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(
        summary_stats_display.head(20),
        use_container_width=True,
        height=450
    )
    
    # Download button with enhanced styling
    csv_data = summary_stats.to_csv(index=False)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📥 Download Summary Data (CSV)",
            data=csv_data,
            file_name=f"ecommerce_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border-radius: 15px;'>
            <p style='color: #4a5568; font-size: 1rem; margin: 0;'>📊 E-Commerce Analytics Dashboard | Built with Streamlit & Plotly</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Check if running in Streamlit
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("💡 Make sure you're running this with: streamlit run app.py")
