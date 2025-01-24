import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# @st.cache_data(ttl=3600)
# def load_and_process_data(performance_data):
#     # df = pd.read_parquet("data/2024_bus_performance.parquet")
#     df = performance_data
#
#     # Time processing
#     df['planned_time'] = pd.to_datetime(df['trip_dt'] + ' ' + df['trip_time'])
#     df['actual_time'] = pd.to_datetime(df['bitzua_history_start_dt'])
#
#     # Calculate delays considering potential date crossover
#     time_diff = df['actual_time'] - df['planned_time']
#     df['delay_minutes'] = time_diff.dt.total_seconds() / 60
#     df.loc[df['delay_minutes'] > 720, 'delay_minutes'] -= 1440
#     df.loc[df['delay_minutes'] < -720, 'delay_minutes'] += 1440
#
#     # Add delay categories
#     df['delay_category'] = pd.cut(
#         df['delay_minutes'],
#         bins=[-float('inf'), -5, -2, 2, 5, float('inf')],
#         labels=['Early (>5min)', 'Slightly Early (2-5min)',
#                 'On Time (±2min)', 'Slightly Late (2-5min)', 'Late (>5min)']
#     )
#
#     # Time-related features
#     df['hour'] = df['planned_time'].dt.strftime('%H:00')  # Format as hour of day
#     df['date'] = df['planned_time'].dt.date
#     df['day_name'] = pd.Categorical(df['trip_day_in_week'].map({
#         1: 'Sunday', 2: 'Monday', 3: 'Tuesday',
#         4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'
#     }))
#
#     # Add metropolitan area mapping
#     metro_mapping = {
#         'North': ['גליל עמקים', 'חיפה'],
#         'Center': ['תל אביב', 'ירושלים', 'מרכז'],
#         'South': ['דרום', 'צפון הנגב', 'אשדוד', 'באר שבע', 'אשקלון'],
#         'Inter-city': ['ירושלים קווי צפון', 'ירושלים צפון-ציר מזרחי', 'חיפה-ירושלים-אילת', 'חיפה-שרון-ירושלים', 'בין עירוני']
#     }
#
#     # Create metropolitan area column
#     df['metro_area'] = 'Other'
#     for area, clusters in metro_mapping.items():
#         df.loc[df['cluster_nm'].str.contains('|'.join(clusters), na=False), 'metro_area'] = area
#
#     return df


def show(performance_data):
    st.title("🚌 Bus Departure Time Performance Analysis")
    st.markdown("##### Identifying Routes with Poor Performance and Analyzing Delay Patterns")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.markdown("##### 🤔 How to Use", unsafe_allow_html=True, help=""" # This visualization identify and analyze bus routes with performance issues and delay patterns.

    Route Analysis Tab:
        Use sliders to adjust:
          - Minimum trips per line
          - Number of worst-performing routes
          - Delay threshold
    
    Time Patterns Tab:
        View delays by:
          - Hour of day
          - Delay categories
          - Day of week
    
    Regional Analysis Tab:
        Compare performance across:
          - Center
          - North
          - South
          - Inter-city routes
    
    Key Metrics to Watch:
        - Average delay
        - Percentage of delayed trips
        - On-time performance
        """)

    # Load data
    # df = load_and_process_data(performance_data)
    df = performance_data

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Route Analysis", "🕒 Time Patterns", "🗺 Regional Analysis"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            min_trips = st.slider("Minimum trips per line:", 10, 200, 50)
        with col2:
            n_worst_routes = st.slider("Number of worst performing routes:", 5, 20, 10)
        with col3:
            delay_threshold = st.slider("Significant delay threshold (minutes):", 1, 15, 5)

        # Calculate route performance metrics
        route_stats = df.groupby(['OperatorLineId', 'operator_nm', 'cluster_nm']).agg({
            'delay_minutes': ['mean', 'std', 'count'],
            'delay_category': lambda x: (x == 'On Time (±2min)').mean()
        }).reset_index()

        route_stats.columns = ['line_id', 'operator', 'cluster', 'avg_delay',
                               'std_delay', 'trip_count', 'on_time_ratio']

        # Filter and sort routes
        worst_routes = route_stats[route_stats['trip_count'] >= min_trips] \
            .nlargest(n_worst_routes, 'avg_delay')

        # Create visualization for worst performing routes
        fig1 = go.Figure()
        fig1.add_trace(
            go.Bar(
                x=[str(x) for x in worst_routes['line_id']],  # Convert to string for categorical
                y=worst_routes['avg_delay'],
                text=worst_routes['avg_delay'].round(1),
                textposition='auto',
                error_y=dict(
                    type='data',
                    array=worst_routes['std_delay'],
                    visible=True
                ),
                hovertemplate=(
                        "Line: %{x}<br>" +
                        "Average Delay: %{y:.1f} minutes<br>" +
                        "Trips: %{customdata[0]}<br>" +
                        "Region: %{customdata[1]}<br>" +
                        "On-time: %{customdata[2]:.1%}"
                ),
                customdata=worst_routes[['trip_count', 'cluster', 'on_time_ratio']].values
            )
        )

        fig1.update_layout(
            title=f"Top {n_worst_routes} Routes with Poorest Performance",
            xaxis_title="Route Number",
            yaxis_title="Average Delay (minutes)",
            height=600,
            xaxis={'type': 'category'}  # Force categorical axis
        )

        st.plotly_chart(fig1, use_container_width=True)

        # Detailed route analysis
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 0.5, 1, 0.5])
            with col1:
                st.subheader("Detailed Route Analysis")
            with col2:
                st.write("")
                st.write("Select route:")
            with col3:
                st.write("")
                selected_route = st.selectbox(
                    " ",
                    options=worst_routes['line_id'].astype(str),
                    format_func=lambda x: f"Route {x}",
                    label_visibility="collapsed"
                )

        route_data = df[df['OperatorLineId'].astype(str) == selected_route]

        fig2 = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                "Distribution of Delays (minutes)",
                "Average Delay by Hour of Day (minutes)"
            )
        )

        fig2.add_trace(
            go.Histogram(
                x=route_data['delay_minutes'],
                nbinsx=30,
                name="Delay Distribution"
            ),
            row=1, col=1
        )

        hourly_delays = route_data.groupby('hour')['delay_minutes'].agg(['mean', 'count']) \
            .reset_index()
        fig2.add_trace(
            go.Scatter(
                x=hourly_delays['hour'],
                y=hourly_delays['mean'],
                mode='lines+markers',
                name="Average Delay",
                marker=dict(size=hourly_delays['count'] / 10),
                hovertemplate=(
                        "Hour: %{x}<br>" +
                        "Average Delay: %{y:.1f} minutes<br>" +
                        "Trips: %{customdata}<extra></extra>"
                ),
                customdata=hourly_delays['count']
            ),
            row=1, col=2
        )

        fig2.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Time-Based Analysis")
        fig3 = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Average Delays by Hour of Day (minutes)",
                "Delay Category Distribution",
                "Delays by Day of Week (minutes)",
                "Daily Delay Trend (minutes)"
            ),
            vertical_spacing=0.15
        )

        hourly_stats = df.groupby('hour')['delay_minutes'].agg(['mean', 'std', 'count']) \
            .reset_index()
        fig3.add_trace(
            go.Scatter(
                x=hourly_stats['hour'],
                y=hourly_stats['mean'],
                mode='lines+markers',
                error_y=dict(type='data', array=hourly_stats['std'] / 2),
                hovertemplate=(
                        "Hour: %{x}<br>" +
                        "Average Delay: %{y:.1f} minutes<br>" +
                        "Trips: %{customdata}<extra></extra>"
                ),
                customdata=hourly_stats['count']
            ),
            row=1, col=1
        )

        delay_dist = df['delay_category'].value_counts()
        fig3.add_trace(
            go.Bar(
                x=delay_dist.index,
                y=delay_dist.values,
                hovertemplate="Category: %{x}<br>Count: %{y:,}<extra></extra>"
            ),
            row=1, col=2
        )

        fig3.add_trace(
            go.Box(
                x=df['day_name'],
                y=df['delay_minutes'],
                hovertemplate=(
                        "Day: %{x}<br>" +
                        "Delay: %{y:.1f} minutes<extra></extra>"
                )
            ),
            row=2, col=1
        )

        daily_stats = df.groupby('date')['delay_minutes'].agg(['mean', 'count']) \
            .reset_index()
        fig3.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['mean'],
                mode='lines',
                hovertemplate=(
                        "Date: %{x|%Y-%m-%d}<br>" +
                        "Average Delay: %{y:.1f} minutes<br>" +
                        "Trips: %{customdata}<extra></extra>"
                ),
                customdata=daily_stats['count']
            ),
            row=2, col=2
        )

        fig3.update_layout(height=900, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.subheader("Regional Performance Analysis")

        # Metropolitan area filter
        metro_area = st.radio(
            "Select Metropolitan Area:", ["Center", "North",  "South", "Inter-city", "All"], horizontal=True
        )

        # Filter data based on selection
        if metro_area != "All":
            df_filtered = df[df['metro_area'] == metro_area]
            title_prefix = f"Performance in {metro_area} Region"
        else:
            df_filtered = df
            title_prefix = "Performance Across All Regions"

        # Regional analysis
        cluster_stats = df_filtered.groupby('cluster_nm').agg({
            'delay_minutes': ['mean', 'std', 'count'],
            'delay_category': lambda x: (x == 'On Time (±2min)').mean()
        }).reset_index()

        cluster_stats.columns = ['region', 'avg_delay', 'std_delay', 'trips', 'on_time_ratio']

        fig4 = go.Figure()
        fig4.add_trace(
            go.Bar(
                x=cluster_stats['region'],
                y=cluster_stats['avg_delay'],
                error_y=dict(type='data', array=cluster_stats['std_delay']),
                hovertemplate=(
                        "Region: %{x}<br>" +
                        "Average Delay: %{y:.1f} minutes<br>" +
                        "Trips: %{customdata[0]:,}<br>" +
                        "On-time: %{customdata[1]:.1%}<extra></extra>"
                ),
                customdata=cluster_stats[['trips', 'on_time_ratio']].values
            )
        )

        fig4.update_layout(
            title=title_prefix,
            xaxis_title="Region",
            yaxis_title="Average Delay (minutes)",
            height=700
        )

        st.plotly_chart(fig4, use_container_width=True)

        # Summary metrics
        st.subheader("📊 Key Performance Indicators")
        col1, col2, col3 = st.columns(3)

        with col1:
            avg_delay = df_filtered['delay_minutes'].mean()
            st.metric("Average Delay", f"{avg_delay:.1f} minutes")

        with col2:
            late_pct = (df_filtered['delay_minutes'] > delay_threshold).mean() * 100
            st.metric(f"Trips Delayed >{delay_threshold}min", f"{late_pct:.1f}%")

        with col3:
            on_time = ((df_filtered['delay_minutes'] >= -2) &
                       (df_filtered['delay_minutes'] <= 2)).mean() * 100
            st.metric("On-Time Performance", f"{on_time:.1f}%")
