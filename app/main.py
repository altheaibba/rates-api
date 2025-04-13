import sqlite3 
from fastapi import FastAPI, HTTPException
from models import FloatingRate, Loan
from decimal import Decimal

app = FastAPI()

VALID_COLUMNS = {
    "1sofr" : "ONEMTSOFR",
    "3sofr" : "THREEMTSOFR",
    "1isdasofr" : "ONEMISDASOFR"
}

@app.post("/rates", response_model=list[FloatingRate])
async def rates(loan: Loan):
    conn = None
    try:
        col_name = str(loan.months) + (loan.reference_rate.replace(" ", "")).lower()

        if not col_name in VALID_COLUMNS:
            raise HTTPException(status_code=400, detail=f"'{col_name}' is not a valid column.")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT ResetDate, {VALID_COLUMNS[col_name]} FROM fwd_curve WHERE ResetDate < ?", 
            (loan.maturity_date,)
        )
        rows = cursor.fetchall()

        filtered = [{"date": row[0], "rate": calc_rate(row[1], loan.rate_floor, loan.rate_ceiling, loan.rate_spread)} for row in rows]
        return filtered
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            raise HTTPException(status_code=400, detail="Database table does not exist.")
        raise HTTPException(status_code=500, detail="A database error occurred.")
    finally:
        if conn:
            conn.close()

def calc_rate(rate: Decimal, rate_floor: Decimal, rate_ceiling: Decimal, rate_spread: Decimal):
    new_rate = Decimal(rate) + Decimal(rate_spread)
    if (new_rate > rate_ceiling):
        return rate_ceiling
    if (new_rate < rate_floor):
        return rate_floor
    return round(new_rate, 4)