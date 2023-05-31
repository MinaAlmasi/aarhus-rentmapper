'''
Script to map Aarhus data. 
'''
# utils 
import pathlib
import numpy as np

# data wrangling 
import geopandas as gpd
import pandas as pd
from utils import add_missing_districts # custom function to add missing districts to plots 

# plotting 
import matplotlib.pyplot as plt
import seaborn as sns 
import mpl_toolkits.axes_grid1.inset_locator as mpl_il
from shapely.geometry import LineString

# spatial statistics
import libpysal as lps
from esda.moran import Moran, Moran_Local

# colors
from matplotlib.colors import ListedColormap

import random
import numpy as np

# import custom functions
from utils import filter_midtbyen

## HELPER FUNCTIONS ##
def load_data(datapath:pathlib.Path, geometry_col:str, crs=25832): 
    '''
    Function to load data from path and convert to geodataframe with custom CRS. 

    Args:
        datapath: The path to the data
        geometry_col: The name of the geometry column
        crs: The crs to use (defaults to 25832 as this is the crs for Denmark)
    
    Returns: 
        data: The data as a geodataframe
    '''

    # read in data
    data = pd.read_csv(datapath)

    # change wkt to geometry
    data["geometry"] = gpd.GeoSeries.from_wkt(data[geometry_col])

    # convert to geodataframe
    data = gpd.GeoDataFrame(data, geometry="geometry")

    # set epsg to 25832
    data = data.set_crs(epsg=crs)

    return data

## DISTRICTS ## 
def plot_district_overview(district_data, savepath):
    '''
    Function to plot the districts in Aarhus

    Args:
        district_data: dataframe containing the district data
        savepath: The path to save the plot to

    Outputs: 
        .png: A plot of the districts in Aarhus
    '''
    # add missing districts
    missing_districts = add_missing_districts(pathlib.Path(__file__))

    # seperate midtbyen from the rest of the districts
    midtbyen_districts = filter_midtbyen(district_data, midtbyen=True)
    other_districts = filter_midtbyen(district_data, midtbyen=False)

    # create figure and axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))

    # set font to times new roman
    plt.rcParams["font.family"] = "Times New Roman"

    # reduce whitespace between plots
    plt.subplots_adjust(wspace=0, hspace=0, top=1, bottom=0.0, left=0.0, right=1)

    # rename Skolegade/Bispetorv/Europaplads to Skolegade/../.. for better plotting
    midtbyen_districts["district"] = midtbyen_districts["district"].replace({"Skolegade/Bispetorv/Europaplads": "Skolegade/../.."})

    # rename Klostertorv/Vesterbro Torv to Klostertorv/.. for better plotting
    midtbyen_districts["district"] = midtbyen_districts["district"].replace({"Klostertorv/Vesterbro Torv": "Klostertorv/.."})

    # plot the districts
    district_data.plot(ax=ax1, edgecolor="black", color = "#F1F1F1", linewidth=0.5)
    missing_districts.plot(ax=ax1, edgecolor="white", color = "lightgrey", linewidth=0.5)
    midtbyen_districts.plot(ax=ax1, edgecolor="white", color = "lightgrey", linewidth=0.5)

    # annotate all districts that are not in midtbyen
    for x, y, label in zip(other_districts.geometry.centroid.x, other_districts.geometry.centroid.y, other_districts["district"]):
        ax1.annotate(label, xy=(x, y), fontsize=11, ha = "center", va = "center", fontweight="bold")

    # plot the districts in midtbyen
    midtbyen_districts.plot(ax=ax2, edgecolor="white", color = "lightgrey", linewidth=0.5)

    # annotate all districts that are in midtbyen
    for x, y, label in zip(midtbyen_districts.geometry.centroid.x, midtbyen_districts.geometry.centroid.y, midtbyen_districts["district"]):
        ax2.annotate(label, xy=(x, y), fontsize=9, ha = "center", va = "center", fontweight="bold")

    # remove all spines and ticks
    for ax in [ax1, ax2]:
        ax.tick_params(labelleft=False, labelbottom=False, left=False, bottom=False)
        ax.set_aspect("equal")

    # titles for both plots
    ax1.text(0.02, 0.93, "[A]", fontsize=35, fontweight="bold", transform=ax1.transAxes)
    ax2.text(0.02, 0.93, "[B]", fontsize=35, fontweight="bold", transform=ax2.transAxes)

    # save figure
    plt.savefig(savepath, bbox_inches="tight", dpi=300, pad_inches=0.5)


## HEAT MAP ##
def add_minimap(ax, district_data:gpd.GeoDataFrame, column_to_plot:str, district_name:str, cmap:str, max_value, min_value): 
    '''
    Add a minimap to the plot

    Args:
        ax: The axes to add the minimap to
        district_data: The dataframe containing the district data
        column_to_plot: The column to plot
        district_name: The name of the district to zoom in on
        cmap: The colormap to use
        max_value: The maximum value of the column to plot
        min_value: The minimum value of the column to plot
    '''

    # find the geometry of the district "Latinerkvarteret" as it is centrally placed
    district_geometry = district_data[district_data["district"] == district_name].geometry

    if not district_geometry.empty:
        # get the bounding box coordinates
        xmin, ymin, xmax, ymax = district_geometry.total_bounds

        # define the zoomed-in region with margin on each side to get a better view 
        xmargin = (xmax - xmin) * 2.1  # 10% margin on each side
        ymargin = (ymax - ymin) * 6
        xmin -= xmargin
        ymin -= ymargin
        xmax += xmargin
        ymax += ymargin

        # define the zoomed-in region
        zoomed_region = district_data.cx[xmin:xmax, ymin:ymax]

        # create the inset plot
        ax_inset = mpl_il.inset_axes(ax, width="35%", height="35%", loc="lower right", bbox_to_anchor=(0.14, 0.30, 1, 1), bbox_transform=ax.transAxes)
        zoomed_region.plot(ax=ax_inset, column=column_to_plot, cmap=cmap, edgecolor='black', linewidth=0.5, missing_kwds={"color": "lightgrey", "edgecolor": "darkgrey", "hatch": "///"}, vmin=min_value, vmax=max_value)

        # set the limits of the inset plot to match the zoomed region
        ax_inset.set_xlim(xmin, xmax)
        ax_inset.set_ylim(ymin, ymax)

        # remove ticks and labels from the inset plot
        ax_inset.tick_params(labelleft=False, labelbottom=False, left=False, bottom=False)

def plot_districts_heatmap(district_data:gpd.GeoDataFrame, rental_type:str, savepath:pathlib.Path):
    '''
    Plot the districts as a heatmap
    Args:
        district_data: dataframe containing the district data
        rental_type: The type of rental to plot
        savepath: The path to save the plot to

    Outputs: 
        .png: A plot of the districts and their average rent on the given rental type
    '''
    # identify the correct columns based on rental type and set colorbar label
    if rental_type == "apartment":
        col_now = "apartment_rent_sqm_now"
        col_then = "apartment_rent_sqm_then"
        cmap_label = "Average Apartment rent (DKK per m2)"
        cmap = "Blues"
        
    if rental_type == "room":
        col_now = "room_rent_now"
        col_then = "room_rent_then"
        cmap_label = "Average Room rent (DKK)"
        cmap = "Purples"

    # calculate min and max values for both years
    min_value = min(district_data[col_now].min(), district_data[col_then].min())
    max_value = max(district_data[col_now].max(), district_data[col_then].max())

    # set font to Times New Roman
    plt.rcParams["font.family"] = "Times New Roman"
    
    # create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # reduce whitespace between plots
    plt.subplots_adjust(wspace=0, hspace=0, top=1, bottom=0.0, left=0.0, right=1)

    # plot apartment rent per square meter in 2023
    district_data.plot(column=col_now, ax=ax1, legend=False, cmap=cmap, edgecolor="black", linewidth=0.5, missing_kwds={"color": "lightgrey", "edgecolor": "darkgrey", "hatch": "///"}, vmin=min_value, vmax=max_value)

    # set ax title to the left top of the plot
    ax1.text(0.02, 0.93, "[A]", fontsize=35, fontweight="bold", transform=ax1.transAxes)

    # plot apartment rent per square meter in "then" (2014-2016) (Include NA values as gray)
    district_data.plot(column=col_then, ax=ax2, legend=False, cmap=cmap, edgecolor="black", linewidth=0.5, missing_kwds={"color": "lightgrey", "edgecolor": "darkgrey", "hatch": "///"}, vmin=min_value, vmax=max_value)
    ax2.text(0.02, 0.93, "[B]", fontsize=35, fontweight="bold", transform=ax2.transAxes)

    # plot colorbar
    cbar = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min_value, vmax=max_value)), ax=[ax1, ax2], orientation="horizontal", shrink=0.5, aspect=20, pad=0.05)

    # set label for colorbar
    cbar.set_label(cmap_label, fontsize=16, labelpad=10)
    
    # remove all axis tick labels for both (loop)
    for ax in [ax1, ax2]:
        ax.tick_params(labelleft=False, labelbottom=False, left=False, bottom=False)

    # add minimap to axes
    add_minimap(ax = ax1, district_data = district_data, column_to_plot = col_now, district_name="Klostertorv/Vesterbro Torv", cmap=cmap, max_value = max_value, min_value = min_value)
    add_minimap(ax = ax2, district_data = district_data, column_to_plot = col_then, district_name="Klostertorv/Vesterbro Torv", cmap=cmap, max_value = max_value, min_value = min_value)
    
    # save the plots
    plt.savefig(savepath, dpi=300, bbox_inches="tight", pad_inches=0.5)

## PLOT STREETS ## 
def plot_streets(street_data, district_data, savepath):
    # keep only midtbyen districts
    street_data = filter_midtbyen(street_data)
    district_data = filter_midtbyen(district_data)

    # filter out "strandvejen" and "stadion alle" as they run outside of bounds of the district map
    street_data = street_data[~street_data["street"].isin(["Strandvejen", "Stadion Alle"])]

    # define figure with one ax
    fig, ax = plt.subplots(1, figsize=(5, 10))
    
    # define custom cmap with ListedColormap
    cmap = ListedColormap(["#389F38", "#595AFF", "#FF595A"])

    # specify legend kwds 
    legend_kwds = {'loc':'upper left', 
                        'markerscale':0.8, 
                        'title_fontsize':'medium', 
                        'fontsize':'medium' ,
                        "labels": ["72-124 DKK", "124-138 DKK", "138-250 DKK"], 
                        "title": "Average Apartment Rent (per m2)",
                        "alignment": "left"
                        }

    # add map add distrits as background
    district_data.plot(ax=ax, color="#F2F3F4", edgecolor="black", linewidth=2.5)

    # add streets
    street_data.plot(column="rent_per_square_meter", legend=True, cmap=cmap, legend_kwds=legend_kwds, scheme = "quantiles", k = 3, linewidth=0.8, ax=ax)

    # remove axis ticks
    ax.tick_params(labelleft=False, labelbottom=False, left=False, bottom=False)
    
    # remove axis spines in all directions
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)

    fig.savefig(savepath, dpi=300, bbox_inches="tight")

## MORANS I ##
def calculate_global_moran(street_data):
    # set seed for reproducibility
    np.random.seed(1999)

    # filter midtbyen
    street_data_midtbyen = filter_midtbyen(street_data)

    # get spatial weights from street data
    w_aarhus = lps.weights.KNN.from_dataframe(street_data, k = 3)
    w_midtbyen = lps.weights.KNN.from_dataframe(street_data_midtbyen, k = 3)
    
    # calculate morans I for all of aarhus and for midtbyen
    mi_aarhus = Moran(street_data["rent_per_square_meter"], w_aarhus)
    mi_midtbyen = Moran(street_data_midtbyen["rent_per_square_meter"], w_midtbyen)

    return mi_aarhus, mi_midtbyen

def plot_local_moran(street_data, savepath): # based on tutorial by Dani Arribas-Bel (http://darribas.org/gds15/content/labs/lab_06.html)
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

    # set font to times new roman
    plt.rcParams["font.family"] = "Times New Roman"

    # get significant and non-significant data
    sig_true = street_data_midtbyen[street_data_midtbyen["signficant"] == True]
    sig_false = street_data_midtbyen[street_data_midtbyen["signficant"] == False]

    # define figure with one ax
    fig, ax = plt.subplots(1, figsize=(10, 10))

    # specify legend kwds
    legend_kwds = {'loc':'upper left', 
                        'markerscale':0.8, 
                        'title_fontsize':'medium', 
                        'fontsize':'medium' ,
                        "labels": ["High Rent in High Rent Area", "Low Rent in High Rent Area (outlier)", "Low Rent in Low Rent Area", "High Rent in Low Rent Area (outlier)"], 
                        "title": "Significance Type",
                        "alignment": "left"
                        }

    # plot all that is not significant in grey
    sig_false.plot(color="#F2F3F4", ax=ax, linewidth = 1.7)

    # create custom cmap with ListedColormap
    cmap = ListedColormap(["#F99B93", "#36B00C", "#A3F864", "#C60C0C"])

    # filter on whether significant or not 
    sig_true.plot(column="quadrant", categorical=True, linewidth = 3, legend=True, cmap=cmap, legend_kwds=legend_kwds, ax=ax)

    # Add black end borders to the havnegade
    havnegade = street_data_midtbyen[street_data_midtbyen["street"] == "Havnegade"].geometry.iloc[0]
    ax.plot(*havnegade.coords[0], marker="$-$", color="black", markersize=4)

    # streetname offset (annotation offset coordinate list)
    offset = [
            (-30,0), (30,-15), (30,5), 
            (-35,0), (-20, -10), (45,0), 
            (30,-5), (-20,20), (-30, 10)
            ]

    # add names of streets using iterrows
    for index, row in sig_true.reset_index().iterrows():
        # get offset for street name
        xy_offset = offset[index]

        # plot annotation
        plt.annotate(text=row["street"], 
                    xy=(row["geometry"].centroid.x, row["geometry"].centroid.y), 
                    horizontalalignment='center', 
                    verticalalignment='center', 
                    textcoords="offset points",
                    xytext=xy_offset,
                    fontsize=10,
                    color="black")

    # remove axis ticks
    ax.tick_params(labelleft=False, labelbottom=False, left=False, bottom=False)

    # remove axis spines in all directions
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)

    # save figure
    fig.savefig(savepath, dpi=300, bbox_inches="tight")


def main():
    # define paths
    path = pathlib.Path(__file__)
    plot_dir = path.parents[1] / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    datapath = path.parents[1] / "data"

    # read in district data 
    district_data = load_data(datapath = datapath / "district_aggregates.csv", geometry_col="geometry", crs=25832)

    # read in street data
    street_data = load_data(datapath = datapath / "street_aggregates.csv", geometry_col="geometry_street", crs=25832)

    # plot district overview
    plot_district_overview(district_data, plot_dir / "district_overview.png")
    # plot apartment rent per square meter
    plot_districts_heatmap(district_data, "apartment", plot_dir / "apartment_rent_comparison.png")

    # plot room rent
    plot_districts_heatmap(district_data, "room", plot_dir / "room_rent_comparison.png")

    # plot streets
    plot_streets(street_data, district_data, plot_dir / "street_apartment_rent_sqm_now.png")

    # calculate global morans I
    mi_aarhus, mi_midtbyen = calculate_global_moran(street_data)

    # print morans I and p-value for midtbyen and all of aarhus
    print("Moran's I for midtbyen: ", mi_midtbyen.I, "p-value: ", mi_midtbyen.p_sim)
    print("Moran's I for all of Aarhus: ", mi_aarhus.I, "p-value: ", mi_aarhus.p_sim)

    # plot morans I
    plot_local_moran(street_data, plot_dir / "streets_morans_i.png")

if __name__ == "__main__":
    main()