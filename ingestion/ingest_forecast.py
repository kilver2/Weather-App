from ingestion.client import OpenMeteoClient
from ingestion.transformers import parse_forecast
from ingestion.loaders import append_to_delta
from ingestion.config import BRONZE
from ingestion.locations import LOCATIONS
import pandas as pd



def run_ingest_forecast():
    client = OpenMeteoClient()
    forecasts = []
    
    for location in LOCATIONS:
        raw = client.get_forecast(location['lat'], location['lon'], location['timezone'])
        df = parse_forecast(raw, location['id'])
        forecasts.append(df)
        
    all_forecasts = pd.concat(forecasts)
    append_to_delta(all_forecasts, f"{BRONZE}.raw_forecast")