'''
Streamlit app

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
from folium.features import GeoJsonPopup, GeoJsonTooltip

# visualisations
import plotly.graph_objects as go
import plotly.express as px

# data wrangling 
import pandas as pd
import geopandas as gpd

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


def plot_neighbor_stats(neighbor_data, y_col, y_title):
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

        folium_static(folium_map, height=475, width=500)
    
    with col1:
        # create columns to display statistics
        st.markdown(f"<h3>Rental Statistics for <span style='color: #FF595A;'>{selected_district}</span></h3>", unsafe_allow_html=True)

        # create subsubheader for apartment rent
        st.write("__Average Rents 2023__")

        apart_col1, apart_col2 = st.columns(2)

        with apart_col1:
            st.metric(label="Apartment (per m2)", value=f"{selected_data['apartment_rent_sqm_now'].values[0]} DKK", delta=f"{selected_data['apartment_rent_change'].values[0]} % since 2014-16", delta_color="inverse")
                
        with apart_col2:
            st.metric(label="Room", value=f"{selected_data['room_rent_now'].values[0]} DKK", delta=f"{selected_data['room_rent_change'].values[0]} % since 2014-16", delta_color="inverse")
        
        # add spacing
        st.write("")
        
        # start plot with neighbor districts
        st.write("__Compared to neighbor districts__")

        # create list of neighbor districts
        neighbors = selected_data["neighbors"].tolist()[0]
        neighbors = literal_eval(neighbors)

        # extract neighbor data from dataframe
        neighbor_data = data[data["district"].isin(neighbors)]

        # convert neighbor data to epsg 4326
        neighbor_data = neighbor_data.to_crs("epsg:4326")

        # concat with selected district
        neighbor_data = pd.concat([selected_data, neighbor_data])

        # define tabs
        tab1, tab2 = st.tabs(["Apartment Rent", "Room Rent"])

        # add plot to streamlit
        with tab1: 
            apartment_fig = plot_neighbor_stats(neighbor_data, "apartment_rent_sqm_now", "Apartment Rent (per m2)")
            st.plotly_chart(apartment_fig, use_container_width=True)

        with tab2:
            room_fig = plot_neighbor_stats(neighbor_data, "room_rent_now", "Room Rent")
            st.plotly_chart(room_fig, use_container_width=True)
    
    # layer control for street view
    folium.LayerControl().add_to(folium_map)

def street_view(path):
    # read in data
    street_data = pd.read_csv(path.parents[1] / "data" / "street_aggregates.csv")

    # change wkt to geometry
    street_data["geometry"] = gpd.GeoSeries.from_wkt(street_data["geometry_street"])

    # convert to geodataframe
    street_data = gpd.GeoDataFrame(street_data, geometry="geometry")

    # set epsg to 25832
    street_data = street_data.set_crs("epsg:25832")

    # create columns for map and statistics
    col1, col2, = st.columns(2)

    with st.sidebar:
        selected_street = st.selectbox('Select a street', street_data['street'])
        selected_data = street_data[street_data['street'] == selected_street]

        st.write(f"{len(street_data)} streets found")

        # convert to epsg 4326
        selected_data = selected_data.to_crs("epsg:4326")

        # extract location coordinates
        selected_location = [selected_data['geometry'].centroid.y, selected_data['geometry'].centroid.x]

    with col2:
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

        folium_static(folium_map, height=475, width=500)
    
    with col1:
        # create columns to display statistics
        st.markdown(f"<h3>Rental Statistics for <span style='color: #FF595A;'>{selected_street}</span></h3>", unsafe_allow_html=True)

        # create small text for "located in" 
        st.markdown(f"<body><b>Located in <span style='color: #FF595A;'>{selected_data['district'].values[0]}</b></span></body>", unsafe_allow_html=True)

        # add spacing
        st.write("")
        st.write("")

        # create columns for rent statistics
        st.write("__Average Apartment Rent (per m2)__")

        col1, col2 = st.columns([2, 2])

        with col1:
            st.metric(label="in 2023", value=f"{selected_data['rent_per_square_meter'].values[0]} DKK")
        
        with col2:
            st.metric(label="based on", value=f"{selected_data['count'].values[0]} apartments")
        
        # add spacing
        st.write("")
        st.write("")

        with st.container():
            st.write("__Similar Priced Streets__")

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
            fig = go.Figure(data=[go.Table(header=dict(values=header, 
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
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                              height=200,
                              width=500)

            # display table in streamlit
            st.write(fig)
        
        




        



def main():
    # define paths
    path = pathlib.Path(__file__)

    # make layout wide 
    st.set_page_config(layout="wide")

    # title of dashboard
    st.write("<style>.block-container {padding-top: 0 !important;}</style>", unsafe_allow_html=True) # remove padding
    st.markdown("<h1 style='text-align: center;'>Aarhus Rental Properties</h1>", unsafe_allow_html=True)
    st.divider()

    # add district view 
    with st.sidebar:
        view = st.radio("Select view", ("District", "Street"))

    if view == "District":
        district_view(path)
    
    if view == 'Street':
        street_view(path)

    

if __name__ == '__main__':
    main()