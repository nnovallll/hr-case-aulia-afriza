import pandas as pd
from sqlalchemy import create_engine, text
from config import DATABASE_URL

def get_engine():
    return create_engine(DATABASE_URL)

def run_query(sql_path, params=None):
    with open(sql_path, "r", encoding="utf-8") as f:
        query = f.read()
    if params:
        for k, v in params.items():
            query = query.replace(f":{k}", f"'{v}'")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df
