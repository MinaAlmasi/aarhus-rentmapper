'''
Script to map Aarhus data. 
'''

import geopandas as gpd
import pandas as pd
import pathlib
import matplotlib.pyplot as plt




def main():
    # define paths
    path = pathlib.Path(__file__)

    # read in data
    district_data = pd.read_csv(path.parents[1] / "data" / "district_aggregates.csv")

    # change wkt to geometry
    district_data["geometry"] = gpd.GeoSeries.from_wkt(district_data["geometry"])

    # convert to geodataframe
    district_data = gpd.GeoDataFrame(district_data, geometry="geometry")

    # set epsg to 25832
    district_data = district_data.set_crs(epsg=25832)

    # plot apartment rent per square meter in 2023
    fig, ax = plt.subplots(figsize=(30, 30))

    district_data.plot(column="apartment_rent_sqm_now", ax=ax, legend=True, legend_kwds={"label": "Apartment rent per square meter in 2023", "orientation": "horizontal"})

    ax.set_title("Apartment rent per square meter in 2023", fontsize=20)

    plt.savefig(path.parents[1] / "apartment_rent_sqm_now.png")

    

if __name__ == "__main__":
    main()