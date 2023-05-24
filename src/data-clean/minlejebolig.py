'''
Script to clean scraped minlejebolig data using pandas.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils
import pathlib

# data wrangling
import pandas as pd

def clean_minlejebolig(data_path:pathlib.Path, zip_codes, save_path=None):
    '''
    Function to clean scraped minlejebolig data using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.
        save_path: Path to save cleaned data. Defaults to None.        

    Returns:
        df: Cleaned dataframe.
    '''
    # read in data
    df = pd.read_csv(data_path / "minlejebolig_aarhus.csv")

    # add website column
    df["website"] = "minlejebolig.dk"

    # add year column
    df["year"] = 2023

    # create rental type (all rows from minlejebolig are apartments)
    df["rental_type"] = "apartment"

    # rooms
    df["rooms"] = df["rooms"].str.split(" ").str[0]

    # number from kvm column
    df["square_meters"] = df["kvm"].str.extract(r'(\d+) m²')

    # fix price
    df["rent_without_expenses"] = df["price"].str.replace(",- pr. mdr.", "", regex=False) # remove kr.
    df["rent_without_expenses"] = df["rent_without_expenses"].str.replace(".", "", regex=False) # remove . in number

    # extract addresses from address column, create street column
    df["street"] = df["address"].str.split(",").str[0]

    # create area column
    df["area"] = df["address"].str.split(",").str[1]

    # replace "Århus" with "Aarhus"
    df["area"] = df["area"].str.replace("Århus", "Aarhus", regex=False)

    # remove whitespace
    df["area"] = df["area"].str.strip()

    # add zip code column
    df["zip_code"] = df["area"].map(zip_codes.set_index("area")["zip_code"])

    # select cols
    df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]

    if save_path is not None:
        df.to_csv(save_path / "clean_minlejebolig_aarhus.csv", index=False)

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

    # clean data
    df = clean_minlejebolig(rawdata_path, zip_codes, processed_path)

    print(df)

if __name__ == "__main__":
    main()
