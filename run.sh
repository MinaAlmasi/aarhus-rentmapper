#!/bin/bash

# activate virtual environment
source ./env/bin/activate

# run cleaning of scraped data
echo -e "[INFO:] Cleaning Rental Data ..." # user msg 
python3 src/clean_data.py

# add geo spatial data to cleaned data
echo -e "[INFO:] Adding Geo Spatial Data to Rentals..." # user msg
python3 src/add_geodata.py

# extract aggregates
echo -e "[INFO:] Extracting Aggregates from Data ..." # user msg
python3 src/aggregate_data.py

# creating visualizations
echo -e "[INFO:] Creating Visualizations for Analysis..." # user msg
python3 src/analysis.py

# deactivate environment
deactivate

# happy msg!
echo -e "[INFO:] Pipeline complete! You can deploy Aarhus RentMapper now from terminal (type: streamlit run app/app.py) after activating the environment again" # user msg