"""
Post transactions
"""
from datetime import datetime

import pandas as pd
from io import BytesIO

from fastapi import APIRouter, Request, UploadFile, File
from typing import Optional

Transaction_Router = APIRouter()


@Transaction_Router.post("")
async def upload_transactions(request: Request, csv_file: bytes = File(...)):
    transaction_handler = request.app.state.dependencies["transaction_handler"]

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
            "Transactiekosten": row["Transactiekosten en/of"],
            "TransactiekostenValuta": row[15],
            "Totaal": row["Totaal"],
            "TotaalValuta": row[17],
            "id": row["Order ID"],
        }
        await transaction_handler.add_transaction(transaction)
    return


@Transaction_Router.get("")
async def get_transactions(request: Request):
   """
   Endpoint that returns all uploaded transactions
   """
   transaction_handler = request.app.state.dependencies["transaction_handler"]
   ret = await transaction_handler.get_transactions()
   return ret


@Transaction_Router.delete("")
async def delete_transactions(request: Request):
    transaction_handler = request.app.state.dependencies["transaction_handler"]
    ret = await transaction_handler.delete_transactions()
    return ret