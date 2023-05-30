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

# colors
from matplotlib.colors import ListedColormap

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


def plot_districts_overview(district_data:gpd.GeoDataFrame, rental_type:str, savepath:pathlib.Path):
    '''

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

def plot_streets(path, district_data):
    # read in data
    street_data = pd.read_csv(path.parents[1] / "data" / "street_aggregates.csv")

    # change wkt to geometry
    street_data["geometry"] = gpd.GeoSeries.from_wkt(street_data["geometry_street"])

    # convert to geodataframe
    street_data = gpd.GeoDataFrame(street_data, geometry="geometry")

    # set epsg to 25832
    street_data = street_data.set_crs(epsg=25832)

    # define midtbyen districts
    midtbyen = ["Trøjborg", "Universitetet/Kommunehospitalet", "Nordre Kirkegård", "Vestervang/Klostervang/Ø-gaderne", "Ø-gaderne Øst",
                "Østbanetorvet/Nørre Stenbro", "Nørregade", "Latinerkvarteret", "Klostertorv/Vesterbro Torv", "Åboulevarden", "Skolegade/Bispetorv/Europaplads",
                "Mølleparken", "TelefonTorvet", "Fredens Torv", "Ceresbyen/Godsbanen", "Rådhuskvarteret", "De Bynære Havnearealer/Aarhus Ø",
                "Sydhavnen og Marselisborg lystbådehavn", "Frederiksbjerg Vest", "Frederiksbjerg Øst", "Erhvervshavnen", "Botanisk Have/Amtssygehuset"]

    # keep only midtbyen districts
    street_data = street_data[street_data["district"].isin(midtbyen)]
    district_data = district_data[district_data["district"].isin(midtbyen)]

    # define figure with one ax
    fig, ax = plt.subplots(1, figsize=(5, 10))
    
    # define custom cmap with ListedColormap
    cmap = ListedColormap(["#389F38", "#595AFF", "#FF595A"])

    # specify legend kwds 
    legend_kwds = {'loc':'lower right', 
                        'fmt':'{:.1f}',
                        'markerscale':0.8, 
                        'title_fontsize':'medium', 
                        'fontsize':'small', 
                        #"labels": ["< 100 DKK", "100 - 200 DKK", "> 200 DKK"]
                        }

    # add map add distrits as background
    district_data.plot(ax=ax, color="#F2F3F4", edgecolor="black", linewidth=2.5)

    # add streets
    street_data.plot(column="rent_per_square_meter", legend=True, cmap=cmap, legend_kwds=legend_kwds, scheme = "quantiles", k = 3, linewidth=0.8, ax=ax)

    # remove axis
    ax.tick_params(labelleft=False, labelbottom=False, left=False, bottom=False)

    plt.savefig(path.parents[1] / "plots" / "street_apartment_rent_sqm_now.png", dpi=300)



def main():
    # define paths
    path = pathlib.Path(__file__)
    plot_dir = path.parents[1] / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    # read in data
    district_data = pd.read_csv(path.parents[1] / "data" / "district_aggregates.csv")

    # change wkt to geometry
    district_data["geometry"] = gpd.GeoSeries.from_wkt(district_data["geometry"])

    # convert to geodataframe
    district_data = gpd.GeoDataFrame(district_data, geometry="geometry")

    # set epsg to 25832
    district_data = district_data.set_crs(epsg=25832)
    
    # plot apartment rent per square meter
    #plot_districts_overview(district_data, "apartment", plot_dir / "apartment_rent_comparison.png")

    # plot room rent
    #plot_districts_overview(district_data, "room", plot_dir / "room_rent_comparison.png")

    plot_streets(path, district_data)


if __name__ == "__main__":
    main()