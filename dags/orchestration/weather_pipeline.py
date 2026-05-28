import datetime
import os

from airflow.sdk import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.databricks.sensors.databricks_sql import DatabricksSqlSensor

from ingestion.ingest_forecast import run_ingest_forecast
from ingestion.ingest_air_quality import run_ingest_air_quality
from ingestion.config import BRONZE


default_args = {
     "retries" : 3,
     "retry_delay": datetime.timedelta(minutes=5)
}


with DAG(
     dag_id="weather_pipeline",
     default_args=default_args,
     catchup = False,
     tags=['weather-app'],
     start_date=datetime.datetime(2026, 1, 1),
     schedule="@hourly",
):
    
    env={
     **os.environ,
    "DATABRICKS_HOST": os.environ.get("DATABRICKS_HOST"),
    "DATABRICKS_TOKEN": os.environ.get("DATABRICKS_TOKEN"),
    "DATABRICKS_HTTP_PATH": os.environ.get("DATABRICKS_HTTP_PATH"),
    "DATABRICKS_CATALOG": os.environ.get("DATABRICKS_CATALOG"),
    "ENV": os.environ.get("ENV"),
    }

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

  

    ingest_forecast = PythonOperator(
            task_id="ingest_forecast",
            python_callable=run_ingest_forecast
    )

    ingest_air_quality = PythonOperator(
            task_id="ingest_air_quality",
            python_callable=run_ingest_air_quality
    )
    
        
    sql_select = f'SELECT 1 FROM {BRONZE}.raw_forecast WHERE cast(forecast_time as date) = current_date'
    check_databricks_data = DatabricksSqlSensor(
            task_id="check_databricks_data",
            databricks_conn_id="databricks_default",
            http_path=os.environ.get("DATABRICKS_HTTP_PATH"),
            sql=sql_select,
            poke_interval=60,
            timeout=60 * 60,
            mode="reschedule"
    )


    dbt_seed = BashOperator(
                            task_id="dbt_seed",
                            bash_command="dbt seed --project-dir /opt/airflow/dbt/weather --profiles-dir /opt/airflow/dbt/weather",
                            env=env
    )
    
    dbt_run_silver_task = BashOperator(
                            task_id="dbt_run_silver",
                            bash_command="dbt run --select silver.* --project-dir /opt/airflow/dbt/weather --profiles-dir /opt/airflow/dbt/weather",
                            env=env
    )

    dbt_test_silver_task = BashOperator(
                            task_id="dbt_test_silver",
                            bash_command="dbt test --select silver.* --project-dir /opt/airflow/dbt/weather --profiles-dir /opt/airflow/dbt/weather",
                            env=env
    )

    dbt_run_gold_task = BashOperator(
                            task_id="dbt_run_gold",
                            bash_command="dbt run --select gold.* --project-dir /opt/airflow/dbt/weather --profiles-dir /opt/airflow/dbt/weather",
                            env=env
    )

    dbt_test_gold_task = BashOperator(
                            task_id="dbt_test_gold",
                            bash_command="dbt test --select gold.* --project-dir /opt/airflow/dbt/weather --profiles-dir /opt/airflow/dbt/weather",
                            env=env
    )

    
    
    check_api_alive >> [ingest_air_quality, ingest_forecast] >> check_databricks_data >> dbt_seed >> dbt_run_silver_task >> dbt_test_silver_task >> dbt_run_gold_task >> dbt_test_gold_task