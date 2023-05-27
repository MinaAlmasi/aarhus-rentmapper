import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd
import pathlib
from folium.features import GeoJsonPopup, GeoJsonTooltip

def add_Erhvervshavnen():
    path = pathlib.Path(__file__)

    # read in geojson
    geojson = gpd.read_file(path.parents[1] / "utils" / "districts.geojson")

    # set crs to 25832
    geojson = geojson.set_crs("epsg:25832")

    # extract "Erhvervshavnen"
    Erhvervshavnen = geojson[geojson["prog_distrikt_navn"] == "Erhvervshavnen"]

    # rename prog_distrikt_navn to district
    Erhvervshavnen = Erhvervshavnen.rename(columns={"prog_distrikt_navn": "district"})

    # remove all columns but district and geometry
    Erhvervshavnen = Erhvervshavnen[["district", "geometry"]]

    # convert to geodataframe
    Erhvervshavnen = gpd.GeoDataFrame(Erhvervshavnen, geometry="geometry")

    return Erhvervshavnen

def add_missing_districts():
    path = pathlib.Path(__file__)

    geojson = gpd.read_file(path.parents[1] / "utils" / "districts.geojson")

    # set crs to 25832
    geojson = geojson.set_crs("epsg:25832")

    # extract "Erhvervshavnen" and "Sydhavnen og Marselisborg lystbådehavn" in one dataframe
    missing_districts = geojson[(geojson["prog_distrikt_navn"] == "Erhvervshavnen") | (geojson["prog_distrikt_navn"] == "Sydhavnen og Marselisborg lystbådehavn")]

    # rename prog_distrikt_navn to district
    missing_districts = missing_districts.rename(columns={"prog_distrikt_navn": "district"})

    # remove all columns but district and geometry
    missing_districts = missing_districts[["district", "geometry"]]

    # convert to geodataframe
    missing_districts = gpd.GeoDataFrame(missing_districts, geometry="geometry")

    return missing_districts

#def style_statistics


def main():
    # define paths
    path = pathlib.Path(__file__)

    # read in data
    data = pd.read_csv(path.parents[1] / "data" / "district_aggregates.csv")

    # change wkt to geometry
    data["geometry"] = gpd.GeoSeries.from_wkt(data["geometry"])

    # convert to geodataframe
    data = gpd.GeoDataFrame(data, geometry="geometry")

    # add zoom level to dataframe 
    data["zoom_level"] = [11,13,11,13,13,14,13,13,11,12,12,12,12,14,14,12,12,11,14,14,14,13,11,12,14,12,12,11,12,14,12,12,11,13,13,12,13,12,14,13,14,14]

    # set epsg to 25832
    data = data.set_crs("epsg:25832")

    # add missing districts to dataframe
    missing_districts = add_missing_districts()

    # make layout wide 
    st.set_page_config(layout="wide")

    # title of dashboard
    st.write("<style>.block-container {padding-top: 0 !important;}</style>", unsafe_allow_html=True) # remove padding
    st.markdown("<h1 style='text-align: center;'>Aarhus Apartment Rent</h1>", unsafe_allow_html=True)
    st.divider()


    # create columns for map and statistics
    col1, col2, = st.columns(2)

    # create sidebar for selecting district
    with st.sidebar:
        selected_district = st.selectbox('Select a district', data['district'])
        selected_data = data[data['district'] == selected_district]

        st.write(f"{len(data)} districts in total")

        # convert to epsg 4326
        selected_data = selected_data.to_crs("epsg:4326")

        # extract zoom level
        selected_zoom_level = selected_data['zoom_level'].astype(int)

        # extract location coordinates
        selected_location = [selected_data['geometry'].centroid.y, selected_data['geometry'].centroid.x]

    with col2:
        # add spacing
        st.write("")
    
        # update center of map to selected district
        folium_map = folium.Map(location=selected_location,
                                zoom_start=int(selected_zoom_level),
                                min_zoom=10)

        # define tooltip, but unclickable
        tooltip = GeoJsonTooltip(
            fields=['district'], 
            aliases=['District: '],
            labels=True,
            permanent=False
        )

        folium.Choropleth(
            geo_data=data,
            name='choropleth',
            data=data,
            columns=['district', 'apartment_rent_sqm_now'],
            key_on='feature.properties.district',
            fill_color='Blues',
            fill_opacity=0.8,
            line_opacity=0.2,
            legend_name='Apartment Rent per sqm Now',
            highlight=True
        ).add_to(folium_map)

        folium.GeoJson(data, 
            tooltip=tooltip,
            style_function=lambda x: {"color": "transparent", "weight": 0, "opacity": 0, "fillOpacity": 0},
        ).add_to(folium_map)     

        # draw missing districts on map, make them grey, make hover effect, write custom text in tooltip
        tooltip_missing = GeoJsonTooltip(
            fields=['district'], 
            aliases=['District: '],
            labels=True,
            permanent=False, 
        )

        folium.GeoJson(missing_districts,
            tooltip=tooltip_missing,
        style_function=lambda x: {"color": "grey", "weight": 1, "opacity": 0.7, "fillOpacity": 0.7},
        ).add_to(folium_map)

        # add selected district to map
        folium.GeoJson(selected_data, 
        style_function=lambda x: {"color": "#FF595A", "weight": 4, "opacity": 1, "fillOpacity": 0},
        ).add_to(folium_map)

        folium_static(folium_map)
    
    with col1:
        # create columns to display statistics
        st.markdown(f"<h3>Rental Statistics for <span style='color: #FF595A;'>{selected_district}</span></h3>", unsafe_allow_html=True)

        # create subsubheader for apartment rent
        st.write("Average Apartment Rent (per m2)")

        apart_col1, apart_col2, apart_col3 = st.columns(3)

        with apart_col1:
            st.metric(label="in 2023", value=f"{selected_data['apartment_rent_sqm_now'].values[0]} DKK", delta=f"{selected_data['apartment_rent_change'].values[0]} %", delta_color="inverse")
                
        with apart_col2:
            st.metric(label="in 2014-2016", value=f"{selected_data['apartment_rent_sqm_then'].values[0]} DKK")
            
        # add spacing
        st.write("")

        # create the same for room rent
        st.write("__Average Room Rent__")

        room_col1, room_col2, room_col3 = st.columns(3)

        with room_col1:
            st.metric(label="in 2023", value=f"{selected_data['room_rent_now'].values[0]} DKK", delta=f"{selected_data['room_rent_change'].values[0]} %", delta_color="inverse")
        
        with room_col2:
            st.metric(label="in 2014-2016", value=f"{selected_data['room_rent_then'].values[0]} DKK")
    


    # layer control for street view
    folium.LayerControl().add_to(folium_map)

if __name__ == '__main__':
    main()