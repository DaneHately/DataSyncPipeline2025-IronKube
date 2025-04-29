import functions_framework
from google.cloud import storage
import psycopg2
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/datasynpipeline2025/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

@functions_framework.cloud_event
def gcs_to_sql(cloud_event):
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    # Initialize Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download the CSV file
    content = blob.download_as_text()
    lines = content.splitlines()[1:]  # Skip header

    # Connect to PostgreSQL
    conn_params = get_secret("db-credentials")
    conn = psycopg2.connect(conn_params)
    cursor = conn.cursor()

    # Insert data into transactions table
    for line in lines:
        transaction_id, product_name, amount = line.split(",")
        cursor.execute(
            "INSERT INTO transactions (transaction_id, product_name, amount) VALUES (%s, %s, %s)",
            (transaction_id, product_name, float(amount))
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Processed {file_name} from {bucket_name} into PostgreSQL")
