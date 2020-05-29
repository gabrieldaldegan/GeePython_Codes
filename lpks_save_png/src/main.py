# -*- coding: utf-8 -*-
"""
Code to convert images from .geotiff (output from GEE) to .png (to be used by LandPKS)
https://pillow.readthedocs.io/en/stable/handbook/tutorial.html#reading-and-writing-images
Date: 05/11/2020
"""
# Copyright 2020 Conservation International

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from builtins import str
import random
import json

import ee

from landdegradation import GEEIOError
from landdegradation.download import download

import os, sys
from PIL import Image

#LandPKS will provide Trends.Earth with the coordinate indicating the location of the plot
point = ee.Geometry.Point([coord_point])

#three different zoom levels will be presented (1km, 10km, and 100km squared boxes around the point location)
### NEED TO REMOVE BUFFERS THAT WON'T BE USED ###
box_001km = point.buffer(500).bounds()
box_002km = point.buffer(1000).bounds()
box_003km = point.buffer(1500).bounds()
box_007km = point.buffer(3500).bounds()
box_008km = point.buffer(4000).bounds()


if (data == 'landsat'){
  ndvi = ee.ImageCollection("LANDSAT/LC8_L1T_32DAY_NDVI").first()

  # pallete for display
  palette_lp_slope = {min: 0.1, max: 0.5, palette: ['#AB2727',	'FFFFE0', '307031']}

  # create vizualization for export
  map_ndvi = ndvi.visualize(palette_lp_slope)}

if (data == 'modis'){

  # land productivity trajectory from MODIS as an example of the 250 m data
  lp_traj_slope = ee.Image("users/geflanddegradation/global_ld_analysis/r20180821_lp_traj_globe_2001_2015_modis").select('slope')

  # pallete for display
  palette_lp_slope = {min: -75, max: 75, palette: ['#AB2727',	'FFFFE0', '307031']}

  # create vizualization for export
  map_ndvi = lp_traj_slope.updateMask(lp_traj_slope.neq(-32768)).visualize(palette_lp_slope)}

# map_1km for export
map_001km = ee.ImageCollection.fromImages([
    map_ndvi,
    ee.Image().int().paint(point.buffer(20), 1).visualize({palette: ['black'], opacity: 1})])
 # map_2km for export   
map_002km = ee.ImageCollection.fromImages([
    map_ndvi,
    ee.Image().int().paint(point.buffer(40), 1).visualize({palette: ['black'], opacity: 1})])
 # map_3km for export   
map_003km = ee.ImageCollection.fromImages([
    map_ndvi,
    ee.Image().int().paint(point.buffer(60), 1).visualize({palette: ['black'], opacity: 1})])
# map_7km for export
map_007km = ee.ImageCollection.fromImages([
    map_ndvi,
    ee.Image().int().paint(point.buffer(140), 1).visualize({palette: ['black'], opacity: 1})])
# map_8km for export
map_008km = ee.ImageCollection.fromImages([
    map_ndvi,
    ee.Image().int().paint(point.buffer(160), 1).visualize({palette: ['black'], opacity: 1})])


Export.image.toCloudStorage({
   image: map_001km.mosaic(),
   description: data+'_ndvi_001km_image',
   bucket: 'tools4ldn',
   region: box_001km,
   scale: 4,
   dimensions: 40000})

Export.image.toCloudStorage({
   image: map_002km.mosaic(),
   description: data+'_ndvi_002km_image',
   bucket: 'tools4ldn',
   region: box_002km,
   scale: 8,
   dimensions: 40000})

Export.image.toCloudStorage({
   image: map_003km.mosaic(),
   description: data+'_ndvi_003km_image',
   bucket: 'tools4ldn',
   region: box_003km,
   scale: 12,
   dimensions: 40000})

Export.image.toCloudStorage({
   image: map_007km.mosaic(),
   description: data+'_ndvi_007km_image',
   bucket: 'tools4ldn',
   region: box_007km,
   scale: 24,
   dimensions: 40000})

Export.image.toCloudStorage({
   image: map_008km.mosaic(),
   description: data+'_ndvi_008km_image',
   bucket: 'tools4ldn',
   region: box_008km,
   scale: 32,
   dimensions: 40000})
   
def save_png(infile):  
    for infile in sys.argv[1:]:
    f, e = os.path.splitext(infile)
    outfile = f + ".png"
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                im.save(outfile)
        except OSError:
            print("cannot convert", infile)

def run(params, logger):
    """."""
    logger.debug("Loading parameters.")
    asset = params.get('asset')
    name = params.get('name')
    coord_point = None
    infile = None
    geojsons = json.loads(params.get('geojsons'))
    ndvi = ee.ImageCollection("LANDSAT/LC8_L1T_32DAY_NDVI").first()
    lp_traj_slope = ee.Image("users/geflanddegradation/global_ld_analysis/r20180821_lp_traj_globe_2001_2015_modis").select('slope')
    
    # Check the ENV. Are we running this locally or in prod?
    if params.get('ENV') == 'dev':
        EXECUTION_ID = str(random.randint(1000000, 99999999))
    else:
        EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")
    out = save_png(map_tiff)
    return out.export(geojsons, 'LandPKS Save PNG', logger, EXECUTION_ID)
