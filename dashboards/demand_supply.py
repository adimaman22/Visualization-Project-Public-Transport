import streamlit as st
# import pandas as pd
import plotly.express as px


# Load dataset
# @st.cache_data(ttl=3600)
# def load_data():
#     file_path = "data/2024_public_transport_ridership.csv"
#     data = pd.read_csv(file_path)
#     return data


# Custom display names:
display_names = {
    "Metropolin": "Metropolitan Area",
    "ClusterName": "Regions",
    "DailyPassengers": "Daily Passengers",
    "DailyRides": "Daily Rides",
    "WeeklyPassengers": "Weekly Passengers",
    "WeekyRides": "Weekly Rides"
}

# Correct city/region names
region_name_corrections = {
    "חולון עירוני ומטרופוליני+תחרות חולון": "חולון עירוני",
    "קווי נצרת - שאמ": "נצרת - שאם",
    "קווי נצרת - נסיעות ותיירות": "נצרת"
}


# Set different chart sizes for ClusterName and Metropolin
def get_chart_size(group_by_option):
    # return: (width, height, l, r)
    if group_by_option == "ClusterName":
        return 1500, 1500, 10, 10   # Larger size for clusters
    else:
        return 900, 600, 50, 50  # Smaller size for metropolitan areas


# Generate the bar chart with dynamic size adjustment
def generate_bar_chart(grouped_data, group_by_option, sort_order):
    width, height, l, r = get_chart_size(group_by_option)

    # Sorting logic
    if sort_order == "Supply":
        grouped_data = grouped_data.sort_values("Supply (%)", ascending=True)
    elif sort_order == "Demand":
        grouped_data = grouped_data.sort_values("Demand (%)", ascending=True)
    elif sort_order == "Name":
        grouped_data = grouped_data.sort_values(group_by_option, ascending=False)

    # Apply city name corrections
    grouped_data[group_by_option] = grouped_data[group_by_option].replace(region_name_corrections)

    fig_bar = px.bar(
        grouped_data,
        y=group_by_option,
        x=["Demand (%)", "Supply (%)"],
        orientation='h',
        title=f"Demand vs Supply Percentage by {display_names.get(group_by_option, group_by_option)}",
        labels={"value": "Percentage", "variable": "Metric"},
        text_auto=True,
        barmode='group',
        color_discrete_map={"Demand (%)": "#2E86C1", "Supply (%)": "#F39C12"}  # Green for demand, red for supply
    )

    # Ensure text orientation downwards and alignment
    fig_bar.update_traces(textangle=0, textposition='inside')

    fig_bar.update_layout(
        height=height,
        width=width,
        margin=dict(l=l, r=r, t=50, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        xaxis_title="Percentage",
        yaxis_title="Regions",
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgrey'),
        font=dict(size=14),
        title_font=dict(size=22)
    )

    return fig_bar


def show(ridership_data):
    st.title("📊 Demand vs. Supply Analysis")
    st.markdown("##### Analyze demand and supply discrepancies in public transportation by comparing ridership data with service frequency.")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.markdown("##### 🤔 How to Use", unsafe_allow_html=True, help=""" # This visualization compares passenger demand with bus service frequency across different regions.

    - Analysis type: choose between Weekly to Daily Comparison
    - Group By: Choose to view data by Metropolitan Area or Regions
    - Sort By:
       `Supply`: Sort by bus service frequency
       `Demand`: Sort by passenger numbers
       `Name`: Sort alphabetically

    Interpretation Tips:
    - Blue bars represent passenger demand
    - Orange bars represent bus service supply
    - Bars closer in length indicate better balance
    - Longer blue bars vs. short orange bars suggest under-served routes
    - Longer orange bars vs. short blue bars suggest over-serviced routes
        """)

    # Load data
    data = ridership_data

    # Select columns for demand vs. supply comparison
    # st.markdown("#### Feature Selection", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        # User selection for analysis type
        analysis_type = st.selectbox("Analysis type:", ["Weekly Comparison", "Daily Comparison"])
    with col2:
        # Select group-by criteria
        group_by_option = st.selectbox("Group by:", ["Metropolin", "ClusterName"], format_func=lambda x: display_names.get(x, x))
    with col3:
        sort_order = st.selectbox("Sort by:", ["Supply", "Demand", "Name"])

    # Filter and aggregate data based on selection
    if analysis_type == "Weekly Comparison":
        demand_col, supply_col = 'WeeklyPassengers', 'WeekyRides'
    else:
        demand_col, supply_col = 'DailyPassengers', 'DailyRides'

    # Aggregate data by the selected criteria
    grouped_data = data.groupby(group_by_option).agg({
        demand_col: 'sum',
        supply_col: 'sum'
    }).reset_index()

    # Calculate percentage of demand and supply
    grouped_data["Demand (%)"] = round((grouped_data[demand_col] / grouped_data[demand_col].sum()) * 100, 2)
    grouped_data["Supply (%)"] = round((grouped_data[supply_col] / grouped_data[supply_col].sum()) * 100, 2)

    # Filter out rows where both demand and supply percentages are less than 1 (for clusters only)
    if group_by_option == "ClusterName":
        grouped_data = grouped_data[(grouped_data["Demand (%)"] >= 1) | (grouped_data["Supply (%)"] >= 1)]

    # Generate the customized bar chart
    fig_bar = generate_bar_chart(grouped_data, group_by_option, sort_order)
    st.plotly_chart(fig_bar)

    ########################
