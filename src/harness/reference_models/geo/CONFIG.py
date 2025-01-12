#    Copyright 2017 SAS Project Authors. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Provide directory location for geographical database.

If not using the standard data location, simply modify this file to
specify your local directories.
"""

import os

from dotenv import load_dotenv

load_dotenv()

TERRAIN_DIR_ENV = os.getenv('TERRAIN_DIR')
LANDCOVER_DIR_ENV = os.getenv('LANDCOVER_DIR')

# Base data directory
_BASE_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '..', '..', '..', '..', 'data'))
ITU_DIR = os.path.join(_BASE_DATA_DIR, 'itu')
COUNTY_DIR = os.path.join(_BASE_DATA_DIR, 'county')
TERRAIN_DIR = os.path.join(_BASE_DATA_DIR, 'geo', 'ned')
LANDCOVER_DIR = os.path.join(_BASE_DATA_DIR, 'geo', 'nlcd')
NTIA_DIR = os.path.join(_BASE_DATA_DIR, 'ntia')
FCC_DIR = os.path.join(_BASE_DATA_DIR, 'fcc')

# If not using the standard location for the data files,
# define the absolute path of your data directories
#ITU_DIR =
TERRAIN_DIR = TERRAIN_DIR_ENV or TERRAIN_DIR
LANDCOVER_DIR = LANDCOVER_DIR_ENV or LANDCOVER_DIR
#COUNTY_DIR
#NTIA_DIR=

def GetItuDir():
  return ITU_DIR

def GetTerrainDir():
  return TERRAIN_DIR

def GetLandCoverDir():
  return LANDCOVER_DIR

def GetCountyDir():
  return COUNTY_DIR

def GetNtiaDir():
  return NTIA_DIR

def GetFccDir():
  return FCC_DIR
