'''
Script to clean scraped boligzonen data using pandas.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils
import pathlib

# data wrangling
import pandas as pd

def clean_boligzonen(data_path:pathlib.Path, zip_codes:pd.DataFrame, save_path=None):
    # read in data, set type to string
    df = pd.read_csv(data_path / "boligzonen_aarhus.csv", dtype=str)

    # add website column
    df["website"] = "boligzonen.dk"

    # add year column
    df["year"] = 2023

    # exract rental type from type_rooms_kvm column
    df['rental_type'] = df["type_rooms_kvm"].str.split("/").str[0]

    # extract number of rooms from type_rooms_kvm column
    df["rooms"] = df["type_rooms_kvm"].str.extract(r'(\d+)')

    # extract size from type_rooms_kvm column, convert to int
    df['square_meters'] = df["type_rooms_kvm"].str.extract(r'(\d+)\s*m2')

    # translate "Lejlighed" to "apartment" and "Værelse" to "room"
    df["rental_type"] = df["rental_type"].str.replace("Lejlighed", "apartment")
    df["rental_type"] = df["rental_type"].str.replace("Værelse", "room")

    # remove whitespace from rental_type column
    df["rental_type"] = df["rental_type"].str.strip()

    # print unique values in rental_type column
    df = df[df["rental_type"].isin(["apartment", "room"])]

    # print type of price 
    df["price"] = df["price"].str.replace(".", "", regex=False) # remove . in number
    df["price"] = df["price"].astype(int) # convert to int

    # rename price to rent_without_expenses
    df = df.rename(columns={"price": "rent_without_expenses"})

    # add area column, remove whitespace
    df["area"] = df["address"].str.split(",").str[1]
    df["area"] = df["area"].str.strip()

    # add street code column, remove whitespace
    df["street"] = df["address"].str.split(",").str[0]
    df["street"] = df["street"].str.strip()

    # add zip code column, convert to int
    df["zip_code"] = df["area"].map(zip_codes.set_index("area")["zip_code"])
    df["zip_code"] = df["zip_code"].astype(int)

    # select cols
    df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]

    # save to csv
    if save_path is not None:
        save_path.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path / "clean_boligzonen_aarhus.csv", index=False)

    return df

def main():
    # path to file 
    path = pathlib.Path(__file__)

    # define paths
    rawdata_path = path.parents[2] / "data" / "raw_data"
    processed_path = path.parents[2] / "data" / "processed_data"
    zip_codes_path = path.parents[2] / "utils"

    # read in zip codes dataframe from utils folder
    zip_codes = pd.read_csv(zip_codes_path / "zipcode_lookup.csv")

    # clean boligzonen data
    df = clean_boligzonen(rawdata_path, zip_codes, processed_path)

    print(df)

if __name__ == "__main__":
    main()