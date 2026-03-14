# APIs Fiscales España

Suite de tres APIs REST para el ecosistema fiscal español. Publicadas en RapidAPI, Zyla y APILayer. Diseñadas para integrarse en software de contabilidad, ERPs, aplicaciones para autónomos y gestorías.

## Demo en vivo

[adrianmoreno-dev.com/demo/apis-fiscales-spain](https://adrianmoreno-dev.com/demo/apis-fiscales-spain)

## APIs incluidas

### 1. Validador NIF/NIE/CIF (`/validador/` · puerto 8093)

Validación fiscal de identificadores españoles con soporte batch.

```
GET  /v1/validate?nif={valor}    Valida un NIF/NIE/CIF individual
POST /v1/batch                   Valida hasta 100 identificadores en lote
GET  /health
```

**Tipos soportados:** NIF (personas físicas), NIE (extranjeros residentes), CIF (sociedades)

**Respuesta:**
```json
{
  "nif": "12345678Z",
  "valid": true,
  "type": "NIF",
  "letter": "Z",
  "message": "NIF válido"
}
```

---

### 2. Generador de Facturas PDF (`/facturas/` · puerto 8094)

Genera facturas en PDF conformes con el formato español (Ley 37/1992 IVA).

```
POST /v1/invoice/generate    Genera factura PDF (devuelve base64)
POST /v1/invoice/validate    Valida estructura de una factura
GET  /health
```

**Campos soportados:** emisor/receptor (nombre, NIF, dirección), líneas de factura, tipos de IVA (0%, 4%, 10%, 21%), retención IRPF, número de serie, fecha de vencimiento.

**Generación:** ReportLab (Python) — PDF vectorial sin dependencias externas.

---

### 3. Calculadora IRPF (`/irpf/` · puerto 8095)

Cálculos fiscales para el IRPF español — trabajadores y autónomos.

```
POST /v1/autonomo/simulate    Simula cuota autónomo + IRPF anual
POST /v1/calculate            Calcula IRPF por tramos (base imponible)
POST /v1/salary               Calcula neto de salario bruto con retención
GET  /v1/communities          Listado de CCAA con tipos autonómicos
GET  /health
```

**Tramos IRPF 2024:** Aplica tabla estatal + autonómica según comunidad autónoma seleccionada.

## Autenticación (marketplaces)

| Plataforma | Header | Estado |
|-----------|--------|--------|
| RapidAPI | `X-RapidAPI-Proxy-Secret` | Activo |
| Zyla API Hub | `User-Agent: GuzzleHttp/7` | Activo |
| APILayer | `X-Apilayer-Secret` | Pendiente aprobación |

La autenticación es transparente — cada API detecta automáticamente la plataforma de origen.

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| API | FastAPI + Uvicorn |
| Validación | Pydantic v2 |
| PDF | ReportLab |
| Cálculos | Python puro (lógica fiscal) |
| Auth | Multi-marketplace (RapidAPI, Zyla, APILayer) |
| Frontend demo | Laravel + Blade |

## Estructura del repositorio

```
apis/
├── validador/
│   ├── api.py          FastAPI app
│   ├── router.py       Endpoints v1
│   ├── auth.py         Multi-marketplace auth
│   └── services/validators/
│       ├── nif.py      Lógica NIF/NIE/CIF
│       └── batch.py    Procesamiento en lote
├── facturas/
│   ├── api.py
│   ├── router.py
│   ├── auth.py
│   └── services/
│       └── pdf_generator.py   ReportLab
└── irpf/
    ├── api.py
    ├── router.py
    ├── auth.py
    └── services/
        ├── autonomo.py    Cuota autónomos
        ├── irpf.py        Tramos IRPF
        └── salary.py      Salario bruto→neto
```

## Instalación

```bash
# Requiere el venv compartido en /var/www/chatbot/venv
pip install fastapi uvicorn pydantic reportlab python-dotenv

# Configuración por API (ejemplo validador)
cd validador
cp .env.example .env
# RAPIDAPI_PROXY_SECRET=xxx
# ZYLA_ENABLED=true

# Desarrollo
uvicorn api:app --host 127.0.0.1 --port 8093 --reload

# Producción (systemd — 3 servicios)
sudo systemctl start apis-validador apis-facturas apis-irpf
```

## Servicios systemd

Cada API tiene su propio proceso independiente:
- `apis-validador.service` → puerto 8093
- `apis-facturas.service` → puerto 8094
- `apis-irpf.service` → puerto 8095
