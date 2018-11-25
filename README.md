# UdaCity 'Wrangle OpenStreetMap Data' project applied to Toulouse,FR
To generate SQL database, you need to execute:
- data.py
- create_sql_db.py

Report and SQL queries are gathered in report.ipynb (.html version is also available)

## constants.py
This file contains all constants of the project. Only following three ones should be modified:
- `ROOT_SOURCE_FOLDER`: location of inputs data files (OSM + SQL schema)
- `OSMFILE`: name of OSM in ROOT_SOURCE_FOLDER: 
- `ROOT_OUTPUT_FOLDER`: destination folder for generated files: CSV files + SQL .db

SQL databse FILE is generated in `ROOT_OUTPUT_FOLDER` and named `<OSMFILE>.db` based on `SQL_SCHEMA`  and list of CSV files:

```python
NODES_PATH = ROOT_OUTPUT_FOLDER+"nodes.csv"
NODE_TAGS_PATH = ROOT_OUTPUT_FOLDER+"nodes_tags.csv"
WAYS_PATH = ROOT_OUTPUT_FOLDER+"ways.csv"
WAY_NODES_PATH = ROOT_OUTPUT_FOLDER+"ways_nodes.csv"
WAY_TAGS_PATH = ROOT_OUTPUT_FOLDER+"ways_tags.csv"
```

## audit.py
Functions used to audit OSM file.
Cleaning / Renaming fucntions are defined in this file.

## data.py
Functions used to process OSM into CSV files. These functions use cleaning & renaming function defined in audit.py. Optionally, intermediate dictionnaries can be cross-checked versus schema.py before CSV export.

## schema.py
Scheam used by data.py to check dictionnaries versus schema before generating CSV files

## create_sql_db.py
This script generates SQL database based on SQL_SCHEMA and list of CSV files defined in constants.py

## Report.ipynb: 
Jupyter script containing the main report of the project and gathering all SQL queries. This script doesn't generate any file. To generate SQL database, you need to execute `data.py` and `create_sql_db.py` first. This report is consistent with the full database (e.g whole Toulouse OSM file) but the script can be executed into a reduced one. 

## Report.html
Html version of Juputer script execution.



