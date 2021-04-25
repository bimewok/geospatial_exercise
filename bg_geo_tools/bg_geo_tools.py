# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 09:11:58 2021
 
@author: bimew
"""
 
def get_projection(path):
    from osgeo import gdal, osr
    import re
    import geopandas as gpd
    try:
        layer = gdal.Open(path)
        prj = layer.GetProjection()#.split('[')[-1]
        epsg = re.findall(r'\d+', prj)[0]
        #layer = None 
        prj = osr.SpatialReference(wkt=layer.GetProjection())
        prj = prj.GetAttrValue('AUTHORITY',1)
        layer = None 
    except:
        layer = gpd.read_file(path)
        prj = str(layer.crs)
        layer = None
    return prj

def multi_poly_to_single_poly(gpdf):
    import geopandas as gpd
    import pandas as pd
    
    gpdf_singlepoly = gpdf[gpdf.geometry.type == 'Polygon']
    gpdf_multipoly = gpdf[gpdf.geometry.type == 'MultiPolygon']

    for i, row in gpdf_multipoly.iterrows():
        Series_geometries = pd.Series(row.geometry)
        df = pd.DataFrame()
        #df['geometry']  = Series_geometries
        
        df = pd.concat(
            [gpd.GeoDataFrame(
                    row, crs=gpdf_multipoly.crs
                    ).T]*len(Series_geometries), 
                ignore_index=True
            )
        
        gpdf_singlepoly = pd.concat([gpdf_singlepoly, df])

    gpdf_singlepoly.reset_index(inplace=True, drop=True)
    return gpdf_singlepoly


def raster_to_poly(raster_path, shp_out_path, layer_name, field_name):
    from osgeo import gdal, ogr, osr
    
    raster = gdal.Open(raster_path)
    band = raster.GetRasterBand(1)
    driver = ogr.GetDriverByName('ESRI Shapefile')        
    poly = driver.CreateDataSource(shp_out_path)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(raster.GetProjectionRef())

    out_layer = poly.CreateLayer(layer_name, srs)        
    new_field = ogr.FieldDefn(field_name, ogr.OFTReal)
    
    out_layer.CreateField(new_field)        
    gdal.FPolygonize(band, band, out_layer, 0, [], callback=None)        
    poly.Destroy()
    source_raster = None