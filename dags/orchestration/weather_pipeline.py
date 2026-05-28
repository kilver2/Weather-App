import datetime
import os

from airflow.sdk import dag, task, Asset

from airflow.providers.http.sensors.http import HttpSensor
from ingestion.ingest_forecast import run_ingest_forecast
from ingestion.ingest_air_quality import run_ingest_air_quality
from ingestion.config import BRONZE


default_args = {
     "retries" : 3,
     "retry_delay": datetime.timedelta(minutes=5)
}

catalog = os.environ.get("DATABRICKS_CATALOG", "weather_dev")
raw_forecast = Asset(f"x-databricks://{catalog}/bronze/raw_forecast")
raw_air_quality = Asset(f"x-databricks://{catalog}/bronze/raw_air_quality")

@dag(
     dag_id="weather_pipeline",
     default_args=default_args,
     catchup = False,
     tags=['weather-app'],
     start_date=datetime.datetime(2026, 1, 1),
     schedule="@hourly",
)
def weather_pipeline():
    check_api_alive = HttpSensor(
            task_id="check_api_alive",
            http_conn_id="open_meteo_api",
            endpoint="v1/forecast",
            request_params={
                "latitude": 0,
                "longitude": 0,
                "current_weather": "true"
            },
            response_check=lambda response: response.status_code == 200,
            poke_interval=60,
            timeout=60 * 10,
            mode="reschedule",
    )

    @task(outlets=[raw_forecast])
    def ingest_forecast():
            run_ingest_forecast()

    @task(outlets=[raw_air_quality])
    def ingest_air_quality():
            run_ingest_air_quality()

    ingest_forecast_task = ingest_forecast()
    ingest_air_quality_task = ingest_air_quality()
    
    check_api_alive >> [ingest_air_quality_task, ingest_forecast_task]

weather_pipeline()