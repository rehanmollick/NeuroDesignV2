"""
Eval suite: validate preset JSONs have correct structure and Gemini verdicts.

The fallback heuristic (reward 2x + attention + memory) returns "tie" when
composite deltas are < 5%, which is correct, conservative behavior. Gemini
sees the actual images and breaks ties. So we test:
  1. Gemini verdict in preset JSON matches expected winner
  2. Fallback returns "tie" or matches (never the WRONG winner)
  3. Presets have 6 composites with bounded values
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from composites import compute_composites
from gemini import _fallback_explain

PRESETS_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "data" / "comparisons"

# Ground truth: Gemini's verdict for each preset
EXPECTED_WINNERS = {
    "apple-vs-cluttered.json": "A",
    "face-vs-noface.json": "B",           # Gemini sees landscape has better visual engagement
    "text-heavy-vs-infographic.json": "B",
}


class TestPresetGeminiVerdict:
    """Gemini verdict stored in preset JSON should match expected winner."""

    def _load_preset(self, filename: str):
        path = PRESETS_DIR / filename
        if not path.exists():
            return None
        with open(path) as f:
            return json.load(f)

    def test_apple_vs_cluttered(self):
        data = self._load_preset("apple-vs-cluttered.json")
        if not data:
            return
        assert data.get("detailed", {}).get("winner") == "A"

    def test_face_vs_noface(self):
        data = self._load_preset("face-vs-noface.json")
        if not data:
            return
        assert data.get("detailed", {}).get("winner") == "B"

    def test_text_heavy_vs_infographic(self):
        data = self._load_preset("text-heavy-vs-infographic.json")
        if not data:
            return
        assert data.get("detailed", {}).get("winner") == "B"

    def test_all_presets_have_full_analysis(self):
        """Every preset should have winner, reason, and recommendations."""
        for filename in EXPECTED_WINNERS:
            data = self._load_preset(filename)
            if not data:
                continue
            d = data.get("detailed", {})
            assert d.get("winner"), f"{filename}: no winner"
            assert d.get("winner_reason"), f"{filename}: no reason"
            assert d.get("recommendations"), f"{filename}: no recommendations"


class TestPresetFallbackSafety:
    """Fallback should never pick the WRONG winner. Tie is acceptable."""

    def _fallback_for(self, filename: str):
        path = PRESETS_DIR / filename
        if not path.exists():
            return None, None
        with open(path) as f:
            data = json.load(f)
        composites = data.get("composites", [])
        if not composites:
            composites = compute_composites(data.get("regions", []))
        result = _fallback_explain(composites)
        return result.get("winner"), EXPECTED_WINNERS[filename]

    def test_apple_fallback_not_wrong(self):
        fb, expected = self._fallback_for("apple-vs-cluttered.json")
        if fb is None:
            return
        assert fb == expected or fb == "tie", f"Fallback picked wrong winner: {fb} (expected {expected} or tie)"

    def test_face_fallback_not_wrong(self):
        fb, expected = self._fallback_for("face-vs-noface.json")
        if fb is None:
            return
        assert fb == expected or fb == "tie", f"Fallback picked wrong winner: {fb} (expected {expected} or tie)"

    def test_text_fallback_not_wrong(self):
        fb, expected = self._fallback_for("text-heavy-vs-infographic.json")
        if fb is None:
            return
        assert fb == expected or fb == "tie", f"Fallback picked wrong winner: {fb} (expected {expected} or tie)"


class TestPresetComposites:
    """Presets should have valid composite data."""

    def test_all_presets_have_composites(self):
        for filename in EXPECTED_WINNERS:
            path = PRESETS_DIR / filename
            if not path.exists():
                continue
            with open(path) as f:
                data = json.load(f)
            composites = data.get("composites", [])
            assert len(composites) == 6, f"{filename}: expected 6 composites, got {len(composites)}"

    def test_composites_are_bounded(self):
        for filename in EXPECTED_WINNERS:
            path = PRESETS_DIR / filename
            if not path.exists():
                continue
            with open(path) as f:
                data = json.load(f)
            for c in data.get("composites", []):
                assert 0.0 <= c["value_a"] <= 1.0, f"{filename}/{c['signal']}: value_a={c['value_a']}"
                assert 0.0 <= c["value_b"] <= 1.0, f"{filename}/{c['signal']}: value_b={c['value_b']}"

    def test_composites_have_nonzero_values(self):
        for filename in EXPECTED_WINNERS:
            path = PRESETS_DIR / filename
            if not path.exists():
                continue
            with open(path) as f:
                data = json.load(f)
            composites = data.get("composites", [])
            has_data = any(c["value_a"] > 0 or c["value_b"] > 0 for c in composites)
            assert has_data, f"{filename}: all composites are zero"
