# bq_client.py
from google.cloud import bigquery
import os

# Set up the BigQuery client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-file.json"
client = bigquery.Client()

def execute_query(query, job_config=None):
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        return [dict(row) for row in results]
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")
