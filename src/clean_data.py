'''
Functions to clean scraped data. Includes seperate functions to clean data from boligzonen.dk, edc.dk, boligportal.dk, minlejebolig.dk. 

As the datasets differ in structure, seperate cleaning functions are defined.
The sites are named with randomized IDs to ensure anonymity.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils
import pathlib

# data wrangling
import pandas as pd

import numpy as np

## functions ##
def clean_site_A(data_path:pathlib.Path, zip_codes:pd.DataFrame):
    '''
    Function to clean scraped data from site A using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.

    Returns:
        df: Cleaned dataframe.
    '''

    # read in data
    df = pd.read_csv(data_path / "rental_scrape_A.csv")

    # add website column (random ID)
    df["website"] = "Site A"

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

    # remove whitespace from price, rename price to rent_without_expenses
    df["rent_without_expenses"] = df["price"].str.strip()
    
    # area column
    df["area"] = df["address"].str.split(",").str[0]

    # street column
    df["street"] = df["address"].str.split(",").str[1]

    # rm white space in street column
    df["street"] = df["street"].str.strip()

    # zip_code column
    df["zip_code"] = df["area"].map(zip_codes.set_index("area")["zip_code"])

    # rm all rows with missing zip codes as they are not in Aarhus kommune
    df = df.dropna(subset=["zip_code"])

    # convert to int
    df["zip_code"] = df["zip_code"].astype(int)

    # select cols
    df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]
    
    return df

def clean_site_B(data_path:pathlib.Path, zip_codes:pd.DataFrame):
    '''
    Function to clean scraped data from site B using pandas.

    Args:
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.

    Returns:
        df: Cleaned dataframe.
    '''

    # read in data, set type to string
    df = pd.read_csv(data_path / "rental_scrape_B.csv", dtype=str)

    # add website column (random ID)
    df["website"] = "Site B"

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

    return df

def clean_site_C(data_path:pathlib.Path):
    '''
    Function to clean scraped data from site C using pandas.

    Args: 
        data_path: Path to raw data.

    Returns:
        df: Cleaned dataframe.
    '''

    # read in data
    df = pd.read_csv(data_path / "rental_scrape_C.csv")

    # remove first row which contains weird address
    df = df.iloc[1:]

    # add website column (random ID)
    df["website"] = "Site C"

    # add year column
    df["year"] = 2023

    # create rental type (all rows from site C are apartments)
    df["rental_type"] = "apartment"

    # extract addresses, rename to street
    df["street"] = df["address"].str.replace(r'\d.*', '', regex=True)

    # get area
    df["area"] = df['zip_code'].str.extract(r'\d{4}(.*)')

    # extract zip code from address column
    df["zip_code"] = df['zip_code'].str.extract(r'(\d{4})')

    # rooms, square meters 
    df[["rooms", "square_meters"]] = df["rooms_kvm"].str.extract(r'(\d+) rum, (\d+) m²')

    # fix price
    df["rent_without_expenses"] = df["prices"].str.replace(" kr./md.", "", regex=False) # remove kr.
    df["rent_without_expenses"] = df["rent_without_expenses"].str.replace(".", "", regex=False) # remove . in number

    # select cols
    df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]

    # remove whitespace all cols
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    return df

def clean_site_D(data_path:pathlib.Path, zip_codes):
    '''
    Function to clean scraped data from site D using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.

    Returns:
        df: Cleaned dataframe.
    '''
    # read in data
    df = pd.read_csv(data_path / "rental_scrape_D.csv")

    # add website column
    df["website"] = "Site D"

    # add year column
    df["year"] = 2023

    # create rental type (all rows from site D are apartments)
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

    return df

def fix_spelling_streetnames(df:pd.DataFrame):
    '''
    Function to manually fix streetnames in dataframe to correspond to the streetnames in "streetnames.geojson"

    Args:
        df: Dataframe with streetnames.
    
    Returns:
        df: Dataframe with corrected streetnames.
    '''

    # define corrections for all streetnames with discrepancies 
    corrections = {
    'M. P. Bruuns Gade': 'M.P. Bruuns Gade',
    'M.P Bruuns Gade': 'M.P. Bruuns Gade',
    "Paludan Müllers Vej": "Paludan-Müllers Vej"
    }  

    df["street"] = df["street"].replace(corrections)

    return df     

def clean_all_data(data_path:pathlib.Path, zip_codes:pd.DataFrame, save_path:pathlib.Path=None):
    '''
    Function to clean all data using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.
        save_path: Path to save cleaned data. Defaults to None.
    
    Output:
        clean_all_data.csv: Cleaned data. If save_path is not None.
    '''

    # site A
    A_df = clean_site_A(data_path, zip_codes)

    # site B
    B_df = clean_site_B(data_path, zip_codes)

    # site C
    C_df = clean_site_C(data_path)

    # site D
    D_df = clean_site_D(data_path, zip_codes)

    # read manually scraped historical data 
    historical_1 = pd.read_csv(data_path / "historical-data-anton.csv")

    # read manually scraped historical data
    historical_2 = pd.read_csv(data_path / "historical-data-mina.csv")

    # concat dataframes 
    all_df = pd.concat([A_df, B_df, C_df, D_df, historical_1, historical_2])

    # remove accents
    all_df["street"] = all_df["street"].str.replace('é', 'e')

    # remove duplicates, consider everything but website and year
    all_df = all_df.drop_duplicates(subset=["year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"])

    # add id column
    all_df["id"] = all_df.index

    # create aggregates for rent per square meter and rent per room
    all_df["rent_per_square_meter"] = all_df["rent_without_expenses"].astype(int) / all_df["square_meters"].astype(int)
    all_df["rent_per_room"] = all_df["rent_without_expenses"].astype(int) / all_df["rooms"].astype(int)

    # remove decimals
    all_df["rent_per_square_meter"] = all_df["rent_per_square_meter"].astype(int)
    all_df["rent_per_room"] = all_df["rent_per_room"].astype(int)

    # make all rooms above 4 into +4 
    all_df['rooms'] = np.where(all_df['rooms'].astype(int) >= 5, '4+', all_df['rooms'])

    # fix spelling of streetnames
    all_df = fix_spelling_streetnames(all_df)

    # save data
    if save_path is not None:
        all_df.to_csv(save_path / "cleaned_data.csv", index=False)


## run script ##
def main(): 
    # path to file 
    path = pathlib.Path(__file__)

    # define paths
    data_path = path.parents[1] / "data" / "scrape_data"
    zip_codes_path = path.parents[1] / "data" / "geo_data"

    # read in zip codes dataframe from geodata folder
    zip_codes = pd.read_csv(zip_codes_path / "zipcode_lookup.csv")

    # clean data
    clean_all_data(data_path, zip_codes, data_path)

if __name__ == "__main__":
    main()