"use client"

import { PRESETS } from "@/lib/api"

interface PresetTabsProps {
  activePreset: string | null
  onSelect: (presetId: string) => void
  onTryOwn: () => void
}

export default function PresetTabs({ activePreset, onSelect, onTryOwn }: PresetTabsProps) {
  const isTryOwn = activePreset === "__custom__"

  return (
    <div
      role="tablist"
      className="flex gap-1 overflow-x-auto"
      style={{
        scrollbarWidth: "none",
        msOverflowStyle: "none",
      }}
    >
      {PRESETS.map((preset) => {
        const isActive = activePreset === preset.id
        return (
          <button
            key={preset.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onSelect(preset.id)}
            className="whitespace-nowrap transition-colors duration-200 px-3 py-2"
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "12px",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: isActive ? "#e8e6e3" : "#8a8a9a",
              background: "transparent",
              border: "none",
              borderBottom: isActive ? "2px solid #00e5a0" : "2px solid transparent",
              cursor: "pointer",
            }}
          >
            {preset.label}
          </button>
        )
      })}
      <button
        role="tab"
        aria-selected={isTryOwn}
        onClick={onTryOwn}
        className="whitespace-nowrap transition-colors duration-200 px-3 py-2"
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "12px",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: isTryOwn ? "#0a0a0f" : "#00e5a0",
          background: isTryOwn ? "#00e5a0" : "transparent",
          border: isTryOwn ? "none" : "1px solid #00e5a044",
          borderBottom: isTryOwn ? "2px solid #00e5a0" : "2px solid transparent",
          borderRadius: "4px 4px 0 0",
          cursor: "pointer",
          marginLeft: "8px",
        }}
      >
        Try Your Own
      </button>
    </div>
  )
}
