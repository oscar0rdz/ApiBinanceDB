# file: app/main.py (o main.py si lo prefieres en la raíz)

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
from dotenv import load_dotenv
import os
import uvicorn
import asyncio
import logging
import pandas as pd
import aiohttp
from datetime import datetime

# IMPORTA TUS MODELOS Y SCHEMAS
from app.models import Trade, HistoricalPrice
# from app.schemas import TradeSchema, HistoricalPriceSchema  # si lo usas

# Cargar variables de entorno
load_dotenv()

# Configuración logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializa FastAPI
app = FastAPI(title="Binance-Postgres Service",
              description="Servicio que conecta a Binance, descarga datos OHLCV y los almacena en PostgreSQL.")

# Config DB Tortoise
DATABASE_CONFIG = {
    'connections': {
        'default': 'postgres://{user}:{password}@{host}:{port}/{db}'.format(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", 5432),
            db=os.getenv("POSTGRES_DB")
        )
    },
    'apps': {
        'models': {
            'models': ['app.models'],  # Ajusta la ruta a tus modelos
            'default_connection': 'default',
        }
    }
}

register_tortoise(
    app,
    config=DATABASE_CONFIG,
    generate_schemas=True,  
    add_exception_handlers=True,
)

# --------------------------------------------------------------------------------
# Ejemplo de schemas Pydantic (podrías moverlos a un `schemas.py` propio)
# --------------------------------------------------------------------------------
class TradeSchema(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: str  # "YYYY-MM-DD HH:MM:SS"

class HistoricalPriceSchema(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: str

# --------------------------------------------------------------------------------
# Función utilitaria para insertar si no existe
# --------------------------------------------------------------------------------
async def store_data_if_not_exists(model, data_dict):
    async with in_transaction():
        symbol = data_dict['symbol']
        timestamp = pd.to_datetime(data_dict['timestamp'])
        existing_data = await model.filter(symbol=symbol, timestamp=timestamp).first()
        if existing_data:
            return False
        await model.create(**data_dict)
        return True

# --------------------------------------------------------------------------------
# Endpoints para Trades
# --------------------------------------------------------------------------------
@app.post("/trades/", tags=["Trades"])
async def create_trade(trade: TradeSchema):
    try:
        data_dict = trade.dict()
        success = await store_data_if_not_exists(Trade, data_dict)
        if success:
            return {"status": "Trade created successfully"}
        else:
            return {"status": "Trade already exists"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating trade: {e}")

@app.get("/trades/", tags=["Trades"])
async def get_trades():
    return await Trade.all().order_by("-timestamp")

# --------------------------------------------------------------------------------
# Endpoints para Historical Prices
# --------------------------------------------------------------------------------
@app.post("/historical_prices/", tags=["HistoricalPrices"])
async def create_historical_price(price: HistoricalPriceSchema):
    try:
        data_dict = price.dict()
        success = await store_data_if_not_exists(HistoricalPrice, data_dict)
        if success:
            return {"status": "Historical price created successfully"}
        else:
            return {"status": "Historical price already exists"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating historical price: {e}")

@app.get("/historical_prices/", tags=["HistoricalPrices"])
async def list_historical_prices():
    return await HistoricalPrice.all().order_by("-timestamp")

# --------------------------------------------------------------------------------
# Funciones internas de fetch de datos (versión simplificada, sin indicadores)
# --------------------------------------------------------------------------------
async def fetch_klines_from_binance(symbol: str, interval: str, start_ts: int, end_ts: int, limit=1000):
    """Descarga un lote de velas desde Binance API (ENDPOINT SPOT)."""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_ts,
        'endTime': end_ts,
        'limit': limit
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            return data if isinstance(data, list) else []

async def get_historical_data_raw(symbol: str, interval: str, start_date: str, end_date: str, max_candles: int):
    """Descarga OHLCV en bruto sin calcular indicadores."""
    try:
        start_ts = int(pd.to_datetime(start_date).timestamp() * 1000)
        end_ts = int(pd.to_datetime(end_date).timestamp() * 1000)
        limit = 1000
        all_klines = []
        total_fetched = 0

        # Calcular el delta en milisegundos según interval
        interval_ms = interval_to_milliseconds(interval)

        while total_fetched < max_candles and start_ts < end_ts:
            batch = await fetch_klines_from_binance(symbol, interval, start_ts, end_ts, limit)
            if not batch:
                break
            all_klines.extend(batch)
            total_fetched += len(batch)
            # Avanza el start_ts para la próxima tanda
            last_open_time = batch[-1][0]  # en ms
            start_ts = last_open_time + interval_ms
            await asyncio.sleep(0.2)

        if not all_klines:
            return pd.DataFrame()

        df = pd.DataFrame(all_klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
        return df
    except Exception as e:
        logging.error(f"Error en get_historical_data_raw: {e}", exc_info=True)
        return pd.DataFrame()

def interval_to_milliseconds(interval: str) -> int:
    """Convierte un string (1m, 15m, 1h, etc.) a milisegundos."""
    unit = interval[-1]
    value = int(interval[:-1])
    if unit == 'm':
        return value * 60_000
    elif unit == 'h':
        return value * 3_600_000
    elif unit == 'd':
        return value * 86_400_000
    elif unit == 'w':
        return value * 604_800_000
    elif unit == 'M':
        # Esto es aproximado (1 mes ~ 30 días):
        return value * 2_592_000_000
    else:
        raise ValueError(f"Intervalo no soportado: {interval}")

# --------------------------------------------------------------------------------
# Endpoint para descargar datos y guardarlos en HistoricalPrice
# --------------------------------------------------------------------------------
@app.get("/fetch_and_store_data/{symbol}", tags=["Binance"])
async def fetch_and_store_data(
    symbol: str,
    interval: str = Query("15m"),
    start_date: str = Query("2020-01-01"),
    end_date: str = Query("2025-01-01"),
    max_candles: int = Query(1000)
):
    """
    Descarga datos OHLCV desde Binance (sin indicadores) y guarda en la DB.
    """
    try:
        df_raw = await get_historical_data_raw(symbol, interval, start_date, end_date, max_candles)
        if df_raw.empty:
            return {"message": f"No se obtuvieron datos para {symbol} con ese rango."}
        
        inserted_count = 0
        for _, row in df_raw.iterrows():
            data_dict = {
                "symbol": symbol,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
                "timestamp": str(row["open_time"])
            }
            success = await store_data_if_not_exists(HistoricalPrice, data_dict)
            if success:
                inserted_count += 1

        return {
            "message": "Datos descargados y almacenados correctamente.",
            "total_fetched": len(df_raw),
            "inserted_new": inserted_count
        }
    except Exception as e:
        logging.error(f"Error al descargar/almacenar datos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------------------------------------
# Arranque local
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
