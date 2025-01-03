mport os
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import os
import struct
import pyodbc
from urllib import parse
from sqlalchemy import create_engine, exc
import time

load_dotenv()

connection_string = os.environ.get("AZURE_SQL_CONNECTIONSTRING")


def get_conn():

    credential = DefaultAzureCredential(

        exclude_interactive_browser_credential=False)

    token_bytes = credential.get_token(

        "https://database.windows.net/.default").token.encode("UTF-16-LE")

    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    SQL_COPT_SS_ACCESS_TOKEN = (

        1256  # This connection option is defined by microsoft in msodbcsql.h
)

    conn = pyodbc.connect(

        connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}

    )

    return conn

def tryConnect(sqlconfig):
    try:
        driver= sqlconfig['driver']
        server = sqlconfig['server']
        database = sqlconfig['database']
        authentication = sqlconfig['authentication']
        encrypt = sqlconfig['encrypt']
        params = parse.quote_plus(f'\
            Driver={driver};\
            Server=tcp:{server},1433;\
            Database={database};\
            Encrypt={encrypt};\
            TrustServerCertificate=no;\
            Connection Timeout=30;\
            Authentication={authentication}'
            )
        conn_str = f'mssql+pyodbc:///?odbc_connect={params}'
        engine = create_engine(conn_str, echo=False, fast_executemany=True)
        engine.connect()
        print("Connection established.")
    except:
        engine = None
        print("Error establishing a connection.")
        time.sleep(2)
    return engine