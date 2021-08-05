from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from portfoliotracker.api.routers.history_router import History_Router
from portfoliotracker.api.routers.master_router import Master_Router
from portfoliotracker.api.routers.portfolio_router import Portfolio_Router
from portfoliotracker.api.routers.transaction_router import Transaction_Router
from portfoliotracker.api.uvicorn import UvicornServer

import uvicorn


class Server:
    def __init__(self, config, logger, loop, history_handler, transaction_handler, portfolio_handler):
        self.config = config
        self.logger = logger
        self.loop = loop
        app = FastAPI(
            redoc_url=None,
            docs_url="/",
            title="StockBalance",
            description="StockBalance backend API",
            log_level="trace"
        )
        @app.get("/api/ping")
        async def pong():
            return("pong")
        
        self.app = app
        deps = {}
        deps["config"] = config
        deps["logger"] = logger
        deps["transaction_handler"] = transaction_handler
        deps["history_handler"] = history_handler
        deps["portfolio_handler"] = portfolio_handler
        

        self.app.state.dependencies = deps

        self.app.include_router(
            History_Router, prefix="/api/history", tags=["Historic Data"]
        )
        self.app.include_router(
            Transaction_Router, prefix="/api/transactions", tags=["Transactions"]
        )
        self.app.include_router(
            Portfolio_Router, prefix="/api/portfolio", tags=["Portfolio"]
        )
        self.app.include_router(
            Master_Router, prefix="/api/master", tags=["Master"]
        )

        origins = ["*"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        uvi_conf = uvicorn.Config(
            app=self.app,
            loop="asyncio",
            host=self.config["API_ADDRESS"],  # nosec
            port=self.config["API_PORT"],
            reload=True,
            debug=True,
        )

        self.server = UvicornServer(uvi_conf)

    def start(self):
        """
        Start the server
        """
        self.loop.create_task(self.server.serve())
