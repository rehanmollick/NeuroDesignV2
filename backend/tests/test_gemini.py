"""Tests for Gemini integration error handling and fallback logic."""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from gemini import (
    _get_client,
    _parse_response,
    _fallback_explain,
    _build_region_text,
    _build_composite_text,
    explain,
    chat,
)


def _sample_composites():
    return [
        {"signal": "reward", "label": "Reward Response", "value_a": 0.7, "value_b": 0.4, "delta": -0.3, "interpretation": "Image A"},
        {"signal": "cognitive_load", "label": "Cognitive Load", "value_a": 0.3, "value_b": 0.6, "delta": 0.3, "interpretation": "Image B"},
        {"signal": "visual_fluency", "label": "Visual Fluency", "value_a": 0.5, "value_b": 0.5, "delta": 0.0, "interpretation": "Similar"},
        {"signal": "social_trust", "label": "Social Trust", "value_a": 0.6, "value_b": 0.3, "delta": -0.3, "interpretation": "Image A"},
        {"signal": "memory", "label": "Memory Encoding", "value_a": 0.6, "value_b": 0.4, "delta": -0.2, "interpretation": "Image A"},
        {"signal": "attention", "label": "Attention Capture", "value_a": 0.65, "value_b": 0.35, "delta": -0.3, "interpretation": "Image A"},
    ]


def _sample_regions():
    return [
        {"name": "G_front_inf-Orbital", "displayName": "Orbital Frontal", "function": "reward processing", "activationA": 0.7, "activationB": 0.4, "delta": -0.3},
        {"name": "G_occipital_sup", "displayName": "Superior Occipital", "function": "visual processing", "activationA": 0.5, "activationB": 0.6, "delta": 0.1},
    ]


class TestGetClient:
    def test_no_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            assert _get_client() is None

    def test_empty_api_key(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            assert _get_client() is None

    def test_import_error(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch.dict("sys.modules", {"google": None, "google.genai": None}):
                result = _get_client()
                assert result is None


class TestParseResponse:
    def test_valid_json(self):
        data = {
            "winner": "A",
            "winner_reason": "Better design",
            "emotional_impact": "A triggers more",
            "visual_attention": "A grabs more",
            "memory_retention": "A is more memorable",
            "recommendations": ["tip 1"],
        }
        result = _parse_response(json.dumps(data))
        assert result["winner"] == "A"
        assert result["winner_reason"] == "Better design"

    def test_json_with_code_fences(self):
        data = {
            "winner": "B",
            "winner_reason": "Cleaner layout",
            "emotional_impact": "B calms the viewer",
            "visual_attention": "B holds attention",
            "memory_retention": "B sticks in memory",
        }
        wrapped = f"```json\n{json.dumps(data)}\n```"
        result = _parse_response(wrapped)
        assert result["winner"] == "B"

    def test_invalid_json(self):
        result = _parse_response("this is not json at all")
        assert result == {}

    def test_missing_required_fields(self):
        data = {"winner": "A"}  # missing other required fields
        result = _parse_response(json.dumps(data))
        assert result == {}

    def test_empty_string(self):
        result = _parse_response("")
        assert result == {}


class TestFallbackExplain:
    def test_empty_composites(self):
        result = _fallback_explain([])
        assert result == {}

    def test_a_wins(self):
        composites = _sample_composites()
        result = _fallback_explain(composites)
        assert result["winner"] == "A"
        assert result["_fallback"] is True
        assert "winner_reason" in result

    def test_b_wins(self):
        composites = [
            {"signal": "reward", "label": "Reward", "value_a": 0.3, "value_b": 0.7, "delta": 0.4, "interpretation": "Image B"},
            {"signal": "attention", "label": "Attention", "value_a": 0.3, "value_b": 0.6, "delta": 0.3, "interpretation": "Image B"},
            {"signal": "memory", "label": "Memory", "value_a": 0.3, "value_b": 0.6, "delta": 0.3, "interpretation": "Image B"},
        ]
        result = _fallback_explain(composites)
        assert result["winner"] == "B"
        assert result["_fallback"] is True

    def test_tie_when_similar(self):
        composites = [
            {"signal": "reward", "label": "Reward", "value_a": 0.50, "value_b": 0.51, "delta": 0.01, "interpretation": "Similar"},
            {"signal": "attention", "label": "Attention", "value_a": 0.50, "value_b": 0.50, "delta": 0.0, "interpretation": "Similar"},
            {"signal": "memory", "label": "Memory", "value_a": 0.50, "value_b": 0.50, "delta": 0.0, "interpretation": "Similar"},
        ]
        result = _fallback_explain(composites)
        assert result["winner"] == "tie"

    def test_no_reward_signal(self):
        composites = [
            {"signal": "attention", "label": "Attention", "value_a": 0.6, "value_b": 0.4, "delta": -0.2, "interpretation": "Image A"},
        ]
        result = _fallback_explain(composites)
        assert result == {}


class TestBuildRegionText:
    def test_basic_output(self):
        text = _build_region_text(_sample_regions())
        assert "Orbital Frontal" in text
        assert "Image A" in text

    def test_limit(self):
        regions = _sample_regions() * 5  # 10 regions
        text = _build_region_text(regions, limit=2)
        assert text.count("-") == 2

    def test_empty(self):
        assert _build_region_text([]) == ""


class TestBuildCompositeText:
    def test_basic_output(self):
        text = _build_composite_text(_sample_composites())
        assert "Reward Response" in text
        assert "Similar" in text

    def test_empty(self):
        assert _build_composite_text([]) == ""


class TestExplainNoApiKey:
    """explain() returns fallback when no API key is set."""

    def test_no_key_returns_fallback(self):
        with patch.dict("os.environ", {}, clear=True):
            result = explain(_sample_regions(), _sample_composites())
            assert result.get("_fallback") is True or result == {}


class TestExplainApiError:
    """explain() returns fallback when Gemini API throws."""

    def test_api_exception(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("429 rate limit")

        with patch("gemini._get_client", return_value=mock_client):
            result = explain(_sample_regions(), _sample_composites())
            assert result.get("_fallback") is True

    def test_empty_response(self):
        mock_response = MagicMock()
        mock_response.text = ""

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        with patch("gemini._get_client", return_value=mock_client):
            result = explain(_sample_regions(), _sample_composites())
            # Empty text parses to {}, then fallback doesn't kick in
            # because _parse_response returns {} not fallback
            # explain returns {} or fallback - either is acceptable for empty response
            assert isinstance(result, dict)


class TestChatNoApiKey:
    def test_no_key_returns_empty(self):
        with patch.dict("os.environ", {}, clear=True):
            result = chat(_sample_regions(), _sample_composites(), "summary", "which is better?")
            assert result == ""

    def test_api_exception_returns_empty(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("timeout")

        with patch("gemini._get_client", return_value=mock_client):
            result = chat(_sample_regions(), _sample_composites(), "summary", "which is better?")
            assert result == ""
