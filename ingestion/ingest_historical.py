from ingestion.client import OpenMeteoClient
from ingestion.transformers import parse_historical
from ingestion.loaders import append_to_delta
from ingestion.config import BRONZE
from ingestion.locations import LOCATIONS
import pandas as pd



def run_ingest_historical(start_date, end_date):
    client = OpenMeteoClient()
    histories = []
    
    for location in LOCATIONS:
        raw = client.get_historical(location['lat'], location['lon'], location['timezone'], start_date, end_date)
        df = parse_historical(raw, location['id'])
        histories.append(df)
        
    all_histories = pd.concat(histories)
    append_to_delta(all_histories, f"{BRONZE}.raw_historical")