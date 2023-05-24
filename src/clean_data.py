'''
Functions to clean scraped data. Includes seperate functiosn to clean data from boligportal.dk, boligzonen.dk, edc.dk, minlejebolig.dk. 

As the datasets differ in structure, seperate cleaning functions are defined.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils
import pathlib

# data wrangling
import pandas as pd

## functions ##
def clean_boligportal(data_path:pathlib.Path, zip_codes:pd.DataFrame):
    '''
    Function to clean scraped boligportal data using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.

    Returns:
        df: Cleaned dataframe.
    '''

    # read in data
    df = pd.read_csv(data_path / "boligportal_aarhus.csv")

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

def clean_boligzonen(data_path:pathlib.Path, zip_codes:pd.DataFrame):
    '''
    Function to clean scraped boligzonen data using pandas.

    Args:
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.

    Returns:
        df: Cleaned dataframe.
    '''

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

    return df

def clean_edc(data_path:pathlib.Path):
    '''
    Function to clean scraped edc data using pandas.

    Args: 
        data_path: Path to raw data.

    Returns:
        df: Cleaned dataframe.
    '''

    # read in data
    df = pd.read_csv(data_path / "edc_aarhus.csv")

    # remove first row which contains weird address
    df = df.iloc[1:]

    # add website column
    df["website"] = "edc.dk"

    # add year column
    df["year"] = 2023

    # create rental type (all rows from EDC are apartments)
    df["rental_type"] = "apartment"

    # rm extract addresses from address column, create street column
    df["street"] = df["address"].str.split(" ").str[0]

    # convert zip code to int
    df['area'] = df['zip_code'].str.extract(r'\d{4}(.*)')

    # extract zip code from address column
    df['zip_code'] = df['zip_code'].str.extract(r'(\d{4})')

    # rooms, square meters 
    df[['rooms', 'square_meters']] = df["rooms_kvm"].str.extract(r'(\d+) rum, (\d+) m²')

    # fix price
    df["rent_without_expenses"] = df["prices"].str.replace(" kr./md.", "", regex=False) # remove kr.
    df["rent_without_expenses"] = df["rent_without_expenses"].str.replace(".", "", regex=False) # remove . in number

    # select cols
    df = df[["website", "year", "rental_type", "rent_without_expenses", "square_meters", "zip_code", "street", "area", "rooms"]]

    return df

def clean_minlejebolig(data_path:pathlib.Path, zip_codes):
    '''
    Function to clean scraped minlejebolig data using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.

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

    return df

def clean_all_data(data_path, zip_codes, save_path=None):
    '''
    Function to clean all data using pandas.

    Args: 
        data_path: Path to raw data.
        save_path: Path to save cleaned data. Defaults to None.

    Returns:
        df: Cleaned dataframe.
    
    Output:
        clean_all_data.csv: Cleaned data. If save_path is not None.
    '''

    # boligzonen
    bz_df = clean_boligzonen(data_path, zip_codes)

    # boligportal
    bp_df = clean_boligportal(data_path, zip_codes)

    # edc
    edc_df = clean_edc(data_path)

    # minlejebolig
    ml_df = clean_minlejebolig(data_path, zip_codes)

    # concat dataframes 
    all_df = pd.concat([bz_df, bp_df, edc_df, ml_df])

    # save data
    if save_path is not None:
        all_df.to_csv(save_path / "cleaned_data.csv", index=False)

    return all_df


## run script ##
def main(): 
    # path to file 
    path = pathlib.Path(__file__)

    # define paths
    rawdata_path = path.parents[1] / "data" / "raw_data"
    processed_path = path.parents[1] / "data"
    zip_codes_path = path.parents[1] / "utils"

    # read in zip codes dataframe from utils folder
    zip_codes = pd.read_csv(zip_codes_path / "zipcode_lookup.csv")

    # clean data
    all_df = clean_all_data(rawdata_path, zip_codes, processed_path)

if __name__ == "__main__":
    main()