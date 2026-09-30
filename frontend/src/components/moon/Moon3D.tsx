"use client"

import React, { useRef, useState, useEffect } from "react"
import { useParallax } from "../../state/ParallaxContext"
import { LUNAR_REGIONS } from "../../data/regionsData"
import { LunarRegion } from "../../types/regions"

export const MOON_IMG =
  "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/1280px-FullMoon2010.jpg"

export interface Moon3DProps {
  size?: string
  zoom?: number
  rotate?: number
  className?: string
  interactive?: boolean
  showGlow?: boolean
  showMarkers?: boolean
  onSelectRegion?: (region: LunarRegion) => void
  autoRotate?: boolean
}

export function Moon3D({
  size = "400px",
  zoom = 1,
  rotate: controlledRotate,
  className = "",
  interactive = true,
  showGlow = true,
  showMarkers = true,
  onSelectRegion,
  autoRotate = true,
}: Moon3DProps) {
  const [internalRotate, setInternalRotate] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const dragStartXRef = useRef<number>(0)
  const baseRotateRef = useRef<number>(0)
  const { selectedRegion, setSelectedRegion, setCursorLabel } = useParallax()

  // Scroll-driven rotation (deg = y * 0.03) as demonstrated in user spec
  useEffect(() => {
    if (controlledRotate !== undefined) return

    const handleScroll = () => {
      const y = window.scrollY
      const deg = y * 0.03
      setInternalRotate(baseRotateRef.current + deg)
    }

    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [controlledRotate])

  // Optional gentle idle rotation when not dragging
  useEffect(() => {
    if (!autoRotate || controlledRotate !== undefined) return

    let animFrame: number
    let lastTime = performance.now()

    const loop = (now: number) => {
      const dt = (now - lastTime) / 1000
      lastTime = now

      if (!isDragging) {
        baseRotateRef.current += dt * 0.8 // slow drift
        setInternalRotate((r) => r + dt * 0.8)
      }

      animFrame = requestAnimationFrame(loop)
    }

    animFrame = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(animFrame)
  }, [autoRotate, isDragging, controlledRotate])

  // Mouse drag-to-rotate interaction
  const handlePointerDown = (e: React.PointerEvent) => {
    if (!interactive) return
    setIsDragging(true)
    dragStartXRef.current = e.clientX
    ;(e.target as HTMLElement).setPointerCapture?.(e.pointerId)
  }

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging) return
    const deltaX = e.clientX - dragStartXRef.current
    dragStartXRef.current = e.clientX
    const step = deltaX * 0.25
    baseRotateRef.current += step
    setInternalRotate((r) => r + step)
  }

  const handlePointerUp = (e: React.PointerEvent) => {
    if (isDragging) {
      setIsDragging(false)
      ;(e.target as HTMLElement).releasePointerCapture?.(e.pointerId)
    }
  }

  const currentRotate = controlledRotate !== undefined ? controlledRotate : internalRotate

  // Projected 2D positions for lunar regions based on rotation
  const regionsOnDisk = [
    { id: "faustini-rim", label: "Faustini Rim", baseAngle: 260, r: 0.84 },
    { id: "boguslawsky-e", label: "Boguslawsky-E", baseAngle: 215, r: 0.68 },
    { id: "shackleton-ridge", label: "Shackleton Ridge", baseAngle: 275, r: 0.90 },
    { id: "tycho-peak", label: "Tycho Peak", baseAngle: 140, r: 0.52 },
  ]

  return (
    <div
      className={`relative inline-flex items-center justify-center select-none ${className}`}
      style={{ width: size, height: size }}
    >
      {/* Glow behind the moon */}
      {showGlow && (
        <div
          style={{
            position: "absolute",
            inset: "-20%",
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(74,142,245,0.08) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
      )}

      {/* Moon sphere viewport */}
      <div
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        style={{
          position: "relative",
          width: size,
          height: size,
          borderRadius: "50%",
          overflow: "hidden",
          flexShrink: 0,
          cursor: interactive ? (isDragging ? "grabbing" : "grab") : "default",
          touchAction: "none",
        }}
      >
        {/* Moon photo — rotates to simulate slow spin */}
        <img
          src={MOON_IMG}
          alt="Moon"
          style={{
            position: "absolute",
            width: `${112 * zoom}%`,
            height: `${112 * zoom}%`,
            top: `${50 - 56 * zoom}%`,
            left: `${50 - 56 * zoom}%`,
            objectFit: "cover",
            filter: "brightness(0.78) contrast(1.12) saturate(0.58)",
            transform: `rotate(${currentRotate}deg)`,
            willChange: "transform",
            transition: isDragging ? "none" : "transform 0.1s linear",
            userSelect: "none",
            pointerEvents: "none",
          }}
        />

        {/* Selenographic Coordinate Markers on Lunar Disc */}
        {showMarkers &&
          regionsOnDisk.map((item) => {
            const angleRad = ((item.baseAngle + currentRotate) * Math.PI) / 180
            const xPercent = 50 + item.r * 45 * Math.cos(angleRad)
            const yPercent = 50 + item.r * 45 * Math.sin(angleRad)
            const isSelected = selectedRegion.id === item.id
            const matchedRegion = LUNAR_REGIONS.find((r) => r.id === item.id)

            return (
              <div
                key={item.id}
                onClick={(e) => {
                  e.stopPropagation()
                  if (matchedRegion) {
                    setSelectedRegion(matchedRegion)
                    if (onSelectRegion) onSelectRegion(matchedRegion)
                  }
                }}
                onPointerEnter={() => {
                  if (matchedRegion) {
                    setCursorLabel(`TARGET: ${matchedRegion.name} (${matchedRegion.latDisplay})`)
                  }
                }}
                onPointerLeave={() => setCursorLabel("")}
                style={{
                  position: "absolute",
                  left: `${xPercent}%`,
                  top: `${yPercent}%`,
                  transform: "translate(-50%, -50%)",
                  zIndex: 25,
                  cursor: "pointer",
                }}
                className="group"
              >
                <div className="relative flex items-center justify-center">
                  {/* Ping effect for active target */}
                  {isSelected && (
                    <span className="absolute h-4 w-4 rounded-full bg-cyan-400 opacity-75 animate-ping" />
                  )}
                  {/* Marker point */}
                  <span
                    className={`h-2.5 w-2.5 rounded-full border border-white/60 transition-all ${
                      isSelected
                        ? "bg-cyan-accent shadow-[0_0_8px_#64D2FF] scale-125"
                        : "bg-amber-400 hover:bg-cyan-accent hover:scale-125"
                    }`}
                  />
                </div>
              </div>
            )
          })}

        {/* Limb darkening — fades edges to black like a real sphere */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(circle at 50% 50%, transparent 40%, rgba(6,8,16,0.58) 72%, rgba(6,8,16,0.88) 100%)",
            pointerEvents: "none",
            zIndex: 10,
          }}
        />

        {/* Directional sunlight — top-left highlight */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at 36% 30%, rgba(255,248,230,0.12) 0%, transparent 60%)",
            pointerEvents: "none",
            zIndex: 11,
          }}
        />

        {/* Shadow hemisphere — darkens bottom-right */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at 72% 70%, rgba(6,8,16,0.46) 0%, transparent 62%)",
            pointerEvents: "none",
            zIndex: 12,
          }}
        />

        {/* Earthshine — subtle teal rim glow on dark limb */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse at 80% 58%, rgba(45,210,170,0.055) 0%, transparent 42%)",
            pointerEvents: "none",
            zIndex: 13,
          }}
        />
      </div>
    </div>
  )
}

export default Moon3D
