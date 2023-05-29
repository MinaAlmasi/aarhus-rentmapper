#!/bin/bash

# create virtual environment called env
python3.9 -m venv env

# activate virtual environment
source ./env/bin/activate

# install requirements
python3.9 -m pip install -r requirements.txt