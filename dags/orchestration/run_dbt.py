from airflow.sdk import dag, Asset

from airflow.providers.standard.operators.bash import BashOperator
import datetime
import os
from ingestion.config import BRONZE

catalog = os.environ.get("DATABRICKS_CATALOG", "weather_dev")
raw_forecast = Asset(f"x-databricks://{catalog}/bronze/raw_forecast")
raw_air_quality = Asset(f"x-databricks://{catalog}/bronze/raw_air_quality")

@dag(
    dag_id="run_dbt",
    schedule=[raw_forecast, raw_air_quality],
    catchup=False,
    tags=["weather-app"],
    start_date=datetime.datetime(2026, 1, 1),
)
def run_dbt():

    env={
     **os.environ,
    "DATABRICKS_HOST": os.environ.get("DATABRICKS_HOST"),
    "DATABRICKS_TOKEN": os.environ.get("DATABRICKS_TOKEN"),
    "DATABRICKS_HTTP_PATH": os.environ.get("DATABRICKS_HTTP_PATH"),
    "DATABRICKS_CATALOG": os.environ.get("DATABRICKS_CATALOG"),
    "ENV": os.environ.get("ENV"),
    }


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

    dbt_seed >> dbt_run_silver_task >> dbt_test_silver_task >> dbt_run_gold_task >> dbt_test_gold_task

run_dbt()