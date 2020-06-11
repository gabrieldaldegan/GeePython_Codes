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

import os, sys
from PIL import Image

%matplotlib inline

from IPython.display import Image

import ee

# The service account email address authorized by your Google contact.
# Set up a service account as described in the README.
EE_ACCOUNT = 'gef-ldmp-server@gef-ld-toolbox.iam.gserviceaccount.com'

# The private key associated with your service account in JSON format.
EE_PRIVATE_KEY_FILE = 'D:/Gabriel/CI/TrendsEarth/Git/GeePython_Codes/te_key.json'

EE_CREDENTIALS = ee.ServiceAccountCredentials(EE_ACCOUNT, EE_PRIVATE_KEY_FILE)
#ee.Initialize(EE_CREDENTIALS)
ee.Initialize()

"""
// Code to export static images at different zoom levels for Trends.Earth integration
// with LandPKS as part of the Tools4LDN project (https://www.tools4ldn.org/)
// by Mariano Gonzalez-Roglich (mgonzalez-roglich@conservation.org)
// Date: 03/19/2020
"""
box_side = 10000 ## box side in meters

## LandPKS will provide Trends.Earth with the coordinate indicating the location of the plot
#coordinates of the point
##aoi = get_region(aoi)
point = ee.Geometry.Point([-66.8571, -8.7864])

oli_sr_coll = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')##.filterBounds(point.buffer(1000))

## print(oli_sr_coll)

def maskL8sr(image):
  ## Bits 3 and 5 are cloud shadow and cloud, respectively.
    cloudShadowBitMask = (1 << 3)
    cloudsBitMask = (1 << 5)
  ## Get the pixel QA band.
    qa = image.select('pixel_qa')
  ## Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
    return image.updateMask(mask)

def ndvi(image):
    return image.normalizedDifference(['B5', 'B4']).rename('NDVI')

ndvi_14 = oli_sr_coll.filterDate('2014-01-01', '2014-12-31').map(maskL8sr).map(ndvi).mean().addBands(ee.Image(2014).float()).rename(['ndvi','year'])
ndvi_15 = oli_sr_coll.filterDate('2015-01-01', '2015-12-31').map(maskL8sr).map(ndvi).mean().addBands(ee.Image(2015).float()).rename(['ndvi','year'])
ndvi_16 = oli_sr_coll.filterDate('2016-01-01', '2016-12-31').map(maskL8sr).map(ndvi).mean().addBands(ee.Image(2016).float()).rename(['ndvi','year'])
ndvi_17 = oli_sr_coll.filterDate('2017-01-01', '2017-12-31').map(maskL8sr).map(ndvi).mean().addBands(ee.Image(2017).float()).rename(['ndvi','year'])
ndvi_18 = oli_sr_coll.filterDate('2018-01-01', '2018-12-31').map(maskL8sr).map(ndvi).mean().addBands(ee.Image(2018).float()).rename(['ndvi','year'])
ndvi_19 = oli_sr_coll.filterDate('2019-01-01', '2019-12-31').map(maskL8sr).map(ndvi).mean().addBands(ee.Image(2019).float()).rename(['ndvi','year'])
l8sr_19 = oli_sr_coll.filterDate('2019-01-01', '2019-12-31').map(maskL8sr).mean()

ndvi_coll = ee.ImageCollection([ndvi_14,ndvi_15,ndvi_16,ndvi_17,ndvi_18,ndvi_19])

## compute linear trend function to predict ndvi based on year (ndvi trend)
lf_trend = ndvi_coll.select(['year', 'ndvi']).reduce(ee.Reducer.linearFit())

ndvi_trnd = (lf_trend.select('scale').divide(ndvi_14.select("ndvi"))).multiply(100)


p_ndvi_mean = {'min': 0.3, 'max': 0.9, 'palette':['#ffffcc','#006600']}
p_ndvi_trnd = {'min': -10, 'max': 10, 'palette':['#00CC00','#D0D0D0',' #ff0000']}
p_l8sr = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.5,}

## Map.addLayer(ndvi_19.select("ndvi"),p_ndvi_mean,"ndvi_19")
## Map.addLayer(ndvi_trnd,p_ndvi_trnd,"ndvi_slope")

## three different zoom levels will be presented (1km, 10km, and 100km squared boxes around the point location)
box = point.buffer(box_side/2).bounds()
## box_modis = point.buffer(125).bounds()

## create vizualization for export
map_mean = map_mean = ndvi_19.select("ndvi").visualize(p_ndvi_mean)
map_trnd = map_trnd = ndvi_trnd.visualize(p_ndvi_trnd)
map_l8sr = map_l8sr = l8sr_19.visualize(p_l8sr)

## maps for export
map_mean = ee.ImageCollection.fromImages([map_mean, ee.Image().int().paint(point.buffer(box_side/50), 1).visualize({'palette': ['black'], 'opacity': 1})])
    
map_trnd = ee.ImageCollection.fromImages([map_trnd, ee.Image().int().paint(point.buffer(box_side/50), 1).visualize({'palette': ['black'], 'opacity': 1})])

map_l8sr = ee.ImageCollection.fromImages([map_l8sr, ee.Image().int().paint(point.buffer(box_side/100), 1).visualize({'palette': ['black'], 'opacity': 1})])

# preview image to be exported
image_ndvi_mean = map_mean.mosaic().visualize(p_ndvi_mean)

# generate url to image thumbnail
url = image_ndvi_mean.getThumbUrl({'region': box.getInfo(), 'dimensions': 256})

# display image
Image(url=url, embed=True, format='png')


taskToexport1 = ee.batch.Export.image.toCloudStorage({
  image: map_mean.mosaic(),
  description: 'ndvi_mean_box_'+box_side/1000+'km',
  bucket: 'tools4ldn',
  region: box,
  scale: box_side/250,
  dimensions: 40000})

taskToexport2 = ee.batch.Export.image.toCloudStorage({
  image: map_trnd.mosaic(),
  description: 'ndvi_trnd_box_'+box_side/1000+'km',
  bucket: 'tools4ldn',
  region: box,
  scale: box_side/250,
  dimensions: 40000})

taskToexport3 = ee.batch.Export.image.toCloudStorage({
  image: map_l8sr.mosaic(),
  description: 'l8sr_box_'+box_side/1000+'km',
  bucket: 'tools4ldn',
  region: box,
  scale: box_side/250,
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