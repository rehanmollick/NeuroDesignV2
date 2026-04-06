"use client"

import { useRef } from "react"
import { motion, useInView } from "framer-motion"
import { ComparisonResult } from "@/lib/types"

interface AnalysisCardsProps {
  comparison: ComparisonResult
}

// Animated SVG icons for each insight type
function HeartIcon({ color }: { color: string }) {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
      <path
        d="M20 35S4 26 4 15.5C4 10 8 6 13 6c3.5 0 6 2 7 4 1-2 3.5-4 7-4 5 0 9 4 9 9.5C36 26 20 35 20 35z"
        stroke={color}
        strokeWidth="1.5"
        fill="none"
        opacity="0.8"
      >
        <animate attributeName="stroke-opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite" />
      </path>
      <circle cx="20" cy="18" r="3" fill={color} opacity="0.15">
        <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.15;0.3;0.15" dur="2s" repeatCount="indefinite" />
      </circle>
    </svg>
  )
}

function EyeIcon({ color }: { color: string }) {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
      <path
        d="M4 20s6-10 16-10 16 10 16 10-6 10-16 10S4 20 4 20z"
        stroke={color}
        strokeWidth="1.5"
        fill="none"
        opacity="0.8"
      />
      <circle cx="20" cy="20" r="5" stroke={color} strokeWidth="1.5" fill="none" opacity="0.8" />
      <circle cx="20" cy="20" r="2" fill={color} opacity="0.6">
        <animate attributeName="r" values="2;3;2" dur="3s" repeatCount="indefinite" />
      </circle>
      {/* Scanning line */}
      <line x1="10" y1="20" x2="30" y2="20" stroke={color} strokeWidth="0.5" opacity="0.3">
        <animate attributeName="y1" values="14;26;14" dur="2.5s" repeatCount="indefinite" />
        <animate attributeName="y2" values="14;26;14" dur="2.5s" repeatCount="indefinite" />
      </line>
    </svg>
  )
}

function BrainIcon({ color }: { color: string }) {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
      <path
        d="M20 6c-4 0-7 2-8.5 5C9 11 7 13 7 16c0 2 1 3.5 2.5 4.5C8.5 22 8 24 8 26c0 3 2 5.5 5 6.5 1.5 2.5 4 3.5 7 3.5s5.5-1 7-3.5c3-1 5-3.5 5-6.5 0-2-.5-4-1.5-5.5C32 19.5 33 18 33 16c0-3-2-5-4.5-5C27 8 24 6 20 6z"
        stroke={color}
        strokeWidth="1.5"
        fill="none"
        opacity="0.8"
      />
      <line x1="20" y1="11" x2="20" y2="33" stroke={color} strokeWidth="0.8" opacity="0.3" />
      {/* Neural pulse */}
      <circle cx="20" cy="18" r="2" fill={color} opacity="0.2">
        <animate attributeName="cy" values="15;25;15" dur="3s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.1;0.4;0.1" dur="3s" repeatCount="indefinite" />
      </circle>
    </svg>
  )
}

interface InsightCardProps {
  title: string
  subtitle: string
  content: string
  accentColor: string
  align: "left" | "right"
  icon: React.ReactNode
  delay: number
}

function InsightCard({ title, subtitle, content, accentColor, align, icon, delay }: InsightCardProps) {
  if (!content) return null
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-40px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: align === "left" ? -30 : 30 }}
      animate={isInView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, ease: "easeOut", delay }}
      style={{
        width: "min(100%, 720px)",
        marginLeft: align === "right" ? "auto" : 0,
        marginRight: align === "left" ? "auto" : 0,
        display: "flex",
        alignItems: "stretch",
        gap: "0px",
        flexDirection: align === "right" ? "row-reverse" : "row",
      }}
    >
      {/* Icon column */}
      <div style={{
        width: "80px",
        minHeight: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}>
        <div style={{
          width: "64px",
          height: "64px",
          borderRadius: "50%",
          background: `${accentColor}10`,
          border: `1px solid ${accentColor}25`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          {icon}
        </div>
      </div>

      {/* Card */}
      <div style={{
        flex: 1,
        background: "#12121a",
        border: "1px solid #1e1e2e",
        borderLeft: align === "left" ? `3px solid ${accentColor}` : "1px solid #1e1e2e",
        borderRight: align === "right" ? `3px solid ${accentColor}` : "1px solid #1e1e2e",
        borderRadius: "4px",
        padding: "32px",
        position: "relative",
      }}>
        <div style={{
          fontFamily: "var(--font-mono)",
          fontSize: "11px",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "#8a8a9a",
          marginBottom: "6px",
        }}>
          {subtitle}
        </div>
        <div style={{
          fontFamily: "var(--font-heading)",
          fontSize: "20px",
          fontWeight: 600,
          color: accentColor,
          letterSpacing: "-0.02em",
          marginBottom: "16px",
        }}>
          {title}
        </div>
        <div style={{
          fontFamily: "var(--font-sans)",
          fontSize: "16px",
          color: "#e8e6e3",
          lineHeight: 1.7,
        }}>
          {content}
        </div>
      </div>
    </motion.div>
  )
}

// Signal colors for the composite score card
const SIGNAL_COLORS: Record<string, string> = {
  reward: "#00e5a0",
  cognitive_load: "#ff6b6b",
  visual_fluency: "#00b4d8",
  social_trust: "#f5a623",
  memory: "#c084fc",
  attention: "#38bdf8",
}

function NeuralScoreCard({ comparison }: { comparison: ComparisonResult }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-40px" })

  const composites = comparison.composites || []
  if (composites.length === 0) return null

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, ease: "easeOut", delay: 0.2 }}
      style={{
        background: "#12121a",
        border: "1px solid #1e1e2e",
        borderRadius: "4px",
        padding: "36px",
        maxWidth: "800px",
        margin: "0 auto",
      }}
    >
      <div style={{
        fontFamily: "var(--font-heading)",
        fontSize: "20px",
        fontWeight: 600,
        color: "#e8e6e3",
        letterSpacing: "-0.02em",
        marginBottom: "8px",
        textAlign: "center",
      }}>
        Composite Brain Signals
      </div>
      <div style={{
        fontFamily: "var(--font-sans)",
        fontSize: "13px",
        color: "#8a8a9a",
        textAlign: "center",
        marginBottom: "32px",
      }}>
        6 high-level brain patterns derived from region groups
      </div>

      {/* Legend */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        gap: "32px",
        marginBottom: "24px",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: 12, height: 12, borderRadius: 3, background: "#00e5a0" }} />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "#8a8a9a" }}>
            {comparison.imageA.name}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: 12, height: 12, borderRadius: 3, background: "#00b4d8" }} />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "#8a8a9a" }}>
            {comparison.imageB.name}
          </span>
        </div>
      </div>

      {/* Composite signal bars */}
      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {composites.map((c) => {
          const maxScore = Math.max(c.value_a, c.value_b, 0.01)
          const pctA = (c.value_a / maxScore) * 100
          const pctB = (c.value_b / maxScore) * 100
          const mag = Math.abs(c.delta) * 100

          return (
            <div key={c.signal}>
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "4px",
              }}>
                <span style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "14px",
                  color: "#e8e6e3",
                }}>
                  {c.label}
                </span>
                <span style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "12px",
                  color: mag < 2 ? "#8a8a9a" : c.delta > 0 ? "#00b4d8" : "#00e5a0",
                }}>
                  {mag < 2 ? "~" : c.delta > 0 ? "B" : "A"} {mag < 2 ? "even" : `+${mag.toFixed(0)}%`}
                </span>
              </div>
              {/* Interpretation */}
              <div style={{
                fontFamily: "var(--font-sans)",
                fontSize: "11px",
                color: "#8a8a9a",
                marginBottom: "8px",
                lineHeight: 1.4,
              }}>
                {c.interpretation}
              </div>
              {/* A bar */}
              <div style={{ display: "flex", gap: "4px", marginBottom: "4px" }}>
                <div style={{
                  height: "8px",
                  width: isInView ? `${pctA}%` : "0%",
                  background: "linear-gradient(90deg, #00e5a0, #00e5a088)",
                  borderRadius: "4px",
                  transition: "width 800ms ease-out",
                  boxShadow: "0 0 6px rgba(0,229,160,0.2)",
                }} />
              </div>
              {/* B bar */}
              <div style={{ display: "flex", gap: "4px" }}>
                <div style={{
                  height: "8px",
                  width: isInView ? `${pctB}%` : "0%",
                  background: "linear-gradient(90deg, #00b4d8, #00b4d888)",
                  borderRadius: "4px",
                  transition: "width 800ms ease-out 100ms",
                  boxShadow: "0 0 6px rgba(0,180,216,0.2)",
                }} />
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

export default function AnalysisCards({ comparison }: AnalysisCardsProps) {
  const d = comparison.detailed

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      {/* Staggered insight cards with icons */}
      <InsightCard
        title="Emotional Impact"
        subtitle="How it makes people feel"
        content={d?.emotional_impact || ""}
        accentColor="#ff6b6b"
        align="left"
        icon={<HeartIcon color="#ff6b6b" />}
        delay={0}
      />
      <InsightCard
        title="Visual Attention"
        subtitle="Where the eye goes first"
        content={d?.visual_attention || ""}
        accentColor="#00b4d8"
        align="right"
        icon={<EyeIcon color="#00b4d8" />}
        delay={0.1}
      />
      <InsightCard
        title="Memory Retention"
        subtitle="What sticks in the mind"
        content={d?.memory_retention || ""}
        accentColor="#f5a623"
        align="left"
        icon={<BrainIcon color="#f5a623" />}
        delay={0.2}
      />

      {/* Section connector */}
      <div className="section-connector" />

      {/* Neural Score Breakdown — replaces the old recommendations list */}
      <NeuralScoreCard comparison={comparison} />
    </div>
  )
}
