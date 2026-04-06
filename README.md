# NeuroDesign V2

**See how the brain responds to your designs.** Upload two images, get predicted fMRI brain activation maps, 3D heatmaps, and AI-powered analysis telling you which design wins and why.

## What It Does

NeuroDesign predicts how ~20,000 points on the human cortex respond to any image using Meta's TRIBE v2 model. It renders the results as interactive 3D brain heatmaps, compares two designs side by side, and uses Google's Gemini 2.5 Flash (multimodal) to explain the neuroscience differences.

- **3D Brain Heatmaps**: fsaverage5 cortical mesh with per-vertex activation coloring
- **Region Comparison**: Bar chart of top brain region differences with expandable design implications
- **Composite Signals**: Six high-level signals (attention, reward, memory, visual complexity, emotional, language) derived from 74 Destrieux atlas regions
- **Multimodal AI Analysis**: Gemini 2.5 Flash sees both images + brain data to generate verdicts
- **Interactive Chat**: Ask follow-up questions about any comparison
- **Preset Comparisons**: Three precomputed comparisons load instantly
- **Try Your Own**: Upload any two images for real-time neural comparison

## How It Works

```
Upload 2 images
    |
    v
Convert to 1-second silent video (TRIBE v2 expects video input)
    |
    v
Run Meta TRIBE v2 on T4 GPU (~60s per image)
    |
    v
Get 20,484 cortical vertex predictions per image
    |
    v
Aggregate into 74 named regions (Destrieux atlas)
  + compute 6 composite signals
    |
    v
Send regions + composites + both images to Gemini 2.5 Flash
    |
    v
Render 3D brain heatmaps + structured analysis + verdict
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| 3D Brain | React Three Fiber, Three.js, fsaverage5 mesh |
| Backend | FastAPI, Python 3.11 |
| GPU Inference | Modal (serverless T4 GPU) |
| Brain Model | Meta TRIBE v2 |
| AI Analysis | Google Gemini 2.5 Flash (multimodal) via google-genai SDK |
| Brain Atlas | nilearn Destrieux atlas (74 regions) |
| Deploy | Vercel (frontend), Modal (backend) |

## Architecture

```
Vercel (Next.js)
    |
    | POST /compare (2 images, multipart)
    v
Modal (T4 GPU, serverless)
    |
    +-- inference.py    TRIBE v2 prediction pipeline
    +-- regions.py      Destrieux atlas region aggregation + composite signals
    +-- gemini.py       Gemini 2.5 Flash multimodal analysis + chat
    +-- rag.py          Neuroscience knowledge base for grounded explanations
    |
    v
JSON response -> 3D brain heatmaps + verdict + region chart + chat
```

## Run Locally

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local  # set NEXT_PUBLIC_API_URL
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
# Set GEMINI_API_KEY in Modal secrets
modal deploy app.py
```

Requires a [Modal](https://modal.com) account and a [Google AI Studio](https://aistudio.google.com/apikey) API key.

## Project Structure

```
frontend/
  src/
    app/              Next.js app router
    components/       BrainViewer, HeroBrain, UploadZone, ChatAdvisor,
                      AnalysisSection, VerdictSection, TopDifferences, etc.
    lib/              types.ts, api.ts, colors.ts
  public/data/        mesh.json, preset comparison JSONs

backend/
  app.py              FastAPI endpoints + Modal GPU setup
  inference.py        Image -> video -> TRIBE v2 -> vertex activations
  regions.py          Destrieux atlas aggregation + composite signal computation
  gemini.py           Gemini 2.5 Flash multimodal (explain, verdict, chat)
  rag.py              Neuroscience RAG knowledge base
  tests/              test_gemini.py, test_composites.py, test_eval_presets.py
```

## The Science

TRIBE v2 (Meta, 2024) predicts the blood-oxygen-level-dependent (BOLD) fMRI response at each point on the cortical surface given visual input. The output maps to the fsaverage5 standard mesh.

Raw vertex predictions are aggregated into named regions using the Destrieux atlas (74 regions per hemisphere), then further combined into six composite signals:

| Signal | What it measures | Key regions |
|--------|-----------------|-------------|
| Attention | Where gaze is drawn | Intraparietal sulcus, superior parietal, frontal eye fields |
| Reward | Emotional value, desire | Orbitofrontal cortex, ventral striatum, anterior cingulate |
| Memory | Likelihood of being remembered | Parahippocampal, posterior cingulate, precuneus |
| Visual Complexity | How much visual processing is needed | V1, V2, cuneus, middle occipital |
| Emotional | Gut reaction, arousal | Insula, amygdala, anterior cingulate |
| Language | Text processing load | Angular gyrus, supramarginal, Broca's area |

More activation is not always better. A cluttered design overloads visual and attention regions without engaging reward. A clean, focused design activates fewer regions but hits the ones that matter: reward, focused attention, memory encoding.

## License

MIT
