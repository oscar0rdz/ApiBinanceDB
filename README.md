
Binance-Postgres Service
Este proyecto personal fue desarrollado para demostrar mis habilidades en el desarrollo backend y manejo de bases de datos.
Se conecta a la API de Binance, descarga datos OHLCV (candlestick) de criptomonedas y los almacena en una base de datos PostgreSQL utilizando FastAPI y Tortoise ORM.

Nota personal: Este proyecto forma parte de mi portafolio y es la base sobre la que he desarrollado ideas para futuros proyectos, incluyendo un modelo de aprendizaje automático (machine learning) y un bot market maker. ¡Espero que te resulte interesante!

Tabla de Contenido
Características
Requerimientos
Instalación
Configuración
Estructura del Proyecto
Cómo Usar
Ejecutar la API
Endpoints Disponibles
Licencia
Próximos Pasos
Características
Descarga de datos desde Binance
Permite obtener velas (OHLCV) de criptomonedas para intervalos específicos (ej.: 1m, 15m, 1h, etc.).

Almacenamiento en PostgreSQL
Guarda los datos descargados en tablas de la base de datos para un análisis posterior o para alimentar modelos de Machine Learning.

API REST con FastAPI
Ofrece endpoints para crear y listar:

Trades
Precios históricos (Historical Prices)
Con documentación interactiva accesible en /docs y /redoc.
Inserción segura
Verifica la existencia previa de datos para evitar duplicados, manteniendo la integridad de la base de datos.

Diseño asincrónico
Se aprovecha async/await junto con aiohttp para optimizar las consultas a la API de Binance sin bloquear el sistema.

Requerimientos
Python 3.9+
PostgreSQL 12+
Entorno virtual (recomendado para gestionar dependencias de forma aislada)
Git
Dependencias Clave
FastAPI
Uvicorn
Tortoise ORM
aiohttp
pandas
python-dotenv
Por qué estas dependencias:

FastAPI y Uvicorn permiten construir y servir una API rápida y escalable.
Tortoise ORM simplifica el manejo de la base de datos mediante modelos asincrónicos.
aiohttp se utiliza para realizar peticiones HTTP de forma no bloqueante, fundamental para consumir la API de Binance.
pandas facilita el procesamiento y análisis de los datos descargados.
python-dotenv asegura una gestión segura y sencilla de las variables de entorno.
Instalación
Clona el repositorio:

bash
Copiar
git clone https://github.com/oscar0rdz/ApiBinanceDB.git
cd ApiBinanceDB
Crea un entorno virtual (opcional, pero recomendado):

bash
Copiar
python -m venv venv
source venv/bin/activate  # En MacOS/Linux
# En Windows:
# venv\Scripts\activate
Instala las dependencias:

bash
Copiar
pip install -r requirements.txt
Configura PostgreSQL:

Crea una base de datos (por ejemplo, binance_db).
Asegúrate de tener un usuario y contraseña con los permisos adecuados.
Configuración
El proyecto utiliza variables de entorno para la configuración de la base de datos y otros ajustes sensibles.
Se usa python-dotenv para cargar automáticamente los valores definidos en el archivo .env.

Crea un archivo .env en la raíz del proyecto con el siguiente formato (ejemplo):

ini
Copiar
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=binance_db
Ajusta los valores según tu entorno local o de producción.

Importante: No compartas el archivo .env en repositorios públicos.

Estructura del Proyecto
Una estructura sugerida para el proyecto es la siguiente:

bash
Copiar
.
├── app
│   ├── models.py            # Modelos de Tortoise ORM
│   ├── schemas.py           # Schemas de Pydantic (opcional)
│   ├── main.py              # Archivo principal de la aplicación (FastAPI)
│   └── ...
│
├── ML
│   ├── model_training.py    # Script de entrenamiento/ejemplo para futuros desarrollos
│   ├── data
│   │   ├── raw              # Datos en bruto
│   │   └── processed        # Datos procesados
│   └── ...
│
├── tests                    # (Directorio preparado para pruebas, aunque en este portafolio se incluirán fotos y evidencias visuales)
│   └── ...                  
│
├── .env                     # Variables de entorno (no incluir en repositorios públicos)
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Documentación principal
├── .gitignore
└── ...
Cómo Usar
Ejecutar la API
Verifica que PostgreSQL esté en ejecución y que la configuración en .env sea correcta.

Inicia la aplicación:

bash
Copiar
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
O alternativamente:

bash
Copiar
python app/main.py
Accede a la documentación interactiva:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
Endpoints Disponibles
1. Trades
POST /trades/
Crea un nuevo trade (evita duplicados basándose en symbol y timestamp).

GET /trades/
Lista todos los trades ordenados por fecha descendente.

2. Historical Prices
POST /historical_prices/
Crea un registro de precio histórico.

GET /historical_prices/
Lista todos los precios históricos ordenados por fecha descendente.

3. Binance Fetch
GET /fetch_and_store_data/{symbol}
Descarga datos OHLCV para un symbol (por defecto, intervalo 15m, fechas de 2020-01-01 a 2025-01-01 y hasta 1000 velas).

Parámetros (Query):

interval: Ej. 15m, 1h, 1d, etc.
start_date y end_date: Rango de fechas en formato YYYY-MM-DD.
max_candles: Número máximo de velas a descargar.
Ejemplo:

bash
Copiar
curl "http://127.0.0.1:8000/fetch_and_store_data/BTCUSDT?interval=1h&start_date=2021-01-01&end_date=2021-02-01&max_candles=500"
Licencia
Este es un proyecto personal.
El código se comparte para fines de demostración y aprendizaje.
Puedes usarlo y modificarlo para inspirarte en tus propios proyectos, siempre dando el crédito correspondiente cuando sea necesario.

Próximos Pasos
Este proyecto sirvió como base para futuros desarrollos, tales como:

Un modelo de aprendizaje automático (machine learning):
Utilizando los datos descargados para entrenar modelos predictivos en el ámbito de las criptomonedas.

Un Bot Market Maker:
Aprovechando la estructura y la ingesta de datos para desarrollar un bot que pueda realizar operaciones automatizadas en el mercado.
