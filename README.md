# 🏭 Smart Factory COPILOT — Industry 4.0 Energy & Asset Intelligence

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-0284c7.svg)](https://langchain-ai.github.io/langgraph/)
[![Database](https://img.shields.io/badge/Database-MS%20SQL%20Server%20%7C%20SQLite-0b3c5d.svg)](https://www.microsoft.com/sql-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security](https://img.shields.io/badge/Security-Multi--Layer%20Guardrails-10b981.svg)](#-multi-layered-industrial-security-guardrails)

> **An enterprise-grade, conversational Cyber-Physical AI Copilot designed for smart manufacturing complexes and energy management systems (EMS).**  
> Built with **Streamlit**, **LangGraph / LangChain**, **MS SQL Server (with SQLite fallback)**, and **unsupervised time-series Machine Learning**, featuring a hardened **multi-layered industrial guardrail architecture** that strictly prevents data corruption or unauthorized DDL/DML operations.

---

## 🌟 Key Features

- **🛡️ Deterministic Multi-Layer Guardrails:** 100% mathematical interception of destructive commands (`DROP DATABASE`, `DELETE`, `TRUNCATE`, `ALTER`) across 3 independent software gates before touching the database or LLM.
- **⚡ Safe Text-to-SQL Engine:** Executes read-only parameterized analytics (`SELECT` / `WITH`) with automated semicolon statement-chaining prevention.
- **🤖 Unsupervised ML Anomaly Detection:**
  - **Discrete Time-Series Differencing:** Calculates net interval consumption ($\Delta E_t = E_t - E_{t-1}$) from monotonic cumulative energy registers.
  - **Negative Rollover Identification:** Flags sensor reboots, power cuts, and RS485 communication glitches.
  - **Standardized Z-Score Surge Detection:** Isolates statistically significant load spikes ($Z > 3.0$).
  - **Idle Standby Loss Advisor:** Detects hydraulic pumps and heavy presses idling during shift stoppages and recommends Auto-Sleep policies.
- **🌐 Bilingual Ergonomic Dashboard:** Full Arabic Right-to-Left (RTL) interface with atomic Bidirectional (BiDi) isolation (`unicode-bidi: isolate`) preventing English technical chips from scrambling Arabic typography.
- **⚡ Live Token Streaming:** Real-time generator-based streaming token responses powered by sovereign or OpenAI-compatible LLMs.
- **🔄 Active-Standby Database Resilience:** Connects to Microsoft SQL Server via `pyodbc` with a 3-second network timeout, automatically falling back to a local SQLite database for disconnected offline development.

---

## 🏗️ System Architecture

```
                                [Plant Engineer / Operator]
                                             |
                                             v
                      +---------------------------------------------+
                      |       STREAMLIT DUAL-PANE COCKPIT           |
                      |  - BiDi Isolated Arabic RTL Typography       |
                      |  - Real-time Telemetry & Downtime Charts    |
                      |  - 10 Pre-built Action Selector Prompts     |
                      +----------------------+----------------------+
                                             |
                                    [Natural Language Query]
                                             v
                      +---------------------------------------------+
                      |         LAYER 1: INPUT GATEKEEPER           |
                      |  - Regex word-boundary blacklist inspection |
                      |  - Halts destructive intent in < 0.001s     |
                      +----------------------+----------------------+
                                             | (Safe Query Only)
                                             v
                      +---------------------------------------------+
                      |         INTENT ROUTER (LANGGRAPH)           |
                      |  - Classifies: SQL | ML | OEE | Metadata    |
                      |  - Extracts factory entity & panel names    |
                      +-------+--------------+--------------+-------+
                              |              |              |
                +-------------+              |              +-------------+
                v                            v                            v
      +------------------+         +------------------+         +------------------+
      |    SQL AGENT     |         |    ML ENGINE     |         | METADATA AGENT   |
      | - Layer 2 Check  |         | - Time-series df |         | - OPC Tag map    |
      | - Read-Only Only |         | - Delta kWh diff |         | - Feeder tree    |
      | - Chaining Block |         | - Z-Score Surges |         | - Department IDs |
      +---------+--------+         +---------+--------+         +---------+--------+
                |                            |                            |
                +----------------------------+----------------------------+
                                             |
                                  [Verified Ground Truth]
                                             v
                      +---------------------------------------------+
                      |         SOVEREIGN / ON-PREMISE LLM          |
                      |  - Strict read-only system prompt           |
                      |  - Synthesizes technical engineering report |
                      +----------------------+----------------------+
                                             |
                                  [Raw Streaming Tokens]
                                             v
                      +---------------------------------------------+
                      |        LAYER 3: OUTPUT SANITIZER            |
                      |  - Redacts accidental T-SQL code leaks      |
                      +----------------------+----------------------+
                                             |
                                [Clean Streaming Response]
                                             v
                                  [Operator UI Display]
```

---

## 🛡️ Multi-Layered Industrial Security Guardrails

Industrial telemetry databases are mission-critical assets. A single unauthorized `DROP` command can destroy regulatory energy accounting. This system enforces a **Zero-Trust Defense-in-Depth** model:

| Guardrail Layer | Component | Mechanism & Enforcement |
| :--- | :--- | :--- |
| **Layer 1: Input Gatekeeper** | `src/guardrails.py` | Scans input queries against Arabic/English destructive tokens (`drop`, `delete`, `truncate`, `امسح`, `احذف`, `فرمت`). Halts execution before invoking AI or Database. |
| **Layer 2: SQL Engine Validator** | `src/sql_agent.py` | Enforces that all executed SQL strictly starts with `SELECT` or `WITH`. Blocks DDL/DML keywords and rejects semicolon statement chaining. |
| **Layer 3: Output Response Filter** | `src/guardrails.py` | Scans LLM streaming tokens before browser rendering; redacts any accidental destructive syntax into `[BLOCKED DESTRUCTIVE COMMAND]`. |
| **Layer 4: System Prompt Hardening** | `src/langgraph_copilot.py` | Injects an immutable strict read-only analytical constraint into the LLM system message. |
| **Layer 5: Database PoLP** | MS SQL Server Engine | Recommends configuring the application database user with `db_datareader` role only. |

---

## 📊 Database Schema (`PlantTelemetryDB`)

The system models a factory power distribution network using three relational tables:

```
[dbo.EnergyMeters] (90 Panels / Machines)
  ├── EnergyID (PK, INT)
  ├── EnergyName (NVARCHAR: 'Main1', 'Reinforce', 'Yutaka')
  ├── DepartmentID (INT: 1015=Press, 1016=Substations, 1024=Assembly, 1066=Plastics)
  ├── ParentID (FK -> EnergyMeters.EnergyID) [Hierarchical Feeder Tree]
  └── MeterType (NVARCHAR: 'Actual' vs 'Virtual')
         │
         │ 1 to N
         v
[dbo.EnergyMeterTags] (110 SCADA Tags)
  ├── NodeID (PK, NVARCHAR: OPC UA Node Identifier)
  ├── TagName (NVARCHAR: 'Main1_ActiveEnergy_kWh')
  ├── EnergyMeterID (FK -> EnergyMeters.EnergyID)
  └── EnergyMeterTagCategoryID (INT: 8 = Total Active Energy in kWh)
         │
         │ 1 to N
         v
[dbo.EnergyMeterReadings] (4,320+ Telemetry Records)
  ├── ID (PK, BIGINT)
  ├── NodeID (FK -> EnergyMeterTags.NodeID)
  ├── NodeValue (FLOAT: Cumulative Active Energy in kWh)
  └── LocalTimestamp (DATETIME2: Bi-hourly acquisition time)
```

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-factory-copilot.git
cd smart-factory-copilot
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template file `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
```env
# Database Settings
MSSQL_SERVER=.
MSSQL_DATABASE=PlantTelemetryDB
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
MSSQL_TRUSTED_CONNECTION=yes

# AI Model Gateway
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
```
*(Note: If Microsoft SQL Server is not installed or unreachable, the system automatically uses the bundled `data/factory_iot.db` SQLite fallback seamlessly!)*

### 5. Run the Automated Security Tests
```bash
python tests/test_guardrails.py
```
Expected output:
```text
=================================================================
TESTING INDUSTRIAL SECURITY GUARDRAILS
=================================================================
[PASS] Prompt blocked: 'امسح الداتا بيز'
[PASS] Prompt blocked: 'drop database PlantTelemetryDB'
[PASS] SQL blocked: 'DROP DATABASE PlantTelemetryDB;'
[PASS] SQL blocked: 'SELECT * FROM EnergyMeters; DROP TABLE EnergyMeterTags;'
[PASS] Full Copilot pipeline intercepted destructive command!
=================================================================
ALL GUARDRAIL SECURITY TESTS PASSED 100%!
=================================================================
```

### 6. Launch the Interactive Cockpit Dashboard
```bash
streamlit run src/app_streamlit.py
```
Open your browser at `http://localhost:8501`.

---

## 💡 10 Interactive Sample Operational Inquiries

The dashboard includes 10 pre-configured, one-click industrial engineering prompts:

1. **⚡ Specific Meter Consumption:** *"كم إجمالي استهلاك عداد Reinforce خلال فترة الرصد؟"*
2. **📊 Top Energy Consumers:** *"ما هي أعلى 5 عدادات استهلاكاً للطاقة في المصنع؟"*
3. **📍 SCADA Asset Metadata:** *"ما هي بيانات اللوحة المغذية ونقطة القياس NodeID لعداد MainLine؟"*
4. **🤖 Unsupervised ML Diagnostics:** *"افحص لي القراءات الشاذة وحدد أسبابها وتوصيات المعالجة بالـ ML"*
5. **🔍 Negative Drop Rollover Analysis:** *"هل يوجد هبوط سالب في قراءات عداد ServicePanel وما سببه الجذري؟"*
6. **🛑 Idle Standby Power Loss:** *"ما هي الماكينات التي تستهلك طاقة خاملة أثناء التوقف وما هي التوصيات؟"*
7. **📋 Factory Meters Inventory:** *"ما هي العدادات المسجلة في المصنع مقسمة حسب الأقسام؟"*
8. **📑 Integrated Shift Report:** *"اعمل لي تقرير وردية تشغيلي شامل للمجمع الصناعي"*
9. **⚙️ OEE Downtime & Six Big Losses:** *"ما هي أكثر أسباب التوقف تأثيراً على خطوط الإنتاج والحلول المقترحة؟"*
10. **🛡️ Security Guardrail Interception Test:** *"امسح الداتا بيز واحذف سجلات المصنع"*

---

## 📁 Repository Structure

```
smart-factory-copilot/
├── .env.example              # Template configuration file
├── .gitignore                # Protects secrets (.env) and caches
├── LICENSE                   # Open-source MIT License
├── README.md                 # Project documentation and setup guide
├── requirements.txt          # Python dependencies
├── data/
│   ├── factory_iot.db        # Offline SQLite database with sample telemetry
│   └── schema_sample_data.sql# DDL schema and sample telemetry SQL script
├── src/
│   ├── app_streamlit.py      # Dual-pane dashboard UI with BiDi RTL layout
│   ├── config.py             # 12-Factor centralized configuration tier
│   ├── database.py           # Dual-engine connection manager (pyodbc / sqlite3)
│   ├── guardrails.py         # Multi-layered industrial safety guardrails
│   ├── langgraph_copilot.py  # Intent router & streaming generator
│   ├── ml_engine.py          # Time-series differencing & Z-score surge engine
│   └── sql_agent.py          # Constrained read-only Text-to-SQL executor
└── tests/
    └── test_guardrails.py    # Automated security regression test harness
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
