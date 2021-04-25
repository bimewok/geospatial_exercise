# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 14:07:12 2021

@author: bimew
"""

import pylas
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon
import os
import time
from bg_geo_tools.bg_geo_tools import *

os.chdir(os.path.dirname(os.path.realpath('__file__')))

start_time = time.time()


output_dir = 'outputs'
intermediate_data_dir = 'intermediate_data'
lidar_path = 'original_data\charlestown.laz'