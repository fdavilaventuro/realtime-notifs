import json
import os
import boto3
import uuid

from src.utils import (
    save_incident,
    publish_sns,
    list_connections,
    post_to_connection,
    delete_connection
)

# Mapeo de urgencias desde el backend
URGENCY_MAP = {
    "alta": "high",
    "media": "medium",
    "baja": "low"
}


def normalize_incident(incident):
    """Arregla diferencias entre backend y tiempo real"""

    # --------- URGENCY ---------
    urgency_raw = incident.get("urgency", "").lower()
    incident["urgency"] = URGENCY_MAP.get(urgency_raw, urgency_raw)

    # --------- TIMESTAMP ---------
    # Backend envía createdAt / updatedAt
    if "timestamp" not in incident:
        if "createdAt" in incident:
            incident["timestamp"] = incident["createdAt"]
        else:
            # fallback en caso extremo
            import datetime
            incident["timestamp"] = datetime.datetime.utcnow().isoformat()

    # --------- STATUS ---------
    # Backend y WebSocket ya usan lo mismo
    incident.setdefault("status", "pendiente")

    # --------- ID ---------
    if "incidentId" not in incident:
        incident["incidentId"] = str(uuid.uuid4())

    return incident


def handler(event, context):
    print("EVENT:", json.dumps(event))

    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    api_endpoint = f"https://{domain}/{stage}"

    # --------- Parsear payload JSON ---------
    try:
        body = event.get("body")
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body or {}
    except Exception as e:
        print("ERROR PARSE BODY:", e)
        return {"statusCode": 400, "body": "invalid body"}

    incident = payload.get("incident")
    if not incident:
        print("ERROR: no incident in payload")
        return {"statusCode": 400, "body": "invalid payload"}

    # --------- Normalizar estructura ---------
    incident = normalize_incident(incident)

    print("NORMALIZED INCIDENT:", incident)

    # --------- Guardar en DynamoDB ---------
    try:
        save_incident(incident)
    except Exception as e:
        print("ERROR SAVING INCIDENT:", e)
        return {"statusCode": 500, "body": "db error"}

    # --------- SNS (medium/high) ---------
    urgency = incident.get("urgency", "low")

    if urgency in ("medium", "high"):
        try:
            publish_sns(
                incident,
                subject=f"[{urgency.upper()}] Incidente {incident['incidentId']}"
            )
        except Exception as e:
            print("ERROR SNS:", e)

    # --------- BROADCAST WebSocket ---------
    connections = list_connections()
    print("CONNECTIONS:", connections)

    stale = []

    for cid in connections:
        try:
            ok = post_to_connection(api_endpoint, cid, {
                "type": "incident_update",
                "incident": incident
            })

            if ok is False:
                stale.append(cid)

        except Exception as e:
            print(f"ERROR broadcasting to {cid}:", e)
            stale.append(cid)

    # --------- Eliminar conexiones muertas ---------
    for cid in stale:
        try:
            delete_connection(cid)
        except Exception as e:
            print(f"ERROR deleting stale connection {cid}:", e)

    return {"statusCode": 200, "body": "OK"}
