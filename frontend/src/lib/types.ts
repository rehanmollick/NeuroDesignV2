export interface MeshData {
  vertices: number[][] // [20484][3] xyz positions
  faces: number[][] // [~40960][3] vertex index triples
  regionMap: Record<string, number[]> // "G_temporal_sup" -> [vertex indices]
}

export interface CompositeSignal {
  signal: string // reward, cognitive_load, visual_fluency, social_trust, memory, attention
  label: string // Human-friendly label
  value_a: number
  value_b: number
  delta: number // B - A
  interpretation: string
}

export interface ComparisonResult {
  imageA: { url: string; name: string }
  imageB: { url: string; name: string }
  activations: {
    imageA: number[] // 20484 values, jointly normalized [0, 1]
    imageB: number[] // 20484 values, jointly normalized [0, 1]
  }
  regions: Array<{
    name: string // Destrieux anatomical label
    displayName: string // Human-friendly name (lookup table)
    function: string // Cognitive function (static lookup table)
    activationA: number // Mean activation, [0, 1]
    activationB: number
    delta: number // B - A
    designImplication?: string // What this means for design decisions
    composite?: string // Which composite signal this belongs to
  }>
  composites?: CompositeSignal[]
  summary: string // Gemini explanation
  detailed?: {
    winner?: string
    winner_reason?: string
    emotional_impact?: string
    visual_attention?: string
    memory_retention?: string
    recommendations?: string[]
    _fallback?: boolean
  }
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export interface PresetComparison {
  id: string
  label: string
  file: string // path relative to /data/comparisons/
}

export type PageState =
  | "initial" // preset loaded
  | "uploading" // user has dragged images
  | "scanning" // comparing custom images
  | "results" // showing comparison
  | "error" // something went wrong
