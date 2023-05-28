#!/bin/bash

# activate virtual environment
source ./env/bin/activate

# run cleaning of scraped data
echo -e "[INFO:] Cleaning Data ..." # user msg 
python3 src/clean_data.py

# add geo spatial data to cleaned data
echo -e "[INFO:] Adding Geo Spatial Data..." # user msg
python3 src/add_geodata.py

# extract aggregates
echo -e "[INFO:] Extracting Aggregates from Data ..." # user msg
python3 src/aggregate_data.py

# happy msg!
echo -e "[INFO:] Pipeline complete! ..." # user msg