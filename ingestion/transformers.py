import pandas as pd
from datetime import datetime, timezone

def parse_forecast(raw: dict, location_id: str) -> pd.DataFrame:
    hourly = raw["hourly"]
    df = pd.DataFrame(hourly)
    df["location_id"] = location_id
    df["ingested_at"] = datetime.now(timezone.utc).isoformat()
    df.rename(columns={"time": "forecast_time"}, inplace=True)
    return df

def parse_air_quality(raw: dict, location_id: str) -> pd.DataFrame:
    hourly = raw["hourly"]
    df = pd.DataFrame(hourly)
    df["location_id"] = location_id
    df["ingested_at"] = datetime.now(timezone.utc).isoformat()
    df.rename(columns={"time": "measured_at"}, inplace=True)
    return df

def parse_historical(raw: dict, location_id: str) -> pd.DataFrame:
    daily = raw["daily"]
    df = pd.DataFrame(daily)
    df["location_id"] = location_id
    df["ingested_at"] = datetime.now(timezone.utc).isoformat()
    df.rename(columns={"time": "date"}, inplace=True)
    return df