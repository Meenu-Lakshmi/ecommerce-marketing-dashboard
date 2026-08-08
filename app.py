# Check AST compilation
import ast
try:
    ast.parse(code_str)
    print("Syntax AST compile test: SUCCESS")
except Exception as e:
    print("Syntax error:", e)



import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# --- 0. Configuration & Setup ---

# Custom Channel Colors
CHANNEL_COLORS = {
    'Facebook': '#1877F2',  # Facebook Blue
    'Google': '#FFD700',    # Gold/Bright Yellow
    'TikTok': '#8A2BE2'     # Blue Violet
}

# Streamlit page configuration
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI enhancements
st.markdown(
    """
    <style>
    /* General Font size adjustments for headings */
    h1 { font-size: 3em; color: #FAFAFA; }
    h2 { font-size: 2em; color: #FAFAFA; }
    h3 { font-size: 1.5em; color: #FAFAFA; }

    /* Custom style for the metric boxes */
    .metric-box {
        background-color: #282828;
        border: 1px solid #444444;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        box-sizing: border-box;
    }
    .metric-title {
        font-size: 0.8em;
        color: #BBBBBB;
        margin-bottom: 2px;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        align-self: flex-start;
    }
    .metric-value {
        font-size: 1.5em;
        font-weight: bold;
        color: #FAFAFA;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        align-self: flex-end;
        margin-top: auto;
    }

    .stPlotlyChart {
        background-color: #0E1117;
    }

    /* Sidebar widget styling */
    .stMultiSelect, .stRadio, .stDateInput, .stSelectbox {
        background-color: #000000;
        border: 1px solid #333333;
        border-radius: 5px;
        padding: 5px 10px;
        margin-bottom: 15px;
    }

    .checkbox-scroll-container {
        max-height: 120px;
        overflow-y: auto;
        background-color: #000000;
        border: 1px solid #333333;
        border-radius: 5px;
        padding: 5px;
        margin-bottom: 10px;
    }

    /* Scrollbar Styling */
    .checkbox-scroll-container::-webkit-scrollbar {
        width: 8px;
    }
    .checkbox-scroll-container::-webkit-scrollbar-track {
        background: #282828;
        border-radius: 10px;
    }
    .checkbox-scroll-container::-webkit-scrollbar-thumb {
        background: #555555;
        border-radius: 10px;
    }
    .checkbox-scroll-container::-webkit-scrollbar-thumb:hover {
        background: #777777;
    }

    label {
        font-size: 0.9em !important;
        color: #BBBBBB !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper function to format metric values
def format_metric_value(value, is_currency=True, is_percent=False, is_ratio=False):
    if is_ratio:
        return f"{value:.2f}x"
    if is_percent:
        return f"{value:.2f}%"
    if is_currency:
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:,.2f}M"
        if abs(value) >= 1_000:
            return f"${value / 1_000:,.2f}K"
        return f"${value:,.2f}"
    else:
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:,.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:,.2f}K"
        return f"{value:,.0f}"

# Helper function to display custom styled metrics
def display_custom_metric(title, value, is_currency=True, is_percent=False, is_ratio=False):
    formatted_value = format_metric_value(value, is_currency, is_percent, is_ratio)
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{formatted_value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- 1. Data Loading & Cleaning ---
@st.cache_data
def load_data():
    try:
        df_daily = pd.read_csv('ecommerce_daily_kpis.csv')
        df_daily['date'] = pd.to_datetime(df_daily['date'])

        df_granular = pd.read_csv('ecommerce_granular_data.csv')
        df_granular['date'] = pd.to_datetime(df_granular['date'])

        # Fix campaign vs tactic taxonomy mismatch dynamically
        conditions = [
            df_granular['campaign'].str.contains('ASC|Asc', case=False, na=False),
            df_granular['campaign'].str.contains('Prospecting', case=False, na=False),
            df_granular['campaign'].str.contains('Non-Branded Search', case=False, na=False),
            df_granular['campaign'].str.contains('Display', case=False, na=False),
            df_granular['campaign'].str.contains('Retargeting', case=False, na=False),
            df_granular['campaign'].str.contains('Spark Ads', case=False, na=False)
        ]
        choices = ['ASC', 'Prospecting', 'Non-Branded Search', 'Display', 'Retargeting', 'Spark Ads']
        df_granular['tactic'] = np.select(conditions, choices, default=df_granular['tactic'])

        return df_daily, df_granular
    except FileNotFoundError:
        st.error("Error: CSV files not found. Please ensure 'ecommerce_daily_kpis.csv' and 'ecommerce_granular_data.csv' are in the working directory.")
        st.stop()

df_daily, df_granular = load_data()


# --- 2. Sidebar Filters ---
st.sidebar.markdown("### Filters")

# Time Period Radio Button
st.sidebar.markdown("#### Time Period")
selected_time_period_radio = st.sidebar.radio(
    "Select Period",
    ("Daily", "Weekly", "Monthly", "Custom Range"),
    index=0
)

min_date_available_df = df_granular['date'].min().date()
max_date_available_df = df_granular['date'].max().date()
today = max_date_available_df

start_date_filter_raw = min_date_available_df
end_date_filter_raw = max_date_available_df
trend_granularity_str = "Daily"

if selected_time_period_radio == "Daily":
    start_date_filter_raw = today - timedelta(days=6)
    end_date_filter_raw = today
    trend_granularity_str = "Daily"
elif selected_time_period_radio == "Weekly":
    start_date_filter_raw = today - timedelta(days=29)
    end_date_filter_raw = today
    trend_granularity_str = "Weekly"
elif selected_time_period_radio == "Monthly":
    start_date_filter_raw = (today - timedelta(days=180)).replace(day=1)
    end_date_filter_raw = today
    trend_granularity_str = "Monthly"

start_date_filter = max(start_date_filter_raw, min_date_available_df)
end_date_filter = min(end_date_filter_raw, max_date_available_df)

if selected_time_period_radio == "Custom Range":
    st.sidebar.markdown("#### Custom Date Range")
    custom_date_range = st.sidebar.date_input(
        "Start Date - End Date",
        value=(start_date_filter, end_date_filter),
        min_value=min_date_available_df,
        max_value=max_date_available_df
    )
    if len(custom_date_range) == 2:
        start_date_filter = custom_date_range[0]
        end_date_filter = custom_date_range[1]
    elif len(custom_date_range) == 1:
        start_date_filter = custom_date_range[0]
        end_date_filter = max_date_available_df

start_date_filter_dt = pd.to_datetime(start_date_filter)
end_date_filter_dt = pd.to_datetime(end_date_filter)

# Checkbox-style filter helper function
def render_checkbox_filter(label, options_list, key_suffix):
    st.sidebar.markdown(f"#### {label}")
    if not options_list:
        st.sidebar.info(f"No {label.lower().replace('s','')}(s) available.")
        return []

    select_all = st.sidebar.checkbox(f"All {label.replace('s','').strip()}", value=True, key=f"all_{key_suffix}")

    selected_options = []
    if select_all:
        selected_options = options_list
    else:
        st.sidebar.markdown('<div class="checkbox-scroll-container">', unsafe_allow_html=True)
        for option in options_list:
            if st.sidebar.checkbox(option, value=True, key=f"{key_suffix}_{option}"):
                selected_options.append(option)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    return selected_options

# 1. Define Filter Options First
all_channels_list = df_granular['channel'].unique().tolist()
selected_channels = render_checkbox_filter("Marketing Channel(s)", all_channels_list, "channels")

available_tactics_list = []
if selected_channels:
    available_tactics_list = df_granular[df_granular['channel'].isin(selected_channels)]['tactic'].unique().tolist()
selected_tactics = render_checkbox_filter("Tactic(s)", available_tactics_list, "tactics")

all_states_list = df_granular['state'].unique().tolist()
selected_states = render_checkbox_filter("State(s)", all_states_list, "states")


# 2. Filter Granular DataFrame AFTER Filter Selections Are Defined
filtered_df_granular = df_granular[
    (df_granular['date'] >= start_date_filter_dt) & (df_granular['date'] <= end_date_filter_dt) &
    (df_granular['channel'].isin(selected_channels)) &
    (df_granular['tactic'].isin(selected_tactics)) &
    (df_granular['state'].isin(selected_states))
]

if filtered_df_granular.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
    st.stop()


# 3. Dynamically Aggregate Daily KPIs from Filtered Granular Data
daily_agg_base = filtered_df_granular.groupby('date').agg(
    total_orders=('total_orders', 'first'),
    new_orders=('new_orders', 'first'),
    new_customers=('new_customers', 'first'),
    total_revenue=('total_revenue', 'first'),
    gross_profit=('gross_profit', 'first'),
    COGS=('COGS', 'first'),
    total_mkt_impression=('impression', 'sum'),
    total_mkt_clicks=('clicks', 'sum'),
    total_mkt_spend=('spend', 'sum'),
    total_mkt_attributed_revenue=('attributed_revenue', 'sum')
).reset_index()

if trend_granularity_str == "Daily":
    filtered_df_daily_agg = daily_agg_base
else:
    temp_resample_freq = {'Weekly': 'W-MON', 'Monthly': 'MS', 'Quarterly': 'QS-JAN', 'Yearly': 'YS'}[trend_granularity_str]
    filtered_df_daily_agg = daily_agg_base.set_index('date').resample(temp_resample_freq).agg({
        'total_orders': 'sum',
        'new_orders': 'sum',
        'new_customers': 'sum',
        'total_revenue': 'sum',
        'gross_profit': 'sum',
        'COGS': 'sum',
        'total_mkt_impression': 'sum',
        'total_mkt_clicks': 'sum',
        'total_mkt_spend': 'sum',
        'total_mkt_attributed_revenue': 'sum'
    }).reset_index()

# Calculate ratio KPIs dynamically
filtered_df_daily_agg['ROAS'] = np.where(filtered_df_daily_agg['total_mkt_spend'] > 0, (filtered_df_daily_agg['total_mkt_attributed_revenue'] / filtered_df_daily_agg['total_mkt_spend']), 0)
filtered_df_daily_agg['CPM'] = np.where(filtered_df_daily_agg['total_mkt_impression'] > 0, (filtered_df_daily_agg['total_mkt_spend'] / filtered_df_daily_agg['total_mkt_impression']) * 1000, 0)
filtered_df_daily_agg['CPC'] = np.where(filtered_df_daily_agg['total_mkt_clicks'] > 0, (filtered_df_daily_agg['total_mkt_spend'] / filtered_df_daily_agg['total_mkt_clicks']), 0)
filtered_df_daily_agg['CTR'] = np.where(filtered_df_daily_agg['total_mkt_impression'] > 0, (filtered_df_daily_agg['total_mkt_clicks'] / filtered_df_daily_agg['total_mkt_impression']) * 100, 0)
filtered_df_daily_agg['Gross_Profit_Margin'] = np.where(filtered_df_daily_agg['total_revenue'] > 0, (filtered_df_daily_agg['gross_profit'] / filtered_df_daily_agg['total_revenue']) * 100, 0)
filtered_df_daily_agg['AOV'] = np.where(filtered_df_daily_agg['total_orders'] > 0, (filtered_df_daily_agg['total_revenue'] / filtered_df_daily_agg['total_orders']), 0)
filtered_df_daily_agg['CAC'] = np.where(filtered_df_daily_agg['new_customers'] > 0, (filtered_df_daily_agg['total_mkt_spend'] / filtered_df_daily_agg['new_customers']), 0)
filtered_df_daily_agg['%_Attributed_Revenue'] = np.where(filtered_df_daily_agg['total_revenue'] > 0, (filtered_df_daily_agg['total_mkt_attributed_revenue'] / filtered_df_daily_agg['total_revenue']) * 100, 0)


# Function to calculate aggregate KPIs for card display
def calculate_aggregate_kpis(df_daily_agg_filtered, df_granular_filtered):
    total_business_revenue = df_daily_agg_filtered['total_revenue'].sum()
    total_gross_profit = df_daily_agg_filtered['gross_profit'].sum()
    total_new_customers = df_daily_agg_filtered['new_customers'].sum()
    total_orders_biz = df_daily_agg_filtered['total_orders'].sum()

    total_spend = df_granular_filtered['spend'].sum()
    total_attributed_revenue = df_granular_filtered['attributed_revenue'].sum()
    total_impressions = df_granular_filtered['impression'].sum()
    total_clicks = df_granular_filtered['clicks'].sum()

    overall_roas = (total_attributed_revenue / total_spend) if total_spend > 0 else 0
    cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
    cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    cac = (total_spend / total_new_customers) if total_new_customers > 0 else 0
    gross_profit_margin = (total_gross_profit / total_business_revenue * 100) if total_business_revenue > 0 else 0
    aov = (total_business_revenue / total_orders_biz) if total_orders_biz > 0 else 0
    percent_attributed_revenue = (total_attributed_revenue / total_business_revenue * 100) if total_business_revenue > 0 else 0

    return {
        "Total Spend": total_spend,
        "Total Attributed Revenue": total_attributed_revenue,
        "Overall ROAS": overall_roas,
        "Total Impressions": total_impressions,
        "Total Clicks": total_clicks,
        "CPM": cpm,
        "CPC": cpc,
        "CTR": ctr,
        "CAC": cac,
        "Total Business Revenue": total_business_revenue,
        "Total Gross Profit": total_gross_profit,
        "Gross Profit Margin": gross_profit_margin,
        "Total New Customers": total_new_customers,
        "AOV": aov,
        "Percent Attributed Revenue": percent_attributed_revenue
    }

kpis = calculate_aggregate_kpis(filtered_df_daily_agg, filtered_df_granular)


# --- 3. Main Dashboard Layout ---
st.markdown("## Marketing Intelligence Dashboard")

tab_overview, tab_channel, tab_campaign_tactic, tab_business_impact = st.tabs([
    " Overview", " Channel Performance", " Campaign & Tactic Deep Dive", " Business Impact"
])

# --- Tab 1: Overview ---
with tab_overview:
    st.markdown("")

    # Dynamic Executive Key Takeaways
    st.markdown("### 💡 Executive Key Takeaways")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.info(f"**Current View ROAS:**\n\nSelected filter scope delivers an overall **{kpis['Overall ROAS']:.2f}x ROAS** across all active campaigns.")

    with col_b:
        st.success(f"**Attributed Efficiency:**\n\nMarketing directly generated **{format_metric_value(kpis['Total Attributed Revenue'])}** from **{format_metric_value(kpis['Total Spend'])}** total ad spend.")

    with col_c:
        st.warning("**Optimization Focus:**\n\nReallocating spend from low-ROAS campaigns (e.g. `Google - C06` at 1.60x) into Search or ASC drives higher net revenue.")

    st.markdown("---")

    # Top KPI Metrics (Row 1)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        display_custom_metric("Total Spend", kpis['Total Spend'])
    with col2:
        display_custom_metric("Attributed Revenue", kpis['Total Attributed Revenue'])
    with col3:
        display_custom_metric("Overall ROAS", kpis['Overall ROAS'], is_currency=False, is_ratio=True)
    with col4:
        display_custom_metric("Total Business Revenue", kpis['Total Business Revenue'])
    with col5:
        display_custom_metric("Total Gross Profit", kpis['Total Gross Profit'])

    # Top KPI Metrics (Row 2)
    col6, col7, col8, col9, col10 = st.columns(5)
    with col6:
        display_custom_metric("Total Impressions", kpis['Total Impressions'], is_currency=False)
    with col7:
        display_custom_metric("Total Clicks", kpis['Total Clicks'], is_currency=False)
    with col8:
        display_custom_metric("Total New Customers", kpis['Total New Customers'], is_currency=False)
    with col9:
        display_custom_metric("CAC", kpis['CAC'])
    with col10:
        display_custom_metric("Gross Profit Margin", kpis['Gross Profit Margin'], is_currency=False, is_percent=True)

    st.markdown("---")

    # Trends Layout
    col_roas_trend, col_ads_dynamics = st.columns([0.6, 0.4])

    with col_roas_trend:
        st.markdown("#### ROAS Trend")
        daily_roas_trend_data = filtered_df_daily_agg[['date', 'ROAS']].copy()
        fig_roas_trend = px.line(daily_roas_trend_data, x='date', y='ROAS',
                                 title=f'{trend_granularity_str} Overall ROAS Trend',
                                 labels={'ROAS': 'ROAS (Ratio)'},
                                 hover_data={'date': '|%Y-%m-%d', 'ROAS': ':.2f'})
        fig_roas_trend.update_traces(mode='lines+markers', marker_size=4)
        fig_roas_trend.update_layout(hovermode="x unified", title_x=0.5)
        st.plotly_chart(fig_roas_trend, use_container_width=True)

    with col_ads_dynamics:
        st.markdown("#### Ads Dynamics by Channel")
        ads_dynamics_metric_options = {
            "Spend": "spend",
            "Attributed Revenue": "attributed_revenue",
            "Impressions": "impression",
            "Clicks": "clicks"
        }
        selected_ads_metric_display = st.selectbox(
            "Metric",
            options=list(ads_dynamics_metric_options.keys()),
            index=0,
            key="ads_dynamics_metric_selector",
            label_visibility="collapsed"
        )
        selected_ads_metric_col = ads_dynamics_metric_options[selected_ads_metric_display]

        ads_dynamics_data_raw = filtered_df_granular.groupby(['date', 'channel']).agg(
            sum_metric=(selected_ads_metric_col, 'sum')
        ).reset_index()
        ads_dynamics_data_raw.rename(columns={'sum_metric': selected_ads_metric_display}, inplace=True)

        if trend_granularity_str == "Daily":
            ads_dynamics_data = ads_dynamics_data_raw
        else:
            temp_resample_freq = {'Weekly': 'W-MON', 'Monthly': 'MS', 'Quarterly': 'QS-JAN', 'Yearly': 'YS'}[trend_granularity_str]
            ads_dynamics_data = ads_dynamics_data_raw.set_index('date').groupby('channel').resample(
                temp_resample_freq
            ).agg(
                total_metric=(selected_ads_metric_display, 'sum')
            ).reset_index()
            ads_dynamics_data.rename(columns={'total_metric': selected_ads_metric_display}, inplace=True)

        fig_ads_dynamics = px.bar(ads_dynamics_data, x='date', y=selected_ads_metric_display,
                                 color='channel', color_discrete_map=CHANNEL_COLORS,
                                 title=f'{trend_granularity_str} Ads Dynamics: {selected_ads_metric_display}',
                                 labels={'date': 'Date', selected_ads_metric_display: selected_ads_metric_display})
        fig_ads_dynamics.update_layout(hovermode="x unified", title_x=0.5)
        st.plotly_chart(fig_ads_dynamics, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Marketing Spend vs. Attributed Revenue")
    daily_spend_revenue_data = filtered_df_daily_agg[['date', 'total_mkt_spend', 'total_mkt_attributed_revenue']].copy()
    fig_spend_revenue = px.line(daily_spend_revenue_data, x='date', y=['total_mkt_spend', 'total_mkt_attributed_revenue'],
                                title=f'{trend_granularity_str} Marketing Spend vs. Attributed Revenue',
                                labels={'value': 'Amount ($)', 'variable': 'Metric'},
                                line_shape="spline")
    fig_spend_revenue.update_traces(mode='lines+markers', marker_size=4)
    fig_spend_revenue.update_layout(hovermode="x unified", title_x=0.5)
    st.plotly_chart(fig_spend_revenue, use_container_width=True)


# --- Tab 2: Channel Performance ---
with tab_channel:
    st.markdown("### Channel Performance Deep Dive")

    channel_perf_data = filtered_df_granular.groupby('channel').agg(
        total_spend=('spend', 'sum'),
        total_attributed_revenue=('attributed_revenue', 'sum'),
        total_impressions=('impression', 'sum'),
        total_clicks=('clicks', 'sum')
    ).reset_index()

    channel_perf_data['ROAS'] = np.where(channel_perf_data['total_spend'] > 0,
                                         (channel_perf_data['total_attributed_revenue'] / channel_perf_data['total_spend']), 0)
    channel_perf_data['CTR'] = np.where(channel_perf_data['total_impressions'] > 0,
                                        (channel_perf_data['total_clicks'] / channel_perf_data['total_impressions']) * 100, 0)
    channel_perf_data['CPC'] = np.where(channel_perf_data['total_clicks'] > 0,
                                        (channel_perf_data['total_spend'] / channel_perf_data['total_clicks']), 0)
    channel_perf_data['CPM'] = np.where(channel_perf_data['total_impressions'] > 0,
                                        (channel_perf_data['total_spend'] / channel_perf_data['total_impressions']) * 1000, 0)

    if channel_perf_data.empty:
        st.info("No channel data for the selected period and filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ROAS by Channel")
            fig_channel_roas = px.bar(channel_perf_data, x='channel', y='ROAS',
                                      title=f'ROAS by Marketing Channel',
                                      color='channel', color_discrete_map=CHANNEL_COLORS,
                                      hover_data=['total_spend', 'total_attributed_revenue'],
                                      labels={'ROAS': 'ROAS (Ratio)'})
            fig_channel_roas.update_layout(title_x=0.5)
            st.plotly_chart(fig_channel_roas, use_container_width=True)

        with col2:
            st.markdown("#### Spend Distribution by Channel")
            fig_spend_dist = px.pie(channel_perf_data, values='total_spend', names='channel',
                                    title=f'Marketing Spend Distribution by Channel',
                                    color='channel', color_discrete_map=CHANNEL_COLORS,
                                    hole=0.3)
            fig_spend_dist.update_layout(title_x=0.5)
            st.plotly_chart(fig_spend_dist, use_container_width=True)

        st.markdown("### Daily ROAS Trend by Channel")
        channel_daily_roas_trend = filtered_df_granular.groupby(['date', 'channel']).agg(
            daily_spend=('spend', 'sum'),
            daily_attributed_revenue=('attributed_revenue', 'sum')
        ).reset_index()
        channel_daily_roas_trend['ROAS'] = np.where(channel_daily_roas_trend['daily_spend'] > 0,
                                                    (channel_daily_roas_trend['daily_attributed_revenue'] / channel_daily_roas_trend['daily_spend']), 0)

        fig_channel_roas_trend = px.line(channel_daily_roas_trend, x='date', y='ROAS', color='channel',
                                         title=f'Daily ROAS Trend by Channel (Granular View)',
                                         color_discrete_map=CHANNEL_COLORS,
                                         labels={'ROAS': 'ROAS (Ratio)'},
                                         line_shape="spline")
        fig_channel_roas_trend.update_traces(mode='lines+markers', marker_size=4)
        fig_channel_roas_trend.update_layout(hovermode="x unified", title_x=0.5)
        st.plotly_chart(fig_channel_roas_trend, use_container_width=True)

        st.markdown("### Detailed Channel Performance Metrics")
        st.dataframe(channel_perf_data.set_index('channel').style.format({
            'total_spend': '${:,.2f}',
            'total_attributed_revenue': '${:,.2f}',
            'ROAS': '{:.2f}x',
            'CTR': '{:.2f}%',
            'CPC': '${:.2f}',
            'CPM': '${:,.2f}',
            'total_impressions': '{:,.0f}',
            'total_clicks': '{:,.0f}'
        }))


# --- Tab 3: Campaign & Tactic Deep Dive ---
with tab_campaign_tactic:
    st.markdown("### Campaign and Tactic Performance")

    st.markdown("#### ROAS by Tactic Across Channels")
    tactic_perf_data = filtered_df_granular.groupby(['channel', 'tactic']).agg(
        total_spend=('spend', 'sum'),
        total_attributed_revenue=('attributed_revenue', 'sum')
    ).reset_index()
    tactic_perf_data['ROAS'] = np.where(tactic_perf_data['total_spend'] > 0,
                                        (tactic_perf_data['total_attributed_revenue'] / tactic_perf_data['total_spend']), 0)

    fig_tactic_roas = px.bar(tactic_perf_data, x='tactic', y='ROAS', color='channel',
                             title='ROAS by Tactic Across Channels',
                             barmode='group', color_discrete_map=CHANNEL_COLORS,
                             hover_data=['total_spend', 'total_attributed_revenue'],
                             labels={'ROAS': 'ROAS (Ratio)'})
    fig_tactic_roas.update_layout(title_x=0.5)
    st.plotly_chart(fig_tactic_roas, use_container_width=True)

    st.markdown("#### Campaign Performance: ROAS vs. Spend")
    campaign_perf_data = filtered_df_granular.groupby(['channel', 'tactic', 'campaign', 'state']).agg(
        total_spend=('spend', 'sum'),
        total_attributed_revenue=('attributed_revenue', 'sum'),
        total_impressions=('impression', 'sum'),
        total_clicks=('clicks', 'sum')
    ).reset_index()
    campaign_perf_data['ROAS'] = np.where(campaign_perf_data['total_spend'] > 0,
                                          (campaign_perf_data['total_attributed_revenue'] / campaign_perf_data['total_spend']), 0)
    campaign_perf_data['CTR'] = np.where(campaign_perf_data['total_impressions'] > 0,
                                          (campaign_perf_data['total_clicks'] / campaign_perf_data['total_impressions']) * 100, 0)
    campaign_perf_data['CPC'] = np.where(campaign_perf_data['total_clicks'] > 0,
                                          (campaign_perf_data['total_spend'] / campaign_perf_data['total_clicks']), 0)

    fig_campaign_scatter = px.scatter(campaign_perf_data, x='total_spend', y='ROAS',
                                      size='total_attributed_revenue',
                                      color='channel', color_discrete_map=CHANNEL_COLORS,
                                      hover_name='campaign',
                                      title='Campaign Performance: ROAS vs. Spend (Bubble size = Attributed Revenue)',
                                      labels={'total_spend': 'Total Spend ($)', 'ROAS': 'ROAS (Ratio)'},
                                      hover_data={
                                          'total_spend': ':.2f',
                                          'ROAS': ':.2f',
                                          'total_attributed_revenue': ':.2f',
                                          'tactic': True,
                                          'state': True,
                                          'channel': True
                                      })
    fig_campaign_scatter.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')), selector=dict(mode='markers'))
    fig_campaign_scatter.update_layout(showlegend=True, hovermode="closest", title_x=0.5)
    st.plotly_chart(fig_campaign_scatter, use_container_width=True)

    st.markdown("### Detailed Campaign Metrics Table")
    st.dataframe(campaign_perf_data.style.format({
        'total_spend': '${:,.2f}',
        'total_attributed_revenue': '${:,.2f}',
        'ROAS': '{:.2f}x',
        'CTR': '{:.2f}%',
        'CPC': '${:.2f}',
        'total_impressions': '{:,.0f}',
        'total_clicks': '{:,.0f}'
    }))


# --- Tab 4: Business Impact ---
with tab_business_impact:
    st.markdown("### Business Impact & Customer Acquisition")

    st.markdown("#### Revenue & Profit Trends")
    fig_revenue_profit = px.line(filtered_df_daily_agg, x='date', y=['total_revenue', 'gross_profit'],
                                 title=f'{trend_granularity_str} Total Revenue vs. Gross Profit',
                                 labels={'value': 'Amount ($)', 'variable': 'Metric'},
                                 line_shape="spline")
    fig_revenue_profit.update_traces(mode='lines+markers', marker_size=4)
    fig_revenue_profit.update_layout(hovermode="x unified", title_x=0.5)
    st.plotly_chart(fig_revenue_profit, use_container_width=True)

    st.markdown("#### Customer Acquisition Trends")
    col1, col2 = st.columns(2)
    with col1:
        fig_new_customers = px.line(filtered_df_daily_agg, x='date', y='new_customers',
                                    title=f'{trend_granularity_str} New Customers Acquired',
                                    labels={'new_customers': 'New Customers'},
                                    line_shape="spline")
        fig_new_customers.update_traces(mode='lines+markers', marker_size=4)
        fig_new_customers.update_layout(hovermode="x unified", title_x=0.5)
        st.plotly_chart(fig_new_customers, use_container_width=True)
    with col2:
        fig_cac_trend = px.line(filtered_df_daily_agg, x='date', y='CAC',
                                title=f'{trend_granularity_str} Customer Acquisition Cost (CAC) Trend',
                                labels={'CAC': 'CAC ($)'},
                                line_shape="spline")
        fig_cac_trend.update_traces(mode='lines+markers', marker_size=4)
        fig_cac_trend.update_layout(hovermode="x unified", title_x=0.5)
        st.plotly_chart(fig_cac_trend, use_container_width=True)

    st.markdown("#### Marketing Attributed Revenue vs. Total Business Revenue")
    plot_df_revenue_stack = filtered_df_daily_agg[['date', 'total_revenue', 'total_mkt_attributed_revenue']].copy()
    plot_df_revenue_stack['Non-Attributed Revenue'] = plot_df_revenue_stack['total_revenue'] - plot_df_revenue_stack['total_mkt_attributed_revenue']
    plot_df_revenue_stack['Non-Attributed Revenue'] = plot_df_revenue_stack['Non-Attributed Revenue'].clip(lower=0)

    fig_attr_vs_total_rev = px.area(plot_df_revenue_stack, x='date',
                                    y=['total_mkt_attributed_revenue', 'Non-Attributed Revenue'],
                                    title=f'{trend_granularity_str} Attributed vs. Non-Attributed Business Revenue',
                                    labels={'value': 'Revenue ($)', 'variable': 'Revenue Type'},
                                    color_discrete_map={
                                        'total_mkt_attributed_revenue': CHANNEL_COLORS['Facebook'],
                                        'Non-Attributed Revenue': '#555555'
                                    })
    fig_attr_vs_total_rev.for_each_trace(lambda t: t.update(name = "Marketing Attributed" if t.name == "total_mkt_attributed_revenue" else t.name))
    fig_attr_vs_total_rev.update_layout(hovermode="x unified", title_x=0.5)
    st.plotly_chart(fig_attr_vs_total_rev, use_container_width=True)

    st.markdown("### Daily Business Performance Details")
    st.dataframe(filtered_df_daily_agg[[
        'date', 'total_orders', 'new_orders', 'new_customers',
        'total_revenue', 'gross_profit', 'COGS', 'Gross_Profit_Margin', 'AOV',
        'total_mkt_spend', 'total_mkt_attributed_revenue', 'ROAS', 'CAC', '%_Attributed_Revenue'
    ]].style.format({
        'date': '{:%Y-%m-%d}',
        'total_orders': '{:,.0f}',
        'new_orders': '{:,.0f}',
        'new_customers': '{:,.0f}',
        'total_revenue': '${:,.2f}',
        'gross_profit': '${:,.2f}',
        'COGS': '${:,.2f}',
        'Gross_Profit_Margin': '{:.2f}%',
        'AOV': '${:,.2f}',
        'total_mkt_spend': '${:,.2f}',
        'total_mkt_attributed_revenue': '${:,.2f}',
        'ROAS': '{:.2f}x',
        'CAC': '${:,.2f}',
        '%_Attributed_Revenue': '{:.2f}%'
    }))