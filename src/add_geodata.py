import geopandas as gpd
import pathlib
import pandas as pd

def load_data():
     # define paths
    path = pathlib.Path(__file__)

    apartments = pd.read_csv(path.parents[1] / "data" /  "cleaned_data.csv")
    districts = pd.read_csv(path.parents[1] / "utils" / "street_to_district.csv", sep=';')
    geo_streets = gpd.read_file(path.parents[1] / "utils" / "streetnames.geojson")
    geo_districts = gpd.read_file(path.parents[1] / "utils" / "districts.geojson")

    return path, apartments, districts, geo_streets, geo_districts


def add_street_geometry(apartments, geo_streets):
    # remove final character for all street names in geo_streets if it is a space
    geo_streets['vejnavne'] = geo_streets['vejnavne'].str.rstrip()

    # ensure oprettet_dato is a datetime object
    geo_streets['oprettet_dato'] = pd.to_datetime(geo_streets['oprettet_dato'])

    # only keep the most recent observation of each street name
    geo_streets = geo_streets.sort_values(by='oprettet_dato', ascending=False)
    geo_streets = geo_streets.drop_duplicates(subset=['vejnavne'])

    # merge the data
    merged_df = apartments.merge(geo_streets[['vejnavne', 'geometry']], left_on='street', right_on='vejnavne', how='left')

    # drop the redundant column
    merged_df.drop('vejnavne', axis=1, inplace=True)

    # convert the merged DataFrame back to a GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry')

    return merged_gdf


def update_disticts(districts):
    # This function adds streets with districts that are missing from the original file manually

    # define the missing streets and their districts
    missing_streets = ["Kongevellen", "Brassøvej", "Møllehatten", "Pollenvænget", "Borresøvej", "Broloftet", "Honningvænget",
                       "Eya Jensens Gade", "Kværnloftet", "Dirch Passers Gade", "Doris Kæraas Gade", "Tommy Seebachs Gade",
                       "Ellen Jensens Gade", "Ringen", "Tulipanhaven", "Tove Ditlevsens Gade", "Tulipanlunden", "Sifsgade",
                       "Baldersgade"]

    matching_districts = ["Stat dist: 04.81", "Stat dist: 04.40", "Stat dist: 04.81", "Stat dist: 06.10", "Stat dist: 04.40", "Stat dist: 04.81", "Stat dist: 06.10",
                         "Stat dist: 04.81", "Stat dist: 04.81", "Stat dist: 01.60", "Stat dist: 04.81", "Stat dist: 01.60", 
                         "Stat dist: 04.60", "Stat dist: 05.00", "Stat dist: 06.10", "Stat dist: 04.81", "Stat dist: 06.10", "Stat dist: 03.60",
                         "Stat dist: 03.60"]
    
    # create a DataFrame with the missing streets and their districts
    missing_districts = pd.DataFrame({'Vejnavn': missing_streets, 'StatistikdistriktNavn': matching_districts})

    # append the missing streets and their districts to the original DataFrame
    districts = districts.append(missing_districts)

    return districts

def add_district(apartments, districts):
    # for each "Vejnavn", find the most common "StatistikdistriktNavn"
    districts = districts.groupby(['Vejnavn', 'StatistikdistriktNavn']).size().reset_index(name='counts')

    # keep only the most common "StatistikdistriktNavn" for each "Vejnavn"
    districts = districts.sort_values(by='counts', ascending=False)
    districts = districts.drop_duplicates(subset=['Vejnavn'])

    # merge the data
    merged_df = apartments.merge(districts, left_on='street', right_on='Vejnavn', how='left')

    # drop the redundant column
    merged_df.drop('Vejnavn', axis=1, inplace=True)

    # convert the merged DataFrame back to a GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(merged_df, geometry='geometry')

    return merged_gdf


def update_district_names(apartments, geo_districts):
    ## We use the geodistrict file to go away from keys for district names

    # update district names in apartment to only the key
    apartments['StatistikdistriktNavn'] = apartments['StatistikdistriktNavn'].str.split(':').str[1]

    # remove empty space at end of district names
    apartments['StatistikdistriktNavn'] = apartments['StatistikdistriktNavn'].str.strip()
    geo_districts['noegle'] = geo_districts['noegle'].str.strip()

    # ensure both columns are strings
    apartments['StatistikdistriktNavn'] = apartments['StatistikdistriktNavn'].astype(str)
    geo_districts['noegle'] = geo_districts['noegle'].astype(str)

    # only keep "noegle", "prog_distrikt_navn", and "geometry"
    geo_districts = geo_districts[['noegle', 'prog_distrikt_navn', 'geometry']]

    # merge
    merged_df = apartments.merge(geo_districts, left_on='StatistikdistriktNavn', right_on='noegle', how='left')

    # drop the redundant column
    merged_df.drop('noegle', axis=1, inplace=True)

    # change geomtry_x to "geometry_street" and geometry_y to "geometry_district"
    merged_df.rename(columns={'geometry_x': 'geometry_street', 'geometry_y': 'geometry_district'}, inplace=True)

    # update names of columns
    merged_df.rename(columns={'prog_distrikt_navn': 'district'}, inplace=True)

    return merged_df


def main():
    # load data
    path, apartments, districts, geo_streets, geo_districts = load_data()

    # add geometry to the data
    apartments = add_street_geometry(apartments, geo_streets)

    # update districts
    districts = update_disticts(districts)
    
    # add district to the data
    apartments = add_district(apartments, districts)

    # update district names
    apartments = update_district_names(apartments, geo_districts)

    # drop all rows with missing values
    apartments = apartments.dropna()

    # print the count of each prog_distrikt_navn with avg. price
    print(apartments.groupby('year').count())

    print(apartments)

    # save the data as final data
    apartments.to_csv(path.parents[1] / "data" / "final_aarhus_data.csv", index=False)


if __name__ == "__main__":
    main()
    
