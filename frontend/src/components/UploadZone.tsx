"use client"

import { useCallback, useState, useRef } from "react"

interface UploadZoneProps {
  label: string
  file: File | null
  onFileSelect: (file: File | null) => void
  compact?: boolean
}

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"]
const MAX_SIZE = 10 * 1024 * 1024 // 10MB
const MIN_DIM = 200

export default function UploadZone({ label, file, onFileSelect, compact }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validateFile = useCallback((f: File): string | null => {
    if (!ACCEPTED_TYPES.includes(f.type)) {
      return "Must be JPEG, PNG, or WebP"
    }
    if (f.size > MAX_SIZE) {
      return "File must be under 10MB"
    }
    return null
  }, [])

  const handleFile = useCallback(
    (f: File) => {
      const err = validateFile(f)
      if (err) {
        setError(err)
        return
      }
      setError(null)

      // Check dimensions
      const img = new Image()
      const url = URL.createObjectURL(f)
      img.onload = () => {
        if (img.width < MIN_DIM || img.height < MIN_DIM) {
          setError(`Image must be at least ${MIN_DIM}x${MIN_DIM}px`)
          URL.revokeObjectURL(url)
          return
        }
        setPreview(url)
        onFileSelect(f)
      }
      img.onerror = () => {
        setError("Could not read image")
        URL.revokeObjectURL(url)
      }
      img.src = url
    },
    [validateFile, onFileSelect]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const f = e.dataTransfer.files[0]
      if (f) handleFile(f)
    },
    [handleFile]
  )

  const handleRemove = useCallback(() => {
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setError(null)
    onFileSelect(null)
  }, [preview, onFileSelect])

  if (file && preview) {
    return (
      <div className="relative">
        <div
          className="relative overflow-hidden"
          style={{
            border: "1px solid #1e1e2e",
            borderRadius: "4px",
            height: compact ? "52px" : "100px",
          }}
        >
          <img
            src={preview}
            alt={label}
            className="w-full h-full object-cover"
          />
          <button
            onClick={handleRemove}
            className="absolute top-1 right-1 w-6 h-6 flex items-center justify-center"
            style={{
              background: "rgba(10, 10, 15, 0.8)",
              color: "#e8e6e3",
              fontSize: "14px",
              border: "none",
              cursor: "pointer",
              borderRadius: "2px",
            }}
            aria-label={`Remove ${label}`}
          >
            x
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        aria-label={`Upload ${label}`}
        className="cursor-pointer"
        style={{
          border: `2px dashed ${isDragging ? "#00e5a0" : "#00e5a066"}`,
          borderRadius: "8px",
          background: isDragging ? "#0f1f18" : "#12121a",
          height: compact ? "60px" : "160px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "4px",
          transition: "all 200ms ease-out",
        }}
        onMouseEnter={(e) => {
          if (!isDragging) {
            e.currentTarget.style.borderColor = "#00e5a0"
            e.currentTarget.style.background = "#0f1f18"
          }
        }}
        onMouseLeave={(e) => {
          if (!isDragging) {
            e.currentTarget.style.borderColor = "#00e5a066"
            e.currentTarget.style.background = "#12121a"
          }
        }}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault()
            inputRef.current?.click()
          }
        }}
      >
        <svg
          width={compact ? "24" : "36"}
          height={compact ? "24" : "36"}
          viewBox="0 0 24 24"
          fill="none"
          stroke="#00e5a0"
          strokeWidth="1.5"
          strokeLinecap="round"
        >
          <path d="M12 16V4M12 4l-4 4M12 4l4 4" />
          <path d="M4 18h16" />
        </svg>
        <span
          style={{
            fontFamily: "var(--font-sans)",
            fontSize: compact ? "13px" : "15px",
            fontWeight: 500,
            color: "#e8e6e3",
          }}
        >
          Drop image or click to upload
        </span>
        {!compact && (
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "#8a8a9a",
              letterSpacing: "0.05em",
            }}
          >
            JPG, PNG, or WebP (max 10MB)
          </span>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0]
          if (f) handleFile(f)
        }}
      />

      {error && (
        <p
          style={{
            fontFamily: "var(--font-sans)",
            fontSize: "12px",
            color: "#ff6b6b",
            marginTop: "4px",
          }}
        >
          {error}
        </p>
      )}
    </div>
  )
}
