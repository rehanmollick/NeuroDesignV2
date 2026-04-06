"""
Composite brain signals — maps Destrieux atlas regions into 6 high-level
cognitive signals for design evaluation.

Each composite is the mean activation of its constituent regions.
Regions not present in the input are silently skipped.
"""


# Destrieux atlas key -> composite group
COMPOSITE_REGIONS = {
    "reward": [
        "G_front_inf-Orbital",      # Orbitofrontal cortex
        "S_orbital_lateral",         # Lateral orbital sulcus
        "G_cingul-Post-ventral",     # Ventral posterior cingulate
    ],
    "cognitive_load": [
        "G_front_middle",            # Dorsolateral prefrontal
        "G_and_S_cingul-Mid-Ant",    # Anterior cingulate
        "S_front_middle",            # Middle frontal sulcus
    ],
    "visual_fluency": [
        "S_calcarine",               # Primary visual cortex
        "G_cuneus",                  # Cuneus
        "G_occipital_middle",        # Middle occipital
        "G_occipital_sup",           # Superior occipital
    ],
    "social_trust": [
        "G_oc-temp_lat-fusifor",     # Fusiform gyrus (faces)
        "S_temporal_sup",            # Superior temporal sulcus
        "G_insular_short",           # Insula (gut reactions)
    ],
    "memory": [
        "G_oc-temp_med-Parahip",     # Parahippocampal
        "G_pariet_inf-Angular",      # Angular gyrus
        "G_precuneus",               # Precuneus
        "Pole_temporal",             # Temporal pole
    ],
    "attention": [
        "G_parietal_sup",            # Superior parietal
        "S_intrapariet_and_P_trans", # Intraparietal sulcus
        "S_precentral-sup-part",     # Superior precentral (eye mvmt)
    ],
}

# What each signal means for design evaluation
COMPOSITE_INTERPRETATIONS = {
    "reward": {
        "label": "Reward & Aesthetic Pleasure",
        "high": "Aesthetically pleasing, triggers positive emotional response",
        "low": "Neutral or unpleasant aesthetic reaction",
    },
    "cognitive_load": {
        "label": "Cognitive Load",
        "high": "Brain working hard — confusion OR deep engagement (check reward level)",
        "low": "Easy to process, minimal mental effort required",
    },
    "visual_fluency": {
        "label": "Visual Processing",
        "high": "Rich visual complexity — clutter if extreme, engaging if moderate",
        "low": "Simple visual input, minimal visual processing",
    },
    "social_trust": {
        "label": "Social & Trust Signals",
        "high": "Faces or social cues detected, builds human connection and trust",
        "low": "No social cues, feels impersonal",
    },
    "memory": {
        "label": "Memorability",
        "high": "Memorable, personally relevant, activates meaning-making circuits",
        "low": "Forgettable, generic, low personal relevance",
    },
    "attention": {
        "label": "Directed Attention",
        "high": "Strong visual guidance, sustained focused gaze",
        "low": "Unfocused scanning, no clear visual hierarchy",
    },
}


def compute_composites(regions: list[dict]) -> list[dict]:
    """
    Compute 6 composite brain signals from a full list of region dicts.

    Each region dict must have: name, activationA, activationB.
    Returns a list of composite dicts with: signal, label, value_a, value_b,
    delta, interpretation.
    """
    # Index regions by name for fast lookup
    by_name = {r["name"]: r for r in regions}

    results = []
    for signal, region_keys in COMPOSITE_REGIONS.items():
        matched = [by_name[k] for k in region_keys if k in by_name]

        if not matched:
            results.append({
                "signal": signal,
                "label": COMPOSITE_INTERPRETATIONS[signal]["label"],
                "value_a": 0.0,
                "value_b": 0.0,
                "delta": 0.0,
                "interpretation": "Insufficient data for this signal",
            })
            continue

        value_a = sum(r["activationA"] for r in matched) / len(matched)
        value_b = sum(r["activationB"] for r in matched) / len(matched)
        delta = value_b - value_a

        # Pick interpretation based on which image scores higher
        info = COMPOSITE_INTERPRETATIONS[signal]
        higher = "B" if delta > 0 else "A"
        magnitude = abs(delta) * 100

        if magnitude < 2:
            interpretation = f"Similar {info['label'].lower()} for both images"
        else:
            interpretation = (
                f"Image {higher} scores {magnitude:.0f}% higher. "
                f"High: {info['high']}. Low: {info['low']}."
            )

        results.append({
            "signal": signal,
            "label": info["label"],
            "value_a": round(value_a, 4),
            "value_b": round(value_b, 4),
            "delta": round(delta, 4),
            "interpretation": interpretation,
        })

    return results
