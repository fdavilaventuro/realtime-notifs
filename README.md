# 🛰️ Alerta UTEC – Módulo de Tiempo Real & Notificaciones

**WebSocket API + DynamoDB + SNS + Lambdas (Serverless Framework)**
Autor: *Persona C – Fabio Dávila*

Este módulo implementa la capa de **tiempo real** y **notificaciones** del sistema Alerta UTEC.
Permite:

* Comunicación WebSocket en tiempo real.
* Broadcast instantáneo de incidentes a todos los clientes conectados.
* Gestión automática de conexiones (alta/baja).
* Publicación de notificaciones vía SNS según nivel de urgencia.
* Almacenamiento en DynamoDB.

---

# 📁 Estructura del Proyecto

```
realtime-notifs/
├─ serverless.yml
├─ requirements.txt
├─ README.md
├─ .gitignore
└─ src/
   ├─ utils.py
   ├─ connect.py
   ├─ disconnect.py
   └─ notify_incident.py
```

---

# 🚀 Deploy (SUPER SIMPLE)

Este proyecto está configurado para que el despliegue sea **1 solo comando**.

### 1. Clonar el repo

```bash
git clone <tu-repo>
cd realtime-notifs
```

### 2. Desplegar

```bash
sls deploy
```

¡Eso es todo!
No necesitas:

* `pip install`
* instalar requirements
* usar Docker
* crear recursos manualmente

El `serverless.yml` se encarga de todo.

---

# 🔧 ¿Qué recursos se crean automáticamente?

## 🟢 **WebSocket API**

Con rutas:

| Ruta          | Lambda          | Descripción                                   |
| ------------- | --------------- | --------------------------------------------- |
| `$connect`    | connect         | Registra el connectionId del cliente          |
| `$disconnect` | disconnect      | Lo elimina de DynamoDB                        |
| `notify`      | notify_incident | Procesa incidentes entrantes y hace broadcast |

## 🟢 **DynamoDB**

Tablas autogeneradas:

* **ConnectionsTable**
  Guarda `connectionId` de WebSocket.

* **IncidentsTable**
  Guarda incidentes enviados por frontend o backends.

## 🟢 **SNS Topic**

* `AlertaUTECAlerts-dev`
  Recibe notificaciones cuando un incidente tiene urgencia `medium` o `high`.

## 🟢 **Lambdas**

* `connect.py`
* `disconnect.py`
* `notify_incident.py`

Las dependencias de Python (ej. `boto3`) se instalan automáticamente vía plugin.

---

# 📡 Comunicación WebSocket

## Enviar incidente (desde frontend / backend / wscat)

```json
{
  "action": "notify",
  "incident": {
    "type": "incendio",
    "location": "Aula 101",
    "description": "Humo detectado",
    "urgency": "high",
    "status": "pendiente",
    "timestamp": "2025-11-16T12:00:00Z"
  }
}
```

## Recibido por **todos** los clientes conectados

```json
{
  "type": "incident_update",
  "incident": {...}
}
```

---

# 📨 Notificaciones SNS

El módulo publica automáticamente en SNS si:

* `urgency = "medium"`
* `urgency = "high"`

Puedes suscribirte con:

* Email
* SMS
* Otra Lambda
* Slack/Discord vía webhook
* Servicios externos

Todo desde la consola de Amazon SNS.

---

# 🔍 Logs y Debug

Ver logs en CloudWatch:

* `/aws/lambda/alerta-utec-realtime-dev-connect`
* `/aws/lambda/alerta-utec-realtime-dev-disconnect`
* `/aws/lambda/alerta-utec-realtime-dev-notify`

---

# ✔️ Estado del módulo

Este servicio está listo para:

✅ recibir incidentes
✅ hacer broadcast en tiempo real
✅ almacenar información
✅ generar notificaciones
✅ funcionar solo con `git clone` + `sls deploy`