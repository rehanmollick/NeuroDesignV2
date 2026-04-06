"""
Gemini 2.5 Flash integration via Google AI Studio (google-genai SDK).
Multimodal: sees both actual images + composite brain signals + RAG context.
Replaces the old gemma.py text-only approach.
"""

import os
import json
import base64
from io import BytesIO
from PIL import Image

from neuro_knowledge import KNOWLEDGE_BASE


def _get_client():
    """Get google-genai client. Returns None if no API key."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Gemini client init error: {e}")
        return None


def _resize_for_gemini(img: Image.Image, max_dim: int = 512) -> bytes:
    """Resize image to max_dim and return JPEG bytes."""
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _build_region_text(regions: list[dict], limit: int = 5) -> str:
    """Format top regions by absolute delta as readable text."""
    top = sorted(regions, key=lambda r: abs(r["delta"]), reverse=True)[:limit]
    lines = []
    for r in top:
        direction = "Image B" if r["delta"] > 0 else "Image A"
        pct = abs(r["delta"]) * 100
        lines.append(
            f"- {r['displayName']} ({r['function']}): "
            f"{direction} activates this {pct:.0f}% more"
        )
    return "\n".join(lines)


def _build_composite_text(composites: list[dict]) -> str:
    """Format composite signals as readable text."""
    lines = []
    for c in composites:
        higher = "B" if c["delta"] > 0 else "A"
        mag = abs(c["delta"]) * 100
        if mag < 2:
            lines.append(f"- {c['label']}: Similar for both images")
        else:
            lines.append(
                f"- {c['label']}: Image {higher} is {mag:.0f}% higher"
            )
    return "\n".join(lines)


def explain(
    regions: list[dict],
    composites: list[dict],
    image_a: Image.Image | None = None,
    image_b: Image.Image | None = None,
) -> dict:
    """
    Generate winner verdict + structured analysis in a single Gemini call.
    Returns dict with: winner, winner_reason, emotional_impact,
    visual_attention, memory_retention, recommendations.
    Falls back to text-only if images unavailable or API fails.
    """
    client = _get_client()
    if not client:
        return _fallback_explain(composites)

    composite_text = _build_composite_text(composites)
    region_text = _build_region_text(regions)

    prompt = f"""{KNOWLEDGE_BASE}

---

## BRAIN ACTIVATION DATA FOR THIS COMPARISON

### Composite Brain Signals (6 high-level patterns)
{composite_text}

### Top 5 Individual Region Differences
{region_text}

---

## YOUR TASK

Look at both images. Consider the brain activation patterns above.
Use the neuroaesthetics knowledge to determine which design is more
effective and why.

Respond in EXACTLY this JSON format (no markdown, no code fences, raw JSON):
{{
  "winner": "A" or "B" or "tie",
  "winner_reason": "One clear sentence explaining why this design wins",
  "emotional_impact": "2 sentences comparing the emotional response each image triggers in the brain",
  "visual_attention": "2 sentences about which image captures and holds attention better, based on the attention and visual fluency signals",
  "memory_retention": "1-2 sentences about which image is more memorable and why, based on the memory signal",
  "recommendations": ["specific actionable tip 1", "specific actionable tip 2", "specific actionable tip 3"]
}}

Be specific. Reference actual brain signals. Use plain language, no jargon."""

    # Build multimodal content parts
    try:
        from google.genai import types
    except ImportError:
        types = None

    parts = []

    if image_a is not None and image_b is not None and types:
        try:
            bytes_a = _resize_for_gemini(image_a)
            bytes_b = _resize_for_gemini(image_b)
            parts.append(types.Part.from_text(text="Image A:"))
            parts.append(types.Part.from_bytes(data=bytes_a, mime_type="image/jpeg"))
            parts.append(types.Part.from_text(text="Image B:"))
            parts.append(types.Part.from_bytes(data=bytes_b, mime_type="image/jpeg"))
        except Exception as e:
            print(f"Image encoding error: {e}")

    if types:
        parts.append(types.Part.from_text(text=prompt))
    else:
        parts.append({"text": prompt})

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=parts,
        )
        text = response.text.strip()
        return _parse_response(text)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _fallback_explain(composites)


def _parse_response(text: str) -> dict:
    """Parse Gemini JSON response with cleanup."""
    clean = text
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
        clean = clean.rsplit("```", 1)[0]
    clean = clean.strip()

    required = [
        "winner", "winner_reason", "emotional_impact",
        "visual_attention", "memory_retention",
    ]

    try:
        result = json.loads(clean)
        if all(result.get(k) for k in required):
            return result
        print(f"Gemini incomplete JSON: missing {[k for k in required if not result.get(k)]}")
    except json.JSONDecodeError:
        print(f"Gemini JSON parse error: {text[:200]}")

    return {}


def _fallback_explain(composites: list[dict]) -> dict:
    """
    Degraded fallback when Gemini is unavailable.
    Uses composite signals only, no images.
    """
    if not composites:
        return {}

    # Simple heuristic: reward is the strongest signal for design quality
    reward = next((c for c in composites if c["signal"] == "reward"), None)
    attention = next((c for c in composites if c["signal"] == "attention"), None)
    memory = next((c for c in composites if c["signal"] == "memory"), None)

    if not reward:
        return {}

    # Score: reward weighted 2x, attention 1x, memory 1x
    score_a = reward["value_a"] * 2
    score_b = reward["value_b"] * 2
    if attention:
        score_a += attention["value_a"]
        score_b += attention["value_b"]
    if memory:
        score_a += memory["value_a"]
        score_b += memory["value_b"]

    winner = "A" if score_a > score_b else "B"
    margin = abs(score_a - score_b) / max(score_a, score_b, 0.01) * 100

    if margin < 5:
        winner = "tie"
        reason = "Both designs produce very similar brain responses across reward, attention, and memory signals."
    else:
        reason = (
            f"Image {winner} triggers stronger reward and aesthetic pleasure "
            f"signals in the brain, with better attention capture."
        )

    return {
        "winner": winner,
        "winner_reason": reason,
        "emotional_impact": "Visual analysis unavailable. Verdict based on brain activation patterns only.",
        "visual_attention": "",
        "memory_retention": "",
        "recommendations": [],
        "_fallback": True,
    }


def chat(
    regions: list[dict],
    composites: list[dict],
    summary: str,
    user_message: str,
    history: list[dict] | None = None,
    detailed: dict | None = None,
) -> str:
    """Chat about the comparison. No images, uses analysis + composites."""
    client = _get_client()
    if not client:
        return ""

    region_text = _build_region_text(regions)
    composite_text = _build_composite_text(composites)

    # Build verdict context
    verdict = ""
    if detailed:
        w = detailed.get("winner", "")
        winner_name = f"Image {w}" if w in ("A", "B") else "Neither"
        verdict = f"""
VERDICT (already decided, do not contradict):
- Winner: {winner_name}
- Why: {detailed.get('winner_reason', '')}
- Emotional: {detailed.get('emotional_impact', '')}
- Attention: {detailed.get('visual_attention', '')}
- Memory: {detailed.get('memory_retention', '')}"""

    context = f"""You are a confident neuromarketing advisor. A designer is comparing two images using brain activation prediction.

{KNOWLEDGE_BASE}

---

COMPOSITE BRAIN SIGNALS:
{composite_text}

TOP BRAIN REGION DIFFERENCES:
{region_text}

{verdict}

RULES:
- The verdict above is ground truth. NEVER contradict it.
- If asked which is better, state the winner first, then explain why.
- Be specific ("Image A captures attention 34% more because of stronger parietal activation").
- Give actionable advice ("add a human face to increase trust signals by ~20%").
- Keep responses to 2-4 sentences unless asked for more.
- Sound confident. You are an expert."""

    # Build conversation
    messages = context
    if history:
        for msg in history[-6:]:
            role = "Designer" if msg.get("role") == "user" else "Advisor"
            messages += f"\n\n{role}: {msg['content']}"
    messages += f"\n\nDesigner: {user_message}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini chat error: {e}")
        return ""
