# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 09:49:16 2021

@author: bimew
"""

from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
import sys
import numpy as np
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


from bg_geo_tools.bg_geo_tools import *

#==================== global variables =========================
zip_code_path = 'original_data\ma_zipcodes.shp'
jan_ghi_path = 'original_data\ghi_jan.tif'
jul_ghi_path = 'original_data\ghi_jul.tif'
solar_panels_path = 'original_data\pvsystems_3857.gpkg'

intermediate_data_folder = 'intermediate_data'

output_path = 'outputs'

output_data = pd.DataFrame(
    columns=['zip_code', 'jan_mean_ghi', 'jul_mean_ghi', 'num_solar_pannels'])



#==================== get ghi projection =====================================

jan_prj = get_projection(jan_ghi_path)
jul_prj = get_projection(jul_ghi_path)

if jan_prj == jul_prj:
    print('projections match for input rasters')
    
else:
    sys.exit('''ERROR: rasters have different projections. 
          must reproject using gdal''')
          
#==================== open zip codes =========================================

original_zip_codes = gpd.read_file(zip_code_path)

#==================== convert multipolygons to singlepolygons ================
''' Geopandas does not like multipolygon shapefiles where a single row can 
have multiple geometries. The below trial will convert from multi to single
part if necessary, then dissolves the polygons into a single feature to 
be used as a mask.'''

original_zip_codes = multi_poly_to_single_poly(original_zip_codes)

#==================== ensure zip codes is in the same proj as rasters ========

if get_projection(zip_code_path) != jan_prj:
    zip_codes = original_zip_codes.to_crs("EPSG:{}".format(jan_prj))
    zip_codes.to_file(intermediate_data_folder+'\\'+zip_code_path.split('\\')[-1])
    zip_code_path = intermediate_data_folder+'\\'+zip_code_path.split('\\')[-1]
   
zip_codes_df = pd.DataFrame(zip_codes)

#==================== get mean jan and jul ghi for each polygon ==============
''' The most precise way to get the mean ghi would be to use a polygonized 
ghi and calculate an area-weighted mean from an intersection with the zip 
code layer. However, the ghi data is clearly very low resolution and thus
doing so would not lead to a more accurate final product. The zonal statistics
tool calculates the mean value for all ghi raster cells that intersect
the zip code polygon.'''

jan_mean = zonal_stats(zip_codes,
                    jan_ghi_path, copy_properties=True,
                    stats="mean", all_touched=True)

jul_mean = zonal_stats(zip_codes,
                    jul_ghi_path, copy_properties=True,
                    stats="mean", all_touched=True)

for i in range(len(zip_codes_df)):
    append_dict = {'zip_code':zip_codes_df['POSTCODE'][i],
                   'jan_mean_ghi':jan_mean[i]['mean'],
                   'jul_mean_ghi':jul_mean[i]['mean'],
                   'num_solar_pannels':np.nan}
    output_data = output_data.append(append_dict, ignore_index=True)

#==================== build joined table from zonal statistics result ========

output_data = output_data.groupby('zip_code', axis=0).mean().reset_index()
    
#==================== get solar panel counts =================================

original_solar_panels = gpd.read_file(solar_panels_path)

if get_projection(solar_panels_path) != jan_prj:
    solar_panels = original_solar_panels.to_crs("EPSG:{}".format(jan_prj))
    solar_panels.to_file(intermediate_data_folder+'\\'+solar_panels_path.split('\\')[-1])
    solar_panels_path = intermediate_data_folder+'\\'+solar_panels_path.split('\\')[-1]
else:
    solar_panels = original_solar_panels

#==================== perform spatial join of solar panels and zip codes =====

panels_poly = gpd.sjoin(solar_panels, zip_codes, how="left", op='intersects')

#==================== create dummy field so we can get the sum of panels =====

panels_poly['num_panels'] = 1

panels_poly = pd.DataFrame(panels_poly[['POSTCODE', 'num_panels']])

#==================== get sum of panels for each zip code polygon ============

panels_poly = panels_poly.groupby('POSTCODE', axis=0).sum().reset_index()

#==================== create output dataset ==================================
''' The group by functions have removed the spatial data from the dataframe.
Thus, we need to perform another join by postal code with the geodataframe that
contains the geometry'''

output_data = output_data.merge(
    panels_poly, right_on='POSTCODE', left_on='zip_code', how='left'
    )

output_data.astype({'zip_code': 'str'}).dtypes

#==================== clean up output data ===================================

output_data['jul_jan_ghi_diff'] = output_data['jul_mean_ghi'] - output_data['jan_mean_ghi']
output_data['num_solar_panels'] = output_data['num_panels'].fillna(0)

output_data = output_data[['zip_code', 'num_solar_panels', 'jul_jan_ghi_diff']]

output_data.to_csv(output_path+'\\'+'zip_stats.csv')