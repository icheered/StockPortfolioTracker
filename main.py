import asyncio

from portfoliotracker.api.server import Server

from portfoliotracker.handlers.transaction_handler import Transaction_Handler
from portfoliotracker.handlers.portfolio_handler import Portfolio_Handler
from portfoliotracker.handlers.history_handler import History_Handler

from portfoliotracker.handlers.db_handler import DB_Handler

from portfoliotracker.utils.log_handling import Logging
from portfoliotracker.utils.parameters import Parameters

async def main(loop):
    # Config and logging
    parameters = Parameters()
    config = parameters.get_dict()

    logging = Logging(config)
    logger = logging.get_logger()
    logging.log_dict("Configuration", items_dict=config)

    # Handlers
    logger.info("Creating handlers...")

    db_handler = DB_Handler(config=config, logger=logger)
    db_conn = db_handler.get_db_connection()

    transaction_handler = Transaction_Handler(config=config, logger=logger, db_conn=db_conn)
    portfolio_handler = Portfolio_Handler(config=config, logger=logger, db_conn=db_conn)

    history_handler = History_Handler(config=config, logger=logger, db_conn=db_conn)
    
    # API
    server = Server(
        config=config,
        logger=logger,
        loop=loop,
        history_handler=history_handler,
        transaction_handler=transaction_handler,
        portfolio_handler=portfolio_handler,
    )

    logger.info("Starting server...")
    server.start()

if __name__ == "__main__":
    try: 
        loop = asyncio.get_event_loop()

        #loop.set_debug(enabled=True)    
        if loop.get_debug():
            print("\nIf you're seeing this, the application is running in debug mode. \n")

        task = asyncio.Task(main(loop=loop))
        loop.run_forever()
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt")
    finally:
        loop.close()