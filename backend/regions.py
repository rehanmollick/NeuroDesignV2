"""
Destrieux atlas ROI aggregation + static cognitive function lookup.
Loaded once at Modal container startup.
"""

import numpy as np
from typing import Optional

# Static lookup: Destrieux anatomical label -> (display name, cognitive function)
# Only the regions we actually surface in the UI
REGION_FUNCTIONS = {
    "G_oc-temp_lat-fusifor": (
        "Fusiform Gyrus",
        "Processes face recognition and identifying familiar visual objects",
    ),
    "G_oc-temp_med-Lingual": (
        "Lingual Gyrus",
        "Processes visual word recognition and color perception",
    ),
    "S_calcarine": (
        "Primary Visual Cortex",
        "Receives raw visual information from the eyes",
    ),
    "G_cuneus": (
        "Cuneus",
        "Processes basic visual features like edges and motion",
    ),
    "G_front_middle": (
        "Dorsolateral Prefrontal",
        "Working memory and cognitive effort — higher activation means more mental work",
    ),
    "G_front_inf-Orbital": (
        "Orbitofrontal Cortex",
        "Reward evaluation and emotional response to stimuli",
    ),
    "G_and_S_frontomargin": (
        "Frontomarginal Gyrus",
        "Decision-making and evaluating novel information",
    ),
    "G_precuneus": (
        "Precuneus",
        "Self-referential processing and spatial awareness",
    ),
    "G_parietal_sup": (
        "Superior Parietal",
        "Spatial attention — where you direct your gaze",
    ),
    "G_pariet_inf-Angular": (
        "Angular Gyrus",
        "Reading, language comprehension, and semantic memory",
    ),
    "G_pariet_inf-Supramar": (
        "Supramarginal Gyrus",
        "Processing written text and phonological awareness",
    ),
    "G_temp_sup-Lateral": (
        "Superior Temporal",
        "Auditory processing and social perception",
    ),
    "G_temp_sup-G_T_transv": (
        "Primary Auditory Cortex",
        "Initial processing of sound — responds to rhythm in visual patterns",
    ),
    "G_temporal_middle": (
        "Middle Temporal",
        "Recognizing objects and processing complex visual scenes",
    ),
    "S_temporal_sup": (
        "Superior Temporal Sulcus",
        "Biological motion and perceiving other people's intentions",
    ),
    "G_cingul-Post-dorsal": (
        "Posterior Cingulate",
        "Default mode — active during passive viewing and mind-wandering",
    ),
    "G_cingul-Post-ventral": (
        "Ventral Posterior Cingulate",
        "Emotional memory and autobiographical recall",
    ),
    "G_insular_short": (
        "Insula",
        "Interoception and emotional salience — gut reactions",
    ),
    "G_occipital_middle": (
        "Middle Occipital",
        "Processing complex visual shapes and object recognition",
    ),
    "G_occipital_sup": (
        "Superior Occipital",
        "Higher-order visual processing and spatial relationships",
    ),
    "G_oc-temp_med-Parahip": (
        "Parahippocampal",
        "Scene recognition and spatial memory encoding",
    ),
    "G_and_S_cingul-Mid-Ant": (
        "Anterior Cingulate",
        "Conflict detection and cognitive control",
    ),
    "S_intrapariet_and_P_trans": (
        "Intraparietal Sulcus",
        "Directs spatial attention and tracks where objects are",
    ),
    "S_postcentral": (
        "Postcentral Sulcus",
        "Processes touch and body awareness signals",
    ),
    "S_oc_sup_and_transversal": (
        "Superior Occipital Sulcus",
        "Connects visual areas for depth and motion processing",
    ),
    "S_occipital_ant": (
        "Anterior Occipital Sulcus",
        "Bridges early vision with higher-level object recognition",
    ),
    "S_oc_middle_and_Lunatus": (
        "Middle Occipital Sulcus",
        "Processes visual contours and shape boundaries",
    ),
    "S_oc-temp_lat": (
        "Lateral Occipitotemporal Sulcus",
        "Categorizes visual objects and scenes by type",
    ),
    "S_oc-temp_med_and_Lingual": (
        "Occipitotemporal Sulcus",
        "Connects visual processing to word and face recognition",
    ),
    "S_parieto_occipital": (
        "Parieto-Occipital Sulcus",
        "Integrates vision with spatial awareness and navigation",
    ),
    "S_collat_transv_ant": (
        "Anterior Collateral Sulcus",
        "Supports face and scene recognition memory",
    ),
    "S_collat_transv_post": (
        "Posterior Collateral Sulcus",
        "Processes visual scenes and spatial layout",
    ),
    "S_front_middle": (
        "Middle Frontal Sulcus",
        "Executive planning and sustained attention",
    ),
    "S_circular_insula_sup": (
        "Superior Circular Insular Sulcus",
        "Emotional awareness and sensory integration",
    ),
    "S_interm_prim-Jensen": (
        "Intermediate Sulcus",
        "Links auditory and visual processing areas",
    ),
    "S_orbital_lateral": (
        "Lateral Orbital Sulcus",
        "Evaluates reward value and emotional significance",
    ),
    "S_precentral-sup-part": (
        "Superior Precentral Sulcus",
        "Plans eye movements and visual search",
    ),
    "G_precentral": (
        "Precentral Gyrus",
        "Motor planning, responds to action-oriented imagery",
    ),
    "G_and_S_paracentral": (
        "Paracentral Lobule",
        "Motor and sensory processing for lower body",
    ),
    "G_and_S_subcentral": (
        "Subcentral Gyrus",
        "Taste and mouth sensation, responds to food imagery",
    ),
    "G_front_inf-Opercular": (
        "Inferior Frontal Operculum",
        "Language production and interpreting visual meaning",
    ),
    "G_temp_sup-Plan_polar": (
        "Temporal Polar Planum",
        "Processes familiar voices and emotional tone",
    ),
    "G_Ins_lg_and_S_cent_ins": (
        "Long Insular Gyrus",
        "Pain processing and emotional intensity",
    ),
    "G_and_S_occipital_inf": (
        "Inferior Occipital Gyrus",
        "Early visual processing of objects and faces",
    ),
    "Pole_occipital": (
        "Occipital Pole",
        "Sharpest central vision processing, what you look at directly",
    ),
    "Pole_temporal": (
        "Temporal Pole",
        "Links emotions to memories and familiar concepts",
    ),
    "Lat_Fis-ant-Horizont": (
        "Anterior Horizontal Fissure",
        "Separates frontal and temporal language areas",
    ),
    "Lat_Fis-ant-Vertical": (
        "Anterior Vertical Fissure",
        "Boundary between motor and language regions",
    ),
}

# Reverse mapping: region name -> which composite signal it belongs to
REGION_TO_COMPOSITE = {}
try:
    from composites import COMPOSITE_REGIONS
    for signal, keys in COMPOSITE_REGIONS.items():
        for k in keys:
            REGION_TO_COMPOSITE[k] = signal
except ImportError:
    pass

# What each region's activation means for design decisions (expandable UI)
DESIGN_IMPLICATIONS = {
    "G_oc-temp_lat-fusifor": "This design triggers strong face processing. Faces in layouts build trust and human connection. If Image A activates this more, its use of faces or face-like elements is more effective at engaging viewers.",
    "G_oc-temp_med-Lingual": "Visual word recognition is activated. This region responds to readable text and color perception. Higher activation means the text elements are being actively processed, not skimmed over.",
    "S_calcarine": "Primary visual cortex is processing raw visual information. Higher activation means more visual complexity. Extreme values suggest visual clutter rather than rich content.",
    "G_cuneus": "Basic visual feature processing (edges, motion, contrast). Higher activation means the design has more visual elements competing for early processing. Good if intentional, bad if chaotic.",
    "G_front_middle": "The brain is working hard here. This region handles working memory and cognitive effort. High activation can mean engagement (good) or confusion (bad). Check reward signals to disambiguate.",
    "G_front_inf-Orbital": "This is the reward center. Higher activation means the brain finds this design aesthetically pleasing. This is the strongest predictor of design preference.",
    "G_and_S_frontomargin": "Decision-making circuits are engaged. The viewer is evaluating something novel. This suggests the design presents new or unexpected information that requires active evaluation.",
    "G_precuneus": "Self-referential processing. The viewer is connecting the design to their own experience and identity. High activation means the design feels personally relevant.",
    "G_parietal_sup": "Spatial attention is directed. This region controls where the eye goes. Higher activation means the design has a clear visual hierarchy that guides the viewer's gaze.",
    "G_pariet_inf-Angular": "Language and semantic memory processing. The viewer is reading and comprehending text content. High activation means text elements are being deeply processed, not just seen.",
    "G_pariet_inf-Supramar": "Written text processing. The viewer is reading. If one image activates this more, its text content is more engaging or requires more processing.",
    "G_temp_sup-Lateral": "Social perception is activated. The viewer is processing social cues in the design. Higher means more human/social elements are present and noticed.",
    "G_temp_sup-G_T_transv": "Auditory processing responds to rhythm in visual patterns. Visual rhythm (repeated elements, grids, patterns) can trigger this area.",
    "G_temporal_middle": "Object recognition and complex scene processing. Higher activation means the brain is identifying and categorizing multiple visual elements.",
    "S_temporal_sup": "The brain is reading social intentions. This region tracks biological motion and perceived intentions of people in images. Higher activation means social elements are compelling.",
    "G_cingul-Post-dorsal": "Default mode network is active. The viewer may be mind-wandering or passively viewing. High activation during design viewing can mean the design isn't capturing active attention.",
    "G_cingul-Post-ventral": "Emotional memory is activated. The design is triggering autobiographical associations. High activation means the design connects to personal emotional memories.",
    "G_insular_short": "Gut reaction center. The insula processes emotional salience. Strong activation means the design provokes a visceral emotional response, positive or negative.",
    "G_occipital_middle": "Complex visual shapes are being processed. Higher activation means more intricate visual elements. Good for rich designs, concerning for cluttered ones.",
    "G_occipital_sup": "Higher-order visual processing. Spatial relationships between elements are being analyzed. Higher activation means the layout structure is complex.",
    "G_oc-temp_med-Parahip": "Scene recognition. The brain is encoding the spatial layout as a memorable scene. High activation means the design's composition is being stored in spatial memory.",
    "G_and_S_cingul-Mid-Ant": "Conflict detection. The brain is resolving competing information. High activation can mean confusing navigation or conflicting visual elements.",
    "S_intrapariet_and_P_trans": "Spatial attention tracking. The viewer's eyes are being directed to specific locations. Higher activation means stronger visual guidance in the design.",
    "S_postcentral": "Body awareness signals. Designs with physical/tactile imagery can trigger this area.",
    "S_oc_sup_and_transversal": "Depth and motion processing. The brain is analyzing spatial depth cues in the design.",
    "S_occipital_ant": "Bridging early vision with object recognition. The brain is transitioning from seeing shapes to identifying what they are.",
    "S_oc_middle_and_Lunatus": "Visual contour processing. The brain is tracing boundaries and shape edges in the design. Clean lines and clear boundaries activate this.",
    "S_oc-temp_med_and_Lingual": "Connecting vision to word and face recognition. This region bridges visual processing with higher-level identification.",
    "S_parieto_occipital": "Integrating vision with spatial navigation. The brain is building a spatial map of the design layout.",
    "S_collat_transv_ant": "Face and scene memory. The brain is encoding faces and scenes for later recall. Higher activation = more memorable faces/scenes.",
    "S_collat_transv_post": "Visual scene processing. The brain is analyzing the overall spatial layout of the design as a complete scene.",
    "S_front_middle": "Executive planning and sustained attention. The viewer is maintaining focused attention on the design, possibly planning where to look next.",
    "S_circular_insula_sup": "Emotional awareness. The viewer is consciously processing their emotional response to the design.",
    "S_interm_prim-Jensen": "Audio-visual integration. Visual patterns that suggest sound or rhythm activate this area.",
    "S_orbital_lateral": "Reward evaluation. The brain is assessing the emotional value of what it sees. Higher activation means stronger positive or negative valuation.",
    "S_precentral-sup-part": "Eye movement planning. The viewer is actively scanning the design. Higher activation means the design triggers deliberate visual search.",
    "G_precentral": "Motor planning. Action-oriented imagery (buttons, interactive elements) can trigger this area. Higher activation suggests the design invites interaction.",
    "G_and_S_paracentral": "Motor and sensory processing. Less relevant for static design evaluation.",
    "G_and_S_subcentral": "Taste and oral sensation. Food imagery strongly activates this area.",
    "G_front_inf-Opercular": "Language production and visual meaning. The viewer is interpreting the semantic content of the design.",
    "G_temp_sup-Plan_polar": "Emotional tone processing. The viewer is reading the emotional atmosphere of the design.",
    "G_Ins_lg_and_S_cent_ins": "Emotional intensity. Strong activation means the design provokes intense feelings, positive or negative.",
    "G_and_S_occipital_inf": "Early object and face processing. The brain is detecting faces and objects at a pre-conscious level.",
    "Pole_occipital": "Central vision processing. What the viewer looks at most directly. Higher activation means the design's focal point is engaging.",
    "Pole_temporal": "Linking emotions to memories. The design is connecting with familiar concepts and emotional associations.",
    "Lat_Fis-ant-Horizont": "Boundary between language areas. Relevant for designs with significant text content.",
    "Lat_Fis-ant-Vertical": "Boundary between motor and language regions. Less directly relevant for design evaluation.",
}


def load_region_map(mesh_json_path: str) -> dict[str, list[int]]:
    """Load vertex-to-region mapping from mesh.json."""
    import json
    with open(mesh_json_path) as f:
        mesh = json.load(f)
    return mesh.get("regionMap", {})


def aggregate_regions(
    activations: np.ndarray,
    region_map: dict[str, list[int]],
) -> list[dict]:
    """
    Compute per-region mean activations for ALL regions.
    Returns all regions sorted by absolute delta.
    Caller is responsible for filtering to top_n for display.
    """
    results = []

    for region_name, vertex_indices in region_map.items():
        if not vertex_indices:
            continue

        indices = np.array(vertex_indices)
        # activations is shape (2, n_vertices): [imageA, imageB]
        act_a = float(activations[0, indices].mean())
        act_b = float(activations[1, indices].mean())
        delta = act_b - act_a

        display_name, function_desc = REGION_FUNCTIONS.get(
            region_name,
            (region_name.replace("_", " ").replace("-", " "), "Cortical region"),
        )

        results.append({
            "name": region_name,
            "displayName": display_name,
            "function": function_desc,
            "activationA": act_a,
            "activationB": act_b,
            "delta": delta,
            "designImplication": DESIGN_IMPLICATIONS.get(region_name, ""),
            "composite": REGION_TO_COMPOSITE.get(region_name, ""),
        })

    results.sort(key=lambda r: abs(r["delta"]), reverse=True)
    return results
