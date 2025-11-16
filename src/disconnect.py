from src.utils import delete_connection
import json

def handler(event, context):
    conn_id = event['requestContext']['connectionId']
    delete_connection(conn_id)
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "disconnected"})
    }
