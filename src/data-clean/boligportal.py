# utils 
import pathlib 
import re 

# data wrangling
import pandas as pd

def main():
    # path to file 
    path = pathlib.Path(__file__)

    # path to data folder
    rawdata_path = path.parents[2] / "data" / "raw_data"

    # read in data
    df = pd.read_csv(rawdata_path / "boligportal_aarhus.csv")

    # add website column
    df["website"] = "boligportal.dk"

    # add year column
    df["year"] = 2023

    # exract rental type from rooms_type_kvm column
    df['rental_type'] = df["rooms_type_kvm"].str.extract(r'· ([\w\s]+) ·')

    # extract number of rooms from rooms_type_kvm column
    df["rooms"] = df["rooms_type_kvm"].str.extract(r'(\d+) vær\.')

    # extract size from rooms_type_kvm column
    df['square_meters'] = df["rooms_type_kvm"].str.extract(r'(\d+) m²')

    # translate "Lejlighed" to "apartment" and "Værelse" to "room"
    df["rental_type"] = df["rental_type"].str.replace("Lejlighed", "apartment")
    df["rental_type"] = df["rental_type"].str.replace("Værelse", "room")

    # remove kr on price
    df["price"] = df["price"].str.replace("kr.", "")

    # rename price to rent_without_expenses
    df = df.rename(columns={"price": "rent_without_expenses"})
    
    # area column
    df["area"] = df["address"].str.split(",").str[0]

    # street column
    df["street"] = df["address"].str.split(",").str[1]

    # select cols
    #df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]
    

if __name__ == "__main__":
    main()