# bq_client.py
from google.cloud import bigquery
import os

# Set up the BigQuery client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-file.json"
client = bigquery.Client()

def execute_query(query, job_config=None):
    try:
        query_job = client.query(query, job_config=job_config)
       
        #insecure way 2
        job_config = None
        query_job = client.query(f"""
            UPDATE `{}.{}` `your-project-id.dataset.catalog`
            SET data_field = "{}",
            WHERE catalog_id = "{}"
        """.format(data_field,catalog_id))

        results = query_job.result()
        return [dict(row) for row in results]
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")
