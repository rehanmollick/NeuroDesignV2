# NeuroDesign V2

> See how the human brain actually responds to your designs. Upload two images, get predicted fMRI brain activation maps, 3D heatmaps, and multimodal AI analysis telling you which design wins and why.

**[Live Demo →]([https://frontend-gamma-ten-23.vercel.app](https://neurodesign-v2.vercel.app/))**

This is **V2** — a post-hackathon rewrite of NeuroDesign with a new model stack, composite neural signals, a neuroscience RAG knowledge base, and a real test suite. For the original hackathon build, see the V1 repo: https://github.com/rehanmollick/NeuroDesign

---

## Demo status: preset mode

The live demo currently runs in **preset-only mode**. Three hand-picked precomputed comparisons load instantly so anyone can experience the full interface, 3D brain visualization, composite signal breakdowns, AI verdict, and chat advisor.

**The "Try Your Own" custom upload tab does not work right now.** I took down the Modal GPU backend to stop it from billing — it was accidentally left with a warm container that ran 24/7 regardless of traffic, which got expensive fast. (V1 had the same bug; it's now fixed in both repos by defaulting to scale-to-zero.)

**Want to see how NeuroDesign analyzes your own website, app, or designs?** Reach out and I'll spin the backend back up and run a custom comparison for you. It only takes a few minutes on my end.

**Contact:** rehanmollick07@gmail.com

---

## What it does

NeuroDesign predicts how ~20,000 points on the human cortex respond to any image using Meta's TRIBE v2 model. It renders the results as interactive 3D brain heatmaps, compares two designs side by side, and uses Google's Gemini 2.5 Flash (multimodal) to explain the neuroscience differences with actual images in context.

- **3D brain heatmaps** — fsaverage5 cortical mesh with per-vertex activation coloring
- **Composite signals** — Six high-level neural signals (attention, reward, memory, visual complexity, emotional, language) derived from 74 Destrieux atlas regions
- **Top region differences** — Bar chart of the biggest regional deltas between the two designs, each with expandable design implications
- **Multimodal AI verdict** — Gemini 2.5 Flash sees both images + the brain data and generates a winner verdict with reasoning
- **Neuroscience RAG** — Region-level explanations are grounded in a curated neuroscience knowledge base instead of being hallucinated from scratch
- **Interactive chat advisor** — Ask follow-up questions about any comparison, with the winner verdict passed into context so answers stay consistent
- **Preset comparisons** — Three precomputed comparisons load instantly
- **Try your own** — Upload any two images for real-time neural comparison (currently disabled, see demo status above)

## What changed from V1

V2 is a ground-up rewrite, not a patch. Major changes from the hackathon build:

### Model stack
- **Gemini 2.5 Flash replaces Gemma 4** — V1 used Gemma 4 text-only and fed it region summaries. V2 uses Gemini 2.5 Flash multimodal, so the model actually *sees* both images alongside the brain data. Verdicts are dramatically more grounded.
- **Neuroscience RAG knowledge base** — V1 let Gemma explain brain regions from scratch. V2 grounds those explanations in a curated knowledge base (`backend/neuro_knowledge.py`), so region function descriptions are accurate and consistent.

### Signal aggregation
- **Six composite signals** — V1 showed per-region bar charts directly. V2 aggregates the 74 Destrieux regions into six high-level signals (attention, reward, memory, visual complexity, emotional, language) that are far more legible to non-neuroscientists.
- **Composite-signal winner logic** — V1's verdict sometimes fell back to "whichever brain lit up more wins." V2 picks winners based on the actual composite signal profile, so a cluttered-but-high-activation design can correctly lose to a clean one.

### Architecture
- **Streaming compare endpoint** — Results stream back to the frontend in stages instead of blocking until everything is ready.
- **Client-side image resize** — Uploads are resized in the browser before upload, cutting request size and GPU memory pressure.
- **Test suite** — `backend/tests/` has mock-based Gemini tests and a preset eval harness (`test_eval_presets.py`) that catches regressions when the pipeline changes.

### UX
- **V2 UI overhaul** — Glass cards, dedicated "Try Your Own" upload tab, Gemini 2.5 Flash branding, cleaner analysis section layout.
- **Top differences panel** — Surfaces the most interesting regional deltas upfront instead of making the user hunt for them.
- **Verdict section** — Opinionated, consistent winner call with reasoning, powered by composite signals rather than raw activation averages.

### Infrastructure
- **Scale-to-zero GPU** — Same Modal backend, but no longer keeps a warm container running 24/7. Pay per actual inference, not per idle hour. (This fix landed after the V1 cost incident.)

## How it works

```
Upload 2 images
    |
    v
Client-side resize, convert each to a 1s silent video (TRIBE v2 expects video input)
    |
    v
Run Meta TRIBE v2 on a T4 GPU (~60s per image)
    |
    v
Get 20,484 cortical vertex predictions per image
    |
    v
Aggregate into 74 named Destrieux regions
    + compute 6 composite signals (attention, reward, memory,
      visual complexity, emotional, language)
    |
    v
Send regions + composites + BOTH images to Gemini 2.5 Flash (multimodal)
    |
    v
Stream back verdict + 3D brain heatmaps + region chart + chat context
```

## Tech stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| 3D brain | React Three Fiber, Three.js, fsaverage5 mesh |
| Backend | FastAPI, Python 3.11 |
| GPU inference | Modal (T4 GPU, scale-to-zero) |
| Brain model | Meta TRIBE v2 |
| AI analysis | Google Gemini 2.5 Flash (multimodal) via google-genai SDK |
| Grounding | Custom neuroscience RAG knowledge base |
| Brain atlas | nilearn Destrieux atlas (74 regions) |
| Deploy | Vercel (frontend), Modal (backend, currently offline) |

## Architecture

```
Vercel (Next.js)
    |
    | POST /compare (2 images, multipart, streaming)
    v
Modal (T4 GPU, scale-to-zero) [currently offline]
    |
    +-- inference.py       TRIBE v2 prediction pipeline
    +-- regions.py         Destrieux atlas region aggregation
    +-- composites.py      Six composite signal computation
    +-- neuro_knowledge.py Neuroscience RAG knowledge base
    +-- gemini.py          Gemini 2.5 Flash multimodal (verdict + chat)
    |
    v
Streaming JSON -> 3D brain heatmaps + verdict + composite bars + chat
```

## Preset comparisons

V2 ships with three curated showcase pairs that work without the GPU backend:

1. **Apple homepage vs cluttered brand homepage**
2. **Photo with face vs same composition without face**
3. **Text-heavy slide vs visual infographic**

All three still work in the live demo in preset-only mode.

## Run locally

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL to your Modal URL
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
# Set GEMINI_API_KEY in your Modal secrets
modal deploy app.py
```

Requires a [Modal](https://modal.com) account and a [Google AI Studio](https://aistudio.google.com/apikey) API key. The Modal function is now configured to scale to zero when idle, so you only pay for actual inference time. **Do not set `min_containers=1`** unless you want a T4 running 24/7 on your dime.

### Tests

```bash
cd backend
pytest tests/
```

The test suite includes mocked Gemini integration tests and a preset eval harness that replays the precomputed comparisons through the pipeline to catch regressions.

## Project structure

```
frontend/
  src/
    app/              # Next.js app router
    components/       # BrainViewer, HeroBrain, UploadZone, ChatAdvisor,
                      # AnalysisSection, VerdictSection, TopDifferences, etc.
    lib/              # types.ts, api.ts, colors.ts
  public/data/        # mesh.json, preset comparison JSONs

backend/
  app.py              # FastAPI endpoints + Modal GPU setup (scale-to-zero)
  inference.py        # Image -> video -> TRIBE v2 -> vertex activations
  regions.py          # Destrieux atlas aggregation
  composites.py       # Six composite signal computation
  neuro_knowledge.py  # Neuroscience RAG knowledge base
  gemini.py           # Gemini 2.5 Flash multimodal (verdict + chat)
  tests/              # test_gemini.py, test_composites.py, test_eval_presets.py

scripts/
  precompute.py       # Generate new preset comparisons
  export_mesh.py      # fsaverage5 mesh -> mesh.json
  gemini_media.py     # Imagen 3 and Veo 2 CLI for demo assets
```

## The science

TRIBE v2 (Meta, 2024) predicts the blood-oxygen-level-dependent (BOLD) fMRI response at each point on the cortical surface given visual input. The output maps to the fsaverage5 standard mesh.

Raw vertex predictions are aggregated into named regions using the Destrieux atlas (74 regions per hemisphere), then further combined into six composite signals:

| Signal | What it measures | Key regions |
|--------|------------------|-------------|
| **Attention** | Where gaze is drawn | Intraparietal sulcus, superior parietal, frontal eye fields |
| **Reward** | Emotional value, desire | Orbitofrontal cortex, ventral striatum, anterior cingulate |
| **Memory** | Likelihood of being remembered | Parahippocampal, posterior cingulate, precuneus |
| **Visual complexity** | How much visual processing is needed | V1, V2, cuneus, middle occipital |
| **Emotional** | Gut reaction, arousal | Insula, amygdala, anterior cingulate |
| **Language** | Text processing load | Angular gyrus, supramarginal, Broca's area |

**More activation is not always better.** A cluttered design overloads visual and attention regions without engaging reward. A clean, focused design activates fewer regions but hits the ones that matter: reward, focused attention, memory encoding. V2's composite-signal winner logic interprets this correctly, which was one of the big reasons for the rewrite.

## Background

NeuroDesign started as a weekend hackathon project ([V1 repo](https://github.com/rehanmollick/NeuroDesign)) and won. V2 is the post-hackathon rewrite focused on making the neuroscience side actually rigorous (RAG-grounded explanations, composite signals, multimodal analysis) and making the product side credible enough to show real designers.

## License

MIT

## Contact

Rehan Mollick — rehanmollick07@gmail.com

If you want a brain scan of your own website or designs, just reach out. I'm happy to spin the backend up and run a custom comparison for you.
