
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import pandas as pd
from constants import *
                              
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit_way_tag_k_name(osmfile,option='list_keys'):
    
    if option=='list_keys':
       unidentified_road_types = defaultdict(lambda:set())        
    elif option=='total_keys':
       unidentified_road_types = defaultdict(int)
   
    for event, elem in ET.iterparse(osmfile, events=("start",)):
        
        if elem.tag == "way":
        
            has_name = False
            is_road = True
            is_public_highway =False
            all_tag_keys = set()
                  
            for tag in elem.iter("tag"):
                 key = tag.attrib['k']
                 value = tag.attrib['v']
                 
                 if key=='name':
                     name=value
                     has_name = True
                 
                 all_tag_keys.add('k='+key+' v='+value)
                     
                 if key in EXPECTED_TAG_KEYS_NOT_ROAD:
                     is_road = False                    
                 if (key=='highway') & (not(value in EXCLUDE_HIGHWAYS)):
                    is_public_highway=True
                    
                 
            if has_name & is_road & is_public_highway:
                   road_type=name.split()[0]
                   if not(name.split()[0] in  EXPECTED_ROAD_TOKENS):
                       if option=='list_keys':
                           unidentified_road_types[road_type]=unidentified_road_types[road_type].union(all_tag_keys)
                       elif option=='total_keys':
                           unidentified_road_types[road_type] += 1
                       
        
    return unidentified_road_types
    #osm_file.close()
    
'''
     Utilities functions
'''

# function returns true if v is 'n-p' and values [n,p]
# function used to test if addr:housenumber is defined as range
def is_range(v,values):
    try:
        b=(int(values[1])-int(values[0]))>0
    except:
        b=False
    return (v.find('-')>0)&(len(values)==2)&b


# function returns true if v is 'n-p' and values [n,p]
# function used to test if addr:housenumber is defined as range
def is_range(v,values):
    try:
        b=(int(values[1])-int(values[0]))>0
    except:
        b=False
    return (v.find('-')>0)&(len(values)==2)&b

# function returns true is TAG/@k is addr:* where * in SET_ADDR_SUBFIELD
def is_addr(k):
     tokens = k.split(':')
     if (tokens[0]=='addr'):
         if (tokens[1] in SET_ADDR_SUBFIELD):
             return True
     return False
 
# function returns subfield (token after first ':')     
def get_addr_subfield(k):
    return k.split(':')[1]

# function splits 'txt' according to a set of separators 'seps'
# https://stackoverflow.com/questions/4697006/python-split-string-by-list-of-separators
def split(txt, seps):
    default_sep = seps[0]
    # we skip seps[0] because that's the default seperator
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

# function string map as per TCL one https://www.tcl.tk/man/tcl8.4/TclCmd/string.htm#M33
def string_map(txt,mapping):
    for from_str,to_str in mapping:
        txt=txt.replace(from_str,to_str)
    return txt


'''
     Function rename_tag_addr_value <TAG k=addr:* v= (e.g values of TAG keys addr:*)
    
'''
def rename_tag_addr_value(k,v):

    r_values=[]

    # mapping is in CAPS for housenumber (bis,ter,...)
    if k=='housenumber':
        v=v.upper()
    # string map does most of the job        
    v=string_map(v,STRING_MAP_ADDR[k])   
        
    # split 'v' into a list 
    values = split(v,[';','-',','])
    
    # Consider particular case of range e.g 'n-p' (mainly for 'addr:housenumber')
    # if v,value defines a range
    if is_range(v,values):
        # convert 'values' str list to int list
        values = [int(e) for e in values]
        # sort
        values=sorted(values)
        # build whole range
        values=range(int(values[0]),int(values[1])+1)
        # re-convert to str
        values = [str(e) for e in values]
    
        
    # for each value (for most cases there will only be one ...)
    for v in values:
        if k=='housenumber':  
            # nothing more requried
            pass
        elif k=='postcode':
            # keep only 5 first digits
            RE_POST_CODE=re.compile(r'([0-9]{5}).*$')
            match=RE_POST_CODE.match(v)
            if match!=None:
                v=match.group(1)
        elif (k=='city'):
            # upper first char & lower all following
            v=v[0].upper()+v[1:].lower()
        elif (k=='street'):
            # upper first char & lower all following of first teken only
            first_token=v.split()[0]
            v=first_token[0].upper()+first_token[1:].lower()+v[len(first_token):]
        elif k=='country':
            # nothing requried (as per audit)
            pass
        else:
            # can't get there
            print('Why did you call this function with such a'+k+' key?')
            pass
        
        # return only if update names matches corresponsing regular expression
        if RE_ADDR[k].match(v):
                r_values.append(v)
            
    return r_values


def audit_addr(osmfile,option='list_keys'):
  
    addr_types = pd.DataFrame()
    i = 0
    for event, elem in ET.iterparse(osmfile, events=("start",)):   
        
        if elem.tag == "tag":
            key = elem.attrib['k']
            if is_addr(key):
                value = elem.attrib['v']
                subfield=get_addr_subfield(key)
                if subfield=='street':
                    # get first token only
                    #value = value.split(' ')[0]
                    pass
                
                # if subfield value doesn't match RE expression log it
                if not(RE_ADDR[subfield].match(value)):
                    new_value=rename_tag_addr_value(subfield,value)
                            
                    addr_types.loc[i,'type']=subfield
                    addr_types.loc[i,'value']=value
                    addr_types.loc[i,'new']=str(new_value)
                    
                    i +=1
                    
    return addr_types

def audit_tag_k_v(osmfile,parent_re='.*',k_re='name',record='k'):
    k_re=re.compile(k_re)
    parent_re=re.compile(parent_re)
    tag_k_v = defaultdict(int)
    for event, elem in ET.iterparse(osmfile, events=("start",)):   
        if (parent_re.match(elem.tag)):
            for el in elem.findall('tag'):
                if (k_re.match(el.attrib['k'])):
                    tag_k_v[el.attrib[record]]  += 1    
        
    return (pd.DataFrame(tag_k_v,index=['n']).transpose()).sort_values(by='n',ascending=False)
  
if False:
    #audit_result = audit_tag_k_v(OSMFILE,parent_re='way',k_re='name|addr:')
    audit_result = audit_addr(OSMFILE)
    #audit_result=audit_way_tag_k_name(OSMFILE)
    
    i=0
    for row in range(0,len(audit_result)):
         pprint.pprint(audit_result.iloc[i])
         i+=1
    

