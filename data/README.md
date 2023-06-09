## Data Overview
The data folder contains the file ```complete_data.csv```  and the folders ```geo_data``` and ```scrape_data```. The file ```complete_data.csv``` has the scraped, clean rental data combined with the geospatial data (street and district geometries).

<br>

## Geospatial Data
The ```geo_data``` folder contains geospatial files from [Open Data DK](https://www.opendata.dk/hvad-er-open-data-dk). All files are licensed under the Creative Commons Atribution 4.0. 
| File                           | Purpose                                                                          | Open Data Link                                     |
| ------------------------------ | -------------------------------------------------------------------------------- | -------------------------------------------------- |
| ```street_to_district.csv```       | Extract district names for street names in scraped data                          | https://www.opendata.dk/city-of-aarhus/aarhus-adressedimension       |
| ```statistics_districts.geojson``` | Polygons for statistics districts (smaller districts for mapping central Aarhus) | https://www.opendata.dk/city-of-aarhus/statistikdistrikter |
| ```local_community.geojson```      | Polygons for local community districts within Aarhus                             | https://www.opendata.dk/city-of-aarhus/lokalsamfund-i-aarhus    |
| ```streetnames.geojson```          | Linestrings for street names                                                    | https://www.opendata.dk/city-of-aarhus/vejnavne-i-aarhus-kommune    |

<br>

## Scraped Rental Data 
The ```scrape_data``` folder contains all scraped rental data:
| | Purpose |
|---------|:-----------|
| ```rental_scape_X.csv``` | Scraped data from rental websites A to D (2023)|
| ```historical-data-X.csv``` | Manually scraped data by either Anton or Mina (historical, 2014-2016)| 
| ```cleaned_data.csv``` | All scraped data (2023 and historical)| 
