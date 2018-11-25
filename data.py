#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Code adapted from L013

"""

import csv
import codecs
import pprint
import xml.etree.cElementTree as ET
import os
import cerberus

from constants import *


''' 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    BEGIN - CODE addition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

'''
     Function rename_tag_addr_value <TAG k=addr:* v= (e.g values of TAG keys addr:*)
    
'''
from audit import is_addr,rename_tag_addr_value

''' 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    END - CODE addition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


''' 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    BEGIN - CODE modified
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Below code is tuned from L013_Case study_OpenStreetMap Data
- Main change is addr:* values reformatting based on function 'rename_tag_addr_value'
'''

# function re-used from L013
# 1:2:3 => [2:3,1] (key/type)
# 1:2 => [2:1]
# 1 => 1,regular
def get_key_and_type(k):
  if PROBLEMCHARS.match(k) == None:
      colon_match = LOWER_COLON.match(k)
      if colon_match:
          return [colon_match.group(2),colon_match.group(1)]
      else:
          return[k,'regular']
  else:
      return []

# Main XML parsing to CSV function
# element = current XML node
def shape_element(element):

    # reset all outputs
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    tag_attribs = {}
    
    # save node Id
    id = element.attrib['id']
    
    # process all children <TAG>
    for tag in element.findall('tag'):
        
       k=tag.attrib['k']
       v=tag.attrib['v']
       key_and_type=get_key_and_type(k)
       
       # if TAG/@k doesn't contains any PROBLEMCHARS (see get_key_and_type)
       # fill in the dictionnary
       if key_and_type:
           
           tag_attribs = {}
           tag_attribs['id']=id
           tag_attribs['key']=key_and_type[0]
           tag_attribs['type']=key_and_type[1]
           
           
           # if TAG/@k=addr:*
           if is_addr(k):
               values=rename_tag_addr_value(tag_attribs['key'],v)
           # else for any other @k
           else:
               values=[v]  
               
           for v in values:
               tag_attribs['value']=v    
               tags.append(tag_attribs)           
                  
    
    if element.tag == 'node':
        for node_field in NODE_FIELDS:
           node_attribs[node_field]=element.attrib[node_field]
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for way_field in WAY_FIELDS:
            way_attribs[way_field]=element.attrib[way_field]
        position=0
        for nd in element.findall('nd'):
            nd_attribs={}
            nd_attribs['id']=id
            nd_attribs['node_id']=nd.attrib['ref']
            nd_attribs['position']=position
            position+=1
            way_nodes.append(nd_attribs)
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

''' 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    END - CODE modified
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        for field, errors in validator.errors.items():
            message_string = "\nElement of type '{0}' has the following errors:\n{1}"
            error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v if isinstance(v, str) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    # open fid to all CSV output files
    with codecs.open(NODES_PATH, 'w',encoding='utf-8') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w',encoding='utf-8') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w',encoding='utf-8') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w',encoding='utf-8') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w',encoding='utf-8') as way_tags_file:

        # write headers
        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        # construct validator
        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSMFILE, validate=False)
