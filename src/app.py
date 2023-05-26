import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd
import pathlib

def main():
    # define paths
    path = pathlib.Path(__file__)

    # read in data
    data = pd.read_csv(path.parents[1] / "data" / "district_aggregates.csv")

    # change wkt to geometry
    data["geometry"] = gpd.GeoSeries.from_wkt(data["geometry"])

    # convert to geodataframe
    data = gpd.GeoDataFrame(data, geometry="geometry")

    # set epsg to 25832
    data = data.set_crs("epsg:25832")

    st.title('District Statistics Dashboard')

    # Display the map with polygons
    st.subheader('District Map')
    folium_map = folium.Map(location=[56.1629, 10.2039],
                           zoom_start=10)

    folium.Choropleth(
        geo_data=data,
        name='choropleth',
        data=data,
        columns=['district', 'apartment_rent_sqm_now'],
        key_on='feature.properties.district',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Apartment Rent per sqm Now',
        highlight=True
    ).add_to(folium_map)

    folium.LayerControl().add_to(folium_map)
    folium_static(folium_map)

    # Display the statistics for selected district

    with st.sidebar:
        selected_district = st.selectbox('Select a district', data['district'])
        selected_data = data[data['district'] == selected_district]

        st.subheader('Selected District Statistics')
        st.write(f"{selected_data['apartment_rent_sqm_now'].values[0]} DKK per sqm")
        st.write(f"{selected_data.crs}")
    
    # convert to epsg 4326
    selected_data = selected_data.to_crs("epsg:4326")

    # create new folium map only for selected district
    folium_map = folium.Map(location=[selected_data['geometry'].centroid.y, selected_data['geometry'].centroid.x],
                            zoom_start=12) 

    folium.Choropleth(
        geo_data=data,
        name='choropleth',
        data=data,
        columns=['district', 'apartment_rent_sqm_now'],
        key_on='feature.properties.district',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Apartment Rent per sqm Now',
        highlight=True
    ).add_to(folium_map)

    folium.LayerControl().add_to(folium_map)

    folium_static(folium_map)
    
    
    

if __name__ == '__main__':
    main()