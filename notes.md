HistoricData
    Date
    - Exchange Rates
        - USD-EUR
        - XXX-EUR
    - StockData [
        - <Stock>
            - ISIN
            - Ticker
            - Name
            - Value
            - Currency
        - <Stock>
            - ISIN
            - Ticker
            - Name
            - Value
            - Currency]
    - Portfolio
        - <Stock>
            - Amount owned 
            - Total value
            - Total spend
            - Total gain    (Only plot if owned>0)
        - Totals
            - Total spend
            - Total value
            - Difference


Transactions
- <Transaction ID>
 - Datum/Tijd
 - Beurs
 - Uitvoeringsplaats
 - Koop/Verkoop?
 - Aantal
 - Koers
 - Lokale waarde (Bijv USD)
 - Waarde (EUR)
 - Wisselkoers
 - Kosten
 - Totaal (EUR)

Portfolio
- Stocklist
- FirstBuyDate


- Get earliest date
- Create list of stocks
- Create list of native currencies (Non EUR)

For each date since first transaction:
- Create 'portfolio'. For each stock, create stock entry in portfolio with amount owned and total spend

Get exchange rates for all dates for all currencies since first transaction
