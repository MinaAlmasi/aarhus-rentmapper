import pathlib
import geopandas as gpd

def add_missing_districts(path: pathlib.Path):
    '''
    Function for adding missing districts to dataframe.
    Districts are missing because they have no apartment data.

    Args:
        path: path to script

    Returns:
        missing_districts: geodataframe with missing districts
    '''

    # read in geojson file
    geojson = gpd.read_file(path.parents[1] / "utils" / "districts.geojson")

    # set crs to 25832
    geojson = geojson.set_crs("epsg:25832")

    # extract "Erhvervshavnen" and "Sydhavnen og Marselisborg lystbådehavn" in one dataframe
    missing_districts = geojson[(geojson["prog_distrikt_navn"] == "Erhvervshavnen") | (geojson["prog_distrikt_navn"] == "Sydhavnen og Marselisborg lystbådehavn")]

    # rename prog_distrikt_navn to district
    missing_districts = missing_districts.rename(columns={"prog_distrikt_navn": "district"})

    # remove all columns but district and geometry
    missing_districts = missing_districts[["district", "geometry"]]

    # convert to geodataframe
    missing_districts = gpd.GeoDataFrame(missing_districts, geometry="geometry")

    return missing_districts

def filter_midtbyen(data, midtbyen=True):
    '''
    Function to filter the district data to only include midtbyen

    Args:
        data: dataframe containing the district data
        midtbyen: boolean indicating whether to filter to midtbyen (True) or remove it (False). Defaults to True.
    
    Returns:
        data: dataframe containing the district data for midtbyen
    '''
    # define midtbyen districts
    midtbyen_districts = ["Trøjborg", "Universitetet/Kommunehospitalet", "Nordre Kirkegård", "Vestervang/Klostervang/Ø-gaderne", "Ø-gaderne Øst",
                "Østbanetorvet/Nørre Stenbro", "Nørregade", "Latinerkvarteret", "Klostertorv/Vesterbro Torv", "Åboulevarden", "Skolegade/Bispetorv/Europaplads",
                "Mølleparken", "TelefonTorvet", "Fredens Torv", "Ceresbyen/Godsbanen", "Rådhuskvarteret", "De Bynære Havnearealer/Aarhus Ø",
                "Sydhavnen og Marselisborg lystbådehavn", "Frederiksbjerg Vest", "Frederiksbjerg Øst", "Erhvervshavnen", "Botanisk Have/Amtssygehuset"]
    
    # check if midtbyen should be included or excluded
    if midtbyen == True:
        data = data[data["district"].isin(midtbyen_districts)]
        
    if midtbyen == False:
        data = data[~data["district"].isin(midtbyen_districts)]

    # reset index
    data = data.reset_index(drop=True)

    return data