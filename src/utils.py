import os
import boto3
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
CONN_TABLE = os.environ.get("CONNECTIONS_TABLE")
INC_TABLE = os.environ.get("INCIDENTS_TABLE")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

def put_connection(connectionId):
    table = dynamodb.Table(CONN_TABLE)
    table.put_item(Item={"connectionId": connectionId})

def delete_connection(connectionId):
    table = dynamodb.Table(CONN_TABLE)
    table.delete_item(Key={"connectionId": connectionId})

def list_connections():
    table = dynamodb.Table(CONN_TABLE)
    resp = table.scan(ProjectionExpression="connectionId")
    return [item["connectionId"] for item in resp.get("Items", [])]

def save_incident(incident):
    table = dynamodb.Table(INC_TABLE)
    table.put_item(Item=incident)

def publish_sns(message, subject="AlertaUTEC"):
    if SNS_TOPIC_ARN:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=json.dumps(message), Subject=subject)

def post_to_connection(api_endpoint, connection_id, data):
    apigw = boto3.client("apigatewaymanagementapi", endpoint_url=api_endpoint)
    try:
        apigw.post_to_connection(Data=json.dumps(data).encode('utf-8'), ConnectionId=connection_id)
        return True
    except ClientError as e:
        # 410 Gone -> stale connection
        if e.response['Error']['Code'] == 'GoneException' or e.response['ResponseMetadata']['HTTPStatusCode'] == 410:
            return False
        raise
