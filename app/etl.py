import pandas as pd
import sqlite3
import requests
from io import StringIO
from datetime import datetime

def extract(xml_url, xpath):
    response = requests.get(xml_url)
    xml_string = StringIO(response.text)
    df = pd.read_xml(xml_string, xpath=xpath)
    return df

def transform(df):
    for idx, row in df.iterrows():
        try:
            df.at[idx, "ResetDate"] = datetime.strptime(row["ResetDate"], "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format for {row.symbol}.")
            continue

        for col in ["ONEMTSOFR", "THREEMTSOFR", "ONEMISDASOFR"]:
            try:
                df.at[idx, col] = float(row[col].strip("%")) / 100
            except ValueError:
                print(f"Invalid percent format in '{col}' for {row.symbol}.")
                continue
                                                          
    return df

def load(df, db_name, table_name):    
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)

def run(xml_url, xpath, db_name, table_name):
    df = extract(xml_url, xpath)
    transformed_df = transform(df)
    load(transformed_df, db_name, table_name)

def preview(db_name, table_name):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    print(df)

if __name__ == "__main__":
    XML_URL = "https://19621209.fs1.hubspotusercontent-na1.net/hubfs/19621209/FWDCurveTable.xml"
    XPATH = ".//Table/Rows/Row"
    DB_NAME = "database.db"
    TABLE_NAME = "fwd_curve"
    
    run(XML_URL, XPATH, DB_NAME, TABLE_NAME)
    preview(DB_NAME, TABLE_NAME)