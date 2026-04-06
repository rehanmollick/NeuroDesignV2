"""Tests for composite brain signal computation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from composites import compute_composites, COMPOSITE_REGIONS, COMPOSITE_INTERPRETATIONS
from regions import REGION_FUNCTIONS


def _make_region(name: str, act_a: float = 0.5, act_b: float = 0.5) -> dict:
    return {
        "name": name,
        "displayName": name,
        "function": "test",
        "activationA": act_a,
        "activationB": act_b,
        "delta": act_b - act_a,
    }


class TestCompositeRegionKeys:
    """All composite region keys must exist in REGION_FUNCTIONS."""

    def test_all_keys_in_region_functions(self):
        missing = []
        for signal, keys in COMPOSITE_REGIONS.items():
            for k in keys:
                if k not in REGION_FUNCTIONS:
                    missing.append(f"{signal}: {k}")
        assert not missing, f"Missing from REGION_FUNCTIONS: {missing}"

    def test_all_signals_have_interpretations(self):
        for signal in COMPOSITE_REGIONS:
            assert signal in COMPOSITE_INTERPRETATIONS, f"No interpretation for {signal}"

    def test_six_signals(self):
        assert len(COMPOSITE_REGIONS) == 6
        expected = {"reward", "cognitive_load", "visual_fluency", "social_trust", "memory", "attention"}
        assert set(COMPOSITE_REGIONS.keys()) == expected


class TestComputeComposites:
    """Test the compute_composites function."""

    def test_empty_regions(self):
        result = compute_composites([])
        assert len(result) == 6
        for c in result:
            assert c["value_a"] == 0.0
            assert c["value_b"] == 0.0
            assert c["interpretation"] == "Insufficient data for this signal"

    def test_full_region_list(self):
        # Build a region list with all composite constituent regions
        regions = []
        for signal, keys in COMPOSITE_REGIONS.items():
            for k in keys:
                regions.append(_make_region(k, act_a=0.6, act_b=0.4))

        result = compute_composites(regions)
        assert len(result) == 6

        for c in result:
            assert c["value_a"] == 0.6
            assert c["value_b"] == 0.4
            assert abs(c["delta"] - (-0.2)) < 0.001

    def test_partial_regions(self):
        # Only provide 1 region from the reward group
        regions = [_make_region("G_front_inf-Orbital", act_a=0.8, act_b=0.3)]
        result = compute_composites(regions)

        reward = next(c for c in result if c["signal"] == "reward")
        assert reward["value_a"] == 0.8
        assert reward["value_b"] == 0.3

        # Other signals should show "Insufficient data"
        cognitive = next(c for c in result if c["signal"] == "cognitive_load")
        assert cognitive["value_a"] == 0.0

    def test_similar_values_show_similar_text(self):
        regions = []
        for keys in COMPOSITE_REGIONS.values():
            for k in keys:
                regions.append(_make_region(k, act_a=0.5, act_b=0.51))

        result = compute_composites(regions)
        for c in result:
            assert "Similar" in c["interpretation"]

    def test_b_higher_shows_image_b(self):
        regions = []
        for keys in COMPOSITE_REGIONS.values():
            for k in keys:
                regions.append(_make_region(k, act_a=0.3, act_b=0.7))

        result = compute_composites(regions)
        for c in result:
            assert "Image B" in c["interpretation"]

    def test_a_higher_shows_image_a(self):
        regions = []
        for keys in COMPOSITE_REGIONS.values():
            for k in keys:
                regions.append(_make_region(k, act_a=0.7, act_b=0.3))

        result = compute_composites(regions)
        for c in result:
            assert "Image A" in c["interpretation"]

    def test_output_shape(self):
        regions = [_make_region("G_front_inf-Orbital")]
        result = compute_composites(regions)

        for c in result:
            assert "signal" in c
            assert "label" in c
            assert "value_a" in c
            assert "value_b" in c
            assert "delta" in c
            assert "interpretation" in c
