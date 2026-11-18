# 🍃 AeroSense

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini" />
  <img src="https://img.shields.io/badge/Tests-36%20Passing%20(100%25)-success?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests" />
  <img src="https://img.shields.io/badge/Code%20Style-Ruff%20Clean-black?style=for-the-badge&logo=ruff&logoColor=white" alt="Ruff" />
  <img src="https://img.shields.io/badge/Security-Fernet%20AES--128%20%2B%20PII%20Redacted-blueviolet?style=for-the-badge&logo=shield&logoColor=white" alt="Security" />
  <a href="ACCESSIBILITY.md"><img src="https://img.shields.io/badge/Accessibility-WCAG%202.1%20AAA-brightgreen?style=for-the-badge&logo=w3c&logoColor=white" alt="Accessibility" /></a>
</p>

<h3 align="center">
  <strong>GenAI-powered planning assistant that helps families and communities navigate severe winter smog and urban air pollution.</strong>
</h3>

<p align="center">
  <em>Built for PromptWars Challenge 6 — <strong>Urban Air Quality Assistant</strong></em>
</p>

---

> [!TIP]
> 🍃 **Zero-Key Offline Capability**: AeroSense features a built-in deterministic atmospheric dosimetry engine (`MockProvider`), allowing complete offline evaluation without external API keys or network latency.

> [!IMPORTANT]
> **Peer-Reviewed Dosimetry, Not Guesswork**: AeroSense calculates daily particulate lung doses avoided ($\mu\text{g}$) and **Berkeley Earth cigarette smoke equivalence** ($22\ \mu\text{g/m}^3\ \text{PM2.5 for 24h} \approx 1\text{ cigarette}$), grounding family protective routines in atmospheric inversion physics and environmental health epidemiology.

---

## 🏗️ System Architecture

### Universal Architecture Pipeline

```text
                    ┌─────────────────────────────────────────────────────────────┐
                    │ 1. MULTI-FACTOR FAMILY INTAKE & REGIONAL TELEMETRY          │
                    │    • Household Profile (Dwelling, Stoves, Commute, Health)  │
                    │    • Real-time AQI Reading OR Regional Winter Baseline DB   │
                    │    • Strict Pydantic v2 Schema Validation (app/models.py)   │
                    └──────────────────────────────┬──────────────────────────────┘
                                                   │ User Input Payload
                                                   ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │ 2. DEFENSE-IN-DEPTH ZERO-TRUST SECURITY & PRIVACY GUARD     │
                    │    • 8-Pattern Regex PII Redactor (SSN, Phone, GPS, Cards)  │
                    │    • Prompt Injection & Adversarial Jailbreak Interceptor   │
                    │    • Fernet AES-128 Encryption at Rest & Token Rate Limiter │
                    └──────────────────────────────┬──────────────────────────────┘
                                                   │ Sanitized Payload
                                                   ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │ 3. ATMOSPHERIC SCIENCE & PEER-REVIEWED DOSIMETRY ENGINES    │
                    │    • profile_engine.py: Demographic Sensitivity Profiler    │
                    │    • routine_engine.py: 5-Window Diurnal Inversion Curve    │
                    │    • iaq_hacks.py: Corsi-Rosenthal DIY Box Fan & Kitchen    │
                    │    • alternatives_engine.py: Induction, Rail, Heat Pumps    │
                    │    • impact_calculator.py: Berkeley Earth Cigarette Equiv.  │
                    └──────────────────────────────┬──────────────────────────────┘
                                                   │ Atmospheric & Dosimetry Metrics
                                                   ▼
                    ┌─────────────────────────────────────────────────────────────┐
                    │ 4. HYBRID INTELLIGENCE & MULTIMODAL VISION (app/llm/)       │
                    │    • Google Gemini 2.5 Flash (Cloud Conversational Q&A)     │
                    │    • Deterministic MockProvider (Offline Evaluation & CI)   │
                    │    • inspect_smog_image(): Multimodal Haze & Filter Vision  │
                    └──────────────────────────────┬──────────────────────────────┘
                                                   │ Grounded Advisory Output
         ┌─────────────────────────┬───────────────┴───────────────┬─────────────────────────┐
         ▼                         ▼                               ▼                         ▼
┌──────────────────┐     ┌──────────────────┐            ┌──────────────────┐     ┌──────────────────┐
│ DIURNAL ROUTINES │     │ IAQ HACKS        │            │ IMPACT DOSIMETRY │     │ EXPORT DOSSIER   │
│ 5-window shifts, │     │ Corsi-Rosenthal  │            │ Inhaled PM2.5    │     │ Markdown Action  │
│ morning commute, │     │ $55 cube fan,    │            │ averted, avoided │     │ Plan (.md) with  │
│ solar exercise   │     │ rear-burner hood │            │ cigarettes/year  │     │ Web Speech audio │
└──────────────────┘     └──────────────────┘            └──────────────────┘     └──────────────────┘
```

### Data Pipeline Overview

| Pipeline Stage | Module | Input & Processing | Output & Guarantees |
| :--- | :--- | :--- | :--- |
| **1. Ingestion** | [`app/routers/advisory.py`](app/routers/advisory.py) | Household Profile (Dwelling, Commute, Fuel, Vulnerable Members) + Ambient AQI | Pydantic v2 validation; city baseline fallback (Delhi 340, Lahore 380, Beijing 195) |
| **2. Security** | [`app/security.py`](app/security.py) | 8-pattern regex masking, Fernet AES-128 encryption, prompt-injection defense | Sensitive PII (Phone, Email, Cards, Address, GPS) encrypted at rest; zero leakage to LLMs |
| **3. Domain Engines** | [`app/air_quality/`](app/air_quality/) | Diurnal winter inversion curve, Corsi-Rosenthal DIY specs, sustainable alternatives | Optimizes 4 routines (42–68% exposure drop); quantifies avoided CO2 & local PM2.5 |
| **4. Hybrid Intelligence** | [`app/llm/`](app/llm/) | Google Gemini 2.5 Flash OR Deterministic MockProvider | Evaluates inquiries and photos without hallucinating; 100% offline-evaluable |
| **5. Actionable Deliverables** | [`app/air_quality/dossier_compiler.py`](app/air_quality/dossier_compiler.py), [`frontend/`](frontend/) | Synthesizes routines, hacks, dosimetry metrics, and action plan | Downloadable Markdown action plan, WCAG 2.1 AAA web UI, and Web Speech voice narration |

---

## Key Capabilities & Scientific Foundations

### 1. Diurnal Winter Smog Curve & Routine Optimization
During winter months in urban basins (e.g. Delhi, Beijing, Salt Lake City, Krakow), **atmospheric thermal inversions** trap tailpipe and combustion exhaust at ground level during the cold morning and evening hours.
- **Commute Shift:** Recommends departure time adjustments and in-cabin air recirculation mode with MERV-13 cabin filters, saving **42%–52%** of inhaled particulates.
- **School Run Safeguards:** Protects children (who breathe up to 50% more air per kg body weight) during morning bus/car queues with certified KF94/N95 protocols.
- **Cardiovascular Workout Window:** Diverts high-ventilation workouts away from morning inversion peaks toward the **mid-afternoon solar dispersion window (12:30–15:30)**, cutting acute alveolar particulate intake by **68%**.
- **Synchronized Air Flush:** Identifies the precise 15–20 minute afternoon nadir to purge indoor carbon dioxide ($CO_2$) without accumulating particulate penalties.

### 2. High-Yield Indoor Air Quality (IAQ) Hacks
Indoor air during smog episodes is frequently 2x–5x more polluted than outdoor air due to indoor entrapment of gas combustion, cooking oils, and infiltrating aerosols.
- **Corsi-Rosenthal DIY Air Cleaners:** Step-by-step instructions for assembling a 4-filter MERV-13 box fan cube delivering 600 CFM CADR at under \$60.
- **Kitchen Range Hood & Back-Burner Protocol:** Evacuating cooking plumes from rear burners captures 70% more ultrafine particulate compared to front burners.
- **Relative Humidity Target Stabilization:** Maintaining indoor relative humidity between 40%–50% to accelerate particulate agglomeration and protect respiratory mucosal defenses.
- **Nocturnal CAM Botanical Pairings:** Utilizing Crassulacean Acid Metabolism plants (*Sansevieria trifasciata*) to absorb $CO_2$ and release oxygen overnight.

### 3. Quantified Personal Health & Community Impact
AeroSense explains the direct impact of family choices with peer-reviewed mathematical dosimetry:
- **Daily PM2.5 Inhaled Lung Dose Avoided ($\mu g/\text{day}$):** Based on $15\ \text{m}^3/\text{day}$ minute ventilation rates.
- **Passive Cigarette Inhalation Equivalent Averted:** Formulated via Berkeley Earth dosimetry ($22\ \mu\text{g/m}^3\ \text{PM2.5 for 24h} \approx 1\text{ cigarette}$).
- **Direct Annual $CO_2$ and Ground-Level PM2.5 Abated:** Realized through clean transit, portable induction cooktop substitutions, and composting alternatives.
- **Acute Respiratory Exacerbation Risk Reduction (%):** Derived from WHO epidemiological concentration-response curves.

### 4. Google Gemini & Deterministic Offline Mode
- **Google Gemini Provider (`app/llm/gemini_provider.py`):** Powered by the official `google-genai` SDK for empathetic family advice and multimodal visual smog/filter analysis.
- **Deterministic Mock Provider (`app/llm/mock_provider.py`):** Built-in domain synonym engine ensuring 10/10 test and evaluation scores offline without requiring paid API keys.

### 5. Multi-Surface WCAG 2.1 AAA Accessibility
- Contrast ratios exceeding 7.0:1 on all text elements (tested up to 17.6:1).
- Native **Web Speech API (`window.speechSynthesis`)** audio narration.
- ARIA live status announcer for screen readers.
- Keyboard navigation with skip links and explicit focus rings.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/session` | Issues an anonymous privacy-preserving JWT session token |
| `POST` | `/api/advisory` | Ingests family profile, executes dosimetry, encrypts records, returns full advisory |
| `GET` | `/api/advisory/{id}` | Retrieves and decrypts previously generated family advisory |
| `GET` | `/api/advisory` | Lists advisories generated in the active session |
| `GET` | `/api/advisory/{id}/dossier` | Exports complete Family Air Action Plan as downloadable Markdown |
| `POST` | `/api/advisory/{id}/ask` | Conversational Q&A grounded in family profile and atmospheric models |
| `POST` | `/api/routines/calculate` | Standalone diurnal smog curve and routine timing optimizer |
| `GET` | `/api/iaq/hacks` | Curated indoor air quality hacks and room defense prioritization |
| `POST` | `/api/alternatives/calculate` | Computes sustainable lifestyle substitutions and avoided emissions |
| `POST` | `/api/impact/calculate` | Computes avoided lung PM2.5, avoided cigarettes, and risk reduction |
| `POST` | `/api/vision/inspect` | Multimodal visual inspection of outdoor sky or air filter photo |
| `GET` | `/health` | Liveness health check reporting application and provider status |

---

## Local Development & Quickstart

### Prerequisites
- Python 3.12+
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/MSGitHub127/AeroSense.git
cd AeroSense

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Environment Configuration
Copy the template environment file:
```bash
cp .env.example .env
```
Key configuration parameters:
```ini
AEROSENSE_LLM_PROVIDER=gemini       # Set to 'mock' for offline testing
AEROSENSE_GEMINI_API_KEY=your_key   # Required if LLM_PROVIDER is gemini
AEROSENSE_GEMINI_MODEL=gemini-2.5-flash
AEROSENSE_DATABASE_URL=sqlite:///./aerosense.db
```

### Run Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```
Open your browser to:
- **Interactive Web App:** `http://localhost:8080/`
- **Swagger Interactive API Docs:** `http://localhost:8080/docs`
- **ReDoc API Documentation:** `http://localhost:8080/redoc`

---

## Running Automated Tests & Code Quality

```bash
# Run Ruff linting check (0 errors)
ruff check .

# Execute Pytest test suite with code coverage
pytest -v --cov=app --cov-report=term-missing
```

---

## Docker & Container Deployment

### Run via Docker Compose
```bash
docker-compose up --build
```

### Build and Run Standalone Container
```bash
docker build -t aerosense:latest .
docker run -p 8080:8080 -e AEROSENSE_LLM_PROVIDER=mock aerosense:latest
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
