<p align="center">
  <img src="https://github.com/MinaAlmasi/aarhus-rentmapper/blob/main/docs/logo.png" alt="Logo">
</p>

<p align="center">
  Anton Drasbæk Schiønning (<strong><a href="https://github.com/drasbaek">@drasbaek</a></strong>) and
  Mina Almasi (<strong><a href="https://github.com/MinaAlmasi">@MinaAlmasi</a></strong>)
</p>

<p align="center">
  Spatial Analytics | Cultural Data Science <br>
  Aarhus University (June 2023) 
</p>

<hr>

This repository contains the code used to design and deploy the tool ```Aarhus RentMapper``` along with the geospatial analysis used within it. 

The tool can be accessed from the link below (NB. optimized for computer browser only!):

<p align="center">
  <a href="https://aarhus-rentmap.streamlit.app/">https://aarhus-rentmap.streamlit.app/</a>
</p>


To reproduce the code, please refer to the section [*Technical Pipeline*](https://github.com/MinaAlmasi/aarhus-rentmapper/tree/main#technical-pipeline). For any further information regarding the project or its reproducibility, contact the authors (see [*Authors*](https://github.com/MinaAlmasi/aarhus-rentmapper#authors)).

## Project Structure 
The repository is structured as such:
| <div style="width:120px"></div>| Description |
|---------|:-----------|
| ```app```  | Folder with all relevant scripts to build and deploy the ```Aarhus RentMapper``` tool.           |
| ```data``` | Folder with scraped rental data, the geodata and the merged datafile ```complete_data.csv``` with rental data containing geospatial information.     |
| ```results``` | Folder with aggregated results. |
| ```plots```| Folder with plots used in the paper.
| ```src```  | Folder with scripts used for cleaning scraped data, combining rental data with geodata, performing data analysis and plotting. See [src/README.md]() for a detailed breakdown.        |
| ```run.sh```    | Run entire analysis pipeline (except for cartograms)      |
| ```X```    |            |


## Technical Pipeline
The code was mainly developed in Python (3.9.13) on a Macbook Pro ‘13 (2020, 2GHz Intel i5, 16GB of ram). Whether it will work on Windows cannot be guaranteed. Moreover, Python's [venv](https://docs.python.org/3/library/venv.html) needs to be installed for the Python pipeline to work.

### Setup 
To be able to reproduce the code, type the following in the terminal: 
```
bash setup.sh
```
The script creates a new virtual environment (```env```) and installs the necessary packages within it.


### Running the Analysis Pipeline
To run the entire analysis pipeline, which laid the foundation for deploying the tool
```
bash run.sh
```

#### Running the R-script
As no Python packages supported plotting cartograms easily, this plot was created in R (4.2.3). 

Firstly, install the library ```pacman``` in the R console by typing:
```
install.packages("pacman")
```

Then, run the script in the terminal by typing:
```

```

### Deploying Aarhus RentMapper Locally 
For testing and development purposes, the ```Aarhus RentMapper``` tool can be deployed locally by typing:
```
streamlit run app/app.py
```
Note that you need to activate the virtual environment first (by running ```source env/bin/activate``` in the terminal)

## Authors 
This code repository was a joint effort by Anton Drasbæk Sciønning ([@drasbaek](https://github.com/drasbaek)) and Mina Almasi ([@MinaAlmasi](https://github.com/MinaAlmasi)). 

### Contact us
For any questions regarding the reproducibility or project in general, you can contact us:
* drasbaek@post.au.dk (Anton)
* mina.almasi@post.au.dk (Mina)