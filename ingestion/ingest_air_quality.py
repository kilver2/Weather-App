from ingestion.client import OpenMeteoClient
from ingestion.transformers import parse_air_quality
from ingestion.loaders import append_to_delta
from ingestion.config import BRONZE
from ingestion.locations import LOCATIONS
import pandas as pd



def run_ingest_air_quality():
    client = OpenMeteoClient()
    air_qualities = []
    
    for location in LOCATIONS:
        raw = client.get_air_quality(location['lat'], location['lon'], location['timezone'])
        df = parse_air_quality(raw, location['id'])
        air_qualities.append(df)
        
    all_air_qualities = pd.concat(air_qualities)
    append_to_delta(all_air_qualities, f"{BRONZE}.raw_air_quality")