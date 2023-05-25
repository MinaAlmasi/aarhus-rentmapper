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
    geo_society = gpd.read_file(path.parents[1] / "utils" / "lokalsamfund.geojson")

    return path, apartments, districts, geo_streets, geo_districts, geo_society


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


def update_stat_disticts(districts):
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
    districts = pd.concat([districts, missing_districts])

    return districts


def add_stat_district(apartments, districts):
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


def update_stat_district_names(apartments, geo_districts):
    ## We use the geodistrict file to go away from keys for district names.

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

    # change geomtry_x to "geometry_street" and geometry_y to "stat_geometry"
    merged_df.rename(columns={'geometry_x': 'geometry_street', 'geometry_y': 'stat_geometry'}, inplace=True)

    # update names of columns
    merged_df.rename(columns={'prog_distrikt_navn': 'stat_district'}, inplace=True)

    # remove irrelevant columns
    merged_df.drop(['StatistikdistriktNavn', 'counts'], axis=1, inplace=True)

    # convert the merged DataFrame back to a GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(merged_df, geometry="stat_geometry")

    return merged_gdf


def add_society_districts(apartments, geo_society):
    """
    Add society districts ("Lokal Samfund") to apartments data based on the statistics districts ("Statistikdistrikt")

    Args: 
        apartments: GeoDataFrame with apartments
        geo_society: GeoDataFrame with society districts ("Lokal Samfund")

    Returns:
        apartments: GeoDataFrame with apartments with society districts ("Lokal Samfund")
    """
    
    # subset relevant columns from geo_society
    geo_society = geo_society[["distrikt", "geometry"]]

    # empty lists for new columns 
    society_district = []
    society_geometry = []

    # loop over apartments data 
    for i in range(len(apartments)):
        # define the polygon of the statistics district (stat_dist)
        statistik_polygon = apartments["stat_geometry"][i]

        max_overlap_area = 0
        max_overlap_index = None

        # loop over the geo_society data 
        for k in range(len(geo_society)):
            # define the polygon of the society district 
            society_polygon = geo_society["geometry"][k]

            # find the intersection of the two polygons (stat_dist and society)
            intersection = society_polygon.intersection(statistik_polygon)
            
            # find the area of the intersection
            overlap_area = intersection.area

            # if the area of the intersection is larger than the previous largest intersection, update the largest intersection
            if overlap_area > max_overlap_area:
                max_overlap_area = overlap_area
                max_overlap_index = k
        
        # append the society district and geometry to the empty lists
        society_district.append(geo_society["distrikt"].iloc[max_overlap_index])
        society_geometry.append(geo_society["geometry"].iloc[max_overlap_index])
    
    # add the new columns to the apartments data
    apartments["society_district"] = society_district
    apartments["society_geometry"] = society_geometry

    return apartments 


def merge_districts(apartments):
    """
    Merge "Statistikdistriker" (statistics districts) into larger districts based on the "Lokal Samfund" (society districts). 
    Done for all statistics districts except "Midtbyen" (city center).

    Args:
        apartments: GeoDataFrame with apartments with both statistics districts and society districts

    Returns:
        apartments: GeoDataFrame with apartments with both statistics districts and society districts merged into larger districts
    """

    # define midtbyen districts
    midtbyen = ["Trøjborg", "Universitetet/Kommunehospitalet", "Nordre Kirkegård", "Vestervang/Klostervang/Ø-gaderne", "Ø-gaderne Øst",
                "Østbanetorvet/Nørre Stenbro", "Nørregade", "Latinerkvarteret", "Klostertorv/Vesterbro Torv", "Åboulevarden", "Skolegade/Bispetorv/Europaplads",
                "Mølleparken", "TelefonTorvet", "Fredens Torv", "Ceresbyen/Godsbanen", "Rådhuskvarteret", "De Bynære Havnearealer/Aarhus Ø",
                "Sydhavnen og Marselisborg lystbådehavn", "Frederiksbjerg Vest", "Frederiksbjerg Øst", "Erhvervshavnen"]
    
    # initialize empty column for final districts
    districts = []
    geometry = []
    
    for i in range(len(apartments)):
        if apartments["stat_district"][i] in midtbyen:
            districts.append(apartments["stat_district"][i])
            geometry.append(apartments["stat_geometry"][i])
        
        else:
            districts.append(apartments["society_district"][i])
            geometry.append(apartments["society_geometry"][i])
    
    # add the new columns to the apartments data
    apartments["district"] = districts
    apartments["geometry"] = geometry

    # drop irrelevant columns
    apartments.drop(["stat_district", "stat_geometry", "society_district", "society_geometry"], axis=1, inplace=True)

    # convert the merged DataFrame back to a GeoDataFrame
    apartments = gpd.GeoDataFrame(apartments, geometry="geometry")

    return apartments


def main():
    # load data
    path, apartments, districts, geo_streets, geo_districts, geo_society = load_data()

    # add geometry to the data
    apartments = add_street_geometry(apartments, geo_streets)

    # update districts
    districts = update_stat_disticts(districts)
    
    # add district to the data
    apartments = add_stat_district(apartments, districts)

    # update district names
    apartments = update_stat_district_names(apartments, geo_districts)

    # drop all rows with missing values
    apartments = apartments.dropna()

    # reset index
    apartments = apartments.reset_index(drop=True)

    # add society districts
    apartments = add_society_districts(apartments, geo_society)

    # get overlaps
    apartments = merge_districts(apartments)
    
    print(apartments)

    # save as csv
    apartments.to_csv(path.parents[1] / "data" / "complete_data.csv", index=False)



if __name__ == "__main__":
    main()
    
