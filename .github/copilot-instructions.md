# Copilot Instructions for OCPP 2.0.1 EV Charger Management System

## Project Overview

OCPP 2.0.1 기반 전기차 충전기 시뮬레이터, 중앙 관리 서버, REST API, 그리고 GIS 기반 대시보드를 포함한 통합 충전 인프라 관리 시스템.

- **Core Protocol**: OCPP 2.0.1 (Open Charge Point Protocol) over WebSocket
- **Database**: PostgreSQL (with SQLite fallback)
- **API**: FastAPI (GIS Dashboard), aiohttp (Legacy REST API)
- **Frontend**: Leaflet.js GIS Dashboard with real-time monitoring
- **Language**: Python 3.8+ with async/await patterns

## Architecture & Component Boundaries

### 1. **OCPP Server** (`4_PYTHON_SOURCE/ocpp_server.py`)
- WebSocket server on `ws://0.0.0.0:9000` with subprotocol `ocpp2.0.1`
- Manages multiple charger connections via `ChargerConnection` class
- Key responsibilities:
  - Parse OCPP messages via `OCPPMessage` class
  - Route incoming requests (Call/CallResult/CallError)
  - Maintain transaction state for each charger
  - Support pending request tracking with async timeouts
- **Critical Pattern**: `await self.send()` and `await self.receive()` use 60-second timeout
- **Integration Point**: Reads/updates charger status but doesn't persist data directly (stateless)

### 2. **Charger Simulator** (`4_PYTHON_SOURCE/charger_simulator.py`)
- Simulates real charger behavior connecting to OCPP server
- Spawns multiple async tasks:
  - `connect()` → establishes WebSocket connection
  - `send_boot_notification()` → triggers boot sequence
  - `heartbeat_loop()` → sends heartbeat every 30 seconds
  - `charging_loop()` → simulates charging with meter values
- **Data Flow**: Sends TransactionEvent (Started/Updated/Ended), StatusNotification, MeterValues
- **Meter Simulation**: `charge_rate = 0.1 kWh/second`, simulates voltage (400V), current

### 3. **GIS Dashboard API** (`4_PYTHON_SOURCE/gis_dashboard_api.py`)
- FastAPI application on `http://localhost:8000`
- **20+ endpoints** for charger management and GIS visualization
- Database integration via `DatabaseManager` from `database/models_postgresql.py`
- **Critical Services**:
  - `StationService` - charger station CRUD
  - `ChargerService` - charger info and status
  - `UsageLogService` - transaction history
  - `StatisticsService` - daily/hourly analytics
- **Real-time Data**: Endpoints query PostgreSQL and return JSON (no caching layer)
- **Frontend Sync**: HTML dashboards served at `/` (gis_dashboard.html) and `/advanced_dashboard.html`

### 4. **Database Layer** (`8_DATABASE/`)
- **Two model versions**:
  - `database/models_postgresql.py` - PostgreSQL ORM (7 tables)
  - `database/models.py` - SQLite fallback
- **Core Tables**: StationInfo, ChargerInfo, ChargerUsageLog, PowerConsumption, DailyChargerStats, HourlyChargerStats, StationDailyStats
- **DatabaseManager Pattern**: 
  - Reads `DATABASE_URL` env var (default: `postgresql://charger_user:admin@localhost:5432/charger_db`)
  - Lazy initialization via `db_manager.initialize()`
  - Session pooling with `SessionLocal`
- **Key Enums**: `ChargerTypeEnum` (DC_FAST, AC_L2, etc.), `ChargerStatusEnum` (AVAILABLE, IN_USE, FAULT)

### 5. **Message Protocol** (`4_PYTHON_SOURCE/ocpp_messages.py`)
- Implements OCPP 2.0.1 JSON-RPC format:
  - `[2, messageId, action, payload]` = Call (charger→server)
  - `[3, messageId, payload]` = CallResult (server→charger)
  - `[4, messageId, errorCode, errorMsg]` = CallError
- **Message Builder**: `OCPPv201RequestBuilder` creates typed requests
- **Debug Logging**: Controlled via `OCPP_PROTOCOL_DEBUG=true` env var - logs each message type separately
- **Message Types**: BootNotification, TransactionEvent, StatusNotification, MeterValues, etc.

## Critical Workflows & Commands

### Setup & Initialization
```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Set database URL (required for PostgreSQL)
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 3. Initialize database (creates tables, inserts sample Jeju charger data)
python 6_PYTHON_SCRIPTS\init_jeju_chargers.py

# 4. (Optional) Reset database
python 6_PYTHON_SCRIPTS\init_jeju_chargers.py --reset
```

### Running the System (3 terminals)
```powershell
# Terminal 1: OCPP WebSocket Server
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "true"  # Optional: verbose logging
python 4_PYTHON_SOURCE\ocpp_server.py
# Expected: "OCPP 2.0.1 server started: ws://0.0.0.0:9000"

# Terminal 2: FastAPI GIS Dashboard
python 4_PYTHON_SOURCE\gis_dashboard_api.py
# Expected: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 3: Charger Simulator (connects to server)
python -c "
import asyncio
from charger_simulator import ChargerSimulator

async def main():
    charger = ChargerSimulator('TEST_CHARGER_001', 'ws://localhost:9000')
    try:
        await charger.connect()
        print('✅ Connected')
        await asyncio.sleep(30)  # Run for 30 seconds
    finally:
        await charger.disconnect()

asyncio.run(main())
"
```

### Testing
```powershell
# Quick integration test (3-5 minutes)
python 5_PYTHON_TESTS\manual_test.py

# Detailed test guide
# See 2_GUIDES_TESTING\MANUAL_TEST_GUIDE.md

# Database connectivity check
python 5_PYTHON_TESTS\test_db_connection.py
```

## Project-Specific Patterns & Conventions

### 1. **Async/Await Usage**
- **All network I/O is async**: WebSocket server uses `asyncio.run()`, simulator uses `asyncio.create_task()`
- **Never block**: All long operations (heartbeat, charging simulation) run as background tasks
- **Timeout Protection**: WebSocket operations enforce 60-second timeout to prevent hangs
- **Pattern**: 
  ```python
  asyncio.create_task(self.heartbeat_loop())  # Fire and forget
  await self.send_boot_notification()  # Wait for result
  ```

### 2. **Message ID Correlation**
- Both server and charger maintain `pending_requests` dict mapping messageId → request metadata
- Server expects charger to echo messageId in CallResult for correlation
- **Important**: Request handlers must set a timeout (typically 30 seconds) before waiting for response

### 3. **Database Session Management**
- All database operations require explicit session handling:
  ```python
  session = db_manager.get_session()
  try:
      result = StationService.get_all_stations(session)
  finally:
      session.close()
  ```
- No ORM lazy loading - use explicit joins if needed
- Services are stateless; they accept session as first parameter

### 4. **Environment Variables & Configuration**
- `DATABASE_URL`: PostgreSQL connection string (mandatory for prod, optional for tests)
- `OCPP_PROTOCOL_DEBUG`: Set to `true` to enable protocol logging (writes detailed JSON to logs)
- No config files - all settings via env vars or code defaults
- **Fallback Strategy**: If PostgreSQL unavailable, SQLite (`charger_management.db`) is auto-created

### 5. **Data Persistence & OCPP States**
- OCPP server doesn't persist charger state - state lives in memory (`ChargerConnection` objects)
- Database stores historical data: transactions, meter values, usage logs
- When charger reconnects, it sends BootNotification again (server treats as new connection)
- **Implication**: Dashboard reads from DB for historical data, but real-time charger status is from OCPP in-memory state

### 6. **Error Handling Patterns**
- OCPP errors use CallError format: `[4, messageId, errorCode, errorMsg]`
- Common error codes: `GenericError`, `NotSupported`, `RpcFrameError`, `SecurityError`
- All async tasks use try/finally to ensure cleanup (e.g., `websocket.close()`)
- Database errors propagate (no silent failures) for visibility

### 7. **Encoding & Localization**
- Project is **Korean-first**: all comments, docstrings, and UI are in Korean
- On Windows, UTF-8 explicit setup: 
  ```python
  if sys.platform == 'win32':
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  ```
- File paths use backslashes on Windows (auto-converted by pathlib)

## Key Files & Their Responsibilities

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `ocpp_server.py` | OCPP 2.0.1 WebSocket server | `OCPPServer`, `ChargerConnection` |
| `charger_simulator.py` | Simulates EV charger behavior | `ChargerSimulator` |
| `ocpp_messages.py` | Protocol serialization/parsing | `OCPPMessage`, `OCPPv201RequestBuilder` |
| `gis_dashboard_api.py` | FastAPI GIS dashboard backend | `StationService`, `ChargerService` |
| `database/models_postgresql.py` | ORM models & DB manager | `DatabaseManager`, `StationInfo`, `ChargerInfo` |
| `database/services.py` | Business logic (CRUD, stats) | `ChargerService`, `StatisticsService` |
| `6_PYTHON_SCRIPTS/init_jeju_chargers.py` | Sample data initialization | Loads Jeju charger stations |

## Common Development Tasks

### Adding a new OCPP message type
1. Define Pydantic model in `ocpp_models.py` (e.g., `class MyRequest(BaseModel)`)
2. Add message creation method in `OCPPv201RequestBuilder` in `ocpp_messages.py`
3. Add handler in `OCPPServer.handle_charger_connection()` to process incoming message
4. Update charger simulator if needed to send/receive new message type

### Adding a new database field
1. Add column to model in `database/models_postgresql.py` (or both `models.py` and `models_postgresql.py`)
2. Update service methods in `database/services.py` to populate/retrieve field
3. Update dashboard API endpoints if exposing field in `gis_dashboard_api.py`
4. Run `init_jeju_chargers.py` to migrate schema (creates missing columns)

### Adding a new API endpoint
1. Define request/response Pydantic models in `gis_dashboard_api.py`
2. Use service layer (e.g., `ChargerService.get_charger()`) to fetch data
3. Register route with FastAPI decorator: `@app.get("/chargers/{charger_id}")`
4. Test with `pytest` or manual curl/Postman requests

### Debugging Protocol Issues
1. Set `export OCPP_PROTOCOL_DEBUG=true`
2. Run server and simulator, capture logs
3. Search logs for `[OCPP-CALL-RECV]`, `[OCPP-PAYLOAD-SEND]`, `[OCPP-CALLERROR-SEND]`
4. Use Wireshark on port 9000 if async logging is insufficient

## Deployment & Ports

- **OCPP WebSocket Server**: Port 9000 (ws://0.0.0.0:9000)
- **FastAPI Dashboard**: Port 8000 (http://0.0.0.0:8000)
- **PostgreSQL**: Port 5432 (localhost only, not exposed)
- **Legacy aiohttp API**: Port 8080 (deprecated, kept for backward compatibility)

Default all services to `0.0.0.0` (bind to all interfaces) for Docker/prod compatibility.

## Documentation Structure

- `0_START_HERE/` → Quick orientation
- `1_GUIDES_SERVER/` → Running servers and dashboards
  - **INTEGRATED_EXECUTION_GUIDE.md** - Full step-by-step integration guide
  - **QUICK_START_INTEGRATED.md** - 5-minute quick start
- `2_GUIDES_TESTING/` → Test procedures and protocols
- `3_GUIDES_SETUP/` → PostgreSQL, git, environment setup
- `4_PYTHON_SOURCE/` → Core implementation
- `8_DATABASE/` → ORM models and services
- `10_CONFIG_BUILD/` → Build scripts and requirements

When contributors ask questions, direct them to the guide matching their need; docs are comprehensive.

## Quick Integration Testing

To validate the complete system end-to-end:

```powershell
# Option 1: Automated (recommended)
cd "c:\Project\OCPP201(P2M)"
.\run_integrated.ps1 -Mode all

# Option 2: Manual (detailed in INTEGRATED_EXECUTION_GUIDE.md)
# Terminal 1: python 4_PYTHON_SOURCE\ocpp_server.py
# Terminal 2: python 4_PYTHON_SOURCE\gis_dashboard_api.py
# Terminal 3: Run Python simulator
# Terminal 4 (optional): python monitor_realtime.py
```

## Verification Checklist

- `verify_setup.py` - Validates all module imports and file structure
- `monitor_realtime.py` - Real-time monitoring dashboard for Terminal 4
- GIS Dashboard: http://localhost:8000 shows live charger status and statistics
