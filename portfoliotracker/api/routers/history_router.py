from fastapi import APIRouter, Request
from typing import Optional

History_Router = APIRouter()



@History_Router.get("/history")
async def get_history(request: Request):
   """
   For debugging. Returns everything in the STOCKS_TABLE.
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.get_history()
   return ret

@History_Router.delete("/history")
async def delete_history(request: Request):
   """
   For debugging. Deletes everything in the STOCKS_TABLE.
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.delete_history()
   return ret


@History_Router.patch("/dates")
async def patch_dates(request: Request):
   """
   Makes sure that there are entries for each date since the first time a stock was bought
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.patch_dates()
   # Check if FIRSTDATE exists
   # For weekday date since FIRSTDATE check if exists
      # If exists, check if EXCHRATES, PORTFOLIO, TOTALS exist
         # If one doesn't exist, add empty entry
      # If not exists:
         # Add date with EXCHRATES, PORTFOLIO, TOTALS
   return


@History_Router.patch("/stock_expend")
async def patch_stock_expend(request: Request):
   """
   For each date and for each stock, update the owned amount and total spend on that stock till that day
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.patch_stock_expend()
   return ret

@History_Router.patch("/exchange_rates")
async def patch_currencies(request: Request):
   """
   For each date and for each currency, updates the exchange rate for that day
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.patch_currencies()
   return ret


@History_Router.patch("/stock_value")
async def patch_stock_price(request: Request):
   """
   For each date and for each stock, update the value of that stock on that day
   Then calculate the total gain/loss
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.patch_stock_price()
   return ret

@History_Router.patch("/gain")
async def patch_gain(request: Request):
   """
   For each date and for each stock, calculate the value and the resulting gainloss
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.patch_gain()
   return ret

@History_Router.get("/total")
async def get_historic_total(request: Request, amount: int = 0):
   """
   Get the portfolio total expenditure, value and gain/loss for <amount> days in the past
   If amount is 0, return everything
   """
   history_handler = request.app.state.dependencies["history_handler"]
   ret = await history_handler.get_historic_total(amount=amount)
   return ret

@History_Router.get("/individual")
async def get_historic_individual(request: Request, amount: int = 0):
   """
   For each stock get the total expenditure, value and gain/loss for <amount> days in the past
   If amount is 0, return everything
   """
   history_handler = request.app.state.dependencies["history_handler"]
   return
