# 📘 **README — Alerta UTEC Realtime (Tiempo Real & Notificaciones)**

## 🚀 Descripción General

Este módulo implementa la capa de **Tiempo Real y Notificaciones** para el sistema *Alerta UTEC*.
Se encarga de:

* WebSocket API para comunicación en tiempo real
* Gestión automática de conexiones (connect / disconnect)
* Envío de notificaciones broadcast a todos los clientes
* Persistencia de incidentes en DynamoDB
* Envío de alertas por **SNS** según urgencia
* Lambda Functions serverless (Python 3.13)

Este componente funciona de manera independiente y se integra sin fricción con frontend, backend, y pipelines (Airflow).

---

## 🏗 Arquitectura

```
Cliente Web
     ▲
     │ WebSocket (wss)
     ▼
Amazon API Gateway (WebSocket API)
     ├── $connect       → Lambda connect.py
     ├── $disconnect    → Lambda disconnect.py
     ├── notify         → Lambda notify_incident.py
     └── $default       → Lambda default.py
     
Lambdas acceden a:
     ├── DynamoDB: Connections (connectionId por cliente)
     ├── DynamoDB: Incidents (historial de incidentes)
     └── SNS Topic: alerta-utec-realtime-alarms
```

---

## 📁 Estructura del Proyecto

```
realtime-notifs/
│
├── serverless.yml
├── requirements.txt
├── README.md
├── .gitignore
│
└── src/
    ├── connect.py
    ├── disconnect.py
    ├── notify_incident.py
    ├── default.py
    └── utils.py
```

---

## ⚡ Despliegue (solo dos comandos)

Requisitos previos:

* Serverless Framework instalado
* AWS CLI configurado
* NodeJS 18+
* Cuenta AWS con permisos

### 1️⃣ Clonar el repositorio

```bash
git clone <este-repo>
cd realtime-notifs
```

### 2️⃣ Deploy

```bash
sls deploy
```

**Eso es todo.**
Serverless empaqueta dependencias, crea tablas DynamoDB, tópico SNS, WebSocket API y Lambdas.

Tras desplegar, verás algo como:

```
endpoint: wss://xxxxxxx.execute-api.us-east-1.amazonaws.com/dev
functions:
  connect
  disconnect
  notify
  default
```

---

## 🧪 Pruebas

### 1️⃣ Probar conexión WebSocket

Puedes usar **Postman** o **wscat**.

#### Conectar

```
wss://xxxxxxx.execute-api.us-east-1.amazonaws.com/dev
```

Si funciona, deberías ver:

```
Connected (101 Switching Protocols)
```

---

### 2️⃣ Probar broadcast en tiempo real

Abre **dos clientes WebSocket** (dos pestañas de Postman o Postman + wscat).

Envía desde uno:

```json
{
  "action": "notify",
  "incident": {
    "type": "prueba",
    "location": "Laboratorio A",
    "description": "Mensaje de prueba en tiempo real",
    "urgency": "high",
    "status": "pendiente",
    "timestamp": "2025-11-16T18:12:00Z"
  }
}
```

#### Resultado esperado:

* **Ambos clientes** reciben:

```json
{
  "type": "incident_update",
  "incident": { ... }
}
```

* DynamoDB registra el incidente
* SNS envía un correo si urgencia = medium/high

---

## ✉️ Suscribirse a SNS por Email

1. Ir a **AWS SNS**
2. Menú → Topics
3. Abrir:

```
alerta-utec-realtime-alarms
```

4. Click → **Create Subscription**
5. Protocol: Email
6. Endpoint: tu correo
7. Confirmar desde el email recibido

### Probar notificación medium

```json
{
  "action": "notify",
  "incident": {
    "type": "temperatura elevada",
    "location": "Laboratorio B",
    "description": "Temperatura del servidor por encima de 70°C",
    "urgency": "medium",
    "status": "pendiente",
    "timestamp": "2025-11-16T19:20:00Z"
  }
}
```

**Debes recibir un correo automático.**

---

## 🗄 Tablas DynamoDB creadas automáticamente

### 1️⃣ Connections

Almacena conectados vía WebSocket:

| connectionId | timestamp |
| ------------ | --------- |

### 2️⃣ Incidents

Guarda incidentes enviados:

| incidentId | type | location | urgency | timestamp | ... |

---

## 🧩 Utilidades (`utils.py`)

Incluye:

* `save_connection()`
* `delete_connection()`
* `list_connections()`
* `post_to_connection()`
* `save_incident()`
* `publish_sns()`

Todo centralizado y limpio.

---

## 🏁 Estado final

✔ WebSocket funcionando
✔ Broadcast multi-cliente
✔ DynamoDB persistente
✔ SNS notificaciones funcionales
✔ Deploy con un solo comando
✔ Import fix aplicado
✔ Probado con Postman + wscat
✔ Estructura limpia para mantenimiento