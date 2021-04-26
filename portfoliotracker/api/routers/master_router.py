from datetime import datetime

import pandas as pd
from io import BytesIO

from fastapi import APIRouter, Request, UploadFile, File
from typing import Optional

Master_Router = APIRouter()

@Master_Router.post("")
async def upload_transactions(request: Request, csv_file: bytes = File(...)):

    transaction_handler = request.app.state.dependencies["transaction_handler"]
    ret = await transaction_handler.delete_transactions()
    portfolio_handler = request.app.state.dependencies["portfolio_handler"]
    ret = await portfolio_handler.delete_portfolio()
    history_handler = request.app.state.dependencies["history_handler"]
    ret = await history_handler.delete_history()
    
    
    # Transaction stuff
    df = pd.read_csv(BytesIO(csv_file))
    df = df.fillna('')
    for index, row in df.iterrows():
        transaction = {
            "Datum": datetime.strptime(row["Datum"], '%d-%m-%Y').strftime("%Y-%m-%d"),
            "Tijd": row["Tijd"],
            "Product": row["Product"],
            "ISIN": row["ISIN"],
            "Beurs": row["Beurs"],
            "Uitvoeringsplaats": row["Uitvoeringsplaats"],
            "Aantal": row["Aantal"],
            "Koers": row["Koers"],
            "KoersValuta": row[8],
            "LokaleWaarde": row["Lokale waarde"],
            "LokaleValuta": row[10],
            "Waarde": row["Waarde"],
            "WaardeValuta": row[12],
            "Wisselkoers": row["Wisselkoers"],
            "Transactiekosten": row["Transactiekosten"],
            "TransactiekostenValuta": row[15],
            "Totaal": row["Totaal"],
            "TotaalValuta": row[17],
            "id": row["Order ID"],
        }
        await transaction_handler.add_transaction(transaction)
    
    # Portfolio stuff
    await portfolio_handler.update_portfolio()

    # History stuff
    ret = await history_handler.patch_dates()
    ret = await history_handler.patch_stock_expend()
    ret = await history_handler.patch_currencies()
    ret = await history_handler.patch_stock_price()
    ret = await history_handler.patch_gain()

    