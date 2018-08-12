"""
Goal: To build a basic economic model for the US Economy in order to roughly predict 
a downturn. Prob(downturn in 3 months). 

Steps: 
Gather quality data in time-series
Train/Test model
Automate from the outset so model can ingest new data and re-run daily
Alert if target probability exceeds alert threshold

Data sources:
FRED API (st louis federal reserve)
"""

import json, sqlite3, os, pandas, fredapi
from fredapikey import apikey

verbose = 1
dir_path = os.path.dirname(os.path.realpath(__file__))
dbpathname = '/stego.db'

def echo(msg, verbosity=verbose):
    if verbosity == 1:
        print msg 
    else:
        return None

def dbprocess(path):
    try:
        echo(msg='Loading DB...',verbosity=1)
        con = sqlite3.connect(str(path)+dbpathname) #connect to existing or create new if does not exist
        cur = con.cursor()
        cur.execute('CREATE TABLE daily_trades([index] bigint, asset varchar(5), exchange varchar(100), time_start datetime, time_end datetime, trades_count bigint, volume_traded decimal(20,10), price_open decimal(20,10), price_high decimal(20,10), price_low decimal(20,10), price_close decimal(20,10))')
        #cur.execute('CREATE INDEX IDX_time ON daily_trades (time_start, time_end)')
        con.commit()
    except sqlite3.Error, e:
    	echo(msg="Error {}:".format(e.args[0]),verbosity=1)
        sys.exit(1)
    finally:
        if con:
            con.close()

#Create or Connect to existing Sqlite DB
if not os.path.isfile(str(dir_path)+dbpathname):
    con=dbprocess(path=dir_path)

con = sqlite3.connect(str(dir_path)+dbpathname) #connect to existing sqlite db
cur = con.cursor()