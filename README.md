Listo, Mtro. Yarek. Aquí tienes el archivo en Markdown para descargar y también el contenido completo para **copiar y pegar**.

**[Descargar README_Binance_Postgres_Service.md](sandbox:/mnt/data/README_Binance_Postgres_Service_v2.md)**

---

```markdown
<!-- Encabezado centrado con badges -->
<h1 align="center">Binance-Postgres Service</h1>
<p align="center"><b>FastAPI + Tortoise ORM + PostgreSQL (async)</b></p>

<p align="center">
  <a href="#"><img alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white"></a>
  <a href="#"><img alt="FastAPI" src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white"></a>
  <a href="#"><img alt="PostgreSQL" src="https://img.shields.io/badge/DB-PostgreSQL-336791?logo=postgresql&logoColor=white"></a>
  <a href="#"><img alt="Async" src="https://img.shields.io/badge/Async-aiohttp%20%7C%20asyncio-2C3E50"></a>
  <a href="#"><img alt="ORM" src="https://img.shields.io/badge/ORM-Tortoise%20ORM-6E44FF"></a>
</p>

<p align="center">
  Servicio backend que <b>descarga velas OHLCV desde la API de Binance</b> y las <b>almacena en PostgreSQL</b> mediante una <b>API REST</b> asincrónica con FastAPI.
  <br/>Proyecto de portafolio orientado a backend: reproducible, explicable y fácil de extender.
</p>

---

## Tabla de contenidos
- [Narrativa: ¿Qué hace y cómo lo hace?](#narrativa-qué-hace-y-cómo-lo-hace)
- [Arquitectura](#arquitectura)
- [Stack (y por qué)](#stack-y-por-qué)
- [Características](#características)
- [Esquema de Datos (SQL & ORM)](#esquema-de-datos-sql--orm)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints](#endpoints)
- [Buenas prácticas y decisiones](#buenas-prácticas-y-decisiones)
- [Pruebas (sugerido)](#pruebas-sugerido)
- [Roadmap](#roadmap)
- [Docker Compose (opcional)](#docker-compose-opcional)
- [Licencia](#licencia)
- [Sobre este repo](#sobre-este-repo)

---

## Narrativa: ¿Qué hace y cómo lo hace?

**Historia corta:** quieres un **histórico confiable de velas (OHLCV)** de Binance en **tu propia base de datos** para análisis, ETL o ML. Este servicio lo resuelve así:

1) **Recibes una petición** a la API (`/fetch_and_store_data/{symbol}`) con parámetros como `interval`, `start_date`, `end_date`, `max_candles`.  
2) **Consultamos Binance** de forma asincrónica con `aiohttp`, respetando timeouts y reintentos.  
3) **Normalizamos la respuesta** a un esquema claro de velas: `open_time, open, high, low, close, volume, close_time, trades`, etc.  
4) **Insertamos en PostgreSQL** con `Tortoise ORM` y una **constraint única** `UNIQUE(symbol, interval, open_time)` para evitar duplicados (idempotencia).  
5) **Respondemos un resumen**: cuántas velas se insertaron, cuántas se omitieron por duplicado, rango temporal cubierto y el estado de la operación.

Resultado: un backend que **descarga, valida y guarda** datos de mercado listos para **ciencia de datos, dashboards, pipelines de ML o un bot** posterior.

---

## Arquitectura

```

```
      ┌─────────────┐        HTTP (async)        ┌───────────────┐
```

Request → │   FastAPI   │  ───────────────────────→  │  Binance API  │
└─────┬───────┘                            └───────────────┘
│
│  Models / Repos (Tortoise ORM async)
▼
┌─────────────┐     SQL (async)     ┌────────────────────┐
│  Services   │  ─────────────────→ │   PostgreSQL 12+   │
│  Layer      │  ←─────────────────  │ (índices únicos)   │
└─────────────┘                      └────────────────────┘

````

---

## Stack (y por qué)

- **FastAPI + Uvicorn** → rendimiento, tipado, OpenAPI, auto-docs.  
- **Tortoise ORM (async)** → modelos Python→SQL con consultas no bloqueantes; `unique_together` para idempotencia.  
- **PostgreSQL** → precisión numérica (`NUMERIC`) e integridad (índices, constraints).  
- **aiohttp** → cliente HTTP asincrónico con timeouts/backoff para Binance.  
- **pandas** → ayudante para normalización/validación cuando aplica.  
- **python-dotenv** → configuración segura y portable via `.env`.

---

## Características

- **Descarga** velas OHLCV por `symbol` y `interval` (1m, 15m, 1h, 1d…).  
- **Inserción segura** en PostgreSQL con `UNIQUE(symbol, interval, open_time)`.  
- **API REST** para insertar y listar **trades** y **historical prices**, y una ruta de **captura** hacia Binance.  
- **Async/await** end-to-end → menor latencia, mejor throughput.  
- **Documentación interactiva**: `/docs` (Swagger) y `/redoc`.

---

## Esquema de Datos (SQL & ORM)

**SQL (tabla `candle`)**
```sql
CREATE TABLE IF NOT EXISTS candle (
    id BIGSERIAL PRIMARY KEY,
    symbol        VARCHAR(15)   NOT NULL,
    interval      VARCHAR(8)    NOT NULL,
    open_time     TIMESTAMPTZ   NOT NULL,
    open          NUMERIC(20,8) NOT NULL,
    high          NUMERIC(20,8) NOT NULL,
    low           NUMERIC(20,8) NOT NULL,
    close         NUMERIC(20,8) NOT NULL,
    volume        NUMERIC(30,10) NOT NULL,
    close_time    TIMESTAMPTZ   NOT NULL,
    trades        INTEGER       NOT NULL,
    quote_volume        NUMERIC(30,10),
    taker_base_volume  NUMERIC(30,10),
    taker_quote_volume NUMERIC(30,10),
    created_at    TIMESTAMPTZ   DEFAULT NOW(),
    UNIQUE(symbol, interval, open_time)
);
````

**Tortoise ORM (equivalente)**

```python
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
```

---

## Instalación

```bash
# 1) Clonar
git clone https://github.com/oscar0rdz/ApiBinanceDB.git
cd ApiBinanceDB

# 2) Entorno
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) PostgreSQL (local o Docker)
# docker run --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
# docker exec -it pg psql -U postgres -c "CREATE DATABASE binance_db;"
```

---

## Configuración

Crea un archivo `.env` en la raíz (no lo subas a Git):

```ini
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
```

---

## Ejecución

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Docs**

* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Endpoints

<details>
<summary><b>Trades</b> — crear y listar</summary>

**POST /trades** — crea un trade (idempotente por `symbol+timestamp`)
**GET /trades** — lista trades (orden desc por fecha)

```bash
# Crear
curl -X POST "http://127.0.0.1:8000/trades" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","price":68000.0,"qty":0.01,"timestamp":"2025-01-01T00:00:00Z"}'

# Listar (paginado)
curl "http://127.0.0.1:8000/trades?limit=50&offset=0"
```

</details>

<details>
<summary><b>Historical Prices (OHLCV)</b> — insertar y consultar</summary>

**POST /historical_prices** — inserta un registro OHLCV
**GET /historical_prices** — lista velas (filtros por `symbol`, `interval`, `from`, `to`)

```bash
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

# Listar por rango
curl "http://127.0.0.1:8000/historical_prices?symbol=BTCUSDT&interval=15m&from=2021-01-01&to=2021-01-02&limit=200"
```

</details>

<details>
<summary><b>Binance Fetch</b> — descarga y guarda en DB</summary>

**GET /fetch_and_store_data/{symbol}**
Parámetros: `interval`, `start_date`, `end_date`, `max_candles`

```bash
curl "http://127.0.0.1:8000/fetch_and_store_data/BTCUSDT?interval=1h&start_date=2021-01-01&end_date=2021-02-01&max_candles=500"
```

**Respuesta típica**

```json
{
  "symbol": "BTCUSDT",
  "interval": "1h",
  "inserted": 480,
  "duplicates_skipped": 20,
  "status": "ok",
  "from": "2021-01-01T00:00:00Z",
  "to": "2021-02-01T00:00:00Z"
}
```

</details>

---

## Buenas prácticas y decisiones

* **Async end-to-end**: evitar bloqueos I/O y mejorar throughput.
* **Idempotencia por diseño**: `UNIQUE(symbol, interval, open_time)` evita duplicados.
* **Validación**: parseo estricto de fechas y numéricos (Pydantic/ORM).
* **Rate limits**: reintentos con backoff; timeouts definidos.
* **Observabilidad**: logs estructurados, métricas básicas de inserción/omisión.

---

## Pruebas (sugerido)

* **Unit**: servicios y repos (`pytest`, `pytest-asyncio`).
* **DB**: PostgreSQL en Docker o `testcontainers`.
* **API**: `httpx.AsyncClient` sobre la app FastAPI.

---

## Roadmap

* Jobs programados (APScheduler/Celery) para capturas periódicas.
* Endpoints de exportación (CSV/Parquet) para ciencia de datos/ML.
* Integración ML (entrenar modelos con OHLCV persistidos).
* Bot market maker (replay + live con colas de mensajes).

---

## Docker Compose (opcional)

```yaml
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
```

---

## Licencia

Proyecto personal con fines educativos/demostrativos. Úsalo y adáptalo; se agradece atribución cuando corresponda.

---

## Sobre este repo

“<b>Binance-Postgres Service</b>” demuestra habilidades de <b>backend</b>: diseño de servicios, <b>persistencia SQL</b>, asincronía y buenas prácticas en <b>APIs de datos</b>. Es una base clara para crecer hacia ETL/ML/automatización.

```
::contentReference[oaicite:0]{index=0}
```
