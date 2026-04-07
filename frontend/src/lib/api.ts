import { ComparisonResult, PresetComparison, ChatMessage } from "./types"

const API_TIMEOUT = 180000 // 180s — TRIBE v2 inference + Gemini analysis

export const PRESETS: PresetComparison[] = [
  { id: "apple-vs-cluttered", label: "Apple vs Cluttered", file: "apple-vs-cluttered.json" },
  { id: "face-vs-noface", label: "Face vs No Face", file: "face-vs-noface.json" },
  { id: "text-vs-infographic", label: "Text vs Visual", file: "text-heavy-vs-infographic.json" },
]

export async function loadPreset(presetId: string): Promise<ComparisonResult> {
  const preset = PRESETS.find((p) => p.id === presetId)
  if (!preset) throw new Error(`Unknown preset: ${presetId}`)

  const res = await fetch(`/data/comparisons/${preset.file}`)
  if (!res.ok) throw new Error(`Failed to load preset: ${res.status}`)
  return res.json()
}

export async function compareImages(
  imageA: File,
  imageB: File
): Promise<ComparisonResult> {
  const formData = new FormData()
  formData.append("imageA", imageA)
  formData.append("imageB", imageB)

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT)

  try {
    const res = await fetch(
      process.env.NEXT_PUBLIC_API_URL + "/compare",
      { method: "POST", body: formData, signal: controller.signal }
    )
    if (!res.ok) throw new Error(`API error: ${res.status}`)
    return res.json()
  } finally {
    clearTimeout(timeout)
  }
}

/**
 * Streaming compare: calls /compare-stream SSE endpoint.
 * onBrain fires as soon as heatmap data is ready (before Gemini).
 * onAnalysis fires when Gemini verdict arrives.
 */
export async function compareImagesStream(
  imageA: File,
  imageB: File,
  onBrain: (partial: ComparisonResult) => void,
  onAnalysis: (full: ComparisonResult) => void,
): Promise<void> {
  const formData = new FormData()
  formData.append("imageA", imageA)
  formData.append("imageB", imageB)

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT)

  try {
    const res = await fetch(
      process.env.NEXT_PUBLIC_API_URL + "/compare-stream",
      { method: "POST", body: formData, signal: controller.signal }
    )
    if (!res.ok) throw new Error(`API error: ${res.status}`)

    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ""
    let brainData: Partial<ComparisonResult> = {}

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // Parse SSE events from buffer
      const parts = buffer.split("\n\n")
      buffer = parts.pop() || "" // keep incomplete chunk

      for (const part of parts) {
        const eventMatch = part.match(/^event:\s*(.+)$/m)
        const dataMatch = part.match(/^data:\s*(.+)$/m)
        if (!eventMatch || !dataMatch) continue

        const eventType = eventMatch[1]
        const data = JSON.parse(dataMatch[1])

        if (eventType === "brain") {
          brainData = {
            ...data,
            summary: "",
            detailed: undefined,
          }
          onBrain(brainData as ComparisonResult)
        } else if (eventType === "analysis") {
          const full: ComparisonResult = {
            ...(brainData as ComparisonResult),
            summary: data.summary,
            detailed: data.detailed,
          }
          onAnalysis(full)
        }
      }
    }
  } finally {
    clearTimeout(timeout)
  }
}

export async function chatWithAdvisor(
  message: string,
  regions: ComparisonResult["regions"],
  summary: string,
  history: ChatMessage[],
  detailed?: ComparisonResult["detailed"],
  composites?: ComparisonResult["composites"]
): Promise<string> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 90000)

  try {
    const res = await fetch(
      process.env.NEXT_PUBLIC_API_URL + "/chat",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, regions, summary, history, detailed, composites }),
        signal: controller.signal,
      }
    )

    if (!res.ok) throw new Error(`Chat error: ${res.status}`)
    const data = await res.json()
    return data.response
  } finally {
    clearTimeout(timeout)
  }
}
