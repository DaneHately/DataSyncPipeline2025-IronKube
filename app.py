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
