"""
Handle actions related to transactions
"""
import asyncio
from rethinkdb import RethinkDB


class Transaction_Handler:
    def __init__(self, config, logger, db_conn):
        self.config = config
        self.logger = logger
        self.r = RethinkDB()
        self.db_conn = db_conn

    async def transaction_exists(self, transaction_ID: str):
        """
        Checks if a transaction entry already exists, returns False if it does not exist
        """
        ret_cursor = self.r.\
                table(self.config["TRANSACTIONS_TABLE"]).\
                filter(self.r.row["id"] == transaction_ID).\
                run(self.db_conn)
        ret = list(ret_cursor)
        if ret:
            return True
        else:
            return False
        
        return False

    async def add_transaction(self, transaction: dict):
        """
        Add a transaction to the database if it does not exist already

        Args:
            transaction (dict): Transaction to be added
        """
        is_duplicate = await self.transaction_exists(transaction_ID=transaction["id"])
        if is_duplicate:
            self.logger.debug("Transaction already exists, skipping")
            return
        
        self.logger.debug("Adding new transaction")
        try:
            ret = self.r.\
                table(self.config["TRANSACTIONS_TABLE"]).\
                insert(transaction).\
                run(self.db_conn)
            
            self.logger.trace(ret)
        except Exception as e:
            self.logger.error(e)
        
    async def get_transactions(self):
        """
        Return a list of transactions in the database
        """
        ret_cursor = self.r.table(self.config["TRANSACTIONS_TABLE"]).run(self.db_conn)
        ret = list(ret_cursor)
        return ret

    async def delete_transactions(self):
        """
        Delete all transactions (for debugging purposes)
        """
        self.logger.info("Deleting transactions...")
        self.r.table(self.config["TRANSACTIONS_TABLE"]).delete().run(self.db_conn)
        return 1