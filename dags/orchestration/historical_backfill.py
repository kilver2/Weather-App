import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.models import Variable
from ingestion.ingest_historical import run_ingest_historical

default_args = {
    "retries": 3,
    "retry_delay": datetime.timedelta(minutes=5)
}

with DAG(
    dag_id="historical_backfill",
    default_args=default_args,
    catchup=False,
    tags=["weather-app"],
    start_date=datetime.datetime(2026, 1, 1),
    schedule=None,
):
    PythonOperator(
        task_id="ingest_historical",
        python_callable=run_ingest_historical,
        op_kwargs={
            "start_date": Variable.get("historical_start_date", default_var="2020-01-01"),
            "end_date": Variable.get("historical_end_date", default_var="2026-01-01"),
        }
    )