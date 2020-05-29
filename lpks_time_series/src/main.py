# -*- coding: utf-8 -*-
"""
Code to export time series of ndvi, rainfall, and land cover for Trends.Earth 
integration with LandPKS as part of the Tools4LDN Project (https://www.tools4ldn.org/)
GEE code by Mariano Gonzalez-Roglich (mgonzalez-roglich@conservation.org) 
Python code by Gabriel Antunes Daldegan(gdaldegan@conservation.org)
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

from landdegradation.download import download
from landdegradation.util import get_region

def plotting_time_series(dataset, aoi, year_start, year_end):
    # datasets
    lcov = ee.Image(lcover).select(ee.List.sequence(yr_start-1992,26,1))
    ndvi = ee.Image(vegindex).select(ee.List.sequence(yr_start-2001,yr_end-2001,1))
    prec = ee.Image(precip).select(ee.List.sequence(yr_start-1981,yr_end-1981,1))
    
    #coordinates of the point
    aoi = get_region(aoi)
    
def run(params, logger):
    """."""
    logger.debug("Loading parameters.")
    dataset = params.get('asset')
    name = params.get('name')
    year_start = None
    year_end = None
    aoi = None
    geojsons = json.loads(params.get('geojsons'))
    precip = "users/geflanddegradation/toolbox_datasets/lcov_esacc_1992_2018"
    vegindex = "users/geflanddegradation/toolbox_datasets/ndvi_modis_2001_2019"
    lcover = "users/geflanddegradation/toolbox_datasets/prec_chirps_1981_2019"
    
    # Check the ENV. Are we running this locally or in prod?
    if params.get('ENV') == 'dev':
        EXECUTION_ID = str(random.randint(1000000, 99999999))
    else:
        EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")
    out = plotting_time_series(dataset, aoi, year_start, year_end)
    return out.export(geojsons, 'LandPKS Time Series', dataset, logger)
    
    