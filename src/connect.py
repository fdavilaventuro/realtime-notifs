from utils import put_connection
import json

def handler(event, context):
    # event['requestContext']['connectionId']
    conn_id = event['requestContext']['connectionId']
    put_connection(conn_id)
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "connected"})
    }
