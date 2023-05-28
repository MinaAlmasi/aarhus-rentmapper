'''
Script containing functions for creating district view page of Aarhus in streamlit app (app.py)

Helper functions:
- "add_missing_districts" for adding missing districts to dataframe.
- "plot_neighbor_stats" for plotting statistics of neighbor districts

Main function:
- "district_view" for creating district view page of Aarhus in streamlit app

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils 
import pathlib
from ast import literal_eval

# web app
import streamlit as st

# geospatial mapping
import folium
from streamlit_folium import folium_static
from folium.features import GeoJsonTooltip

# visualisations
import plotly.express as px

# data wrangling 
import pandas as pd
import geopandas as gpd

def add_missing_districts(path: pathlib.Path):
    '''
    Function for adding missing districts to dataframe.
    Districts are missing because they have no apartment data.

    Args:
        path: path to script

    Returns:
        missing_districts: geodataframe with missing districts
    '''
    # read in geojson file
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

def plot_neighbor_stats(neighbor_data, y_col, y_title):
        '''
        Function for plotting statistics of neighbor districts

        Args
            neighbor_data: dataframe with statistics of neighbor districts
            y_col: column to plot on y-axis
            y_title: title of y-axis
        
        Returns 
            fig: plotly figure
        '''
        # define color
        colors = ["lightslategray",] * len(neighbor_data)
        
        # change color of first element to make it stand out
        colors[0] = ["#FF595A"]

        # create plot of neighbor districts with plotly
        fig = px.bar(neighbor_data, x="district", y=y_col, color="district", color_discrete_sequence=colors)

        # update layout to have descending order
        fig.update_layout(
            xaxis=dict(
                categoryorder="total descending"
            ),
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=300
        )

        # rm xaxis title
        fig.update_xaxes(title=None)

        # add yaxis title
        fig.update_yaxes(title=y_title)

        return fig

def district_view(path): 
    '''
    Function to create district view page of Aarhus in streamlit app

    Args:
        path: path to script
    '''
    # read in data
    data = pd.read_csv(path.parents[1] / "data" / "district_aggregates.csv")

    # change wkt to geometry
    data["geometry"] = gpd.GeoSeries.from_wkt(data["geometry"])

    # convert to geodataframe
    data = gpd.GeoDataFrame(data, geometry="geometry")

    # add zoom level to dataframe manually. Each value corresponds to a district in the same order as in the dataframe
    data["zoom_level"] = [11,13,11,13,13,14,13,13,11,12,12,12,12,14,14,12,12,11,14,14,14,13,11,12,14,12,12,11,12,14,12,12,11,13,13,12,13,12,14,13,14,14]

    # set epsg to 25832
    data = data.set_crs("epsg:25832")

    # add missing districts to dataframe
    missing_districts = add_missing_districts(path)

    # create columns for map and statistics
    left_col, right_col, = st.columns(2, gap = "large")

    # create sidebar for selecting district
    with st.sidebar:
        selected_district = st.selectbox('Select a district', data['district'])
        st.markdown(
            """<style>
        div[class*="stSelectbox"] > label > div[data-testid="stMarkdownContainer"] > p {
            font-size: 25px;
            </style>
            """, unsafe_allow_html=True)

        selected_data = data[data['district'] == selected_district]

        st.write(f"{len(data)} districts in total")

        # convert to epsg 4326
        selected_data = selected_data.to_crs("epsg:4326")

        # extract zoom level
        selected_zoom_level = selected_data['zoom_level'].astype(int)

        # extract location coordinates
        selected_location = [selected_data['geometry'].centroid.y, selected_data['geometry'].centroid.x]

    with right_col:
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

        folium_static(folium_map, height=630, width=482)
    
    with left_col:
        # create columns to display statistics
        st.markdown(f"<h3>Rental Statistics for <span style='color: #FF595A;'>{selected_district}</span></h3>", unsafe_allow_html=True)

        # create subsubheader for apartment rent
        st.markdown("<p style='margin-top: 5px; margin-bottom: 4px; font-weight: bold;'>Average Rents 2023</p>", unsafe_allow_html=True)

        # initialize columns for displaying rents
        apart_col, room_col = st.columns(2)

        with apart_col:
            st.metric(label="Apartment (per m2)", value=f"{selected_data['apartment_rent_sqm_now'].values[0]} DKK", delta=f"{selected_data['apartment_rent_change'].values[0]} % since 2014-16", delta_color="inverse")
                
        with room_col:
            st.metric(label="Room", value=f"{selected_data['room_rent_now'].values[0]} DKK", delta=f"{selected_data['room_rent_change'].values[0]} % since 2014-16", delta_color="inverse")
        
        # add spacing
        st.write("")
        
        # start plot with neighbor districts
        st.markdown("<p style='margin-top: 5px; margin-bottom: 0; font-weight: bold;'>Compared to Neighbor Districts</p>", unsafe_allow_html=True)

        # create list of neighbor districts
        neighbors = selected_data["neighbors"].tolist()[0]
        neighbors = literal_eval(neighbors)

        # extract neighbor data from dataframe
        neighbor_data = data[data["district"].isin(neighbors)]

        # convert neighbor data to epsg 4326
        neighbor_data = neighbor_data.to_crs("epsg:4326")

        # concat with selected district
        neighbor_data = pd.concat([selected_data, neighbor_data])

        # make all NA values 0.001 for plotting to avoid bug in plotly that maps all NA values to ALL plots
        neighbor_data = neighbor_data.fillna(0.001)

        # define tabs
        tab1, tab2 = st.tabs(["Apartment Rent", "Room Rent"])

        # add plot to streamlit
        with tab1: 
            apartment_fig = plot_neighbor_stats(neighbor_data, "apartment_rent_sqm_now", "Apartment Rent (per m2)")
            st.plotly_chart(apartment_fig, use_container_width=True)

        with tab2:
            # if all values are NA (0.001 due to NA bug), then no room data is available
            if (neighbor_data['room_rent_now'] == 0.001).all():
                # make neighbors into string
                neighbors = ", ".join(neighbors)
                # write message
                st.markdown(f"No room rent data available for <span style='color: #FF595A;'>{selected_district}</span> and neighbor districts \n {neighbors}.", unsafe_allow_html=True)
            else:
                room_fig = plot_neighbor_stats(neighbor_data, "room_rent_now", "Room Rent")
                st.plotly_chart(room_fig, use_container_width=True)
    
    # layer control for street view
    folium.LayerControl().add_to(folium_map)