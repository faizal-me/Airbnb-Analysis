import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_option_menu import option_menu

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("airbnbnew1.csv")

# Countries with Defined Seasons
SEASONAL_COUNTRIES = ['United States', 'Turkey', 'Hong Kong', 'Australia', 
                      'Portugal', 'Brazil', 'Canada', 'Spain', 'China']

# Determine the hemisphere for a given country
def get_hemisphere(country):
    if country in ['United States', 'Turkey', 'Hong Kong', 'Portugal', 'Canada', 'Spain', 'China']:
        return "Northern"
    elif country in ['Australia', 'Brazil']:
        return "Southern"
    else:
        return "Unknown"

# Map seasons based on hemisphere
def map_season(month, hemisphere):
    if hemisphere == "Northern":
        return "Winter" if month in [12, 1, 2] else \
               "Spring" if month in [3, 4, 5] else \
               "Summer" if month in [6, 7, 8] else "Autumn"
    elif hemisphere == "Southern":
        return "Winter" if month in [6, 7, 8] else \
               "Spring" if month in [9, 10, 11] else \
               "Summer" if month in [12, 1, 2] else "Autumn"
    else:
        return "Unknown"

# App Title
st.set_page_config(page_title="Airbnb Availability Analysis", page_icon="🏠")

# Sidebar Menu with option_menu
with st.sidebar:
    selected = option_menu("Menu", ["Home", "Explore Availability Analysis"],  
                           icons=["house", "graph-up-arrow"], 
                           menu_icon="menu-button-wide", 
                           default_index=0,
                           styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "red"},
                                   "nav-link-selected": {"background-color": "red"}})

# Load Data
df = load_data()

# Preprocessing
# Ensure availability columns are numeric
availability_cols = ['availability_365', 'availability_30', 'availability_60', 'availability_90']
for col in availability_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert `last_review` column to datetime
df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

# Filter dataset to include only relevant countries
df = df[df['country'].isin(SEASONAL_COUNTRIES)]

# Extract Month and Hemisphere-Based Season
df['review_month'] = df['last_review'].dt.month
df['hemisphere'] = df['country'].apply(get_hemisphere)
df['season'] = df.apply(lambda x: map_season(x['review_month'], x['hemisphere']), axis=1)

# Define Home Page Content
def home_page():
    # Hero Section with a Welcome Image
    st.title("Welcome to the Airbnb Availability Analysis App👋")
    st.image(r"C:\Users\faiza\OneDrive\Desktop\project 3\466843-weird-places-you-can-stay-on-airbnb.jpg", use_column_width=True)
    st.markdown("""
        This application allows you to explore the **availability trends** of Airbnb listings across different countries and seasons.
        You can explore detailed insights on how the **availability** changes month-to-month and by season, based on the **location** of the listing.
    """)

    # App Features Section (with Icons)
    st.subheader("🔍 Features")
    st.markdown("""
        - **Explore Availability Analysis**: Dive into specific details regarding listing availability, monthly trends, and seasonal insights.
        - **Filters**: Choose from multiple filters including country, suburb, season, and availability period to analyze the data.
        - **Interactive Visualizations**: View the trends through interactive charts and graphs.
    """)

    # How to Use Section
    st.subheader("📖 How to Use the App")
    st.markdown("""
        1. Select the **Explore Availability Analysis** section to start exploring the data.
        2. Apply filters to narrow down the data based on your preferences.
        3. Analyze the trends and view the visualizations on the availability of Airbnb listings.
    """)

# Define Availability Analysis Page Content
def availability_analysis_page():
    # Sidebar Filters
    st.sidebar.header("Filters")

    # Country Filter
    selected_country = st.sidebar.selectbox("🌍 Select Country", options=['All'] + sorted(df['country'].dropna().unique()))

    # Filter data based on selected country
    country_filtered_data = df.copy()
    if selected_country != 'All':
        country_filtered_data = country_filtered_data[country_filtered_data['country'] == selected_country]

    # Suburb Filter (Dependent on Country)
    suburb_options = ['All'] + country_filtered_data['suburb'].dropna().unique().tolist()
    selected_suburb = st.sidebar.selectbox("🏙️ Select Suburb", options=suburb_options)

    # Season Filter
    selected_season = st.sidebar.selectbox("🍂 Select Season", options=['All', 'Winter', 'Spring', 'Summer', 'Autumn'])

    # Availability Filter
    selected_availability = st.sidebar.selectbox("📆 Select Availability Period", 
                                                  options=['availability_365', 'availability_30', 'availability_60', 'availability_90'])

    # Filter Data Based on Suburb and Season
    filtered_data = country_filtered_data.copy()
    if selected_suburb != 'All':
        filtered_data = filtered_data[filtered_data['suburb'] == selected_suburb]
    if selected_season != 'All':
        filtered_data = filtered_data[filtered_data['season'] == selected_season]

    # Availability Analysis Section
    st.header("📊 Explore Availability Analysis")
    st.write(f"Analyzing **{selected_availability}** for listings in **{selected_suburb if selected_suburb != 'All' else 'all suburbs'}** "
             f"in **{selected_country if selected_country != 'All' else 'all countries'}** during "
             f"**{selected_season if selected_season != 'All' else 'all seasons'}**.")

    # Visualization 1: Line Chart for Monthly Availability Trend
    st.subheader("📈 Monthly Availability Trend")
    if not filtered_data.empty:
        monthly_availability = filtered_data.groupby('review_month')[selected_availability].mean()
        fig = plt.figure(figsize=(10, 6))
        sns.lineplot(x=monthly_availability.index, y=monthly_availability.values, marker='o', color='teal')
        plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        plt.xlabel("Month (Last Review)", fontsize=12)
        plt.ylabel(f"Average {selected_availability}", fontsize=12)
        plt.title(f"Monthly Trend of {selected_availability}", fontsize=16, color='darkblue')
        st.pyplot(fig)
    else:
        st.write("No data available for the selected filters.")

    # Visualization 2: Bar Chart for Season-Wise Average Availability
    st.subheader("📊 Average Availability by Season")
    if not filtered_data.empty:
        season_availability = filtered_data.groupby('season')[selected_availability].mean().reset_index()
        fig = px.bar(season_availability, x='season', y=selected_availability, color='season',
                     color_discrete_sequence=px.colors.sequential.Blues, 
                     title=f"Average {selected_availability} by Season",
                     labels={'season': 'Season', selected_availability: f"Average {selected_availability}"}).update_layout(
            xaxis_title='Season', yaxis_title=f'Average {selected_availability}')
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected filters.")

# Select the page based on the sidebar menu
if selected == "Home":
    home_page()
elif selected == "Explore Availability Analysis":
    availability_analysis_page()
