"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import gsap from "gsap"
import { Compass, BookOpen, Activity, X } from "lucide-react"
import { useParallax } from "../../state/ParallaxContext"

export interface NavItem {
  id: string
  number: string
  label: string
  href: string
  description: string
  category: string
}

export const PARALLAX_NAV_ITEMS: NavItem[] = [
  {
    id: "mission",
    number: "01",
    label: "MISSION",
    href: "/",
    description: "Adaptive multi-modal registration for heterogeneous Chandrayaan-2 lunar observations",
    category: "OVERVIEW",
  },
  {
    id: "explore",
    number: "02",
    label: "EXPLORE",
    href: "/explore",
    description: "Interactive 3D lunar globe with candidate crater pair formation & lighting context",
    category: "SELENOGRAPHY",
  },
  {
    id: "instruments",
    number: "03",
    label: "INSTRUMENTS",
    href: "/instruments",
    description: "OHRC (0.25m), TMC-2 (5.0m stereo), and IIRS hyperspectral challenge matrix",
    category: "PAYLOAD LAB",
  },
  {
    id: "correspondence",
    number: "04",
    label: "CORRESPONDENCE",
    href: "/correspondence",
    description: "Adaptive model router, ranked candidate bank, ANMS & sub-pixel local refinement",
    category: "CORE ENGINE",
  },
  {
    id: "analysis",
    number: "05",
    label: "ANALYSIS",
    href: "/analysis",
    description: "Trustworthy evaluation: RMSE, inlier ratio, ANMS spatial dispersion & uncertainty",
    category: "QUALITY GATES",
  },
  {
    id: "simulator",
    number: "06",
    label: "SIMULATOR",
    href: "/simulator",
    description: "Controlled difficulty sandbox: solar elevation, noise & model candidate shifts",
    category: "SANDBOX",
  },
  {
    id: "about",
    number: "07",
    label: "ABOUT",
    href: "/about",
    description: "Scientific motivation, literature citations, maturity matrix & ISRO provenance",
    category: "SCIENCE",
  },
]

export function SterlingGateKineticNavigation() {
  const [isOpen, setIsOpen] = useState(false)
  const [hoveredIndex, setHoveredIndex] = useState<number>(0)
  const navigate = useNavigate()
  const location = useLocation()
  const { 
    explainMode, 
    toggleExplainMode, 
    sourceInstrument, 
    targetInstrument, 
    sourceProduct,
    targetProduct,
    pairCharacterization,
    metrics,
    simulationParams,
    setCursorLabel
  } = useParallax()

  const overlayRef = useRef<HTMLDivElement>(null)
  const menuContentRef = useRef<HTMLDivElement>(null)
  const linksContainerRef = useRef<HTMLDivElement>(null)
  const visualPreviewRef = useRef<HTMLDivElement>(null)
  const timelineRef = useRef<gsap.core.Timeline | null>(null)

  // Determine active item from current route
  const activeIndex = PARALLAX_NAV_ITEMS.findIndex((item) =>
    item.href === "/" ? location.pathname === "/" : location.pathname.startsWith(item.href)
  )

  // Scroll lock when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "unset"
    }
    return () => {
      document.body.style.overflow = "unset"
    }
  }, [isOpen])

  // Synchronize initial hovered index with active route
  useEffect(() => {
    if (activeIndex !== -1) {
      setHoveredIndex(activeIndex)
    }
  }, [activeIndex, isOpen])

  // GSAP Kinetic Reveal Sequence
  useEffect(() => {
    const overlay = overlayRef.current
    const links = linksContainerRef.current?.querySelectorAll(".kinetic-nav-link")
    const visual = visualPreviewRef.current

    if (!overlay || !links) return

    if (isOpen) {
      overlay.style.display = "flex"

      // Kill previous animations
      if (timelineRef.current) timelineRef.current.kill()

      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
      })

      // 1. Unfold overlay background
      tl.fromTo(
        overlay,
        { opacity: 0, scale: 0.98 },
        { opacity: 1, scale: 1, duration: 0.35 }
      )

      // 2. Cascade links staggering
      tl.fromTo(
        links,
        { y: 20, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.3,
          stagger: 0.04,
        },
        "-=0.15"
      )

      // 3. Reveal visual preview panel
      if (visual) {
        tl.fromTo(
          visual,
          { opacity: 0, x: 20 },
          { opacity: 1, x: 0, duration: 0.3 },
          "-=0.2"
        )
      }

      timelineRef.current = tl
    } else {
      if (timelineRef.current) timelineRef.current.kill()

      const tl = gsap.timeline({
        defaults: { ease: "power3.in" },
        onComplete: () => {
          overlay.style.display = "none"
        },
      })

      tl.to(links, {
        y: -10,
        opacity: 0,
        duration: 0.15,
        stagger: 0.02,
      })

      if (visual) {
        tl.to(visual, { opacity: 0, duration: 0.15 }, "<")
      }

      tl.to(
        overlay,
        {
          opacity: 0,
          scale: 0.99,
          duration: 0.2,
        },
        "-=0.1"
      )

      timelineRef.current = tl
    }

    return () => {
      if (timelineRef.current) timelineRef.current.kill()
    }
  }, [isOpen])

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen])

  // Route navigation handler
  const handleNavigate = useCallback(
    (href: string) => {
      setIsOpen(false)
      navigate(href)
      window.scrollTo({ top: 0, left: 0, behavior: "instant" })
    },
    [navigate]
  )

  const activeHoverItem = PARALLAX_NAV_ITEMS[hoveredIndex] || PARALLAX_NAV_ITEMS[0]

  return (
    <>
      {/* ─── FIXED GLOBAL HUD HEADER BAR ─── */}
      <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 bg-[#111111] border-b border-[#262626] py-3 text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Brand Logo & Wordmark */}
          <div
            onClick={() => handleNavigate("/")}
            onMouseEnter={() => setCursorLabel("MISSION HOME")}
            onMouseLeave={() => setCursorLabel("")}
            className="flex items-center gap-3 cursor-pointer group select-none"
          >
            <div className="h-7 w-7 rounded-none border border-[#383838] flex items-center justify-center bg-[#161616]">
              <Compass className="h-3.5 w-3.5 text-[#E4E4E2]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-sans font-bold tracking-tight text-base sm:text-lg text-[#F7F7F5]">
                  PARALLAX
                </span>
                <span className="px-1.5 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#1A1A1A] border border-[#333333] text-[#A0A0A0] font-semibold">
                  CH-2
                </span>
              </div>
              <p className="hidden md:block text-[9px] font-mono-tech text-[#8C8C89] tracking-wider uppercase">
                CROSS-INSTRUMENT LUNAR CORRESPONDENCE
              </p>
            </div>
          </div>

          {/* Right Controls: Telemetry Pill + Mode Toggle + Kinetic Menu Button */}
          <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
            {/* Active Processed Images Pill */}
            <div className="hidden xl:flex items-center gap-2 px-2.5 py-1 rounded-none border border-[#262626] bg-[#161616] text-[11px] font-mono-tech text-[#A0A0A0] max-w-md truncate">
              <Activity className="h-3 w-3 text-[#86D88E] shrink-0" />
              <span className="truncate text-[#F7F7F5]" title={sourceProduct?.label || sourceProduct?.productId || sourceInstrument}>
                {sourceProduct?.label ? sourceProduct.label.replace('Chandrayaan-2 ', '').split(' (')[0] : sourceInstrument}
              </span>
              <span className="text-[#646462] shrink-0">×</span>
              <span className="truncate text-[#F7F7F5]" title={targetProduct?.label || targetProduct?.productId || targetInstrument}>
                {targetProduct?.label ? targetProduct.label.replace('Chandrayaan-2 ', '').split(' (')[0] : targetInstrument}
              </span>
            </div>

            {/* Scientific vs Explain Mode Toggle */}
            <button
              onClick={toggleExplainMode}
              className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-none text-xs font-mono-tech tracking-wider border transition-colors flex-shrink-0 ${
                explainMode
                  ? "bg-[#2E2211] border-[#5E4218] text-[#E0A855] hover:bg-[#3D2E16]"
                  : "bg-[#161616] border-[#333333] text-[#F7F7F5] hover:bg-[#222222]"
              }`}
              title="Toggle between scientific precision and conceptual explanation"
            >
              <BookOpen className="h-3 w-3" />
              <span className="font-semibold text-[11px]">{explainMode ? "EXPLAIN" : "SCIENTIFIC"}</span>
            </button>

            {/* MENU TRIGGER BUTTON */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
              aria-expanded={isOpen}
              className={`min-w-[40px] min-h-[36px] px-3 py-1.5 rounded-none font-mono-tech text-xs tracking-wider font-semibold flex items-center justify-center gap-2 border transition-colors flex-shrink-0 ${
                isOpen
                  ? "bg-[#F7F7F5] text-[#111111] border-[#F7F7F5]"
                  : "bg-[#161616] text-[#F7F7F5] border-[#333333] hover:bg-[#222222] hover:border-[#555555]"
              }`}
            >
              {isOpen ? (
                <>
                  <X className="h-3.5 w-3.5" />
                  <span className="inline text-[11px]">CLOSE</span>
                </>
              ) : (
                <>
                  <div className="flex flex-col gap-1 w-3">
                    <span className="h-[1.5px] w-full bg-[#F7F7F5]" />
                    <span className="h-[1.5px] w-full bg-[#F7F7F5]" />
                    <span className="h-[1.5px] w-full bg-[#F7F7F5]" />
                  </div>
                  <span className="inline text-[11px]">INDEX</span>
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* ─── FULL-SCREEN REVEAL OVERLAY ─── */}
      <div
        ref={overlayRef}
        onClick={(e) => {
          if (e.target === overlayRef.current) {
            setIsOpen(false)
          }
        }}
        style={{ display: "none" }}
        className="fixed inset-0 z-40 bg-[#111111] flex-col justify-between pt-20 pb-8 px-4 sm:px-8 lg:px-16 overflow-y-auto select-none"
      >
        <div
          ref={menuContentRef}
          className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 my-auto py-6"
        >
          {/* Left Column: Numbered Navigation Links */}
          <div
            ref={linksContainerRef}
            className="lg:col-span-7 flex flex-col justify-center space-y-1"
          >
            <div className="font-mono-tech text-[10px] text-[#8C8C89] tracking-widest uppercase pb-3 border-b border-[#262626] flex items-center justify-between">
              <span>SYSTEM DIRECTORY // MODULE INDEX</span>
              <span>[01 — 07]</span>
            </div>

            {PARALLAX_NAV_ITEMS.map((item, idx) => {
              const isCurrentRoute = idx === activeIndex
              const isHovered = hoveredIndex === idx

              return (
                <div
                  key={item.id}
                  onMouseEnter={() => setHoveredIndex(idx)}
                  onClick={() => handleNavigate(item.href)}
                  className={`kinetic-nav-link group flex items-baseline gap-4 sm:gap-6 py-2.5 px-3 rounded-none cursor-pointer transition-colors duration-150 ${
                    isCurrentRoute
                      ? "bg-[#1A1A1A] border border-[#383838]"
                      : isHovered
                      ? "bg-[#161616] border border-[#262626]"
                      : "border border-transparent"
                  }`}
                >
                  {/* Item Number */}
                  <span
                    className={`font-mono-tech text-xs sm:text-sm ${
                      isCurrentRoute
                        ? "text-[#F7F7F5] font-bold"
                        : isHovered
                        ? "text-[#E4E4E2]"
                        : "text-[#646462]"
                    }`}
                  >
                    {item.number}
                  </span>

                  {/* Main Label */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span
                        className={`font-sans text-xl sm:text-3xl font-extrabold tracking-tight ${
                          isCurrentRoute
                            ? "text-[#F7F7F5]"
                            : isHovered
                            ? "text-white"
                            : "text-[#A0A0A0]"
                        }`}
                      >
                        {item.label}
                      </span>
                      {isCurrentRoute && (
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-none text-[9px] font-mono-tech bg-[#1A2E1C] text-[#86D88E] border border-[#2E5E32] uppercase">
                          ACTIVE
                        </span>
                      )}
                    </div>
                    <p className="hidden sm:block text-xs text-[#8C8C89] font-sans pt-1">
                      {item.description}
                    </p>
                  </div>

                  {/* Arrow Indicator */}
                  <span
                    className={`font-mono-tech text-sm transition-opacity duration-150 ${
                      isHovered || isCurrentRoute
                        ? "text-[#F7F7F5] opacity-100"
                        : "text-[#646462] opacity-0 group-hover:opacity-60"
                    }`}
                  >
                    →
                  </span>
                </div>
              )
            })}
          </div>

          {/* Right Column: Scientific Telemetry Preview Panel */}
          <div
            ref={visualPreviewRef}
            className="hidden lg:flex lg:col-span-5 flex-col justify-between p-6 rounded-none border border-[#262626] bg-[#161616] relative text-left"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#262626] pb-3 text-[10px] font-mono-tech">
              <span className="text-[#A0A0A0] uppercase tracking-wider">
                MODULE PREVIEW // {activeHoverItem.category}
              </span>
              <span className="text-[#646462]">CH-2 POLAR 100 KM</span>
            </div>

            {/* Geometric Diagram depending on activeHoverItem */}
            <div className="my-auto flex items-center justify-center py-8">
              {hoveredIndex === 0 && (
                /* 01 MISSION: Orbit */
                <div className="relative w-44 h-44 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border border-[#333333]" />
                  <div className="absolute inset-4 rounded-full border border-dashed border-[#262626]" />
                  <div className="w-14 h-14 rounded-none bg-[#111111] border border-[#383838] flex items-center justify-center">
                    <Compass className="h-5 w-5 text-[#F7F7F5]" />
                  </div>
                  <div className="absolute top-0 text-[9px] font-mono-tech text-[#A0A0A0] bg-[#111111] px-1 border border-[#333333]">
                    100 KM POLAR
                  </div>
                </div>
              )}

              {hoveredIndex === 1 && (
                /* 02 EXPLORE: Coordinates */
                <div className="relative w-44 h-44 flex items-center justify-center border border-[#262626]">
                  <div className="absolute inset-6 rounded-full border border-[#333333]" />
                  <div className="absolute h-full w-[1px] bg-[#333333]" />
                  <div className="absolute w-full h-[1px] bg-[#333333]" />
                  <div className="h-2 w-2 bg-[#F7F7F5]" />
                  <div className="absolute bottom-2 font-mono-tech text-[9px] text-[#A0A0A0]">
                    87° 11' S • 84° 19' E
                  </div>
                </div>
              )}

              {hoveredIndex === 2 && (
                /* 03 INSTRUMENTS: Spectrometer */
                <div className="w-full space-y-3 px-2">
                  <div className="flex justify-between text-[9px] font-mono-tech text-[#8C8C89]">
                    <span>0.25 m PAN</span>
                    <span>5.0 m STEREO</span>
                    <span>0.8-5.0 µm IR</span>
                  </div>
                  <div className="h-20 flex items-end justify-between gap-1 border-b border-[#333333] pb-1">
                    {[40, 85, 60, 95, 30, 75, 90, 45, 80, 100, 65, 50, 70, 85, 40].map((h, i) => (
                      <div
                        key={i}
                        style={{ height: `${h}%` }}
                        className="flex-1 bg-[#2C2C2C] hover:bg-[#F7F7F5] transition-colors"
                      />
                    ))}
                  </div>
                  <div className="text-[9px] font-mono-tech text-center text-[#8C8C89]">
                    HETEROGENEOUS SPECTRAL INTEGRATION
                  </div>
                </div>
              )}

              {hoveredIndex === 3 && (
                /* 04 CORRESPONDENCE: Bridge */
                <div className="relative w-full flex items-center justify-between px-2">
                  <div className="w-24 h-24 rounded-none border border-[#333333] bg-[#111111] flex flex-col items-center justify-center p-2 text-center overflow-hidden">
                    <span className="text-[10px] font-mono-tech text-[#F7F7F5] font-bold truncate max-w-full" title={sourceProduct?.label}>
                      {sourceProduct?.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : sourceInstrument}
                    </span>
                    <span className="text-[8px] font-mono-tech text-[#8C8C89]">{sourceProduct?.gsdDisplay || '0.25 m/px'}</span>
                  </div>
                  <div className="flex-1 flex flex-col items-center justify-center px-2">
                    <span className="h-[1px] w-full bg-[#383838]" />
                    <span className="text-[8px] font-mono-tech text-[#86D88E] pt-1 text-center font-bold">
                      ADAPTIVE ROUTER
                    </span>
                    <span className="text-[7px] font-mono-tech text-[#8C8C89] text-center">
                      RANSAC + ANMS + ECC
                    </span>
                  </div>
                  <div className="w-24 h-24 rounded-none border border-[#333333] bg-[#111111] flex flex-col items-center justify-center p-2 text-center overflow-hidden">
                    <span className="text-[10px] font-mono-tech text-[#F7F7F5] font-bold truncate max-w-full" title={targetProduct?.label}>
                      {targetProduct?.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : targetInstrument}
                    </span>
                    <span className="text-[8px] font-mono-tech text-[#8C8C89]">{targetProduct?.gsdDisplay || '5.0 m/px'}</span>
                  </div>
                </div>
              )}

              {hoveredIndex === 4 && (
                /* 05 ANALYSIS: Error */
                <div className="w-full flex flex-col items-center justify-center space-y-2">
                  <div className="text-2xl font-mono-tech font-bold text-[#F7F7F5]">
                    {metrics.candidateMatches > 0 ? metrics.rmse.toFixed(2) : '—'} <span className="text-xs text-[#8C8C89]">px RMSE</span>
                  </div>
                  <div className="text-[10px] font-mono-tech text-[#86D88E]">
                    {metrics.candidateMatches > 0 ? `INLIER CONSENSUS: ${metrics.inlierRatio.toFixed(1)}%` : 'CONSENSUS: AWAITING RUN'}
                  </div>
                  <div className="w-full bg-[#262626] h-1">
                    <div 
                      className="bg-[#86D88E] h-full transition-all duration-300" 
                      style={{ width: `${metrics.candidateMatches > 0 ? Math.min(100, metrics.inlierRatio) : 0}%` }} 
                    />
                  </div>
                  <div className="flex justify-between w-full text-[9px] font-mono-tech text-[#8C8C89] pt-1">
                    <span>ANMS COVERAGE:</span>
                    <span className="text-[#F7F7F5]">
                      {metrics.candidateMatches > 0 ? `${metrics.spatialCoverage.toFixed(1)}%` : '—'}
                    </span>
                  </div>
                </div>
              )}

              {hoveredIndex === 5 && (
                /* 06 SIMULATOR */
                <div className="w-full space-y-2 font-mono-tech text-[10px]">
                  <div className="flex justify-between text-[#8C8C89]">
                    <span>SOLAR INCIDENCE:</span>
                    <span className="text-[#F7F7F5]">{simulationParams.sunElevationAngle}° SUN</span>
                  </div>
                  <div className="w-full bg-[#262626] h-1">
                    <div 
                      className="bg-[#E0A855] h-full" 
                      style={{ width: `${Math.min(100, (simulationParams.sunElevationAngle / 80) * 100)}%` }} 
                    />
                  </div>
                  <div className="flex justify-between text-[#8C8C89] pt-2">
                    <span>OCTAVE DISPARITY:</span>
                    <span className="text-[#F7F7F5]">{pairCharacterization.scaleRatioDisplay} SCALE GAP</span>
                  </div>
                  <div className="w-full bg-[#262626] h-1">
                    <div 
                      className="bg-[#86D88E] h-full" 
                      style={{ width: `${Math.min(100, simulationParams.spatialScaleRatio * 4)}%` }} 
                    />
                  </div>
                </div>
              )}

              {hoveredIndex === 6 && (
                /* 07 ABOUT */
                <div className="text-center space-y-2 font-mono-tech">
                  <div className="text-xs text-[#F7F7F5] font-bold">ISRO CHANDRAYAAN-2</div>
                  <div className="text-[10px] text-[#A0A0A0]">ISSDC / SAC AHMEDABAD</div>
                  <p className="text-[9px] text-[#8C8C89] leading-relaxed max-w-xs mx-auto">
                    Automated subpixel cross-sensor alignment for polar volatile characterization & hazard mapping.
                  </p>
                </div>
              )}
            </div>

            {/* Bottom Preview Metadata */}
            <div className="border-t border-[#262626] pt-3 flex items-center justify-between text-[10px] font-mono-tech text-[#8C8C89]">
              <span className="text-[#F7F7F5] font-semibold">{activeHoverItem.label}</span>
              <span className="text-[#A0A0A0]">{activeHoverItem.category}</span>
            </div>
          </div>
        </div>

        {/* Bottom Status Bar */}
        <div className="max-w-7xl mx-auto w-full pt-4 border-t border-[#262626] flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] font-mono-tech text-[#8C8C89]">
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 bg-[#86D88E]" />
            <span className="text-[#A0A0A0]">PARALLAX MISSION OBSERVATORY // ACTIVE</span>
          </div>
          <div className="flex items-center gap-4">
            <span>PRESS ESC TO CLOSE</span>
            <span>|</span>
            <span className="text-[#E4E4E2]">ISRO CHANDRAYAAN-2 DATA</span>
          </div>
        </div>
      </div>
    </>
  )
}

export default SterlingGateKineticNavigation
