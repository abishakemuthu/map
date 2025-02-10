import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import ast

# Load the dataset
df = pd.read_excel("combined_fuel_stops.xlsx")

# Ensure the amenities column is properly parsed
df["amenities"] = df["amenities"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df["amenities"] = df["amenities"].apply(lambda x: x if isinstance(x, dict) else {})

# Fill NaN values in fuel_diesel_price
df["fuel_diesel_price"] = df["fuel_diesel_price"].fillna("N/A")

# Extract unique amenities
all_amenities = set()
for entry in df["amenities"]:
    all_amenities.update(entry.keys())

# Sidebar for filtering amenities
st.sidebar.header("Filter Amenities")
selected_amenities = st.sidebar.multiselect("Select Amenities", sorted(all_amenities))

# Filter locations based on selected amenities
if selected_amenities:
    filtered_df = df[df["amenities"].apply(lambda a: all(am in a for am in selected_amenities))]
else:
    filtered_df = df  # Show all if no filter is selected

# Create a map centered at an average location
m = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()], zoom_start=5)

# Add marker cluster
marker_cluster = MarkerCluster().add_to(m)

# Add markers to the map
for _, row in filtered_df.iterrows():
    stop_name = row.get("stop_name", "Unknown")
    diesel_price = row.get("fuel_diesel_price", "N/A")  # Get diesel price, default "N/A"
    amenities_list = ", ".join(row["amenities"].keys()) if row["amenities"] else "No amenities listed"

    popup_content = f"""
        <b>{stop_name}</b><br>
        <b>Diesel Price:</b> {diesel_price}<br>
        <b>Amenities:</b> {amenities_list}
    """

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup_content,
        tooltip=stop_name,
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(marker_cluster)

# Display the map
folium_static(m, width=900, height=600)
