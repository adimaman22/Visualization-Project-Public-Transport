import streamlit as st
# import pandas as pd


# # Load datasets
# @st.cache_data(ttl=3600)
# def load_ridership_data():
#     file_path = "data/2024_public_transport_ridership.csv"
#     data = pd.read_csv(file_path)
#     return data
#
#
# @st.cache_data(ttl=3600)
# def load_performance_data():
#     file_path = "data/2024_bus_performance.parquet"
#     data = pd.read_parquet(file_path)
#     return data


def show(ridership_data, performance_data):
    # Load data for statistics
    st.markdown("### Data Overview")

    data = ridership_data

    # Calculate key statistics
    total_trips = data["WeekyRides"].sum()
    total_day_trips = data["DailyRides"].sum()
    daily_passengers = int(data["DailyPassengers"].sum())
    ratio = round((total_day_trips/daily_passengers)*100, 2)  # round((total_trips/(daily_passengers * 365))*100, 2)
    total_routes = data["RouteID"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; line-height: 1.3; align-items: flex-start;">
                <span style="font-size: 18px;">🚍 Total Trips in 2024</span>
                <span style="font-size: 34px; color: #333; text-align: center; padding-left: 40px;"><b>{round((total_trips / 1000000), 1):,}M</b></span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; line-height: 1.3; align-items: flex-start;">
                <span style="font-size: 18px;">🧑‍🤝‍🧑 Daily Passengers</span>
                <span style="font-size: 34px; color: #333; text-align: center; padding-left: 40px;"><b>{round((daily_passengers / 1000000), 1):,}M</b></span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; line-height: 1.3; align-items: flex-start;">
                <span style="font-size: 18px;">🛣️ Total Routes Available</span>
                <span style="font-size: 34px; color: #333; text-align: center; padding-left: 50px;;"><b>{total_routes}</b></span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        # Determine color and status based on the ratio value
        if ratio < 15:
            color = "red"
            ratio_status = "Under-supplied 🚨"
        elif 15 <= ratio <= 30:
            color = "green"
            ratio_status = "Balanced ✅"
        else:
            color = "orange"
            ratio_status = "Over-supplied ⚠️"

        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; line-height: 1.3; align-items: flex-start;">
                <span style="font-size: 18px;">📊 Service Coverage Ratio /day</span>
                <div style="text-align: center; width: 100%;">
                    <span style="font-size: 34px; color: {color}; text-align: center">
                        <b>{ratio}%</b>
                    </span>
                </div>
                <div style="text-align: center; width: 100%;">
                    <small style="font-size: 15px; color: black;">{ratio_status}</small><br>
                    <small style="font-size: 15px; color: black;">Balanced range: 15%-30%</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Show dataset sample with filtering and selection

    # Dataset description
    st.markdown("""
    #### Available Datasets:
    - **Ridership Data (2024):** Provides weekly and daily passenger numbers across different routes and regions. [🔗](https://data.gov.il/dataset/ridership/resource/e6cfac2f-979a-44fd-b439-ecb116ec0b16)
    - **Performance Data (March 2024):** Compares planned vs. actual bus trips to analyze service efficiency. [🔗](https://data.gov.il/dataset/bitzua_bus_trip/resource/aba233c2-6a5a-487d-b0a8-9413ef849f15?filters=erua_hachraga_ind%3A0)
    """)

    # Select dataset
    selected_dataset = st.radio(
        "Select dataset to view:",
        ("Ridership Data", "Performance Data"),
        horizontal=True
    )

    # Load selected dataset
    if selected_dataset == "Ridership Data":
        data = ridership_data

    else:
        data = performance_data
        excluded_columns = ["planned_time", "actual_time", "delay_minutes", "delay_category", "hour", "date", "day_name", "metro_area"]
        data = data.drop(columns=excluded_columns)

    # Add filter options
    with st.expander("🔍 Filter Data"):
        st.write("Select columns to filter the data:")
        columns_to_show = st.multiselect("Select columns:", data.columns.tolist(), default=data.columns.tolist())
        num_rows = st.slider("Select number of rows to display:", min_value=5, max_value=len(data), value=5)

    # Display filtered table
    st.dataframe(data[columns_to_show].head(num_rows))

    if selected_dataset == "Ridership Data":
        # Summary Statistics with dynamic selection
        st.markdown("#### Summary Statistics")
        with st.expander("View Summary Statistics"):
            numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

            # Exclude unwanted columns
            excluded_columns = ["RouteID", "RouteName"]
            numeric_columns = [col for col in numeric_columns if col not in excluded_columns]

            selected_column = st.selectbox("Select column to summarize:", numeric_columns)

            # Transpose the summary table for better readability
            summary_stats = data[selected_column].describe().to_frame().T
            st.dataframe(summary_stats.style.format("{:.2f}"), use_container_width=True)
