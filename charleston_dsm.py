# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 14:07:12 2021

@author: bimew
"""

import pylas
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import os, sys
import time
from bg_geo_tools.bg_geo_tools import *

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    if os.getcwd().split('\\')[-1] != 'geospatial_exercise':
        print('unable to change working directory')
        print('please manually change wd to folder')
        print('/geospatial_exercise')
        sys.exit()

start_time = time.time()


output_dir = 'outputs'
intermediate_data_dir = 'intermediate_data'
lidar_path = 'original_data\charlestown.laz'

#==================== load laz lidar file ====================================

las = pylas.read(lidar_path)

#==================== get coordinates of points in point cloud ===============

x_coord = las.x.astype(np.float32)
y_coord = las.y.astype(np.float32)
z_coord = las.z.astype(np.float32)

#==================== get extent of dataset to create grid of cells for dsm ==

xmax = np.max(x_coord)
ymax = np.max(y_coord)
xmin = np.min(x_coord)
ymin = np.min(y_coord)

#==================== create grid of shapely polygons in a 2m x 2m grid ======

cell_size = 2


cols = list(np.arange(xmin, xmax + cell_size, cell_size))
rows = list(np.arange(ymin, ymax + cell_size, cell_size))

polygons = []
for x in cols[:-1]:
    for y in rows[:-1]:
        polygons.append(
            Polygon(
                [(x,y), (x+cell_size, y), 
                 (x+cell_size, y+cell_size), (x, y+cell_size)
                 ]
                    )
                )

print('polygons appended')

#==================== create geodataframe from polygon geometries ============

grid = gpd.GeoDataFrame({'geometry':polygons})
grid['poly_num'] = np.arange(0, len(grid))
print('polygon gdf created')

#==================== convert raw x, y, z coordinates to shapely geodataframe 
points = gpd.GeoDataFrame(z_coord, columns=['z'],
                          geometry=gpd.points_from_xy(x=x_coord, y=y_coord))

print('points gdf created')



#==================== perform spatial join and aggregate =====================                                      
''' this join takes the points and finds which polygon they are in.
Then it aggregates the dataframe so that only the max height for each 
polygon cell is retained. This takes a while'''

intersection_cnt = gpd.sjoin(
    grid, points, how='left', op='intersects'
        ).groupby('poly_num').max().reset_index()

#==================== get spatial information back by performing a join ======
final_grid = grid.merge(intersection_cnt, on='poly_num')
print('grid created')

#==================== set the crs of the coordinates =========================
'''I could not figure out how to find the projection of the .laz file.
The coordinates were similar to global meter-based projections and I was
easily able to find the right one '''

final_grid = final_grid.set_crs(3857, allow_override=True)

#==================== save the shapefile so we can call gdal from cli ========
print('Saving Shapefile')
final_grid.to_file(intermediate_data_dir+'/'+'grid.shp')




#==================== call gdal from command line to convert polygon to raster

gdal_string = ('gdal_rasterize -l grid -a z -tr {cell_size} {cell_size} '
               '-a_nodata -99.99 -te '
               '{xmin} {ymin} {xmax} {ymax} '
               '-ot Float32 -of GTiff {inpath} '
               '{outpath}'
               ).format(cell_size=cell_size,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        inpath=intermediate_data_dir+'/'+'grid.shp',
                        outpath=output_dir+'/'+'charleston.tif'
                        )

os.system(gdal_string)

make_hillshade(output_dir+'/'+'charleston.tif', 
               intermediate_data_dir+'/'+'hillshade.jpg')

print("--- %s seconds ---" % (time.time() - start_time))

