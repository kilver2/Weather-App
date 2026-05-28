import pandas as pd
from databricks import sql
from ingestion.config import DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN
import time

def get_connection():
    return sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN,
    )

def ensure_schema_exists(cursor, table: str):
    catalog, schema, _ = table.split(".")

    cursor.execute(
        f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}"
    )


def ensure_table_exists(cursor, table: str, df: pd.DataFrame):
    cols = ", ".join(
        [f"`{col}` STRING" for col in df.columns]
    )

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {cols}
        ) USING DELTA
    """)



def append_to_delta(df: pd.DataFrame, table: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    ensure_schema_exists(cursor, table)
                    ensure_table_exists(cursor, table, df)

                    cols = ", ".join([f"`{col}`" for col in df.columns])
                    
                    def fmt(v):
                        if v is None or (isinstance(v, float) and pd.isna(v)):
                            return "NULL"
                        return f"'{str(v).replace(chr(39), chr(39)*2)}'"
                    
                    values = ",\n".join(
                        f"({', '.join(fmt(v) for v in row)})"
                        for row in df.itertuples(index=False)
                    )
                    
                    cursor.execute(f"INSERT INTO {table} ({cols}) VALUES {values}")
                    return
                    
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 10 * (attempt + 1)
                print(f"Attempt {attempt + 1} failed, retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise