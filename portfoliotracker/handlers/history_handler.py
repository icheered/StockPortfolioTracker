"""
Handles getting/adding data to the historic database
"""
from datetime import timedelta, datetime, date
import requests

from rethinkdb import RethinkDB
import yfinance as yf

from portfoliotracker.utils import utils


class History_Handler:
    def __init__(self, config, logger, db_conn):
        self.config = config
        self.logger = logger
        self.r = RethinkDB()
        self.db_conn = db_conn
    
    async def get_history(self):
        """
        Return a list of items in the history table
        """
        ret_cursor = self.r.table(self.config["STOCKS_TABLE"]).\
            order_by('Date').run(self.db_conn)
        ret = list(ret_cursor)
        return ret
    
    async def delete_history(self):
        """
        Delete all history items
        """
        self.logger.info("Deleting History...")
        self.r.table(self.config["STOCKS_TABLE"]).delete().run(self.db_conn)
        return 1


    async def patch_dates(self):
        self.logger.info("Patching Dates...")
        # Check if date is known on which first stock is bought
        ret_cursor = self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["FIRSTBUY"]).\
            run(self.db_conn)
        ret = list(ret_cursor)
        if not ret:
            self.logger.error("Tried patching dates but FirstDate was not found")
            return
        
        firstdate = ret[0]['FIRSTBUY']        
        datelist = utils.get_date_list(startdate=firstdate)
        self.logger.trace(f"List of dates to patch: {datelist}")

        
        ret_cursor = self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["STOCKLIST"]).\
            run(self.db_conn)
        ret = list(ret_cursor)
        if not ret:
            self.logger.error("Tried patching dates but no stocks were found")
            return

        stocklist = {}
        for stock in ret[0]["STOCKLIST"]:
            stocklist[stock] = {
                "Amount": 0,
                "Spend": 0,
                "Price": 0,
                "Value": 0,
                "Gain": 0,
            }

        for date in datelist:
            ret = list(self.r.table(self.config["STOCKS_TABLE"]).\
                filter(self.r.row["Date"] == date).run(self.db_conn))
            if not ret:
                # Date does not exist, add a new date
                new_entry = {
                    "Date": date,           # Date
                    "Transactions": [],     # List of transactions done until now
                    "ExchangeRates": {},    # Foreign exchange rates
                    "Portfolio": stocklist, # Data for individual stocks
                    "Total": {
                        "Expenses": 0,      # Total money spend
                        "Value": 0,         # Total value of portfolio
                        "Gain": 0           # Difference between money spend and portfolio value
                    }
                } 
                ret_cursor = self.r.table(self.config["STOCKS_TABLE"]).\
                   insert(new_entry).run(self.db_conn)
                self.logger.trace(f"Ret_cursor: {ret_cursor}")
                continue
            else:
                # Maybe patch missing data but this shouldn't be neccesary
                continue

        return 1
    
    async def patch_stock_expend(self):
        """
        For each date, for each stock, insert amount owned and expenses till that point
        """
        self.logger.info("Calculating Expenses...")
        transactions = list(self.r.table(self.config["TRANSACTIONS_TABLE"]).run(self.db_conn))
        if not transactions:
            self.logger.error("Tried patching stock expend but no transactions were found")
            return
        
        for transaction in transactions:
            t_date = transaction["Datum"]
            t_isin = transaction["ISIN"]
            t_amount = transaction["Aantal"]
            t_expense = transaction["Totaal"]
            t_id = transaction["id"]

            # Get list of dates
                # Filter it to list where transaction has not been added yet
                    # Add transaction to date

            ret = list(self.r.\
                table(self.config["STOCKS_TABLE"]).\
                filter(self.r.row["Date"] >= t_date).\
                run(self.db_conn))
            if not ret:
                self.logger.warning("Received transaction that matches no date")
                continue

            for d in ret:
                if t_id not in d["Transactions"]:
                    d["Portfolio"][t_isin]["Amount"] += t_amount
                    d["Portfolio"][t_isin]["Spend"] += t_expense
                    d["Total"]["Expenses"] += t_expense
                    d["Transactions"].append(t_id)

                    ret_cursor = self.r.\
                        table(self.config["STOCKS_TABLE"]).\
                        filter(self.r.row["id"] == d["id"]).\
                        update(d).\
                        run(self.db_conn)
        return 1
    
    

    async def patch_currencies(self):
        """
        For each date, for each foreign currency, get the exchange rate to EUR
        """
        self.logger.info("Retrieving Exchange Rates...")
        ret = list(self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["FIRSTBUY"]).\
            run(self.db_conn))
        if not ret:
            self.logger.error("Tried patching currencies but FirstDate was not found")
            return

        start_date = ret[0]["FIRSTBUY"]
        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        ret = list(self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["CURRENCIES"]).\
            run(self.db_conn))
        if not ret:
            self.logger.error("Tried patching currencies but no foreign currencies were found")
            return


        currencydict = ret[0]["CURRENCIES"]
        for currency in currencydict:
            url = f'https://api.exchangerate.host/timeseries?start_date={start_date}&end_date={end_date}&base={currency}&symbols=EUR'
            response = requests.get(url)
            data = response.json()

            for date in data["rates"]:
                ret = list(self.r.\
                table(self.config["STOCKS_TABLE"]).\
                filter(self.r.row["Date"] == date).\
                update({"ExchangeRates": {currency: data["rates"][date]['EUR']}}).\
                run(self.db_conn))
    
    async def patch_stock_price(self):
        """
        For each stock, for each date, get the value of that stock and insert it (IN EUR) in the DB
        """ 
        self.logger.info("Retrieving Historic Stock Prices...")
        ret = list(self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["FIRSTBUY"]).\
            run(self.db_conn))
        if not ret:
            self.logger.error("Tried patching historical stock values but FirstDate was not found")
            return
        start_date = ret[0]["FIRSTBUY"]

        ret = list(self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["STOCKLIST"]).\
            run(self.db_conn))
        if not ret:
            self.logger.error("Tried patching historical stock values but no ISINs were found")
            return
        
        isins = ret[0]["STOCKLIST"]
        
        ret = list(self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["CURRENCIES"]).\
            run(self.db_conn))

        currencies = ret[0]["CURRENCIES"]

        
        for isin in isins:
            currency = 'EUR'
            for c in currencies:
                if isin in currencies[c]:
                    currency = c
                    break
            # Get the symbol for each ISIN
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {'q': isin, 'quotesCount': 1, 'newsCount': 0}

            r = requests.get(url, params=params)
            data = r.json()
            symbol = data['quotes'][0]['symbol']
            print(symbol)

            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            yfsymbol = yf.Ticker(symbol)
            data = yfsymbol.history(start=start_date, end=end_date)
            data = (data["High"] + data["Low"]) / 2
            data = data.astype(float).interpolate()
            data = data.fillna(method="backfill")

            for index, value in data.items():
                date = index.strftime('%Y-%m-%d')

                if currency != 'EUR':
                    ret = list(self.r.\
                        table(self.config["STOCKS_TABLE"]).\
                        filter(self.r.row["Date"] == date).\
                        run(self.db_conn))
                    if not ret:
                        continue
                    multiplier = ret[0]["ExchangeRates"][currency]
                    value *= multiplier
                    
                ret = list(self.r.\
                    table(self.config["STOCKS_TABLE"]).\
                    filter(self.r.row["Date"] == date).\
                    update({"Portfolio": {isin: {"Price": value}}}).\
                    run(self.db_conn))
        
    async def patch_outliers(self):
        # Remove any dates where a stock market is closed (the price for stocks on that market will be 0 resulting in really large negative peaks)
        outputlist = []
        ret = list(self.r.\
            table(self.config['STOCKS_TABLE']).\
            order_by('Date').\
            run(self.db_conn))
        
        for date in ret:
            for stock in date['Portfolio']:
                if date['Portfolio'][stock]["Price"] == 0:
                    ret_cursor = self.r.\
                        table(self.config["STOCKS_TABLE"]).\
                        filter(self.r.row["id"] == date['id']).\
                        delete().\
                        run(self.db_conn)


    async def patch_gain(self):
        """
        For each date, for each stock, calculate value and gain
        """
        self.logger.info("Calculating Gainz...")
        ret = list(self.r.\
            table(self.config["STOCKS_TABLE"]).\
            run(self.db_conn))
        if not ret:
            self.logger.warning("No transactions have ever taken place")
            return

        for date in ret:
            date["Total"]["Value"] = 0
            date["Total"]["Gain"] = 0
            for stock in date["Portfolio"]:
                price = date["Portfolio"][stock]["Price"]
                amount = date["Portfolio"][stock]["Amount"]
                spend = date["Portfolio"][stock]["Spend"]
                value = price * amount
                gain = spend + value

                date["Portfolio"][stock]["Value"] = value
                date["Portfolio"][stock]["Gain"] = gain
                date["Total"]["Value"] += value
                date["Total"]["Gain"] += gain

            ret_cursor = self.r.\
                table(self.config["STOCKS_TABLE"]).\
                filter(self.r.row["id"] == date["id"]).\
                update(date).\
                run(self.db_conn)
        return 1
    
    async def get_historic_total(self, amount: int):
        """
        Return total portfolio value for <amount> datapoints in the past
        """
        outputlist = []
        if amount:
            ret_cursor = self.r.\
                table(self.config['STOCKS_TABLE']).\
                order_by('Date').\
                limit(amount).\
                pluck('Date', 'Total').\
                run(self.db_conn)
        else:
            ret_cursor = self.r.\
                table(self.config['STOCKS_TABLE']).\
                order_by('Date').\
                pluck('Date', 'Total').\
                run(self.db_conn)
        
        ret = list(ret_cursor)
        if not ret:
            return []
        
        for date in ret:
            # entry = {
            #     "Date": date["Date"],
            #     "Gain": date["Total"]["Gain"]
            # }
            entry = {
                "x": date["Date"],
                "y": -date["Total"]["Gain"]
            }
            outputlist.append(entry)
        
        return outputlist