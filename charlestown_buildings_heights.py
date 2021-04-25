# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 09:58:00 2021

@author: bimew
"""


from rasterstats import zonal_stats
import geopandas as gpd
import pandas as pd
import os, sys

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    if os.getcwd().split('\\')[-1] != 'geospatial_exercise':
        print('unable to change working directory')
        print('please manually change wd to folder')
        print('/geospatial_exercise')
        sys.exit()

from bg_geo_tools.bg_geo_tools import get_projection


output_dir = 'outputs'
intermediate_data_dir = 'intermediate_data'
original_data_dir = 'original_data'

buildings_path = original_data_dir+'/'+'charlestown_buildings.geojson'
dsm_path = output_dir+'/'+'charleston.tif'


#==================== get input layer projections ============================

buildings = gpd.read_file(buildings_path)
buildings_proj = buildings.crs
dsm_proj = get_projection(dsm_path)

#==================== reproject buildings layer if necessary =================

if str(buildings_proj).split(':')[1] != dsm_proj:
    buildings = buildings.to_crs(
        'EPSG:{dsm_proj}'.format(
            dsm_proj=dsm_proj
            )
                ).to_file(
                    intermediate_data_dir+'/'+'charlestown_buildings.shp'
                        )       
            
    buildings_dir = intermediate_data_dir+'/'+'charlestown_buildings.shp'
    
buildings = gpd.read_file(buildings_dir)

#==================== get the maximum dsm height for each building ===========
''' It may be more appropriate to select the 90th percentile height from the 
dsm to remove the possible impact of communication towers or steeples 
on a buildings' height. This can be achieved here or when creating the dsm. 
Here that would mean replacing 'max' with 'percentile_90' below '''

max_height = zonal_stats(buildings,
                    dsm_path, copy_properties=True,
                    stats='max', all_touched=True)

#==================== build output csv dataframe =============================

building_heights = pd.DataFrame(columns=['building_id', 'height'])

for i in range(len(max_height)):
    building_num = buildings.iloc[i,0]
    height = max_height[i]['max']
    
    building_heights = building_heights.append(
        {'building_id':building_num, 'height':height},
        ignore_index=True
        )

building_heights.to_csv(output_dir+'/'+'charlestown_buildings_heights.csv')

#==================== merge output csv with building footprints and export ===
''' The instructions didn't request a shapefile of building heights but it 
could be useful'''

building_heights = buildings.merge(
    building_heights, 
    left_on='id', 
    right_on='building_id'
    )

building_heights.to_file(output_dir+'/'+'charlestown_buildings_heights.geojson',
                         driver='GeoJSON')