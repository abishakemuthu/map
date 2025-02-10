import streamlit as st
import folium
import pandas as pd
from streamlit_folium import folium_static
from folium.plugins import Fullscreen, MarkerCluster
import ast

# Load data (Replace 'your_data.csv' with actual file path or use a database)
df = pd.read_excel("combined_fuel_stops.xlsx")

def extract_amenities(amenities):
    """Convert amenities JSON-like strings into Python dictionaries."""
    try:
        return ast.literal_eval(amenities) if isinstance(amenities, str) else {}
    except:
        return {}

df['amenities'] = df['amenities'].apply(extract_amenities)

# Get unique amenities
def get_unique_amenities(data):
    unique_amenities = set()
    for amenities in data:
        unique_amenities.update(amenities.keys())
    return sorted(unique_amenities)

all_amenities = get_unique_amenities(df['amenities'])

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Fuel Station Locator with Amenities")

# Sidebar filter panel
selected_amenities = st.sidebar.multiselect("Select Amenities", all_amenities)

# Filter locations based on selected amenities
def filter_locations(data, selected):
    if not selected:
        return data
    return data[data['amenities'].apply(lambda x: all(amenity in x for amenity in selected))]

df_filtered = filter_locations(df, selected_amenities)

# Create map
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=6, control_scale=True)
Fullscreen(position="topright").add_to(m)  # Ensure full-screen functionality
marker_cluster = MarkerCluster().add_to(m)

# Add markers
for _, row in df_filtered.iterrows():
    popup_content = f"""
    Place Name: {row['stop_name']}<br>
    Diesel Price: {row['fuel_diesel_price']} {row['currency']}<br>
    Amenities: {', '.join(row['amenities'].keys()) if row['amenities'] else 'No amenities listed'}
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_content, max_width=300, parse_html=False),
        tooltip=row['stop_name'],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster)

# Display the map
folium_static(m)
