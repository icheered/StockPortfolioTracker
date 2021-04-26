from datetime import datetime
import requests
import pandas as pd

url = "https://query2.finance.yahoo.com/v1/finance/search"
params = {'q': 'US0079031078', 'quotesCount': 1, 'newsCount': 0}

r = requests.get(url, params=params)
data = r.json()
symbol = data['quotes'][0]['symbol']
print(symbol)


import yfinance as yf

start_date = '2020-11-04'
end_date = datetime.now().strftime("%Y-%m-%d")
yfsymbol = yf.Ticker(symbol)
data = yfsymbol.history(start=start_date, end=end_date)
data = (data["High"] + data["Low"]) / 2
data = data.astype(float).interpolate()
data = data.fillna(method="backfill")

for index, value in data.items():
    print(index.strftime('%Y-%m-%d'))




# print(type(d))
# print(d)

# for date, value in d:
#     print(f"Date: {date}, Value: {value}")


# data = yf.download(tickerlist, start_date, end_date, time_interval='daily')
#print(data)
# for ticker in tickerlist:
#     
# data.drop(["High", "Low", "Adj Close", "Close", "Open", "Volume"], axis=1, inplace=True)
# data = data.astype(float).interpolate()
# data = data.fillna(method="backfill")
# data.columns = tickerlist
# print(data)