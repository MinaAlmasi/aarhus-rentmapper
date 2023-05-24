'''
Script to clean scraped edc data using pandas.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils
import pathlib

# data wrangling
import pandas as pd

def clean_edc(data_path:pathlib.Path, save_path=None):
    '''
    Function to clean scraped edc data using pandas.

    Args: 
        data_path: Path to raw data.
        save_path: Path to save cleaned data. Defaults to None.

    Returns:
        df: Cleaned dataframe.
    
    Output:
        clean_edc_aarhus.csv: Cleaned data. If save_path is not None.
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

    if save_path is not None:
        df.to_csv(save_path / "clean_edc_aarhus.csv", index=False)

    return df

def main():
    # path to file 
    path = pathlib.Path(__file__)

    # define paths
    rawdata_path = path.parents[2] / "data" / "raw_data"
    processed_path = path.parents[2] / "data" / "processed_data"
    zip_codes_path = path.parents[2] / "utils"

    # clean data
    df = clean_edc(rawdata_path, processed_path)


if __name__ == "__main__":
    main()