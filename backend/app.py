"""
NeuroDesign backend — FastAPI on Modal with T4 GPU.
POST /compare: accepts two images, returns ComparisonResult JSON.
"""

import modal

# Modal image with all deps + local source files baked in
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "libglib2.0-0", "libsm6", "libxext6", "libxrender-dev")
    .pip_install(
        "fastapi[standard]",
        "python-multipart",
        "pillow",
        "numpy",
        "opencv-python-headless",
        "nilearn",
        "nibabel",
        "google-genai",
    )
    .run_commands(
        "pip install git+https://github.com/facebookresearch/tribev2.git"
    )
    # Bake backend source files into image at /app
    .add_local_file("inference.py", "/app/inference.py")
    .add_local_file("regions.py", "/app/regions.py")
    .add_local_file("composites.py", "/app/composites.py")
    .add_local_file("neuro_knowledge.py", "/app/neuro_knowledge.py")
    .add_local_file("gemini.py", "/app/gemini.py")
    # Bake mesh.json (needed for region map)
    .add_local_file("../frontend/public/data/mesh.json", "/data/mesh.json")
)

app = modal.App("neurodesign", image=image)


@app.function(
    gpu="T4",
    min_containers=1,
    timeout=300,
    secrets=[modal.Secret.from_name("neurodesign-secrets")],
)
@modal.asgi_app()
def fastapi_app():
    import io
    import sys
    import json
    import asyncio
    import numpy as np
    from concurrent.futures import ThreadPoolExecutor
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
    from PIL import Image

    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

    from inference import predict, normalize_joint
    from regions import load_region_map, aggregate_regions
    from composites import compute_composites
    from gemini import explain as gemini_explain, chat as gemini_chat

    api = FastAPI()

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

    try:
        from tribev2 import TribeModel
        model = TribeModel.from_pretrained("facebook/tribev2")
        print("TRIBE v2 loaded")
    except Exception as e:
        print(f"TRIBE v2 load error: {e}")
        model = None

    try:
        region_map = load_region_map("/data/mesh.json")
        print(f"Region map loaded: {len(region_map)} regions")
    except Exception as e:
        print(f"Region map load error: {e}")
        region_map = {}

    @api.post("/compare")
    async def compare(
        imageA: UploadFile = File(...),
        imageB: UploadFile = File(...),
    ):
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Read raw bytes, then open as PIL
        try:
            bytes_a = await imageA.read()
            bytes_b = await imageB.read()
            img_a = Image.open(io.BytesIO(bytes_a)).convert("RGB")
            img_b = Image.open(io.BytesIO(bytes_b)).convert("RGB")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image files")

        # TRIBE v2 inference — run both in parallel via threads
        from concurrent.futures import ThreadPoolExecutor, as_completed
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                fut_a = pool.submit(predict, img_a, model)
                fut_b = pool.submit(predict, img_b, model)
                raw_a = fut_a.result()
                raw_b = fut_b.result()
        except Exception as e:
            print(f"Inference error: {e}")
            raise HTTPException(status_code=500, detail="Inference failed")

        # Normalize and aggregate ALL regions
        norm_a, norm_b = normalize_joint(raw_a, raw_b)
        activations = np.stack([norm_a, norm_b], axis=0)
        all_regions = aggregate_regions(activations, region_map)

        # Compute composite brain signals from full region list
        composites = compute_composites(all_regions)

        # Single Gemini call with images + composites + knowledge base
        loop = asyncio.get_event_loop()
        detailed = await loop.run_in_executor(
            None, gemini_explain, all_regions, composites, img_a, img_b
        )

        # Filter to top 20 regions for the response payload
        top_regions = all_regions[:20]

        return {
            "imageA": {"url": "", "name": imageA.filename or "Image A"},
            "imageB": {"url": "", "name": imageB.filename or "Image B"},
            "activations": {
                "imageA": norm_a.tolist(),
                "imageB": norm_b.tolist(),
            },
            "regions": top_regions,
            "composites": composites,
            "summary": detailed.get("winner_reason", ""),
            "detailed": detailed,
        }

    @api.post("/compare-stream")
    async def compare_stream(
        imageA: UploadFile = File(...),
        imageB: UploadFile = File(...),
    ):
        """
        SSE streaming compare: sends brain data first, then Gemini analysis.
        Event 1: "brain" — activations, regions, composites (renders heatmaps)
        Event 2: "analysis" — Gemini verdict + detailed breakdown
        """
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        try:
            bytes_a = await imageA.read()
            bytes_b = await imageB.read()
            img_a = Image.open(io.BytesIO(bytes_a)).convert("RGB")
            img_b = Image.open(io.BytesIO(bytes_b)).convert("RGB")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image files")

        name_a = imageA.filename or "Image A"
        name_b = imageB.filename or "Image B"

        async def event_stream():
            # Phase 1: parallel TRIBE v2 inference
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=2) as pool:
                fut_a = pool.submit(predict, img_a, model)
                fut_b = pool.submit(predict, img_b, model)
                raw_a = await loop.run_in_executor(None, fut_a.result)
                raw_b = await loop.run_in_executor(None, fut_b.result)

            norm_a, norm_b = normalize_joint(raw_a, raw_b)
            activations_arr = np.stack([norm_a, norm_b], axis=0)
            all_regions = aggregate_regions(activations_arr, region_map)
            composites = compute_composites(all_regions)
            top_regions = all_regions[:20]

            # Send brain data immediately
            brain_payload = {
                "imageA": {"url": "", "name": name_a},
                "imageB": {"url": "", "name": name_b},
                "activations": {
                    "imageA": norm_a.tolist(),
                    "imageB": norm_b.tolist(),
                },
                "regions": top_regions,
                "composites": composites,
            }
            yield f"event: brain\ndata: {json.dumps(brain_payload)}\n\n"

            # Phase 2: Gemini analysis (runs while user sees heatmaps)
            detailed = await loop.run_in_executor(
                None, gemini_explain, all_regions, composites, img_a, img_b
            )
            analysis_payload = {
                "summary": detailed.get("winner_reason", ""),
                "detailed": detailed,
            }
            yield f"event: analysis\ndata: {json.dumps(analysis_payload)}\n\n"

            yield f"event: done\ndata: {{}}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @api.post("/chat")
    async def chat_endpoint(body: dict):
        regions = body.get("regions", [])
        composites = body.get("composites", [])
        summary = body.get("summary", "")
        message = body.get("message", "")
        history = body.get("history", [])
        detailed = body.get("detailed", {})

        if not message:
            raise HTTPException(status_code=400, detail="Message required")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, gemini_chat, regions, composites, summary, message, history, detailed
        )
        if not response:
            raise HTTPException(status_code=503, detail="Chat unavailable")

        return {"response": response}

    @api.get("/health")
    async def health():
        return {"status": "ok", "model_loaded": model is not None}

    return api
