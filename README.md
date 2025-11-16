# 🛰️ Alerta UTEC – Módulo de Tiempo Real & Notificaciones

**WebSocket API + DynamoDB + SNS + Lambdas (Serverless Framework)**
Autor: *Persona C – Fabio Dávila*

Este módulo provee la infraestructura necesaria para **actualizaciones en tiempo real** y **notificaciones** del sistema Alerta UTEC.
El sistema permite:

* Enviar y recibir alertas en tiempo real vía **WebSocket**.
* Gestionar conexiones de clientes (autoridades, brigadistas, usuarios).
* Publicar notificaciones a **SNS** según nivel de urgencia.
* Almacenar incidentes y conexiones en **DynamoDB**.
* Emitir broadcast a todos los dispositivos conectados.

Este servicio está construido usando **Serverless Framework** + **AWS Lambda** + **API Gateway WebSocket**.

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

# 🚀 Despliegue

### 1. Requisitos

Instalar:

```bash
npm install -g serverless
pip install boto3
```

Tener credenciales de AWS configuradas:

```bash
aws configure
```

### 2. Instalar dependencias del proyecto

```bash
pip install -r requirements.txt
```

### 3. Desplegar

```bash
serverless deploy --stage dev --region us-east-1
```

### 4. Obtener el endpoint WebSocket

En la salida del deploy verás algo como:

```
wss://abc123def.execute-api.us-east-1.amazonaws.com/dev
```

Este endpoint será utilizado por frontend y otros microservicios.

---

# 🔧 ¿Qué recursos se crean?

El archivo `serverless.yml` crea automáticamente:

### **1. WebSocket API**

Con rutas:

* `$connect` – se registra el cliente.
* `$disconnect` – se elimina el cliente.
* `notify` – para enviar incidentes al sistema en tiempo real.

### **2. DynamoDB**

* **ConnectionsTable** → almacena `connectionId`.
* **IncidentsTable** → almacena incidentes recibidos por WebSocket.

### **3. SNS Topic**

* `AlertaUTECAlerts-dev`
  Se publican mensajes cuando un incidente tiene urgencia "medium" o "high".

### **4. Lambdas**

| Función      | Descripción                                                         |
| ------------ | ------------------------------------------------------------------- |
| `connect`    | Guarda el connectionId cuando un cliente se conecta                 |
| `disconnect` | Elimina connectionId al desconectarse                               |
| `notify`     | Procesa un incidente, lo guarda, lo publica en SNS y hace broadcast |

---

# 📡 Comunicación WebSocket

## Mensaje enviado desde el frontend o backend:

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

## Mensaje recibido por todos los clientes:

```json
{
  "type": "incident_update",
  "incident": { ... }
}
```

---

# 📲 Pruebas rápidas (local)

Puedes probar con **wscat**:

```bash
npm install -g wscat

wscat -c wss://tu-endpoint.execute-api.us-east-1.amazonaws.com/dev
```

Enviar incidente:

```json
{"action":"notify","incident":{"type":"falla de luz","urgency":"medium"}}
```

---

# 📨 Notificaciones por SNS

Los incidentes con:

* `urgency = "medium"`
* `urgency = "high"`

Se envían automáticamente a SNS.

Puedes:

* Suscribirte por email
* Suscribirte por SMS
* Conectar otra Lambda
* Enviar a un webhook (Slack/Discord)

Todo desde la consola de SNS.

---

# ⚙️ Flujo de Trabajo con GitHub

Sugerencia:

* Subir este repo a GitHub (`main`).
* Añadir un workflow CI/CD con Serverless (te lo puedo generar si quieres).
* Cada push a `main` → despliega automáticamente.

---

# 🛠️ Mantenimiento

### Logs

Verlos en CloudWatch:

```
/aws/lambda/alerta-utec-realtime-dev-connect
/aws/lambda/alerta-utec-realtime-dev-disconnect
/aws/lambda/alerta-utec-realtime-dev-notify
```

### Caché de conexiones

Si una conexión es inválida, la Lambda `notify` la limpia automáticamente.

---

# 📌 Siguientes Mejoras (opcional)

* Mapear `connectionId` ↔ `userId` para enviar alertas a usuarios específicos.
* Añadir autorizador JWT para `$connect`.
* Crear panel de monitoreo en tiempo real.
* Separar broadcast por roles (autoridades vs estudiantes).

---

# ✔️ Estado Actual del Módulo

Todo lo necesario para:

* Tiempo real con WebSocket
* Gestión de conexiones
* Almacenamiento de incidentes
* Notificaciones por urgencia
* Broadcast a todos los clientes

está **listo y desplegable**.