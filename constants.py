# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 12:16:57 2018

@author: to101130
"""
from collections import defaultdict
import schema
import re
import os
# Root folder for input data
ROOT_SOURCE_FOLDER='./data/'
# Root destination folder for CSV and .db 
ROOT_OUTPUT_FOLDER='./map_Roseraie_Toulouse_FR/'

try:
    os.mkdir(ROOT_OUTPUT_FOLDER)
except Exception as e: pass

# OSM FILE to be processed
OSMFILE = ROOT_SOURCE_FOLDER+"map_Roseraie_Toulouse_FR"
# OSMFILE = ROOT_SOURCE_FOLDER+"map_Toulouse_FR"

# SQL db 
SQL_SCHEMA = ROOT_SOURCE_FOLDER+'data_wrangling_schema.sql'
SQLFILE = ROOT_OUTPUT_FOLDER+OSMFILE.split('/')[-1]+".db"

'''
        CONSTANTS used by audit.py only
'''
EXPECTED_TAG_KEYS_NOT_ROAD = {'building','bus','leisure','electrified',
                              'amenity','railway','bicycle','landuse','indoor',
                              'natural','waterway','barrier','service','aerialway',
                              'tourism','golf','aeroway','area','surface','shop',
                              'operator','office','disused:aeroway',
                              'leaf_type','military','cycleway','access',
                              'incline','cycleway:left',
                              'public_transport'}

EXCLUDE_HIGHWAYS = {'unclassified','construction'}



#### CONSTANTS used by both audit.py and data.py  to clean the database 
# <tag k="addr:*"> renaming

# List of all tokens coresponding to a street/road for Toulouse/FR (built during audit)
EXPECTED_ROAD_TOKENS ={'Rue','Route','Autoroute','Avenue','Impasse','Chemin',
                       'Place','Rond-Point','Boulevard','Allée','Allées',
                       'Quai','Promenade','Pont','Passage','Cheminement',
                       'Esplanade','Voie','Square','Port','Passerelle','Clos',
                       'Mail','Rampe','Ponts','Cours','Côte','Descente','Caminot',
                       'Petite','Petit','Grande','Vieux','Périphérique'}

# Sub keys to considered during addr:* checks & rename
# e.g <TAG k='addr:*' where * is in this list
SET_ADDR_SUBFIELD = set(['housenumber','street','city','postcode','country'])

# List of cities <= addr:city
EXPECTED_CITY_LIST = ['Toulouse',
                      'Blagnac',
                      'Aucamville',
                      'Balma',
                      'Colomiers',
                      'Cugnaux',
                      "L'Union",
                      'Ramonville Saint-Agne',
                      'Saint-Jean',
                      'Tournefeuille']

# Expected regular expressions for adr:* 
RE_ADDR=defaultdict()
RE_ADDR['housenumber'] = re.compile(r'([0-9]+)([A-Z]*)$')
RE_ADDR['street'] = re.compile('^'+'|^'.join(EXPECTED_ROAD_TOKENS))
RE_ADDR['postcode'] = re.compile(r'([0-9]{5})$')
RE_ADDR['city'] = re.compile('|'.join(EXPECTED_CITY_LIST))
RE_ADDR['country'] = re.compile(r'FR')

# String mapping for addr:* renaming (built during audit)
STRING_MAP_ADDR=defaultdict()
STRING_MAP_ADDR['housenumber'] = [[' ',''],['QUARTER','Q'],['BIS','B'],['TER','T']]
STRING_MAP_ADDR['street'] = [['ALLEE','Allée'],['Bd','Boulevard']]
STRING_MAP_ADDR['postcode'] = [['3140','31400']]
STRING_MAP_ADDR['city'] = []
STRING_MAP_ADDR['country'] = []


#### data.py constants
NODES_PATH = ROOT_OUTPUT_FOLDER+"nodes.csv"
NODE_TAGS_PATH = ROOT_OUTPUT_FOLDER+"nodes_tags.csv"
WAYS_PATH = ROOT_OUTPUT_FOLDER+"ways.csv"
WAY_NODES_PATH = ROOT_OUTPUT_FOLDER+"ways_nodes.csv"
WAY_TAGS_PATH = ROOT_OUTPUT_FOLDER+"ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z|_]+)+:([a-z|_:]+)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


#### SQL db creation

csv_2_table = [[NODES_PATH,'nodes'],[NODE_TAGS_PATH,'nodes_tags'],[WAYS_PATH,'ways']
              ,[WAY_NODES_PATH,'ways_nodes'],[WAY_TAGS_PATH,'ways_tags']]