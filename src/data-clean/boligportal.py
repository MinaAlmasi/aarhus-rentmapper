'''
Script to clean scraped boligportal data using pandas.

by Anton Drasbæk Schiønning (@drasbaek) and Mina Almasi (@MinaAlmasi)
Spatial Analytics, Cultural Data Science (F2023)
'''

# utils 
import pathlib 

# data wrangling
import pandas as pd

def clean_boligportal(data_path:pathlib.Path, zip_codes:pd.DataFrame, save_path=None):
    '''
    Function to clean scraped boligportal data using pandas.

    Args: 
        data_path: Path to raw data.
        zip_codes: Dataframe with zip codes.
        save_path: Path to save cleaned data. Defaults to None. 

    Returns:
        df: Cleaned dataframe.
    
    Output:
        clean_boligportal_aarhus.csv: Cleaned data. If save_path is not None.
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

    #save to csv
    if save_path is not None:
        save_path.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path / "clean_boligportal_aarhus.csv", index=False)    
    
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

    # clean boligportal data
    df = clean_boligportal(rawdata_path, zip_codes, processed_path)

if __name__ == "__main__":
    main()