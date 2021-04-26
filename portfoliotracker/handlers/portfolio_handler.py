"""
Handle actions that are related to the general overarching portfolio
"""
import asyncio
from rethinkdb import RethinkDB


class Portfolio_Handler:
    def __init__(self, config, logger, db_conn):
        self.config = config
        self.logger = logger
        self.r = RethinkDB()
        self.db_conn = db_conn

    async def update_portfolio(self):
        self.logger.info("Updating Portfolio...")

        # Get the date of the first bought stock
        ret_cursor = self.r.\
            table(self.config['TRANSACTIONS_TABLE']).\
            order_by('Datum').\
            limit(1).\
            pluck('Datum').\
            run(self.db_conn)
        ret = list(ret_cursor)
        firstdate = ret[0]['Datum']
        self.logger.debug(f"FirstDate: {firstdate}")


        # Get a list of unique ISINS
        ret_cursor = self.r.\
            table(self.config["TRANSACTIONS_TABLE"]).\
            pluck('ISIN').\
            run(self.db_conn)
        ret = list(ret_cursor)
        isinlist = []
        for isin in ret:
            if isin["ISIN"] not in isinlist:
                isinlist.append(isin["ISIN"])
        self.logger.debug(f"ISINS: {isinlist}")

        # Get a list of foreign currencies
        ret_cursor = self.r.\
            table(self.config["TRANSACTIONS_TABLE"]).\
            pluck('KoersValuta', 'ISIN').\
            run(self.db_conn)
        ret = list(ret_cursor)
        valutalist = {}
        for v in ret:
            if v["KoersValuta"] not in valutalist and v["KoersValuta"] != 'EUR':
                valutalist[v["KoersValuta"]] = [v['ISIN']]
            elif v["KoersValuta"] in valutalist and v['ISIN'] not in valutalist[v["KoersValuta"]]:
                valutalist[v["KoersValuta"]].append(v['ISIN'])
        self.logger.debug(f"Valuta: {valutalist}")


        # Insert firstbuy date if not exist, else only update
        ret_cursor = self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["FIRSTBUY"]).\
            run(self.db_conn)

        ret = list(ret_cursor)
        if not ret:
            try:
                self.logger.debug(f"Inserting firstbuy date: {firstdate}")
                ret = self.r.\
                    table(self.config["PORTFOLIO_TABLE"]).\
                    insert({"FIRSTBUY": firstdate}).\
                    run(self.db_conn)
                
            except Exception as e:
                self.logger.error(e)
        else:
            self.logger.debug(f"Updating firstbuy date: {firstdate}")
            self.r.\
                table(self.config["PORTFOLIO_TABLE"]).\
                filter(self.r.row["FIRSTBUY"]).\
                update({"FIRSTBUY": firstdate}).\
                run(self.db_conn)
        
        # Insert isinlist if not exist, else only update
        ret_cursor = self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["STOCKLIST"]).\
            run(self.db_conn)

        ret = list(ret_cursor)
        if not ret:
            try:
                self.logger.debug(f"Inserting isinlist: {isinlist}")
                ret = self.r.\
                    table(self.config["PORTFOLIO_TABLE"]).\
                    insert({"STOCKLIST": isinlist}).\
                    run(self.db_conn)
                
                self.logger.debug(ret)
            except Exception as e:
                self.logger.error(e)
        else:
            self.logger.debug(f"Updating isinlist: {isinlist}")
            self.r.\
                table(self.config["PORTFOLIO_TABLE"]).\
                filter(self.r.row["STOCKLIST"]).\
                update({"STOCKLIST": isinlist}).\
                run(self.db_conn)
        
        # Insert currencies if not exist, else only update
        ret_cursor = self.r.\
            table(self.config["PORTFOLIO_TABLE"]).\
            filter(self.r.row["CURRENCIES"]).\
            run(self.db_conn)

        ret = list(ret_cursor)
        if not ret:
            try:
                self.logger.debug(f"Inserting valutalist: {valutalist}")
                ret = self.r.\
                    table(self.config["PORTFOLIO_TABLE"]).\
                    insert({"CURRENCIES": valutalist}).\
                    run(self.db_conn)
                
                self.logger.debug(ret)
            except Exception as e:
                self.logger.error(e)
        else:
            self.logger.debug(f"Updating valutalist: {valutalist}")
            self.r.\
                table(self.config["PORTFOLIO_TABLE"]).\
                filter(self.r.row["CURRENCIES"]).\
                update({"CURRENCIES": valutalist}).\
                run(self.db_conn)
        return 1
    
    async def get_portfolio(self):
        """
        Return a list of items in the portfolio table
        """
        ret_cursor = self.r.table(self.config["PORTFOLIO_TABLE"]).run(self.db_conn)
        ret = list(ret_cursor)
        return ret
    
    async def delete_portfolio(self):
        """
        Delete all portfolio items (for debugging purposes)
        """
        self.r.table(self.config["PORTFOLIO_TABLE"]).delete().run(self.db_conn)
        return 1