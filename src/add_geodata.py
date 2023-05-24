import geopandas as gpd
import pathlib
import pandas as pd

def main():
    # define paths
    path = pathlib.Path(__file__)

    geo_data = gpd.read_file(path.parents[1] / "utils" / "streetnames.geojson")
    apartments = pd.read_csv(path.parents[1] / "data" / "processed_data" / "clean_boligportal_aarhus.csv")

    # remove final character for all street names in geo_data if it is a space
    geo_data['vejnavne'] = geo_data['vejnavne'].str.rstrip()

    # merge the data
    merged_df = apartments.merge(geo_data[['vejnavne', 'geometry']], left_on='street', right_on='vejnavne', how='left')

    # drop the redundant column
    merged_df.drop('vejnavne', axis=1, inplace=True)

    # convert the merged DataFrame back to a GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry')

    # save the data as final data
    merged_gdf.to_csv(path.parents[1] / "data" / "final_aarhus_data.csv", index=False)


if __name__ == "__main__":
    main()
