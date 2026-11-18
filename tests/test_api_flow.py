"""Integration tests validating the end-to-end REST API request-response lifecycles."""
from __future__ import annotations

import io

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Verify application liveness probe."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AeroSense"


def test_session_creation(client: TestClient):
    """Verify anonymous session token issuance."""
    res = client.post("/api/session")
    assert res.status_code == 200
    data = res.json()
    assert "session_token" in data
    assert data["token_type"] == "Bearer"


def test_create_and_fetch_advisory_flow(client: TestClient):
    """Verify full profile intake, calculation, storage, and retrieval."""
    payload = {
        "household_name": "Mukherjee Family",
        "location_city": "Kolkata",
        "home_type": "apartment",
        "cooking_fuel": "natural_gas",
        "commute_mode": "car_solo",
        "has_hepa_purifier": False,
        "vulnerable_members": ["asthmatic_grandparent", "toddler"],
        "baseline_aqi": 260,
    }

    # 1. Create advisory
    create_res = client.post("/api/advisory", json=payload)
    assert create_res.status_code == 200, create_res.text
    data = create_res.json()
    profile_id = data["profile_id"]

    assert data["household_name"] == "Mukherjee Family"
    assert data["current_estimated_aqi"] == 260
    assert data["vulnerability_tier"] in ("high", "critical")
    assert len(data["routines"]["diurnal_windows"]) == 5
    assert len(data["iaq_hacks"]["hacks"]) >= 5
    assert len(data["alternatives"]["alternatives"]) >= 3
    assert data["impact"]["daily_pm25_lung_dose_avoided_ug"] > 0
    assert "# AeroSense: Winter Smog" in data["action_plan_markdown"]

    # 2. Retrieve advisory by ID
    get_res = client.get(f"/api/advisory/{profile_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["profile_id"] == profile_id
    assert fetched["location_city"] == "Kolkata"

    # 3. Export Markdown dossier
    dossier_res = client.get(f"/api/advisory/{profile_id}/dossier")
    assert dossier_res.status_code == 200
    assert "text/markdown" in dossier_res.headers["content-type"]
    assert len(dossier_res.text) > 500

    # 4. Ask conversational assistant
    ask_res = client.post(
        f"/api/advisory/{profile_id}/ask",
        json={"question": "What type of mask should my toddler wear?"},
    )
    assert ask_res.status_code == 200
    answer_data = ask_res.json()
    assert "mask" in answer_data["answer"].lower() or "child" in answer_data["answer"].lower()


def test_routines_calculate_endpoint(client: TestClient):
    """Verify standalone routine calculation endpoint."""
    res = client.post(
        "/api/routines/calculate",
        json={"baseline_aqi": 220, "city": "Beijing", "commute_mode": "cycling"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["diurnal_windows"]) == 5
    assert data["commute_routine"]["pm25_exposure_saved_pct"] > 30.0


def test_iaq_hacks_endpoint(client: TestClient):
    """Verify curated IAQ hacks endpoint."""
    res = client.get("/api/iaq/hacks?cooking_fuel=biomass_wood&has_hepa=true")
    assert res.status_code == 200
    data = res.json()
    assert len(data["hacks"]) >= 5


def test_alternatives_calculate_endpoint(client: TestClient):
    """Verify sustainable alternatives standalone endpoint."""
    res = client.post(
        "/api/alternatives/calculate",
        json={
            "commute_mode": "car_solo",
            "cooking_fuel": "natural_gas",
            "home_type": "detached_house",
            "city": "Salt Lake City",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_annual_co2_saved_kg"] > 0
    assert data["total_local_pm25_averted_grams"] > 0


def test_impact_calculate_endpoint(client: TestClient):
    """Verify impact dosimetry calculation endpoint."""
    res = client.post(
        "/api/impact/calculate",
        json={
            "baseline_aqi": 310,
            "exposure_reduction_pct": 60.0,
            "annual_co2_kg_saved": 1800.0,
            "num_household_members": 4,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["daily_pm25_lung_dose_avoided_ug"] > 1000.0
    assert data["equivalent_cigarettes_avoided"] > 1000.0


def test_vision_inspection_endpoint(client: TestClient):
    """Verify multimodal visual smog image assessment."""
    fake_image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"file": ("skyline.png", io.BytesIO(fake_image_bytes), "image/png")}
    data = {"prompt": "Analyze visual smog level"}

    res = client.post("/api/vision/inspect", files=files, data=data)
    assert res.status_code == 200
    body = res.json()
    assert "AeroSense Vision" in body["analysis"]
