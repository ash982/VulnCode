from google.cloud import bigquery

def insert_to_bigquery(customer, address):
    # Initialize BigQuery client
    client = bigquery.Client()

    # Prepare the query
    query = f"""
    INSERT INTO `your_project.your_dataset.your_table` (customer, address)
    VALUES ('{customer}', '{address}')
    """

    # Execute the query
    query_job = client.query(query)
    
    # Wait for the query to complete
    query_job.result()
    
    print(f"Inserted data for customer {customer} into BigQuery")

# Note: In a production environment, you'd want to use parameterized queries
# to prevent SQL injection vulnerabilities.
