'''
Script to map Aarhus data. 
'''

import geopandas as gpd
import pandas as pd
import pathlib




def main():
    # define paths
    path = pathlib.Path(__file__)

    complete_data = pd.read_csv(path.parents[1] / 'data' / 'complete_data.csv')

    

    # drop "geometry_street"
    complete_data = complete_data.drop(columns=['geometry_street'])

    # convert to geodataframe
    complete_data = gpd.GeoDataFrame(complete_data)

    



if __name__ == "__main__":
    main()