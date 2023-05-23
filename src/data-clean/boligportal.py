# utils 
import pathlib 
import re 

# data wrangling
import pandas as pd

def main():
    # path to file 
    path = pathlib.Path(__file__)

    # define paths
    rawdata_path = path.parents[2] / "data" / "raw_data"
    processed_path = path.parents[2] / "data" / "processed_data"
    zip_codes_path = path.parents[2] / "utils"

    # make sure that the processed_data folder exists
    processed_path.mkdir(parents=True, exist_ok=True)

    # read in data
    df = pd.read_csv(rawdata_path / "boligportal_aarhus.csv")

    # read in zip codes dataframe from utils folder
    zip_codes = pd.read_csv(zip_codes_path / "zipcode_lookup.csv")

    # add website column
    df["website"] = "boligportal.dk"

    # add year column
    df["year"] = 2023

    # exract rental type from rooms_type_kvm column
    df['rental_type'] = df["rooms_type_kvm"].str.extract(r'· ([\w\s]+) ·')

    # extract number of rooms from rooms_type_kvm column
    df["rooms"] = df["rooms_type_kvm"].str.extract(r'(\d+) vær\.')

    # extract size from rooms_type_kvm column, convert to int
    df['square_meters'] = df["rooms_type_kvm"].str.extract(r'(\d+) m²')
    df['square_meters'] = df['square_meters'].astype(int)

    # translate "Lejlighed" to "apartment" and "Værelse" to "room"
    df["rental_type"] = df["rental_type"].str.replace("Lejlighed", "apartment")
    df["rental_type"] = df["rental_type"].str.replace("Værelse", "room")

    # filter everything that is not an apartment or a room
    df = df[df["rental_type"].isin(["apartment", "room"])]

    # fix price 
    df["price"] = df["price"].str.replace("kr.", "", regex=False) # remove kr.
    df["price"] = df["price"].str.replace(".", "", regex=False) # remove . in number
    df["price"] = df["price"].astype(int) # convert to int

    # rename price to rent_without_expenses
    df = df.rename(columns={"price": "rent_without_expenses"})
    
    # area column
    df["area"] = df["address"].str.split(",").str[0]

    # street column
    df["street"] = df["address"].str.split(",").str[1]

    # zip_code column
    df["zip_code"] = df["area"].map(zip_codes.set_index("area")["zip_code"])

    # rm all rows with missing zip codes as they are not in Aarhus kommune
    df = df.dropna(subset=["zip_code"])

    # convert to int
    df["zip_code"] = df["zip_code"].astype(int)

    # select cols
    df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]

    #save to csv
    df.to_csv(processed_path / "clean_boligportal_aarhus.csv", index=False)    

if __name__ == "__main__":
    main()