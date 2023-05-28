'''
Script to display aggregate stats of the complete Aarhus data with geometry. Contains functions to get district and street aggregates.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

import geopandas as gpd
import pandas as pd
import pathlib

def get_neighbor_districts(complete_data:pd.DataFrame):
    '''
    Function to get neighbor districts by finding all districts that touch or overlap with each other using GeoPandas.

    Args
        complete_data: complete pandas dataframe with geometry as string

    Returns
        complete_data: complete pandas dataframe with neighbor districts
    '''

    # convert geometry to wkt
    complete_data["geometry"] = gpd.GeoSeries.from_wkt(complete_data["geometry"])

    # transform into geodataframe
    complete_data = gpd.GeoDataFrame(complete_data, geometry="geometry")

    district_neighbors = []

    # loop through all districts
    for i in range(len(complete_data)):
        # get district name
        district = complete_data.iloc[i]["district"]

        # get neighbors. Both "touches" and "overlaps" is used to get all neighbors due to the resolution of our polygons (some polygons are not perfectly aligned). # solution by https://gis.stackexchange.com/questions/281652/finding-all-neighbors-using-geopandas 
        neighbors_touching = complete_data[complete_data.geometry.touches(complete_data.iloc[i].geometry)].district.tolist()
        neighbors_overlaps = complete_data[complete_data.geometry.overlaps(complete_data.iloc[i].geometry)].district.tolist()

        # find union
        neighbors = neighbors_touching + neighbors_overlaps

        # add neighbors to list
        district_neighbors.append(neighbors)
    
    # add neighbors to dataframe
    complete_data["neighbors"] = district_neighbors

    return complete_data


def get_district_aggregates(complete_data:pd.DataFrame, save_path:pathlib.Path):
    '''
    Function to get district aggregates from complete_data_csv.

    Args
        complete_data: complete pandas dataframe with geometry as string
        save_path: path to save the district aggregates to
    
    Returns
        district_data: district aggregates with geometry object as string
    '''

    # add time column. Should be "now" for year == 2023 and "then" for everything else
    complete_data["time"] = complete_data["year"].apply(lambda x: "now" if x == 2023 else "then")

    # group the data by district, get apartment_rent per square meters for 2023 
    district_data = complete_data.groupby(["district", "rental_type", "time"]).agg({"rent_per_square_meter": "mean", "rent_without_expenses": "mean"}).reset_index()

    # pivot data to get it back into the right format
    district_data = district_data.pivot(index=["district"], columns=["rental_type", "time"], values=["rent_per_square_meter", "rent_without_expenses"]).reset_index()

    # rename columns
    district_data.columns = ["district", "apartment_rent_sqm_now", "apartment_rent_sqm_then", "room_rent_sqm_now", "room_rent_sqm_then",
                             "apartment_rent_now", "apartment_rent_then", "room_rent_now", "room_rent_then"]

    # drop columns 
    district_data = district_data.drop(columns=["room_rent_sqm_now", "room_rent_sqm_then", "apartment_rent_now", "apartment_rent_then"])

    # round
    district_data = district_data.round(1)

    # calculate apartment_rent_change and room_rent_change in percent. It is calculated as (then - now) / now * 100
    district_data["apartment_rent_change"] = round((district_data["apartment_rent_sqm_now"] - district_data["apartment_rent_sqm_then"]) / district_data["apartment_rent_sqm_then"] * 100, 1)
    district_data["room_rent_change"] = round((district_data["room_rent_now"] - district_data["room_rent_then"]) / district_data["room_rent_then"] * 100, 1)

    ## COUNTS
    apartment_rooms_count = complete_data[complete_data["year"] == 2023].groupby(["district", "rooms"])["id"].count()

    # pivot data to get it back into the right format
    apartment_rooms_count = apartment_rooms_count.reset_index().pivot(index=["district"], columns=["rooms"], values=["id"]).reset_index()

    # rename columns
    apartment_rooms_count.columns = ["district", "apartments_w_1_room", "apartments_w_2_rooms", "apartments_w_3_rooms", "apartments_w_4_rooms", "apartments_w_+4_rooms"]

    # replace NaNs with 0
    apartment_rooms_count = apartment_rooms_count.fillna(0)

    # add to district_data
    district_data = district_data.merge(apartment_rooms_count, on="district")

    # add back geometry from complete_data
    district_data = district_data.merge(complete_data[["district", "geometry"]].drop_duplicates(), on="district")

    # get neighbor districts
    district_data = get_neighbor_districts(district_data)

    # write to csv
    district_data.to_csv(save_path / "district_aggregates.csv", index=False)

    return district_data


def similar_rent_prices(street_data, n_similar_streets:int):
    '''
    Get n_similar_streets with similar rent prices for each street in street_data.

    Args
        street_data: pandas dataframe with street names and rent prices
        n_similar_streets: number of similar streets to get
    
    Returns
        street_data: street_data with most_similar_streets and most_similar_rents columns
    '''

    most_similar_streets = []
    most_similar_rents = []
    most_similar_districts = []

    for i in range(len(street_data)):
        # define target street and rent
        target_street = street_data.iloc[i]["street"]
        target_rent = street_data.iloc[i]["rent_per_square_meter"]
        target_district = street_data.iloc[i]["district"]
        
        # get all streets except target street
        other_streets = street_data[street_data["street"] != target_street].copy() # copy to avoid SettingWithCopyWarning

        # add column with absolute difference in rent to target street
        other_streets["abs_diff"] = abs(other_streets["rent_per_square_meter"] - target_rent)

        # get n_similar_streets with smallest absolute difference
        similar_streets = other_streets.sort_values(by="abs_diff", ascending=True).head(n_similar_streets)

        # add street names and rents to lists
        most_similar_streets.append(similar_streets["street"].tolist())
        most_similar_rents.append(similar_streets["rent_per_square_meter"].tolist())
        most_similar_districts.append(similar_streets["district"].tolist())
    
    # add lists to dataframe
    street_data["most_similar_streets"] = most_similar_streets
    street_data["most_similar_rents"] = most_similar_rents
    street_data["most_similar_districts"] = most_similar_districts

    # create new columns for unpacking most_similar_streets
    new_columns_streets = ['most_similar_{}'.format(i+1) for i in range(5)]
    unpacked_df_streets = pd.DataFrame(street_data['most_similar_streets'].to_list(), columns=new_columns_streets)

    # create new columns for unpacking most_similar_rents
    new_columns_rents = ['most_similar_rent_{}'.format(i+1) for i in range(5)]
    unpacked_df_rents = pd.DataFrame(street_data['most_similar_rents'].to_list(), columns=new_columns_rents)

    # create new columns for unpacking most_similar_districts
    new_columns_districts = ['most_similar_district_{}'.format(i+1) for i in range(5)]
    unpacked_df_districts = pd.DataFrame(street_data['most_similar_districts'].to_list(), columns=new_columns_districts)

    # concatenate the new DataFrames with the original DataFrame
    street_data = pd.concat([street_data, unpacked_df_streets, unpacked_df_rents, unpacked_df_districts], axis=1)

    # drop columns
    street_data = street_data.drop(columns=["most_similar_streets", "most_similar_rents", "most_similar_districts"])

    return street_data


def get_street_aggregates(complete_data, savepath, n_similar_streets:int=5):
    '''

    Args
        complete_data: complete pandas dataframe with geometry as string
        savepath: path to save the street aggregates to
    
    Returns
        street_data: street aggregates with geometry object as string
    '''

    # remove all years before 2023
    complete_data = complete_data[complete_data["year"] == 2023]

    # only keep all apartments
    complete_data = complete_data[complete_data["rental_type"] == "apartment"]

    # group by street
    street_data = complete_data.groupby(["street", "district"]).agg({"rent_per_square_meter": "mean", "rent_without_expenses": "mean"}).reset_index()

    # round rent_per_square_meter to 1 decimal
    street_data["rent_per_square_meter"] = round(street_data["rent_per_square_meter"], 1)

    # for each street, find the five other streets with most similar rent_per_square_meter
    street_data = similar_rent_prices(street_data, n_similar_streets)

    # add counts of how many rows per street
    street_counts = complete_data.groupby(["street"])["id"].count()

    # add to street_data
    street_data = street_data.merge(street_counts, on="street")

    # rename from id to count 
    street_data = street_data.rename(columns={"id": "count"})

    # add geometry from complete_data
    street_data = street_data.merge(complete_data[["street", "geometry_street"]].drop_duplicates(), on="street")

    street_data.to_csv(savepath / "street_aggregates.csv", index=False)

    return street_data


def main():
    # define paths
    path = pathlib.Path(__file__)
    data_path = path.parents[1] / "data"

    # read complete data
    complete_data = pd.read_csv(path.parents[1] / "data" / "complete_data.csv")

    # create district aggregates
    district_data = get_district_aggregates(complete_data, data_path)

    # create street aggregates
    street_data = get_street_aggregates(complete_data, data_path, n_similar_streets=5)
    


if __name__ == "__main__":
    main()