"""
Exhaustive tests covering dataset loader resilience (NaN, None, corrupted rows) and API payload limits.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.data.loader import _safe_float, _safe_int, _safe_str

client = TestClient(app)


class TestLoaderSafeHelpers:
    @pytest.mark.parametrize("val,default,expected", [
        (np.nan, 0.0, 0.0),
        (None, 10.5, 10.5),
        ("nan", 0.0, 0.0),
        ("123.45", 0.0, 123.45),
        ("invalid", 5.0, 5.0),
        (42, 0.0, 42.0),
    ])
    def test_safe_float_conversions(self, val, default, expected):
        assert _safe_float(val, default) == expected

    @pytest.mark.parametrize("val,default,expected", [
        (np.nan, 0, 0),
        (None, 10, 10),
        ("nan", 0, 0),
        ("500", 0, 500),
        ("invalid_int", 1, 1),
        (42.9, 0, 42),
    ])
    def test_safe_int_conversions(self, val, default, expected):
        assert _safe_int(val, default) == expected

    @pytest.mark.parametrize("val,default,expected", [
        (np.nan, "default", "default"),
        (None, "default", "default"),
        ("nan", "default", "default"),
        ("None", "default", "default"),
        ("  Python Programming  ", "", "Python Programming"),
        (123, "", "123"),
    ])
    def test_safe_str_conversions(self, val, default, expected):
        assert _safe_str(val, default) == expected


class TestApiPayloadLimitsAndMetadata:
    def test_recommendations_endpoint_returns_role_metadata(self):
        response = client.get("/recommendations?job_role=Machine%20Learning%20Dev")
        assert response.status_code == 200
        data = response.json()
        assert "confidence" in data
        assert "source" in data
        assert "suggestions" in data
        assert "message" in data
        assert data["confidence"] == "high"
        assert data["source"] in ["alias", "Fuzzy Match", "Verified Career Path"]

    def test_recommendations_endpoint_payload_limit_rejection(self):
        long_role = "A" * 200
        response = client.get(f"/recommendations?job_role={long_role}")
        # Should reject with 422 Unprocessable Entity due to max_length=150
        assert response.status_code == 422

    def test_career_path_endpoint_returns_metadata(self):
        response = client.get("/career_path/AI%20Engineer")
        assert response.status_code == 200
        data = response.json()
        assert "confidence" in data
        assert "source" in data
        assert "suggestions" in data
        assert data["confidence"] == "high"

    def test_career_path_payload_limit_rejection(self):
        long_role = "B" * 200
        response = client.get(f"/career_path/{long_role}")
        assert response.status_code == 422

    def test_post_recommendations_payload_limit_rejection(self):
        payload = {
            "current_role": "X" * 200,
            "user_skills": ["Python"],
            "target_role": "AI Engineer"
        }
        response = client.post("/recommendations", json=payload)
        assert response.status_code == 422
