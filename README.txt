To generate SQL database, you need to execute successively:
- data.py
- create_sql_db.py
- SQL queries are gathered into Jupyter report.ipynb

./data/: OSM source file and SQL schema

constants.py: this file contains all constants of the project
- ROOT_SOURCE_FOLDER: location of inputs data files (OSM + SQL schema)
- ROOT_OUTPUT_FOLDER: destiantion folder for generated files (CSV + .db)
- OSMFILE: name of OSM in ROOT_SOURCE_FOLDER: 

SQLFILE is generated in ROOT_OUTPUT_FOLDER and named OSMFILE.db based on SQL_SCHEMA and list of CSV files
NODES_PATH = ROOT_OUTPUT_FOLDER+"nodes.csv"
NODE_TAGS_PATH = ROOT_OUTPUT_FOLDER+"nodes_tags.csv"
WAYS_PATH = ROOT_OUTPUT_FOLDER+"ways.csv"
WAY_NODES_PATH = ROOT_OUTPUT_FOLDER+"ways_nodes.csv"
WAY_TAGS_PATH = ROOT_OUTPUT_FOLDER+"ways_tags.csv"


audit.py: functions used for auditing OSM file 

data.py: functions used to process OSM into CSV files. This file imports renaming function defined in audit.py. 
Optionally, schema.py can be checked.

schema.py: used by data.py to check dictionnaries versus schema before generating CSV files

create_sql_db.py: generate SQL db based on SQL_SCHEMA and list of CSV files defined in constants.py

Report.ipynb: Jupyter script containing the main report of the project and hathering all SQL queries. 
This script doesn't generate any file. To generate SQL database, you need to execute data.py/create_sql_db.py first. 
The report is consistent the full database (map_Toulouse_FR) but the script can be executed into a reduced one
To do so, constants are defined at the very beginign of the Jupyter script.

Report.html: hmtl version of Jupyter script



