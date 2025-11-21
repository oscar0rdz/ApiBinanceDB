Binance-Postgres Service · FastAPI + Tortoise ORM + PostgreSQL (async)










Un servicio backend que descarga velas OHLCV desde la API de Binance y las almacena de forma segura en PostgreSQL, exponiendo una API REST moderna con FastAPI (async). Diseñado y documentado para reclutadores y equipos backend: reproducible, explicable y fácil de extender.



Ingesta confiable de datos de mercado (OHLCV) desde Binance.

Persistencia en PostgreSQL con idempotencia (sin duplicados) y esquema explícito.

API REST lista para integrar: inserta, lista y dispara capturas directamente desde la API.

Diseño asincrónico (FastAPI + aiohttp) para concurrencia y buen throughput sin bloquear.

Base sólida de portafolio: separa capas, explica decisiones y deja espacio para crecer (ETL, ML, bots).

Arquitectura (visión rápida)
          ┌─────────────┐        HTTP (async)        ┌───────────────┐
Request → │   FastAPI   │  ───────────────────────→  │  Binance API  │
          └─────┬───────┘                            └───────────────┘
                │
                │  Models / Repos (async Tortoise ORM)
                ▼
          ┌─────────────┐     SQL (async)     ┌────────────────────┐
          │  Service    │  ─────────────────→ │   PostgreSQL 12+   │
          │  Layer      │  ←─────────────────  │ (índices únicos)   │
          └─────────────┘                      └────────────────────┘


Claves técnicas

FastAPI: OpenAPI automático, validación y rendimiento.

Tortoise ORM (async): modelos/tables y consultas no bloqueantes.

aiohttp: cliente HTTP asincrónico para Binance.

PostgreSQL: tipos numéricos precisos y índices únicos para deduplicar.

Características principales

Descarga de datos desde Binance: velas OHLCV por symbol/interval (1m, 15m, 1h, 1d…).

Inserción segura: verifica existencia previa y evita duplicados por (symbol, interval, open_time).

API REST:

POST /trades · GET /trades

POST /historical_prices · GET /historical_prices

GET /fetch_and_store_data/{symbol} (dispara captura y guarda)

Async/await end-to-end: mejor uso de I/O y latencia.

Configuración por .env: credenciales y parámetros sin exponer secretos.

Documentación interactiva: /docs (Swagger) y /redoc.

Stack (y por qué)

FastAPI + Uvicorn: rendimiento, tipado y OpenAPI “gratis” → acelera integraciones.

Tortoise ORM (async): modelos Python → SQL sin fricción; unique_together para idempotencia.

PostgreSQL: robusto en producción, tipos NUMERIC, índices y constraints.

aiohttp: cliente HTTP no bloqueante para ráfagas controladas a Binance.

pandas: reshape/validación rápida de OHLCV cuando aplica.

python-dotenv: configuración segura sin “quemar” credenciales.

Estructura de proyecto (sugerida)
.
├── app/
│   ├── main.py                # FastAPI app (routers, lifecycle)
│   ├── models.py              # Tortoise ORM models (Candle, Trade, etc.)
│   ├── schemas.py             # Pydantic schemas (request/response)
│   ├── binance_client.py      # Cliente aiohttp para Binance (retry, rate-limit)
│   ├── services.py            # Lógica de negocio (upserts, validación)
│   ├── repositories.py        # Accesos DB (consultas ORM)
│   ├── utils.py               # Helpers (parsers, fechas, validaciones)
│   └── config.py              # Carga de .env
├── tests/                     # (Espacio para pruebas; ver “Pruebas”)
├── ML/                        # (Opcional) bases para futuros modelos
├── requirements.txt
├── .env.example               # Variables de entorno (sin secretos)
├── .gitignore
└── README.md

Esquema de base de datos (PostgreSQL)

Modelo de velas OHLCV con índice único para deduplicar:

CREATE TABLE IF NOT EXISTS candle (
    id BIGSERIAL PRIMARY KEY,
    symbol        VARCHAR(15)  NOT NULL,
    interval      VARCHAR(8)   NOT NULL,
    open_time     TIMESTAMPTZ  NOT NULL,
    open          NUMERIC(20,8) NOT NULL,
    high          NUMERIC(20,8) NOT NULL,
    low           NUMERIC(20,8) NOT NULL,
    close         NUMERIC(20,8) NOT NULL,
    volume        NUMERIC(30,10) NOT NULL,
    close_time    TIMESTAMPTZ   NOT NULL,
    trades        INTEGER       NOT NULL,
    quote_volume  NUMERIC(30,10),
    taker_base_volume  NUMERIC(30,10),
    taker_quote_volume NUMERIC(30,10),
    created_at    TIMESTAMPTZ   DEFAULT NOW(),
    UNIQUE(symbol, interval, open_time)
);


Tortoise ORM (equivalente conceptual):

from tortoise import fields, models

class Candle(models.Model):
    id = fields.BigIntField(pk=True)
    symbol = fields.CharField(max_length=15)
    interval = fields.CharField(max_length=8)
    open_time = fields.DatetimeField()
    open = fields.DecimalField(max_digits=20, decimal_places=8)
    high = fields.DecimalField(max_digits=20, decimal_places=8)
    low = fields.DecimalField(max_digits=20, decimal_places=8)
    close = fields.DecimalField(max_digits=20, decimal_places=8)
    volume = fields.DecimalField(max_digits=30, decimal_places=10)
    close_time = fields.DatetimeField()
    trades = fields.IntField()
    quote_volume = fields.DecimalField(max_digits=30, decimal_places=10, null=True)
    taker_base_volume = fields.DecimalField(max_digits=30, decimal_places=10, null=True)
    taker_quote_volume = fields.DecimalField(max_digits=30, decimal_places=10, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("symbol", "interval", "open_time")

Requerimientos

Python 3.9+

PostgreSQL 12+

(opcional) virtualenv / conda

Dependencias clave: fastapi, uvicorn, tortoise-orm, aiohttp, pandas, python-dotenv.

Instalación
# 1) Clonar
git clone https://github.com/oscar0rdz/ApiBinanceDB.git
cd ApiBinanceDB

# 2) Entorno
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) PostgreSQL listo (local o Docker)
#    Crea DB y usuario con permisos. Ejemplo rápido con Docker:
# docker run --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
# docker exec -it pg psql -U postgres -c "CREATE DATABASE binance_db;"


Configura tu .env (no lo subas a Git):

POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=binance_db

# Opcionales
BINANCE_BASE_URL=https://api.binance.com
DEFAULT_INTERVAL=15m
REQUEST_TIMEOUT=20
MAX_CANDLES=1000

Cómo ejecutar
# App en modo desarrollo (recarga automática)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload


Documentación interactiva

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

Endpoints
1) Trades

POST /trades — crea un trade (idempotente por symbol+timestamp del lado del modelo)
GET /trades — lista trades (orden desc por fecha)

Ejemplos:

# Crear
curl -X POST "http://127.0.0.1:8000/trades" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","price":68000.0,"qty":0.01,"timestamp":"2025-01-01T00:00:00Z"}'

# Listar (paginado)
curl "http://127.0.0.1:8000/trades?limit=50&offset=0"

2) Historical Prices (OHLCV)

POST /historical_prices — inserta un registro OHLCV
GET /historical_prices — lista velas (filtros por symbol, interval, from, to)

# Crear manualmente una vela
curl -X POST "http://127.0.0.1:8000/historical_prices" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "interval": "15m",
    "open_time": "2021-01-01T00:00:00Z",
    "open": 29000.0, "high": 29100.0, "low": 28900.0, "close": 29050.0,
    "volume": 123.45, "close_time": "2021-01-01T00:15:00Z", "trades": 100
  }'

# Listar por rango de fechas
curl "http://127.0.0.1:8000/historical_prices?symbol=BTCUSDT&interval=15m&from=2021-01-01&to=2021-01-02&limit=200"

3) Binance Fetch (descarga y guarda)

GET /fetch_and_store_data/{symbol}
Descarga OHLCV de Binance y guarda en DB. Parámetros de query:
interval, start_date, end_date, max_candles.

curl "http://127.0.0.1:8000/fetch_and_store_data/BTCUSDT?interval=1h&start_date=2021-01-01&end_date=2021-02-01&max_candles=500"


Respuesta típica

{
  "symbol": "BTCUSDT",
  "interval": "1h",
  "inserted": 480,
  "duplicates_skipped": 20,
  "status": "ok",
  "from": "2021-01-01T00:00:00Z",
  "to": "2021-02-01T00:00:00Z"
}

Decisiones de diseño (explicables)

Async end-to-end: fastapi + aiohttp + tortoise evitan bloquear I/O → mejor latencia bajo múltiples descargas.

Idempotencia por constraint: UNIQUE(symbol, interval, open_time) garantiza no duplicar velas; del lado del código, se hace upsert o skip.

Validación: pydantic en entrada/salida; conversiones estrictas de fechas y numéricos.

Rate-limit y reintentos: cliente aiohttp con timeouts, backoff y manejo de 429/5xx.

Paginación & filtros: limit/offset, symbol, interval, rangos from/to.

Observabilidad: logging estructurado (nivel INFO/ERROR), tiempos de respuesta, contadores de registros insertados/omitidos.

Pruebas (sugerido)

Unit: servicios y repos con pytest, pytest-asyncio.

DB: usando PostgreSQL en Docker para pruebas reales (o testcontainers), fixtures limpias por test.

API: httpx.AsyncClient sobre la app FastAPI.

Seguridad y configuración

No subas .env ni credenciales. Usa .env.example.

Revisa CORS si expones públicamente.

Para producción: variables de entorno + conexiones TLS a DB.

Si guardas evidencias (gráficas, GIF/PNG), considera Git LFS.

Roadmap (próximos pasos)

Jobs programados (APScheduler/Celery) para capturas periódicas.

Export endpoints (CSV/Parquet) para ciencia de datos/ML.

Integración ML (entrenar con los OHLCV persistidos).

Bot market maker (replay + live con colas de mensajes).

Cómo correr en Docker (opcional)

docker-compose.yml (ejemplo mínimo)

version: "3.8"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: binance_db
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
  api:
    build: .
    env_file: .env
    depends_on: [db]
    ports: ["8000:8000"]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
volumes:
  pgdata:

Licencia

Proyecto personal con fines educativos y de demostración. Puedes usarlo y adaptarlo; agradezco atribución cuando corresponda.

Sobre el proyecto

“Binance-Postgres Service” es un backend async con FastAPI que conecta a la API de Binance, descarga OHLCV y persiste en PostgreSQL con idempotencia. Es base de futuros módulos (ML y market maker) y prueba mis habilidades de diseño de servicios, persistencia, concurrencia y buenas prácticas en APIs de datos.

Comandos rápidos
# run dev
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# insertar desde Binance
curl "http://127.0.0.1:8000/fetch_and_store_data/BTCUSDT?interval=15m&start_date=2021-01-01&end_date=2021-02-01&max_candles=1000"

# listar por filtros
curl "http://127.0.0.1:8000/historical_prices?symbol=BTCUSDT&interval=15m&from=2021-01-01&to=2021-01-07&limit=100"
