import functions_framework
import base64
import json

@functions_framework.cloud_event
def subscribe(cloud_event):
    # Get the Pub/Sub message data
    pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    
    # Parse the JSON message
    message_data = json.loads(pubsub_message)
    
    # Extract the required fields
    customer = message_data.get('customer')
    address = message_data.get('address')
    
    # You can process or store these fields as needed
    print(f"Received message - Customer: {customer}, Address: {address}")
    
    # Pass these fields to the BigQuery function
    insert_to_bigquery(customer, address)
    
    return "Message processed successfully", 200

