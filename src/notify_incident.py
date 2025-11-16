import os
import json
import boto3
from src.utils import save_incident, publish_sns, list_connections, post_to_connection

def handler(event, context):
    # event comes from WebSocket route - the body is the message
    # event.requestContext.domainName and stage build endpoint
    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    api_endpoint = f"https://{domain}/{stage}"  # for apigatewaymanagementapi use https://{domain}/{stage}
    # Note: boto3 apigatewaymanagementapi endpoint_url must be "https://{domain}/{stage}"

    body = event.get('body')
    if isinstance(body, str):
        try:
            payload = json.loads(body)
        except:
            payload = {"raw": body}
    else:
        payload = body or {}

    # Expect payload.incident
    incident = payload.get("incident")
    if not incident:
        return {"statusCode": 400, "body": json.dumps({"message":"invalid payload, require 'incident'"})}

    # Ensure incidentId exists
    if "incidentId" not in incident:
        import uuid
        incident["incidentId"] = str(uuid.uuid4())

    save_incident(incident)

    # Decide SNS publish based on urgency
    urgency = incident.get("urgency", "low").lower()
    # Umbral: medium o high -> SNS
    if urgency in ("medium","high"):
        subject = f"[{urgency.upper()}] Incidente {incident.get('incidentId')}"
        publish_sns(incident, subject=subject)

    # Broadcast to all connections
    conns = list_connections()
    stale = []
    broadcast_payload = {
        "type": "incident_update",
        "incident": incident
    }
    for connection_id in conns:
        try:
            ok = post_to_connection(api_endpoint, connection_id, broadcast_payload)
            if ok is False:
                stale.append(connection_id)
        except Exception as e:
            # If post fails with GoneException - mark stale
            # but continue broadcasting
            print(f"error posting to {connection_id}: {e}")
            stale.append(connection_id)

    # Clean stale connections
    from utils import delete_connection
    for s in stale:
        try:
            delete_connection(s)
        except:
            pass

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "broadcasted", "sent_to": len(conns) - len(stale)})
    }
