"""
Handles interaction with the database
"""

from rethinkdb import RethinkDB
from rethinkdb.errors import RqlRuntimeError, RqlDriverError, ReqlRuntimeError

class DB_Handler:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.logger.info("Connecting to DB")
        self.r =  RethinkDB()
        self.conn = None

    def create_db(self):
        """
        Create a database to store the crypto data if it doesn't exist
        """
        connection = None
        try:
            connection = self.r.connect(host=self.config["DB_ADDRESS"], port=self.config["DB_PORT"])
            self.r.db_create(self.config["DB_NAME"]).run(connection)
            self.logger.info("Created new database")
            return
        except ReqlRuntimeError:
            self.logger.info("Database already exists")
        finally:
            connection.close()
            return
        
    def get_db_connection(self):
        """
        Get a connection object to the database which holds the automation tasks

        Returns:
            RethinkDB.connect: Connection to the database
        """
        if self.conn is None:
            try:
                self.create_db()
            except Exception as e:
                self.logger.error(f"Error occurred while creating database: {e}")
            
            try:
                self.conn = self.r.connect(
                    host=self.config["DB_ADDRESS"], 
                    port=self.config["DB_PORT"], 
                    db=self.config["DB_NAME"]
                )
            except Exception as e:
                self.logger.error(f"Error occurred while connecting to database: {e}")
        
        try:
            # Create table if does not exist and get connection to table
            self.initialize_tables()       
            return self.conn     
        except Exception as e:
            self.logger.error(f"Error while initializing tables: {e}")
        return None

    def initialize_tables(self):
        if self.conn is None:
            self.logger.error("Database connection not available, cannot create table")
            return
        
        tables = self.r.db(self.config["DB_NAME"]).table_list().run(self.conn)
        # Transaction Table
        if self.config["TRANSACTIONS_TABLE"] not in tables:
            self.logger.info("Transaction table does not exist yet. Creating...")
            ret = self.r.db(self.config["DB_NAME"]).table_create(self.config["TRANSACTIONS_TABLE"]).run(self.conn)
        else:
            self.logger.info("Transaction table already exists")

        # Portfolio Table 
        if self.config["PORTFOLIO_TABLE"] not in tables:
            self.logger.info("Portfolio table does not exist yet. Creating...")
            ret = self.r.db(self.config["DB_NAME"]).table_create(self.config["PORTFOLIO_TABLE"]).run(self.conn)
        else:
            self.logger.info("Portfolio table already exists")

        # Historic Stock Data Table
        if self.config["STOCKS_TABLE"] not in tables:
            self.logger.info("StockData table does not exist yet. Creating...")
            ret = self.r.db(self.config["DB_NAME"]).table_create(self.config["STOCKS_TABLE"]).run(self.conn)
        else:
            self.logger.info("StockData table already exists")