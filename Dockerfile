FROM apache/airflow:3.2.1
COPY requirements.txt .
RUN pip install -r requirements.txt