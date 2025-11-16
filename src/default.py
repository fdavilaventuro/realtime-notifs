def handler(event, context):
    # Se ejecuta cuando un cliente envía un mensaje sin 'action'
    return {
        "statusCode": 200,
        "body": "default route ok"
    }
