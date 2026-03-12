# Forex Analytics API

## Overview

This project implements a **data-driven REST API for foreign exchange
(FX) analytics**. The system ingests historical exchange rate data from
the **European Central Bank (ECB)** dataset and exposes endpoints for
currency conversion, trend analysis, volatility estimation, and market
regime classification.

The API is built using **Python and FastAPI**, with a relational
database backend powered by **SQLite and SQLAlchemy**. It includes
authentication, automated testing, and a simple frontend dashboard.

The goal of this project is to demonstrate the design and implementation
of a **modular web API integrating real-world datasets and analytical
functionality**.

------------------------------------------------------------------------

## Features

### Core API Features

-   Currency conversion between supported exchange pairs
-   Historical exchange rate storage in a relational database
-   Trend detection for currency pairs
-   Volatility analysis of exchange rate movements
-   Market regime classification based on trend and volatility
-   JWT-based authentication
-   User profile endpoints (`/auth/me`) for reading/updating account details
-   CRUD operations on exchange rates (search, summary, bulk create/delete, partial updates)
-   MCP tool server integration for conversion and analytics tools
-   Error handling and input validation

Docs: https://github.com/sc23ls/COMP3011/blob/main/API_Documentation.pdf 

------------------------------------------------------------------------

## Analytics Endpoints

  -----------------------------------------------------------------------
  Endpoint                            Description
  ----------------------------------- -----------------------------------
  `/convert`                          Convert an amount between two
                                      currencies

  `/trend`                            Detect whether a currency pair is
                                      in an uptrend, downtrend, or stable

  `/volatility`                       Estimate volatility of exchange
                                      rate movements

  `/regime`                           Combine trend and volatility to
                                      classify the market regime

  `/latest`                           Get latest cross rate for a pair

  `/history`                          Return historical series for a pair

  `/currencies`                       List available currencies
  -----------------------------------------------------------------------

These endpoints allow users to analyse **time-series characteristics of
currency markets**.

------------------------------------------------------------------------

## Technology Stack

  Component         Technology
  ----------------- ---------------------------
  API Framework     FastAPI
  Database          SQLite
  ORM               SQLAlchemy
  Data Validation   Pydantic
  Authentication    JWT
  Testing           Pytest
  Frontend          HTML / JavaScript
  Dataset           ECB historical FX dataset

The project follows a **modular architecture**, separating routing,
analytics logic, database models, schemas, and services.

------------------------------------------------------------------------

## Project Structure

    app/
    ├── routers/        # API endpoints
    ├── analytics/      # trend, volatility, regime calculations
    ├── models/         # database models
    ├── schemas/        # request/response validation
    ├── services/       # authentication and data import logic
    ├── database.py     # database configuration
    └── main.py         # FastAPI application entry point

    data/
    └── eurofxref-hist.csv

    frontend/
    └── index.html

    tests/
    └── pytest test suite

    mcp_server.py
    forex.db

------------------------------------------------------------------------

## Setup Instructions

Deployed at https://forexanalyticstool.onrender.com/
Alternatively to run locally:

### 1. Clone the repository

``` bash
git clone <repo-url>
cd COMP3011
```

### 2. Create a virtual environment

``` bash
python -m venv .venv
```

Activate it:

Mac / Linux

``` bash
source .venv/bin/activate
```

Windows

``` bash
.venv\Scripts\activate
```

------------------------------------------------------------------------

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

### 4. Database

The repository includes a pre-populated SQLite database (`forex.db`)
containing historical exchange rate data from the ECB dataset.

This allows the API to run immediately without additional setup.

If required, the database can be rebuilt from the dataset using:

python -m app.services.import_data

------------------------------------------------------------------------

### 5. Run the API

``` bash
uvicorn app.main:app --reload
```

The API and frontend will be available at:

    http://127.0.0.1:8000

------------------------------------------------------------------------

## API Documentation

Interactive API documentation is available via **Swagger UI**:

    http://127.0.0.1:8000/docs

Swagger allows users to explore endpoints, send requests, and inspect
responses.

------------------------------------------------------------------------

## Authentication

The API uses **JWT-based authentication**.

Typical workflow:

Register a user

    POST /auth/register

Log in

    POST /auth/login

View profile (authenticated)

    GET /auth/me

Update profile (authenticated)

    PUT /auth/me

Authorize requests in Swagger using:

    Bearer <token>

------------------------------------------------------------------------

## CRUD Operations

The API supports full **Create, Read, Update, Delete (CRUD)** operations
on exchange rates, including search/filtering, partial updates, and bulk
operations.

  Operation   Method
  ----------- --------
  Create      POST
  Read        GET
  Update      PUT
  Delete      DELETE

These operations demonstrate integration between the API layer and the
relational database.

Key routes include:

-   `GET /rates/` and `GET /rates/{rate_id}`
-   `GET /rates/search`
-   `POST /rates/` and `POST /rates/bulk` (authenticated)
-   `PUT /rates/{rate_id}` and `PATCH /rates/{rate_id}` (authenticated)
-   `DELETE /rates/{rate_id}` (authenticated)
-   `DELETE /rates/bulk` (admin-only)
-   `GET /rates/stats/summary` (authenticated)

------------------------------------------------------------------------

## Testing

The project includes automated tests using **pytest**.

Run tests with:

``` bash
python -m pytest
```

Tests verify authentication functionality, analytics endpoints,
conversion logic, and API responses.

------------------------------------------------------------------------

## Dataset

The API uses historical foreign exchange data from the **European
Central Bank (ECB)**.

Dataset file:

    data/eurofxref-hist.csv

The dataset contains daily exchange rates relative to the Euro for
multiple currencies.

------------------------------------------------------------------------

## Frontend Dashboard

A simple frontend dashboard is included to demonstrate interaction with
the API.

Features include:

-   currency selection
-   conversion tool
-   exchange rate chart
-   analytics display (trend, volatility, regime)
-   user registration/login/logout
-   authenticated profile update (username/password)
-   authenticated and role-aware CRUD controls (including admin-only actions)

The dashboard communicates with the API using HTTP requests.

------------------------------------------------------------------------

## MCP Connection

An MCP server is provided in `mcp_server.py` using the `mcp` Python SDK.
It exposes these tools:

-   `convert_currency(base, target, amount)`
-   `detect_trend(base, target)`
-   `calculate_volatility(base, target)`

Before starting MCP, run the API:

``` bash
uvicorn app.main:app --reload
```

Then start the MCP server:

``` bash
python mcp_server.py
```

By default, the MCP server calls `http://127.0.0.1:8000`. If your API is
running elsewhere, update `API_BASE_URL` in `mcp_server.py`.

------------------------------------------------------------------------

## Use of Generative AI

Generative AI tools were used during development to assist with:

-   debugging and troubleshooting
-   exploring alternative implementations
-   refining API design
-   improving documentation

All AI usage is declared and discussed in the accompanying technical
report.

------------------------------------------------------------------------

## Future Improvements

Potential future improvements include:

-   additional financial indicators
-   enhanced frontend visualisations
-   performance optimisation
