import sqlite3
import os
import pandas as pd

from constants import *

try:
    os.remove(SQLFILE)
except:
    print(SQLFILE+' not found')

conn = sqlite3.connect(SQLFILE)
c = conn.cursor()
 
# create SQL TABLEs based on schema

# read schema per instruction
with open(SQL_SCHEMA, 'r') as fid:
   line = fid.readline()
   buffer = line
   while line:
       line = fid.readline()
       buffer = buffer+line
       # end of nstruction detected
       if line.find(';')>=0:
           print(buffer)
           # execute instruction
           c.execute(buffer)
           # reset buffer
           buffer=''

for csv_file,table in csv_2_table:
    #https://stackoverflow.com/questions/41900593/csv-into-sqlite-table-python
    # load data
    df = pd.read_csv(csv_file)
    print('Importing ',csv_file,' to ',SQLFILE)
    #https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_sql.html
    df.to_sql(table, conn, schema=table,if_exists='append',index=False)    
    
        
conn.commit()
conn.close()

    
    
