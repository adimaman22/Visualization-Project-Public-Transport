import streamlit as st
from dashboards import demand_supply, demand_variation, route_performance, overview
import pandas as pd
import os


# Set page configuration with a professional layout
st.set_page_config(
    page_title="Public Transportation Analysis",
    page_icon="🚍",
    layout="wide"
)


# Load data only once
@st.cache_data(ttl=3600)
def load_ridership_data():
    file_path = "data/2024_public_transport_ridership.csv"
    return pd.read_csv(file_path)


@st.cache_data(ttl=3600)
def load_performance_data():
    # file_url = "https://drive.google.com/file/d/1jR7O6RUW4pAB-aWwQTCwD2BQtIHOYptp/view?usp=sharing"
    # output = "data/2024_march_bus_performance.parquet blah "
    # file_path = "data/2024_bus_performance.parquet"
    # gdown.download(file_url, output, fuzzy=True, quiet=False)
    # file_path = "data/2024_march_bus_performance.parquet"
    file_path = os.path.join(os.getcwd(), "data", "2024_march_bus_performance.parquet")
    return pd.read_parquet(file_path)


# Load data at the start
ridership_data = load_ridership_data()
performance_data = load_performance_data()

# Sidebar logo
# st.sidebar.image("data/logo.webp")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select an analysis:",
    [
        "🏠 Home",
        "Demand vs. Supply",
        "Variation Over Time",
        "Under-performing Routes"
    ]
)

# Expander for additional information
with st.sidebar.expander("📄 About the Project"):
    st.write(
        """
        This dashboard analyzes Israel's public bus network to identify demand-supply gaps, 
        trends over time, and low-performing routes.
        """
    )

# Home Page
if page == "🏠 Home":
    st.title("Welcome to the 2024 Public Transportation Analysis Dashboard")

    st.markdown("""
        Public transportation is a vital part of urban mobility, and understanding its dynamics is crucial for improving service efficiency. 
        This dashboard presents an in-depth analysis of Israel's public bus network using official government datasets from data.gov.il for the year 2024.
        By analyzing real-world data, we aim to identify areas for improvement and provide actionable insights that can lead to a better travel experience for the public.
    """)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""            
            ### Key Tasks:
            - **Demand vs. Supply Analysis:**  
              Identify regions where there is a mismatch between passenger demand and bus service frequency.
            - **Variation Over Time:**  
              Explore patterns in demand and availability based on hourly, daily, and weekly trends.
            - **Identifying Low-Performance Routes:**  
              Detect routes with the lowest adherence to scheduled departure times by comparing planned vs. actual trip execution.
    
            **Please select an option from the sidebar to explore insights and findings.**
        """)
    with col2:
        st.image("data/image.webp", caption="Public Transportation in Action by ChatGPT", width=320)

    # main page statistics:
    overview.show(ridership_data, performance_data)

# Load pages based on user selection
elif page == "Demand vs. Supply":
    demand_supply.show(ridership_data)

elif page == "Variation Over Time":
    demand_variation.show(ridership_data, performance_data)

elif page == "Under-performing Routes":
    route_performance.show(performance_data)
