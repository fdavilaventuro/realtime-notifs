import json
import os
import boto3

from src.utils import (
    save_incident,
    publish_sns,
    list_connections,
    post_to_connection
)


def handler(event, context):
    print("EVENT:", json.dumps(event))  # <--- LOG CRÍTICO

    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    api_endpoint = f"https://{domain}/{stage}"

    # Parsear payload
    try:
        body = event.get("body")
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body or {}
    except Exception as e:
        print("ERROR PARSE BODY:", e)
        return {"statusCode": 400, "body": "invalid body"}

    # Validación
    incident = payload.get("incident")
    if not incident:
        print("ERROR: no incident")
        return {"statusCode": 400, "body": "invalid payload"}

    # Agregar ID si falta
    if "incidentId" not in incident:
        import uuid
        incident["incidentId"] = str(uuid.uuid4())

    # Guardar en DynamoDB
    try:
        save_incident(incident)
    except Exception as e:
        print("ERROR SAVING INCIDENT:", e)
        return {"statusCode": 500, "body": "db error"}

    # SNS (según urgencia)
    urgency = incident.get("urgency", "low").lower()
    if urgency in ("medium", "high"):
        try:
            publish_sns(
                incident,
                subject=f"[{urgency.upper()}] Incidente {incident['incidentId']}",
            )
        except Exception as e:
            print("ERROR SNS:", e)

    # Broadcast
    conns = list_connections()
    stale = []

    for cid in conns:
        try:
            ok = post_to_connection(api_endpoint, cid, {
                "type": "incident_update",
                "incident": incident
            })
            if ok is False:
                stale.append(cid)

        except Exception as e:
            print(f"ERROR broadcast to {cid}:", e)
            stale.append(cid)

    # Limpiar conexiones muertas
    from src.utils import delete_connection
    for cid in stale:
        try:
            delete_connection(cid)
        except:
            pass

    return {"statusCode": 200, "body": "OK"}
