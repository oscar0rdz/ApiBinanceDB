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
  <br>Proyecto de portafolio orientado a backend: reproducible, explicable y fácil de extender.
</p>

<hr/>

## Tabla de contenidos
- [TL;DR](#tldr)
- [Arquitectura](#arquitectura)
- [Stack (y por qué)](#stack-y-por-qué)
- [Características](#características)
- [Esquema de Datos (SQL & ORM)](#esquema-de-datos-sql--orm)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints](#endpoints)
- [Pruebas (sugerido)](#pruebas-sugerido)
- [Seguridad y configuración](#seguridad-y-configuración)
- [Roadmap](#roadmap)
- [Docker Compose (opcional)](#docker-compose-opcional)
- [Licencia](#licencia)
- [Sobre este repo](#sobre-este-repo)

---

## TL;DR
- **Ingesta confiable** de OHLCV desde Binance.
- **Persistencia idempotente** en PostgreSQL (sin duplicados) con `UNIQUE(symbol, interval, open_time)`.
- **API REST** lista para integrar: inserta, lista y también **dispara capturas** desde la propia API.
- **Async end-to-end** (FastAPI + aiohttp + Tortoise) → buen throughput sin bloquear.
- Base sólida para **ETL, ML** o un **bot market maker** posterior.

---

## Arquitectura
```text
          ┌─────────────┐        HTTP (async)        ┌───────────────┐
Request → │   FastAPI   │  ───────────────────────→  │  Binance API  │
          └─────┬───────┘                            └───────────────┘
                │
                │  Models / Repos (Tortoise ORM async)
                ▼
          ┌─────────────┐     SQL (async)     ┌────────────────────┐
          │  Services   │  ─────────────────→ │   PostgreSQL 12+   │
          │  Layer      │  ←─────────────────  │ (índices únicos)   │
          └─────────────┘                      └────────────────────┘
