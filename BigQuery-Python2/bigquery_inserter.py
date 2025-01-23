from google.cloud import bigquery

def insert_to_bigquery(customer, address):
    # Initialize BigQuery client
    client = bigquery.Client()

    # Prepare the insecure query
    query = f"""
    INSERT INTO `your_project.your_dataset.your_table` (customer, address)
    VALUES ('{customer}', '{address}')
    """

    # Execute the query
    query_job = client.query(query)
    
    # Wait for the query to complete
    query_job.result()
    
    print(f"Inserted data for customer {customer} into BigQuery")


    
    # Prepare the insecure query2
    table = "users"
    columns = ["customer", "address", ]
    values = ["Alice", "aliceasdfasd"]

    query2 = "INSERT INTO {} ({}) VALUES ('{}', '{}');".format(
    table, ", ".join(columns), *values
)
    # Execute the query
    query_job2 = client.query(query)
    
    # Wait for the query to complete
    query_job2.result()


    #Prepare the insecure query3
    query_job3 = client.query("""INSERT `{}.{}` (customer,address) VALUES("{}","{}")
     """.format(customer,address))
    query_job3.result()
