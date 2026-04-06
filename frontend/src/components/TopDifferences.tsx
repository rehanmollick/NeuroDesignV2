"use client"

import { useRef, useState } from "react"
import { useInView } from "framer-motion"
import { ComparisonResult } from "@/lib/types"

interface TopDifferencesProps {
  regions: ComparisonResult["regions"]
}

export default function TopDifferences({ regions }: TopDifferencesProps) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-60px" })
  const [expanded, setExpanded] = useState<string | null>(null)

  const sorted = [...regions]
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 6)

  const maxVal = Math.max(...sorted.map((r) => Math.max(r.activationA, r.activationB)))

  return (
    <div ref={ref} style={{ width: "100%" }}>
      <div style={{
        fontFamily: "var(--font-heading)",
        fontSize: "20px",
        fontWeight: 600,
        color: "#e8e6e3",
        letterSpacing: "-0.02em",
        marginBottom: "28px",
      }}>
        Brain Region Comparison
      </div>

      {/* Vertical bar chart */}
      <div style={{
        background: "#12121a",
        border: "1px solid #1e1e2e",
        borderRadius: "4px",
        padding: "32px",
      }}>
        <div style={{
          display: "flex",
          gap: "12px",
          alignItems: "flex-end",
          height: "240px",
          padding: "0 8px",
          borderBottom: "1px solid #1e1e2e",
        }}>
          {sorted.map((region, i) => {
            const heightA = maxVal > 0 ? (region.activationA / maxVal) * 100 : 0
            const heightB = maxVal > 0 ? (region.activationB / maxVal) * 100 : 0

            return (
              <div
                key={region.name}
                style={{
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  height: "100%",
                  justifyContent: "flex-end",
                  gap: "4px",
                }}
              >
                {/* Value labels */}
                <div style={{
                  display: "flex",
                  gap: "4px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                }}>
                  <span style={{ color: "#00e5a0" }}>{(region.activationA * 100).toFixed(0)}</span>
                  <span style={{ color: "#00b4d8" }}>{(region.activationB * 100).toFixed(0)}</span>
                </div>
                {/* Bars */}
                <div style={{
                  display: "flex",
                  gap: "4px",
                  alignItems: "flex-end",
                  height: "calc(100% - 24px)",
                }}>
                  <div style={{
                    width: "24px",
                    height: isInView ? `${heightA}%` : "0%",
                    background: "linear-gradient(180deg, #00e5a0, #00e5a044)",
                    borderRadius: "3px 3px 0 0",
                    transition: `height 600ms ease-out ${i * 100}ms`,
                    minHeight: isInView ? "4px" : "0px",
                    boxShadow: "0 0 12px rgba(0,229,160,0.15)",
                  }} />
                  <div style={{
                    width: "24px",
                    height: isInView ? `${heightB}%` : "0%",
                    background: "linear-gradient(180deg, #00b4d8, #00b4d844)",
                    borderRadius: "3px 3px 0 0",
                    transition: `height 600ms ease-out ${i * 100 + 50}ms`,
                    minHeight: isInView ? "4px" : "0px",
                    boxShadow: "0 0 12px rgba(0,180,216,0.15)",
                  }} />
                </div>
              </div>
            )
          })}
        </div>

        {/* Use CSS grid so each sub-row is always aligned across all columns */}
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(${sorted.length}, 1fr)`,
          gap: "0 12px",
          marginTop: "12px",
        }}>
          {/* Row 1: Region names */}
          {sorted.map((region) => (
            <div
              key={`name-${region.name}`}
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "12px",
                color: "#e8e6e3",
                lineHeight: 1.3,
                textAlign: "center",
                paddingBottom: "4px",
              }}
            >
              {region.displayName}
            </div>
          ))}

          {/* Row 2: Delta percentages */}
          {sorted.map((region) => {
            const accentColor = region.delta > 0 ? "#00b4d8" : "#00e5a0"
            return (
              <div
                key={`delta-${region.name}`}
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "13px",
                  fontWeight: 500,
                  color: accentColor,
                  textAlign: "center",
                  paddingBottom: "8px",
                }}
              >
                {region.delta > 0 ? "+" : ""}{(region.delta * 100).toFixed(0)}%
              </div>
            )
          })}

          {/* Row 3: Dropdown pills */}
          {sorted.map((region) => {
            const isExpanded = expanded === region.name
            const accentColor = region.delta > 0 ? "#00b4d8" : "#00e5a0"
            const hasImplication = !!region.designImplication
            return (
              <div
                key={`pill-${region.name}`}
                style={{ textAlign: "center" }}
              >
                <div
                  onClick={hasImplication ? () => setExpanded(isExpanded ? null : region.name) : undefined}
                  style={{
                    fontFamily: "var(--font-sans)",
                    fontSize: "10px",
                    color: hasImplication ? accentColor : "#8a8a9a",
                    lineHeight: 1.3,
                    cursor: hasImplication ? "pointer" : "default",
                    transition: "all 200ms ease-out",
                    padding: "4px 6px",
                    borderRadius: "4px",
                    background: isExpanded ? `${accentColor}15` : hasImplication ? `${accentColor}08` : "transparent",
                    border: hasImplication ? `1px solid ${isExpanded ? accentColor + "40" : accentColor + "20"}` : "1px solid transparent",
                  }}
                >
                  {region.function}
                  {hasImplication && (
                    <span style={{ marginLeft: "4px", fontSize: "9px" }}>
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Expanded design implication panel */}
        {expanded && (() => {
          const region = sorted.find(r => r.name === expanded)
          if (!region?.designImplication) return null
          const accentColor = region.delta > 0 ? "#00b4d8" : "#00e5a0"

          return (
            <div style={{
              marginTop: "16px",
              padding: "20px 24px",
              background: "#0a0a0f",
              border: `1px solid ${accentColor}33`,
              borderTop: `2px solid ${accentColor}`,
              borderRadius: "0 0 4px 4px",
              transition: "all 200ms ease-out",
            }}>
              <div style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: accentColor,
                marginBottom: "8px",
              }}>
                What this means for your design
              </div>
              <div style={{
                fontFamily: "var(--font-sans)",
                fontSize: "14px",
                color: "#e8e6e3",
                lineHeight: 1.65,
              }}>
                {region.designImplication}
              </div>
            </div>
          )
        })()}

        {/* Legend */}
        <div style={{
          display: "flex",
          gap: "24px",
          marginTop: "20px",
          justifyContent: "center",
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontFamily: "var(--font-mono)",
            fontSize: "13px",
            color: "#8a8a9a",
          }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: "#00e5a0" }} />
            IMAGE A
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontFamily: "var(--font-mono)",
            fontSize: "13px",
            color: "#8a8a9a",
          }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: "#00b4d8" }} />
            IMAGE B
          </div>
        </div>
      </div>
    </div>
  )
}
