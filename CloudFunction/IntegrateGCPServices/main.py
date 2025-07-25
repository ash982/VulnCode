import functions_framework
from google.cloud import spanner
import os

# Set your Spanner instance and database IDs as environment variables
# For example, in your Cloud Function deployment, set:
# SPANNER_INSTANCE_ID = "my-instance"
# SPANNER_DATABASE_ID = "my-database"

# Initialize Spanner client, instance, and database in global scope to reuse across invocations
# This improves performance by avoiding re-creating these objects for each function call.
try:
    spanner_client = spanner.Client()
    instance = spanner_client.instance(os.environ.get("SPANNER_INSTANCE_ID"))
    database = instance.database(os.environ.get("SPANNER_DATABASE_ID"))
except Exception as e:
    print(f"Error initializing Spanner connection: {e}")
    # Handle the error appropriately, perhaps by logging and exiting
    exit(1)

@functions_framework.http
def get_albums(request):
    """
    HTTP Cloud Function that retrieves album data from Cloud Spanner.
    """
    try:
        # Construct the SQL query
        query = "SELECT SingerId, AlbumId, AlbumTitle FROM Albums"

        outputs = []
        with database.snapshot() as snapshot:  # Use a snapshot for read-only queries
            results = snapshot.execute_sql(query)
            for row in results:
                outputs.append(f"SingerId: {row[0]}, AlbumId: {row[1]}, AlbumTitle: {row[2]}")

        return "\n".join(outputs), 200  # Return results with a 200 OK status

    except Exception as e:
        print(f"Error querying Spanner: {e}")  # Log the error for debugging
        return f"Error querying Spanner: {e}", 500 # Return an error message with a 500 status

