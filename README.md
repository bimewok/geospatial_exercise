**Ben Garrett Mapdwell Geospatial Data Exercise**

**Introduction**

This Github repository contains Ben Garrett&#39;s submission for the geospatial data wrangling exercise provided by Mapdwell. The repository structure is as follows:

-Geospatial\_Data\_Exercise/

--------------------bg\_geo\_tools/

--------------------original\_data/

--------------------intermediate\_data/

--------------------outputs/

-----------zip\_stats.py

-----------above\_avg\_ghi.py

-----------charleston\_dsm.py

-----------charlestown\_buildings\_heights.py

-----------gis.yml

-----------README.md

where:

_-original\_data_ contains all files provided by Mapdwell

_-intermediate\_data_ contains files produced during processing

_-outputs_ contains four files for each requested output for the project

-_bg\_geo\_tools_ contains a bg\_geo\_tools module

-_zip\_stats.py_, _above\_avg\_ghi.py_, _charleston\_dsm.py_, _charlestown\_buildings\_heights.py_ are the scripts that produced each of the four output files.

**Usage**

**Requirements**

All code is written in an Anaconda python 3.7 environment and tested to work on a windows machine Using Anaconda. No software other than python and the below required packages were used for geoprocessing. You can reproduce this environment by calling:

```
conda env create -f gis.yml
```

This environment contains several packages that are not used in this project. To manually build an environment, make sure you have the following packages used in this project:

-rasterstats=0.14.0

-gdal=3.0.2

-pylas=0.4.3 (install with pip install pylas[lazrs])

-geopandas=0.8.1

**Methods**

**Task One -**
