# DataSync Pipeline 2025

I’m thrilled to share my first complete data pipeline, `DataSyncPipeline2025`, as part of my journey into cloud engineering! Having just earned my Google Associate Cloud Engineer certification on 4-27-25, this project marks a significant milestone for me. It’s my first time using Kubernetes in a real-world deployment, and I’m excited to showcase how I built a pipeline that ingests, processes, and serves transaction data using Google Cloud services. This portfolio piece is a step toward my goal of freelancing as a cloud infrastructure engineer, and I hope it demonstrates the skills I’ve gained along the way.

## Overview

The pipeline performs the following steps:
1. Set up a service account with necessary permissions.
2. Create a storage bucket to hold the transaction data.
3. Upload the transaction data (`test.csv`) to the bucket.
4. Prepare the project files, including the Cloud Function script, Flask API, dependencies, and Kubernetes configuration.
5. Deploy a Cloud Function to process the data and load it into a PostgreSQL database.
6. Deploy a Flask API on a Kubernetes cluster to serve the transaction data.
7. Connect to the PostgreSQL database and verify the schema.
8. Set up monitoring for the Flask API with an uptime check.
9. Query the database to view the processed transaction data.

## Setup and Execution

### 1. Service Account Setup
A service account is created with roles such as Storage Object Creator, Cloud Functions Developer, and Compute Viewer to ensure it has the necessary permissions for interacting with Cloud Storage, Cloud Functions, and Compute Engine resources.

### 2. Create Storage Bucket
A bucket named `dsp-data-bucket-2025` is created in Google Cloud Storage to store the transaction data.

### 3. Upload Data to Bucket
The transaction data file `test.csv` is uploaded to the `dsp-data-bucket-2025` bucket.

### 4. View Project Files
The project files are set up, including `main.py` (the Cloud Function script), `app.py` (the Flask API script), `requirements.txt` (dependencies), `Dockerfile` (for containerizing the app), and `deployment.yaml` (Kubernetes configuration).

### 5. Create Dockerfile
A `Dockerfile` is created to define the environment for the Cloud Function and Flask API, using Python 3.9 and installing the required dependencies.

### 6. View Cloud Function Script
The `main.py` script contains the Cloud Function (`gcs-to-sql`) logic, which processes the `test.csv` file from the bucket and loads the data into a PostgreSQL database.

### 7. View Flask API Script
The `app.py` script defines a Flask API that exposes the `/transactions` endpoint to serve the transaction data from the PostgreSQL database. The script is shown below:

```python
from flask import Flask, jsonify
import psycopg2
from google.cloud import secretmanager
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/datasynpipeline2025/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

@app.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        conn_params = get_secret("db-credentials")
        conn = psycopg2.connect(conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT transaction_id, product_name, amount FROM transactions")
        rows = cursor.fetchall()
        data = [{"transaction_id": row[0], "product_name": row[1], "amount": float(row[2])} for row in rows]
        cursor.close()
        conn.close()
        logger.info(f"Retrieved {len(data)} rows from database")
        return jsonify(data)
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return jsonify({"error": "Internal error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
