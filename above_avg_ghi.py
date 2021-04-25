# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 11:00:24 2021

@author: bimew
"""
from rasterstats import zonal_stats
import geopandas as gpd
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from bg_geo_tools.bg_geo_tools import *

mass_poly_path = 'original_data\ma_zipcodes.shp'
jan_ghi_path = 'original_data\ghi_jan.tif'

intermediate_data_folder = 'intermediate_data'

output_path = r'outputs\high_jan_ghi.geojson'

#==================== dissolve poly outline to one feature ===================
''' Geopandas does not like multipolygon shapefiles where a single row can 
have multiple geometries. The below trial will convert from multi to single
part if necessary, then dissolves the polygons into a single feature to 
be used as a mask.'''

try:
    mass_poly = gpd.read_file(mass_poly_path)
    mass_poly['dummy'] = 1
    mass_poly = mass_poly.dissolve(by='dummy')
except:
    mass_poly = gpd.read_file(mass_poly_path)
    mass_poly = multi_poly_to_single_poly(mass_poly)
    mass_poly['dummy'] = 1
    mass_poly = mass_poly.dissolve(by='dummy')  

mass_poly_path = intermediate_data_folder+'\\'+mass_poly_path.split('\\')[-1]
mass_poly.to_file(mass_poly_path)

#==================== get ghi projection =====================================

ghi_prj = get_projection(jan_ghi_path)
mass_poly_prj = get_projection(mass_poly_path)


if ghi_prj == mass_poly_prj:
    print('projections match for input layers')
else:
    mass_poly = mass_poly.to_crs('EPSG:{}'.format(ghi_prj))
    mass_poly.to_file(mass_poly_path)
          
#==================== get ghi mean ===========================================
''' The most precise way to get the mean would be to use a polygonized ghi and 
calculate an area-weighted mean for the whole state. However, the data is
clearly low resolution and doing so would be overkill in this context. 
Using zonal statistics means there will be some error where raster pixel
edges overlab the state's boundary'''

mass_mean_ghi = zonal_stats(mass_poly,
                    jan_ghi_path, copy_properties=True,
                    stats="mean", all_touched=True)[0]['mean']

#==================== convert ghi to polygon =================================
''' Selecting and exporting portions of vecors is way easier than rasters.
Thus, I convert the ghi cells to polygons to perform a query against the
mean ghi value calsulated above'''

raster_to_poly_name = 'ghi_poly'
raster_to_poly_new_field = 'ghi'

for file in os.listdir(intermediate_data_folder):
    base_name = file.split('\\')[-1].split('.')[0]
    if base_name == raster_to_poly_name:
        os.remove(intermediate_data_folder+'\\'+file)


ghi_poly_path = intermediate_data_folder+'\\'+raster_to_poly_name+'.shp'



raster_to_poly(jan_ghi_path, 
               intermediate_data_folder, 
               raster_to_poly_name, 
               raster_to_poly_new_field
               )



#==================== intersect mass with ghi poly ===========================
'''This ensures the output doesn't extend past the boundaries of MA'''

ghi_poly = gpd.read_file(ghi_poly_path)

ghi_mass = gpd.overlay(ghi_poly, mass_poly, how='intersection')


#==================== filter out below average ghi cells =====================
    
ghi_mass = ghi_mass[ghi_mass['ghi'] > mass_mean_ghi]

ghi_mass.to_file(output_path, driver='GeoJSON')

