# Global Config Service

A Flask microservice for managing global configuration settings across the Godaampe platform. It provides REST API endpoints to create, update, and retrieve per-user configuration records stored in MySQL, protected by JWT authentication and Redis session validation.

## Tech Stack

| Component | Version |
|---|---|
| Python | 3.12 |
| Flask | 2.3.3 |
| Flask-Smorest | 0.41.0 |
| Flask-SQLAlchemy | 3.0.5 |
| Flask-JWT-Extended | 4.5.2 |
| Marshmallow | 3.20.1 |
| Redis | 5.0.0 |
| PyMySQL | 1.1.0 |
| python-dotenv | 1.0.0 |

## Project Structure

```
godaampe-config-service/
├── config/
│   ├── extentions/
│   │   ├── db.py                    # SQLAlchemy instance
│   │   └── redis_client.py          # Redis client instance
│   ├── models/
│   │   └── global_config_model.py   # GLBCONFIG ORM model
│   ├── schemas/
│   │   └── global_config_schema.py  # Marshmallow request/response schema
│   └── resources/
│       └── global_config.py         # POST /glbconfig and GET /glbconfig endpoints
├── tests/
│   └── test_global_config.py        # Unit tests (20+ cases)
├── main.py                          # Flask app factory
├── run.py                           # Entry point
├── requirements.txt
├── sample_payload.json              # Example POST body
├── Dockerfile                       # Multi-stage production build
├── docker-compose.yml               # MySQL + Redis + app services
├── Makefile                         # Convenience commands
├── .env.example                     # Environment variable template
└── .gitignore
```

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- Redis 7+

> For local development without Docker, SQLite can be used instead of MySQL (see [Development Notes](#development-notes)).

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd godaampe-config-service
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Then edit .env with your values
```

See [Environment Variables](#environment-variables) for the full list.

## Running the Application

```bash
python run.py
```

The service starts at `http://localhost:5000`.

| URL | Description |
|---|---|
| `GET /health` | Health check |
| `POST /glbconfig` | Save / update config |
| `GET /glbconfig` | Retrieve config |
| `GET /swagger-ui` | Interactive API docs |
| `GET /openapi.json` | OpenAPI schema |

## API Reference

### Health Check

```
GET /health
```

**Response 200**

```json
{ "status": "healthy", "service": "global-config-service" }
```

---

### Save / Update Global Config

```
POST /glbconfig
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

Creates a new config record for the authenticated user, or updates it if one already exists.

**Response 201** — returns the saved config object.

**Error responses**

| Code | Reason |
|---|---|
| 400 | Validation error or duplicate key |
| 401 | Missing / invalid JWT or expired Redis session |
| 500 | Database error |

---

### Retrieve Global Config

```
GET /glbconfig
Authorization: Bearer <JWT_TOKEN>
```

**Response 200** — returns the config object for the authenticated user.  
**Response 404** — no config found for this user.

---

### Sample Request Body

```json
{
  "DAYSBEFORENOTBEFORE": 5,
  "DAYSBEFORENOTAFTER": 10,
  "ALLOWHANDPICK": 1,
  "ALLOWOVERPICK": 0,
  "INVGENMETHOD": "AUTO",
  "PDTCOMPORT": "COM1",
  "PDTCOMSPEED": 9600,
  "LABELPRINTERNAME": "Zebra ZT230",
  "SCMLABELFORMAT": "SCM_DEFAULT",
  "CHECKEVERYMINUTES": 15,
  "ALLOWSPLITBYSTORE": 1,
  "MAXIMUMSPLITS": 3,
  "BACKUPAFTERSHUTDOWN": 1,
  "BACKUPCOMMAND": "backup.sh"
}
```

See [`sample_payload.json`](sample_payload.json) for a full example with all 70+ fields.

## Configuration Fields

### General

| Field | Type | Description |
|---|---|---|
| `DAYSBEFORENOTBEFORE` | SmallInt | Days before not-before date to show orders |
| `DAYSBEFORENOTAFTER` | SmallInt | Days before not-after date to show orders |
| `ALLOWHANDPICK` | 0/1 | Enable hand-picking |
| `ALLOWOVERPICK` | 0/1 | Allow picking over quantity |
| `ALLOWPICKBYPRODWOSCAN` | 0/1 | Allow picking without barcode scan |
| `THIRDPARTYPACKER` | 0/1 | Enable third-party packer |
| `INVGENMETHOD` | String(30) | Invoice generation method |
| `HIGHLIGHTDAYS` | SmallInt | Number of days for highlight alerts |
| `DAYSTOSHOW` | SmallInt | Days to show completed orders |
| `DAYSTOSHOWDISCARDED` | SmallInt | Days to show discarded orders |
| `DAYSTOSHOWCANCELLED` | SmallInt | Days to show cancelled orders |
| `ALLOWORDERFORWARDING` | 0/1 | Enable order forwarding |
| `SHOWCOSTPRICE` | 0/1 | Display cost price |

### PDT / Label Printer

| Field | Type | Description |
|---|---|---|
| `DISPLAYRACKLOCNONPDT` | 0/1 | Show rack location on PDT |
| `PDTCOMPORT` | String(6) | PDT serial port |
| `PDTCOMSPEED` | Integer | PDT baud rate |
| `PRINTASMICROSOFTPDF` | 0/1 | Print via Microsoft PDF driver |
| `PRINTERNAME` | String(24) | Default printer name |
| `PRINTERCOMPORT` | String(6) | Printer serial port |
| `LABELPRINTERNAME` | String(80) | Label printer name |
| `MC3000PORTNO` | String(24) | MC3000 device port |

### Label Formats

| Field | Type |
|---|---|
| `SCMLABELFORMAT` | String(20) |
| `PRICELABELFORMAT` | String(20) |
| `CTNLABELFORMAT` | String(20) |
| `RATIOPACKLABELFORMAT` | String(20) |
| `TRADEUNITLABELFORMAT` | String(20) |
| `TRADEUNITLABELFORMAT2` | String(20) |
| `BULKPALLETLABELFORMAT` | String(20) |
| `PRODUCEORDERLABELFORMAT` | String(20) |
| `ALLOWTUNPREFIX0AND9` | 0/1 |

### EDI

| Field | Type | Description |
|---|---|---|
| `DEFAULTSENDMETHODKEY` | String(12) | Default EDI send method |
| `CHECKEVERYMINUTES` | Integer | EDI polling interval (minutes) |

### Splits

| Field | Type | Description |
|---|---|---|
| `ALLOWSPLITBYSTORE` | 0/1 | Enable store-based splitting |
| `MAXIMUMSPLITS` | Integer | Maximum number of splits |

### New Orders

| Field | Type | Description |
|---|---|---|
| `NEWORDERACTION` | SmallInt | Action on new order receipt |
| `DISPLAYNEWORDERFLAG` | 0/1 | Show new order flag |
| `CLEARNEWORDFLGONCMD` | 0/1 | Clear flag on command |
| `CLEARNEWORDFLGONDISP` | 0/1 | Clear flag on dispatch |
| `CLEARNEWORDFLGONPRNT` | 0/1 | Clear flag on print |

### Completed Orders

| Field | Type | Description |
|---|---|---|
| `COMPLETEQN1REQ` – `COMPLETEQN5REQ` | 0/1 | Require confirmation questions 1–5 |
| `COMPLETEPWREQ` | 0/1 | Require password on completion |

### External

| Field | Type | Description |
|---|---|---|
| `ACCTCONFREQ` | 0/1 | Require account confirmation |
| `ALLOWACCTORDVALIDATION` | 0/1 | Enable account order validation |
| `EXTDLLNAME` | String(60) | External DLL filename |
| `AUTOIMPORTEXTORD` | 0/1 | Auto-import external orders |

### Shutdown / Backup

| Field | Type | Description |
|---|---|---|
| `BACKUPAFTERSHUTDOWN` | 0/1 | Run backup on shutdown |
| `BACKUPCOMMAND` | String(60) | Backup shell command |
| `BACKUPPROGRAM` | String(60) | Backup program path |

## Environment Variables

```env
# Flask
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database (option A — full connection string)
DATABASE_URL=mysql+pymysql://user:password@host:3306/godaampe_config

# Database (option B — individual components, used if DATABASE_URL is not set)
MYSQL_USER=config_user
MYSQL_PASSWORD=config_password
DB_HOST=localhost
DB_PORT=3306
MYSQL_DATABASE=godaampe_config

# JWT (must match the issuing auth service)
JWT_SECRET_KEY=your_jwt_secret_key_here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Testing

### Run all tests

```bash
python -m unittest tests.test_global_config -v
```

### Run a single test

```bash
python -m unittest tests.test_global_config.GlobalConfigTestCase.test_post_create_global_config -v
```

### Coverage report

```bash
coverage run --source=config -m unittest discover -s tests -p "test_*.py"
coverage report -m
```

### What is tested

- POST creates new config (201)
- POST updates existing config (201)
- GET returns config (200)
- GET returns 404 when no config exists
- JWT validation — missing token, malformed header
- Redis session validation — expired session, token mismatch, invalid JSON in cache
- Marshmallow field validation — boolean (0/1), string, integer
- Database error handling — `IntegrityError` (400), `SQLAlchemyError` (500)

## Docker

See [DOCKER.md](DOCKER.md) for full Docker and docker-compose documentation.

Quick start:

```bash
make build
make up
```

Or to run the container against an existing network:

```bash
docker run -d \
  --name config \
  --network user_service_default \
  -p 5004:5000 \
  --env-file .env \
  global-config:v1
```

## Development Notes

### Using SQLite locally

Set the following in your `.env` (or override in `main.py`) to avoid needing MySQL during local development:

```env
DATABASE_URL=sqlite:///data/config_data.db
```

### Creating / recreating tables

```python
from main import create_app
app = create_app()
with app.app_context():
    from config.extentions import db
    db.create_all()
```

## Error Reference

| HTTP Code | Meaning |
|---|---|
| 200 | Successful GET |
| 201 | Config created / updated |
| 400 | Validation error or integrity violation |
| 401 | Invalid JWT or expired Redis session |
| 404 | Config not found for this user |
| 500 | Unexpected database error |

## Security

- All endpoints except `GET /health` require a valid JWT in the `Authorization: Bearer` header.
- The JWT identity is validated against a Redis-cached session (`session:{user_id}`) to prevent replay attacks with revoked tokens.
- CORS is restricted to origins listed in `ALLOWED_ORIGINS`.
- All database queries go through SQLAlchemy ORM (parameterised) — no raw SQL string formatting.

## License

[Your License Here]
