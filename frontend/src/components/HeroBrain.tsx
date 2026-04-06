"use client"

import { useRef, useMemo, Component, type ReactNode } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls, Environment } from "@react-three/drei"
import * as THREE from "three"
import { MeshData } from "@/lib/types"

class CanvasErrorBoundary extends Component<
  { children: ReactNode },
  { error: string | null }
> {
  state = { error: null as string | null }
  static getDerivedStateFromError(err: Error) {
    return { error: err.message }
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ color: "#ff6b6b", fontSize: "12px", fontFamily: "var(--font-mono)", padding: "20px" }}>
          3D render error: {this.state.error}
        </div>
      )
    }
    return this.props.children
  }
}

// Fast green dash jumping through random brain regions like a neural signal
function SynapsingBrain({ meshData }: { meshData: MeshData }) {
  const meshRef = useRef<THREE.Mesh>(null)

  const regionNames = useMemo(() => Object.keys(meshData.regionMap), [meshData.regionMap])

  // Precompute a shuffled order of regions, and region centroids for trail effect
  const regionOrder = useRef<string[]>([])
  const regionIndex = useRef(0)
  const regionStartTime = useRef(0)

  // Shuffle regions into a random path
  const shuffleRegions = () => {
    const shuffled = [...regionNames]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }
    regionOrder.current = shuffled
    regionIndex.current = 0
  }

  // Track last few regions for fading trail
  const trail = useRef<{ region: string; startTime: number }[]>([])

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    const verts = new Float32Array(meshData.vertices.length * 3)
    for (let i = 0; i < meshData.vertices.length; i++) {
      verts[i * 3] = meshData.vertices[i][0]
      verts[i * 3 + 1] = meshData.vertices[i][1]
      verts[i * 3 + 2] = meshData.vertices[i][2]
    }
    const idx = new Uint32Array(meshData.faces.length * 3)
    for (let i = 0; i < meshData.faces.length; i++) {
      idx[i * 3] = meshData.faces[i][0]
      idx[i * 3 + 1] = meshData.faces[i][1]
      idx[i * 3 + 2] = meshData.faces[i][2]
    }
    geo.setAttribute("position", new THREE.BufferAttribute(verts, 3))
    geo.setIndex(new THREE.BufferAttribute(idx, 1))
    geo.computeVertexNormals()

    const colors = new Float32Array(meshData.vertices.length * 3)
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3))
    return geo
  }, [meshData])

  useFrame((state) => {
    const elapsed = state.clock.elapsedTime
    const colorAttr = geometry.getAttribute("color") as THREE.BufferAttribute
    const colors = colorAttr.array as Float32Array

    const hopDuration = 0.18 // how long each region stays lit
    const trailDuration = 1.8 // long trail = more regions glowing at once

    // Initialize or reshuffle when we've gone through all regions
    if (regionOrder.current.length === 0 || regionIndex.current >= regionOrder.current.length) {
      shuffleRegions()
      regionStartTime.current = elapsed
    }

    // Time to hop to next region?
    const timeSinceHop = elapsed - regionStartTime.current
    if (timeSinceHop >= hopDuration) {
      // Push current region to trail
      trail.current.push({
        region: regionOrder.current[regionIndex.current],
        startTime: elapsed,
      })
      // Advance
      regionIndex.current++
      regionStartTime.current = elapsed

      // If we finished all regions, reshuffle
      if (regionIndex.current >= regionOrder.current.length) {
        shuffleRegions()
        regionStartTime.current = elapsed
      }
    }

    // Clean old trail entries
    trail.current = trail.current.filter(t => elapsed - t.startTime < trailDuration)

    // Reset all to silver base
    for (let i = 0; i < meshData.vertices.length; i++) {
      colors[i * 3] = 0.54
      colors[i * 3 + 1] = 0.54
      colors[i * 3 + 2] = 0.59
    }

    // Draw trail (fading green)
    for (const t of trail.current) {
      const age = elapsed - t.startTime
      const fade = 1 - age / trailDuration
      const intensity = fade * fade * 0.9
      const indices = meshData.regionMap[t.region]
      if (!indices) continue
      for (const idx of indices) {
        colors[idx * 3] = 0.54 * (1 - intensity)
        colors[idx * 3 + 1] = 0.54 * (1 - intensity) + 0.898 * intensity
        colors[idx * 3 + 2] = 0.59 * (1 - intensity) + 0.627 * intensity
      }
    }

    // Draw current active region (bright green)
    const currentRegion = regionOrder.current[regionIndex.current]
    if (currentRegion) {
      const indices = meshData.regionMap[currentRegion]
      if (indices) {
        const flash = 1.0
        for (const idx of indices) {
          colors[idx * 3] = 0.54 * (1 - flash)
          colors[idx * 3 + 1] = 0.54 * (1 - flash) + 0.898 * flash
          colors[idx * 3 + 2] = 0.59 * (1 - flash) + 0.627 * flash
        }
      }
    }

    colorAttr.needsUpdate = true
  })

  return (
    <group rotation={[-Math.PI / 2, 0, Math.PI / 2]}>
      <mesh ref={meshRef} geometry={geometry}>
        <meshStandardMaterial
          vertexColors
          metalness={0.95}
          roughness={0.08}
          envMapIntensity={0.6}
        />
      </mesh>
    </group>
  )
}

function HeroParticles() {
  const ref = useRef<THREE.Points>(null)
  const particles = useMemo(() => {
    const count = 60
    const positions = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const r = 80 + Math.random() * 50
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = r * Math.cos(phi)
    }
    return positions
  }, [])

  useFrame((state) => {
    if (!ref.current) return
    ref.current.rotation.y = state.clock.elapsedTime * 0.015
    ref.current.rotation.x = state.clock.elapsedTime * 0.008
  })

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[particles, 3]} />
      </bufferGeometry>
      <pointsMaterial size={1.2} color="#8a8a9a" transparent opacity={0.12} sizeAttenuation />
    </points>
  )
}

interface HeroBrainProps {
  meshData: MeshData | null
}

export default function HeroBrain({ meshData }: HeroBrainProps) {
  if (!meshData) {
    return (
      <div
        className="flex items-center justify-center"
        style={{ width: "100%", height: "100%" }}
      >
        <span style={{ color: "#8a8a9a", fontSize: "14px" }}>
          Loading brain model...
        </span>
      </div>
    )
  }

  return (
    <CanvasErrorBoundary>
      <Canvas
        camera={{ position: [0, 0, 220], fov: 50 }}
        style={{ background: "transparent", width: "100%", height: "100%" }}
        aria-label="Interactive 3D brain with synapse pulse animation"
      >
        <ambientLight intensity={0.3} />
        <directionalLight position={[5, 5, 5]} intensity={1.2} color="#ffffff" />
        <directionalLight position={[-5, 3, -2]} intensity={0.6} color="#00e5a0" />
        <directionalLight position={[0, -3, 5]} intensity={0.3} color="#00b4d8" />
        <Environment preset="night" />
        <SynapsingBrain meshData={meshData} />
        <HeroParticles />
        <OrbitControls
          autoRotate
          autoRotateSpeed={0.4}
          enableZoom={false}
          enablePan={false}
        />
      </Canvas>
    </CanvasErrorBoundary>
  )
}
