import pandas as pd
import streamlit as st
# import numpy as np
import plotly.graph_objects as go


# Define a consistent color palette
COLOR_MAPPING = {
    'WorkDay': '#2E86C1',
    'Friday': '#16A085',
    'Saturday': '#8E44AD',
    'Trip Count': '#E74C3C'
}


# # Load datasets
# @st.cache_data(ttl=3600)
# def load_data():
#     passenger_data = pd.read_csv("data/2024_public_transport_ridership.csv")
#     trips_data = pd.read_parquet("data/2024_bus_performance.parquet")
#     return passenger_data, trips_data


# Process trips data
@st.cache_data(ttl=3600)
def process_trips_data(trips_df):
    trips_df['hour'] = pd.to_datetime(trips_df['trip_time']).dt.hour

    day_mapping = {
        1: 'WorkDay',
        2: 'WorkDay',
        3: 'WorkDay',
        4: 'WorkDay',
        5: 'WorkDay',
        6: 'Friday',
        7: 'Saturday'
    }
    trips_df['day_type'] = trips_df['trip_day_in_week'].map(day_mapping)

    def get_time_range(hour):
        if 0 <= hour < 4:
            return '00:00-03:59'
        elif 4 <= hour < 6:
            return '04:00-05:59'
        elif 6 <= hour < 9:
            return '06:00-08:59'
        elif 9 <= hour < 12:
            return '09:00-11:59'
        elif 12 <= hour < 15:
            return '12:00-14:59'
        elif 15 <= hour < 19:
            return '15:00-18:59'
        else:
            return '19:00-23:59'

    trips_df['time_range'] = trips_df['hour'].apply(get_time_range)

    grouped_trips = trips_df.groupby(['day_type', 'time_range']).size().reset_index(name='trip_count')
    return grouped_trips


# Process passenger data
@st.cache_data(ttl=3600)
def process_passenger_data(data):
    workday_columns = [col for col in data.columns if col.startswith('WorkDay')]
    friday_columns = [col for col in data.columns if col.startswith('Friday')]
    saturday_columns = [col for col in data.columns if col.startswith('Saturday')]

    ride_columns = {
        "WorkDay": workday_columns,
        "Friday": friday_columns,
        "Saturday": saturday_columns
    }

    all_data = []
    for day_type, columns in ride_columns.items():
        melted_data = data.melt(
            id_vars=["RouteID", "Metropolin"],
            value_vars=columns,
            var_name="TimePeriod",
            value_name="Passengers"
        )
        melted_data['DayType'] = day_type
        melted_data['TimeRange'] = melted_data['TimePeriod'].str.split(' - ').str[1]
        all_data.append(melted_data)

    return pd.concat(all_data)


# Calculate passengers per trip without normalization
@st.cache_data(ttl=3600)
def calculate_passengers_per_trip(passenger_data, trips_data, selected_day):
    passenger_day_data = passenger_data[passenger_data['DayType'] == selected_day]
    trips_day_data = trips_data[trips_data['day_type'] == selected_day]

    passenger_grouped = passenger_day_data.groupby('TimeRange')['Passengers'].sum().reset_index()
    trips_grouped = trips_day_data.groupby('time_range')['trip_count'].sum().reset_index()

    merged_data = pd.merge(passenger_grouped, trips_grouped,
                           left_on='TimeRange', right_on='time_range', how='inner')
    merged_data['passengers_per_trip'] = merged_data['Passengers'] / merged_data['trip_count']

    return merged_data


# Create visualization
def create_dashboard_visualizations(passenger_data, trips_data, selected_day, show_trips):
    passenger_day_data = passenger_data[passenger_data['DayType'] == selected_day]
    trips_day_data = trips_data[trips_data['day_type'] == selected_day]

    # Process passenger data
    passenger_grouped = passenger_day_data.groupby('TimeRange')['Passengers'].sum().reset_index()
    trips_grouped = (trips_day_data.groupby('time_range')['trip_count'].sum() / 90).reset_index()

    time_order = ['00:00-03:59', '04:00-05:59', '06:00-08:59', '09:00-11:59',
                  '12:00-14:59', '15:00-18:59', '19:00-23:59']

    # Merge data to ensure synchronized time ranges
    if show_trips:
        merged_data = pd.merge(
            passenger_grouped,
            trips_grouped,
            left_on='TimeRange',
            right_on='time_range',
            how='outer'
        )
        # Calculate passengers per trip ratio
        merged_data['passengers_per_trip'] = merged_data['Passengers'] / merged_data['trip_count']

        # Sort by time range
        merged_data['TimeRange'] = pd.Categorical(merged_data['TimeRange'],
                                                  categories=time_order,
                                                  ordered=True)
        merged_data = merged_data.sort_values('TimeRange')

        fig = go.Figure()

        # Add passenger trace
        fig.add_trace(
            go.Scatter(
                x=merged_data['TimeRange'],
                y=merged_data['Passengers'],
                mode='lines+markers',
                name='Passenger Count',
                line=dict(color=COLOR_MAPPING[selected_day], shape='spline'),
                customdata=merged_data[['Passengers', 'trip_count', 'passengers_per_trip']],
                hovertemplate=(
                        f"<span style='color: {COLOR_MAPPING[selected_day]}'>Passengers:</span> %{{customdata[0]:,.0f}}<br>" +
                        "<span style='color: #E74C3C'>Trips:</span> %{customdata[1]:.0f}<br>" +
                        "<b>Passengers per Trip: %{customdata[2]:.1f}</b>" +
                        "<extra></extra>"
                )
            )
        )

        # Add trips trace
        fig.add_trace(
            go.Scatter(
                x=merged_data['TimeRange'],
                y=merged_data['trip_count'],
                mode='lines+markers',
                name='Trip Count',
                line=dict(color=COLOR_MAPPING['Trip Count'], shape='spline'),
                customdata=merged_data[['Passengers', 'passengers_per_trip']],
                hoverinfo='skip'
            )
        )

    else:
        # Original single trace visualization
        passenger_grouped['Time Range'] = pd.Categorical(passenger_grouped['TimeRange'],
                                                         categories=time_order,
                                                         ordered=True)
        passenger_grouped = passenger_grouped.sort_values('TimeRange')

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=passenger_grouped['TimeRange'],
                y=passenger_grouped['Passengers'],
                mode='lines+markers',
                name='Passenger Count',
                line=dict(color=COLOR_MAPPING[selected_day], shape='spline'),
                hovertemplate=(
                        "Passengers: %{y:,.0f}<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title=f"Passenger Demand Throughout the Day ({selected_day})",
        xaxis_title="Time Range",
        yaxis_title="Count",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            orientation="v"
        ),
        margin=dict(l=40, r=40, t=50, b=50),
        plot_bgcolor="white",
        showlegend=True,
        hovermode='x unified'  # Show all traces for the same x-value
    )

    st.plotly_chart(fig)


# Main function to show the dashboard
def show(ridership_data, performance_data):
    st.title("⏳ Public Transport Variation Over Time")
    st.markdown("##### Analyze passenger demand and trip counts throughout the day for different day types.")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.markdown("##### 🤔 How to Use", unsafe_allow_html=True, help=""" # This visualization explore passenger demand patterns throughout the day for different day types.

    Day Selection:
      - `WorkDay`: Weekday patterns
      - `Friday`: Weekend pre-Shabbat patterns
      - `Saturday`: Weekend/Shabbat patterns
    
    Trip Count Toggle:
      - When enabled, shows both passenger count and number of trips
      - Hover over points to see detailed breakdown
    
    Insights:
    - Identify peak travel hours
    - Compare passenger load across different days
    - Understand trip frequency and demand correlation
        """)

    passenger_data, trips_data = ridership_data, performance_data
    processed_passenger_data = process_passenger_data(passenger_data)
    processed_trips_data = process_trips_data(trips_data)

    col1, col2 = st.columns(2)
    with col1:
        selected_day = st.radio("Select a day:", ["All Days", "WorkDay", "Friday", "Saturday"], horizontal=True)
    with col2:
        if selected_day != "All Days":
            show_trips = st.checkbox("Show trip count", value=False)

    if selected_day == "All Days":
        combined_data = processed_passenger_data.groupby(['DayType', 'TimeRange'])['Passengers'].sum().reset_index()

        fig = go.Figure()

        for day_type in ['WorkDay', 'Friday', 'Saturday']:
            day_data = combined_data[combined_data['DayType'] == day_type]
            fig.add_trace(
                go.Scatter(
                    x=day_data['TimeRange'],
                    y=day_data['Passengers'],
                    mode='lines+markers',
                    name=day_type,
                    line=dict(color=COLOR_MAPPING[day_type], shape='spline'),
                    hovertemplate=(
                        "Passengers: %{y:,.0f}<extra></extra>"
                    )
                )
            )

        fig.update_layout(
            title="Passenger Demand for All Days",
            xaxis_title="Time Range",
            yaxis_title="Passenger Count",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                orientation="v"
            ),
            margin=dict(l=40, r=40, t=50, b=50),
            plot_bgcolor="white"
        )

        st.plotly_chart(fig)
    else:
        create_dashboard_visualizations(processed_passenger_data, processed_trips_data, selected_day, show_trips)