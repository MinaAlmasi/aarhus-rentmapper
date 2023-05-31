'''
Script containing functions for creating street view page of Aarhus in streamlit app (app.py)

Helper functions:
- "create_street_table" for creating table of most similar streets in streamlit app

Main function:
- "street_view" for creating street view page of Aarhus in streamlit app

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils 
import pathlib

# web app
import streamlit as st

# geospatial mapping
import folium
from streamlit_folium import folium_static
from folium.features import GeoJsonTooltip

# visualisations
import plotly.graph_objects as go

# data wrangling 
import pandas as pd
import geopandas as gpd

# moran's I (local) in APP
from esda.moran import Moran_Local
import numpy as np
import libpysal as lps

# custom module for filtering midtbyen for local moran
import sys
sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))
from utils import filter_midtbyen 

def create_street_table(selected_data): 
    '''
    Function to create table of most similar streets in streamlit app

    Args:
        selected_data: dataframe with most similar streets

    Returns:
        fig: table of most similar streets
    '''

    # add DKK to rent in selected data in most_similar cols 
    for i in range(1, 6):
        selected_data[f"most_similar_rent_{i}"] = selected_data[f"most_similar_rent_{i}"].astype(str) + " DKK"

    # define headers and row values for table
    header = ["<b>Street</b>", "<b>District</b>", "<b>Rent (per m2)</b>"]

    values = [  # streetname 
                        [selected_data["most_similar_1"], selected_data["most_similar_2"], 
                        selected_data["most_similar_3"], selected_data["most_similar_4"],
                        selected_data["most_similar_5"]],
                        # district
                        [selected_data["most_similar_district_1"], selected_data["most_similar_district_2"],
                        selected_data["most_similar_district_3"], selected_data["most_similar_district_4"],
                        selected_data["most_similar_district_5"]],
                        # rent
                        [selected_data["most_similar_rent_1"], selected_data["most_similar_rent_2"],
                        selected_data["most_similar_rent_3"], selected_data["most_similar_rent_4"],
                        selected_data["most_similar_rent_5"]]]
        
    # create table
    fig = go.Figure(data=[go.Table(
                                    header=dict(values=header, 
                                                fill_color="#FF595A", 
                                                line_color="#FF595A", 
                                                align=["left", "left", "center"],
                                                height=30, 
                                                font = dict(size=16, family="Serif")), 
                                    cells=dict(values=values, 
                                                fill_color="#001233", 
                                                line_color="#001233", 
                                                font = dict(size=14, family="Serif"), 
                                                align=["left", "left", "center"], 
                                                height=30)
                                        )
                        ])
            
    # fix weird padding
    fig.update_layout(margin=dict(l=0, r=10, t=0, b=0),
                              height=200,
                              width=500)
    
    return fig 

def calculate_local_moran_midtbyen(street_data):
    '''
    Function to calculate local moran's I for midtbyen

    Args:
        street_data: dataframe with street data
    
    Returns: 
        sig_true: dataframe with significant streets
    '''
    # set seed for reproducibility
    np.random.seed(1999)

    # filter midtbyen
    street_data_midtbyen = filter_midtbyen(street_data)

    # filter out "strandvejen" and "stadion alle" as they run outside of bounds of the district map
    street_data_midtbyen = street_data_midtbyen[~street_data_midtbyen["street"].isin(["Strandvejen", "Stadion Alle"])]

    # get spatial weights
    w_midtbyen = lps.weights.KNN.from_dataframe(street_data_midtbyen, k = 3)

    # calculate morans local I for midtbyen
    li_midtbyen = Moran_Local(street_data_midtbyen["rent_per_square_meter"], w_midtbyen)

    # add local morans I to dataframes
    street_data_midtbyen["signficant"] = li_midtbyen.p_sim < 0.05

    # store quadrant information in dataframe
    street_data_midtbyen["quadrant"] = li_midtbyen.q

    # get significant data
    sig_true = street_data_midtbyen[street_data_midtbyen["signficant"] == True]

    return sig_true


def street_view(path:pathlib.Path):
    '''
    Function to create street view page of Aarhus in streamlit app

    Args: 
        path: path to script
    '''

    # read in data
    street_data = pd.read_csv(path.parents[1] / "data" / "street_aggregates.csv")

    # change wkt to geometry
    street_data["geometry"] = gpd.GeoSeries.from_wkt(street_data["geometry_street"])

    # convert to geodataframe
    street_data = gpd.GeoDataFrame(street_data, geometry="geometry")

    # set epsg to 25832
    street_data = street_data.set_crs("epsg:25832")

    # create columns for map and statistics
    left_col, right_col, = st.columns(2, gap = "large")

    # calculate local moran's I
    sig_true = calculate_local_moran_midtbyen(street_data)

    with st.sidebar:
        # initialize selectbox with all streets
        selected_street = st.selectbox('Select a street', street_data['street'])

        # set bigger font
        st.markdown(
            """<style>
        div[class*="stSelectbox"] > label > div[data-testid="stMarkdownContainer"] > p {
            font-size: 25px;
            </style>
            """, unsafe_allow_html=True)
        selected_data = street_data[street_data['street'] == selected_street]
        
        # indicate number of streets found
        st.write(f"{len(street_data)} streets found")

        # convert seleced data to epsg 4326
        selected_data = selected_data.to_crs("epsg:4326")

        # extract location coordinates
        selected_location = [selected_data['geometry'].centroid.y, selected_data['geometry'].centroid.x]

    with right_col:
        # add spacing
        st.write("")
    
        # update center of map to selected district
        folium_map = folium.Map(location=selected_location,
                                zoom_start=15,
                                min_zoom=10)
        
        # define tooltip, but unclickable
        tooltip = GeoJsonTooltip(
            fields=['street'], 
            aliases=['Street: '],
            labels=True,
            permanent=False
        )
        
        # create map with location being selected_location, but all strets highlighted
        folium.GeoJson(street_data,
            tooltip=tooltip,
            style_function=lambda x: {"color": "#001233", "weight": 3, "opacity": 1, "fillOpacity": 0},
        ).add_to(folium_map)

        # add selected district to map
        folium.GeoJson(selected_data, 
        style_function=lambda x: {"color": "#FF595A", "weight": 5, "opacity": 1, "fillOpacity": 0},
        ).add_to(folium_map)

        folium_static(folium_map, height=630, width=482) 
    
    with left_col:
        # create columns to display statistics
        st.markdown(f"<h3>Rental Statistics for <span style='color: #FF595A;'>{selected_street}</span></h3>", unsafe_allow_html=True)

        # create small text for "located in" 
        st.markdown(f"<body><b>Located in <span style='color: #FF595A;'>{selected_data['district'].values[0]}</b></span></body>", unsafe_allow_html=True)

        # add spacing
        st.write("")
        st.write("")

        # create columns for rent statistics
        st.write("__Average Apartment Rent (per m2)__")
        
        # c columns
        rent_col, count_col = st.columns([2, 2])

        with rent_col:
            st.metric(label="in 2023", value=f"{selected_data['rent_per_square_meter'].values[0]} DKK")
        
        with count_col:
            st.metric(label="based on", value=f"{selected_data['count'].values[0]} apartments")
        
        # add spacing
        st.write("")
        st.write("")

        with st.container():
            st.write("__Similar Priced Streets__")

            # create table 
            fig = create_street_table(selected_data)

            # display table in streamlit
            st.write(fig)

        # check if selected_street is significant
        if selected_street in sig_true["street"].values:
            # write a markdown with no padding informing user that street is a rare case
            st.markdown("<p style='margin: 0;'><b>Please Note:</b></p>", unsafe_allow_html=True)
            
            if sig_true[sig_true["street"] == selected_street]["quadrant"].values[0] == 1:
                st.markdown(f"The average rent in <span style='color:#FF595A'>{selected_street}</span> is significantly higher than expected even for an expensive district (__It's a bad deal!__)", unsafe_allow_html=True)
            
            elif sig_true[sig_true["street"] == selected_street]["quadrant"].values[0] == 2:
                st.markdown(f"The average rent in <span style='color:#FF595A'>{selected_street}</span> is low despite being an expensive district (__It's a very good deal!__)", unsafe_allow_html=True)
            
            elif sig_true[sig_true["street"] == selected_street]["quadrant"].values[0] == 3:
                st.markdown(f"The average rent in <span style='color:#FF595A'>{selected_street}</span> is significantly lower than expected even for an inexpensive district (__It's good deal!__)", unsafe_allow_html=True)
            
            elif sig_true[sig_true["street"] == selected_street]["quadrant"].values[0] == 4:
                st.markdown(f"The average rent in <span style='color:#FF595A'>{selected_street}</span> is high despite being an inexpensive district (__It's a very bad deal!__)", unsafe_allow_html=True)