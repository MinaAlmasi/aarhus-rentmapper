'''
Script to display aggregate stats of the complete Aarhus data with geometry. 
'''

import geopandas as gpd
import pandas as pd
import pathlib


def main():
    # define paths
    path = pathlib.Path(__file__)

    complete_data = pd.read_csv(path.parents[1] / "data" / "complete_data.csv")

    print(complete_data)

    # count column 
    district_count = complete_data[complete_data["year"] == 2023].groupby(["district", "rooms"])["id"].count()

    # change column names
    print(district_count.head(50))
    
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

    #print(district_data)



    
    
    



if __name__ == "__main__":
    main()