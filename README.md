# **Ben Garrett Mapdwell Geospatial Data Exercise**

# **Introduction**

This Github repository contains Ben Garrett&#39;s submission for the geospatial data wrangling exercise provided by Mapdwell. The repository structure is as follows:

-Geospatial\_Data\_Exercise/

--------------------bg\_geo\_tools/

---------------------------- bg\_geo\_tools.py

--------------------original\_data/

--------------------intermediate\_data/

--------------------outputs/

-----------zip\_stats.py

-----------above\_avg\_ghi.py

-----------charleston\_dsm.py

-----------charlestown\_buildings\_heights.py

-----------interactive\_results.ipynb

-----------gis\_env.yml

-----------README.md

where:

_-original\_data_ contains all files provided by Mapdwell

_-intermediate\_data_ contains files produced during processing

_-outputs_ contains four files for each requested output for the project

-_bg\_geo\_tools_ contains a bg\_geo\_tools module

-_zip\_stats.py_, _above\_avg\_ghi.py_, _charleston\_dsm.py_, _charlestown\_buildings\_heights.py_ are the scripts that produced each of the four output files.

-interactive\_results.ipynb is a notebook that allows users to visualize and interact with my outputs.

# **Usage**

Four scripts are located in the main repository:

-zip\_stats.py (task one) (runtime = 13 seconds)

-above\_avg\_ghi.py (task two) (runtime = 8 seconds)

-charleston\_dsm.py (task three) (runtime = 20minutes)

-charleston\_building\_heights.py (task four) ( runtime = 12seconds)

Each of these scripts will produce the requested output and save it in the /outputs folder. These scripts also import functions from a module I created for this project in /bg\_geo\_tools.

The scripts will attempt to change the working directory to match the file structure of the repository. However, running the scripts in interactive mode line by line may produce exception asking the user to manually change the working directory if python could not do so. Other than this, no modification of the code or setting of variables should be required to produce the requested output. Gdal will throw an error in several of the scripts but this is a part of a try / except conditional, so it can be ignored.

**Additionally, my outputs can be visualized with interactive folium maps and dataframes in the i**** nteractive\_results.ipynb**

# **Requirements**

All code is written in an Anaconda python 3.7 environment and tested to work on a windows machine using conda. No software other than python and the below required packages were used for geoprocessing. You can reproduce this environment by calling:

```
conda env create -f gis\_env.yml
```

This environment contains several packages that are not used in this project. To manually build an environment, make sure you have the following packages:

-rasterstats=0.14.0

-gdal=3.0.2

-pylas=0.4.3 (install with pip install pylas[lazrs])

-geopandas=0.8.1

-folium=0.12.0

# **Methods**

## **Task One -**

1. Ensure GHI raster have same projection
2. Check zip code layer&#39;s projection against GHI rasters
3. Reproject zip code layer
4. Convert multipart polygons to singlepart polygons to eliminate GeoPandas error
5. Calculate zonal statistics (mean) for July and January for each zip code. The zonal statistics algorithm calculates the mean value of each cell that intersects the zip code. This leads to a small amount of error by counting GHI cells that barely touch the zip code, but the spatial resolution of the GHI layer is low enough that a more precise solution would not product more accurate results
6. Aggregate zonal statistics by zip code. This is necessary after the multi to single part conversion. This also could lead to some error if GHI changed dramatically over short distances, which it does not
7. Check solar panel layer&#39;s projection against other layers
8. Reproject solar panel layer
9. Perform a spatial join of solar panels and zip codes and sum intersections for each zip code
10. Merge the solar panel join and GHI zonal statistics into one exportable csv. Calculate Jan to Jul difference in mean GHI.

## **Task**  **Two**  **-**

1. Convert zip code layer to singlepart. Perform dissolve to create a mask of the state
2. Reproject zip code layer to math GHI layer
3. Calculate zonal statistics of mean Jan GHI for MA.
4. Convert GHI raster to polygon for querying
5. Perform intersection of GHI polygon and MA mask to remove the GHI cells that are not in MA
6. Filter out GHI polygons whose Jan GHI is below the MA Jan GHI mean

## **Task**  **Three**  **-**

1. Load laz lidar file and extract arrays of x, y and z coordinates
2. Find the min and max x and y coordinates of the lidar dataset
3. Create a fishnet grid of 2 x 2 meter cells that covers the project area
4. Convert grid to Shapely Polygon class and coordinates to Shapely Point class. Specify projection
5. Perform spatial join to find which points are within each cell
6. Aggregate the join by polygon and take the highest z (height) coordinate return for each polygons
7. Convert polygons to a raster dsm. Also export a hillshade jpg using gdal. For best results, it would be a good idea to fill in holes (cells with no lidar returns) by interpolating their nearest neighbors, but I ran out of time.

## **Task**  **Four**  **-**

1. Reproject buildings footprints to match dsm raster.
2. Calculate zonal statistics for polygons and raster cells by selecting maximum dsm height for each building in the footprints dataset. This can be tuned to filter out steeples and communication towers by choosing the 90th percentile max height rather than max height, depending on what the desired results should represent.
3. Join the zonal statistics output to the original buildings footprint layer to create a geojson output of polygons with associated heights.
4. Export geojson and a csv with no spatial information
