"""
Goal: To build a basic economic model for the US Economy in order to roughly predict 
a downturn. Prob(downturn in 3 months). 

Steps: 
Gather quality data in time-series
Train/Test model
Automate from the outset so model can ingest new data and re-run daily
Alert if target probability exceeds alert threshold

Data sources:
FRED Data (st louis federal reserve) - https://fred.stlouisfed.org/
FRED API - https://github.com/mortada/fredapi
List of other datasets: https://www.aeaweb.org/rfe/showCat.php?cat_id=3

Indicators we care about:
Private Debt, Household Debt vs. GDP
Personal Income
Unemployment Rate
Interest rates
Monetary Supply
CPI
GDP
Public Debt
Credit in the economy
VIX index
Total US Population
YieldCurve/Treasury spreads (2-10yr bonds)
S&P500 - Measure of total us stock market prices(target)
Charge Off Rates - FED published for top banks, other source as well
"""

"""
Paul Comments: 
There is some work on this already (check Philly Fed and St louis Fed working papers).  I looked at these recently, highlighted the most important in red. I personally feel it is in the following order:
1.	10-2 yr spread (60%)
2.	S&P500 vs recent(last 12 or 24mo) peak/high (20%)    
3.	Change in Housing permits (10%)
4.	Change in Manufacturing Orders (5%)
5.	Consumer Sentiment (5%)

•	Manufacturing survey….leading indicator. Given lead times to build, this is historically a leading indicator. It was more pronounce when we were more of a manufacturing based society with less global influence but still predictive.
•	Housing Permits….. leading indicator given lead time to build. Also note interest rate increases slow consumer demand and construction companies know this. Somewhat correlated to yield curve.
•	Consumer sentiment….(mich survey) …leading indicator however I feel the S&P500 is a reliable gauge for this and more real time. The two series are highly correlated.

JPMorgan's proprietary model considers the levels of several economic indicators, including consumer sentiment, manufacturing sentiment, building permits, auto sales, and unemployment.
JPMorgan notes that nonfarm payrolls is actually not part of the model. But the unemployment rate is. Interestingly, a low unemployment rate can be considered an ominous sign.

“The unemployment rate enters the model in two ways," Edgerton explained. "As a near-term indicator, we watch for increases in the unemployment rate that occur near the beginning of recessions. So this morning's move down in the unemployment rate lowered the recession probability in our near-term model. But we also find the level of the unemployment rate to be one of the most useful indicators of medium-term recession risk. So the move down in unemployment raises the model's view of the risk of economic overheating in the medium run and raises the 'background risk' of recession."

Indeed, recessions begin when things are very good. It's only when reports come in that the data has turned that we realize we've been in a recession.
https://finance.yahoo.com/news/jpmorgan-recession-risk-new-high-160251309.html

Best investments in case of an inverted yield curve
https://www.wsj.com/articles/the-best-investments-in-case-of-an-inverted-yield-curve-1536545041?emailToken=e7d3ad6442c26d159eb5bc7903c7f80603yQYaTVNumvrlRPOpnMOdMNGYlKz9R0nF7hBawD18PIgfIs2FyveE1L1m8yYL2DkzsrmGL+Gt0ehEfETb7Q1TP6do5LV1+ScyBBPIcgjOqLKKtUfjtFBaeAgRiUo7m2&reflink=article_email_share

Guggenheim Models:
https://www.guggenheiminvestments.com/perspectives/macroeconomic-research/forecasting-the-next-recession
https://www.guggenheiminvestments.com/perspectives/macroeconomic-research/updating-our-outlook-for-recession-timing

"""

import json, sqlite3, os, pandas
from fredapikey import apikey
from fredapi import Fred

verbose = 1
dir_path = os.path.dirname(os.path.realpath(__file__))
dbpathname = '/stego.db'
fred = Fred(api_key=apikey)

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

data = fred.get_series('SP500')
print data.tail()