"""
Precompute TRIBE v2 comparison for an image pair.
Run in Colab or locally with a GPU.

Usage:
  python scripts/precompute.py \
    --imageA images/apple.png \
    --imageB images/cluttered.png \
    --output frontend/public/data/comparisons/apple-vs-cluttered.json \
    --name-a "Apple.com" \
    --name-b "Cluttered Site" \
    --image-url-a "/images/apple.com.png" \
    --image-url-b "/images/cluttered-design.png"
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--imageA", required=True)
    parser.add_argument("--imageB", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--name-a", default="Image A")
    parser.add_argument("--name-b", default="Image B")
    parser.add_argument("--image-url-a", default="")
    parser.add_argument("--image-url-b", default="")
    parser.add_argument("--mesh", default="frontend/public/data/mesh.json")
    args = parser.parse_args()

    import numpy as np
    from PIL import Image

    from inference import predict, normalize_joint
    from regions import load_region_map, aggregate_regions
    from composites import compute_composites
    from gemini import explain as gemini_explain

    # Load model
    print("Loading TRIBE v2...")
    from tribev2 import TribeModel
    model = TribeModel.from_pretrained("facebook/tribev2")
    print("TRIBE v2 loaded")

    # Load images
    img_a = Image.open(args.imageA).convert("RGB")
    img_b = Image.open(args.imageB).convert("RGB")
    print(f"Images: {img_a.size} / {img_b.size}")

    # Run inference
    print("Running inference A...")
    raw_a = predict(img_a, model)
    print("Running inference B...")
    raw_b = predict(img_b, model)

    # Quality check
    corr = np.corrcoef(raw_a, raw_b)[0, 1]
    print(f"Correlation between predictions: {corr:.3f}")
    if corr > 0.95:
        print("WARNING: High correlation -- images may look too similar to TRIBE v2")

    # Normalize
    norm_a, norm_b = normalize_joint(raw_a, raw_b)

    # Load region map
    mesh_path = Path(args.mesh)
    region_map = load_region_map(str(mesh_path)) if mesh_path.exists() else {}
    if not region_map:
        print("WARNING: No region map found. Regions will be empty.")

    # Aggregate ALL regions (no truncation)
    activations = np.stack([norm_a, norm_b], axis=0)
    all_regions = aggregate_regions(activations, region_map)

    # Compute composite brain signals
    composites = compute_composites(all_regions)
    print(f"Composites: {[c['signal'] for c in composites]}")

    # Gemini multimodal explanation (sends actual images)
    print("Generating Gemini analysis...")
    detailed = gemini_explain(all_regions, composites, img_a, img_b)

    if detailed:
        print(f"Winner: {detailed.get('winner', '?')}")
        print(f"Reason: {detailed.get('winner_reason', '(none)')[:100]}")
        if detailed.get("_fallback"):
            print("WARNING: Used fallback (Gemini unavailable). Set GEMINI_API_KEY.")
    else:
        print("WARNING: No analysis generated. Set GEMINI_API_KEY.")

    # Top 20 regions for the response
    top_regions = all_regions[:20]

    result = {
        "imageA": {"url": args.image_url_a, "name": args.name_a},
        "imageB": {"url": args.image_url_b, "name": args.name_b},
        "activations": {
            "imageA": norm_a.tolist(),
            "imageB": norm_b.tolist(),
        },
        "regions": top_regions,
        "composites": composites,
        "summary": detailed.get("winner_reason", ""),
        "detailed": detailed,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(result, f)

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"Written: {out} ({size_mb:.1f} MB)")
    print(f"Regions: {len(top_regions)} (of {len(all_regions)} total)")
    if detailed.get("winner"):
        print(f"Verdict: Image {detailed['winner']} wins")


if __name__ == "__main__":
    main()
