The ```src``` folder contains scripts which do the following:
| <div style="width:120px"></div>| Description |
|---------|:-----------|
| ```clean_data.py```  | Clean scraped rental data (aligning formatting across rental sites).       |
| ```add_geodata.py``` | Perform spatial operations to add various geometries (from ```data/geodata```) to rental data.   |
| ```aggregate_data.py``` | Compute aggregates for districts and streets seperately.  |
| ```analysis.py``` | Create plots and compute geostatistics (Moran's I and Moran's Local I).  |
| ```plot_cartogram.R``` | Create cartogram plot.  |
| ```utils.py``` | Add districts which are missing from data to mapping, filter data to either include or disclude Central Aarhus (```Midtbyen```). Functions in ```utils.py``` are used in various scripts, including scripts in the ```app``` folder.  |

See [*Technical Pipeline*](https://github.com/MinaAlmasi/aarhus-rentmapper/tree/main#technical-pipeline) for instructions on how to run these scripts. 