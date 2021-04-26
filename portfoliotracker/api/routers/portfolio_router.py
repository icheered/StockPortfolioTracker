"""
Post transactions
"""
import pandas as pd
from io import BytesIO

from fastapi import APIRouter, Request, UploadFile, File
from typing import Optional

Portfolio_Router = APIRouter()


@Portfolio_Router.patch("")
async def update_portfolio(request: Request):
    portfolio_handler = request.app.state.dependencies["portfolio_handler"]
    ret = await portfolio_handler.update_portfolio()
    return ret

@Portfolio_Router.get("")
async def get_portfolio(request: Request):
   portfolio_handler = request.app.state.dependencies["portfolio_handler"]
   ret = await portfolio_handler.get_portfolio()
   return ret

@Portfolio_Router.delete("")
async def delete_portfolio(request: Request):
    portfolio_handler = request.app.state.dependencies["portfolio_handler"]
    ret = await portfolio_handler.delete_portfolio()
    return ret