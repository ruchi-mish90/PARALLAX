import React from "react"
import { useNavigate } from "react-router-dom"
import { SimulatorSection } from "../sections/SimulatorSection"
import { GlobalFooter } from "../components/common/GlobalFooter"
import { Sliders, ArrowRight, BookOpen, AlertTriangle } from "lucide-react"

export const SimulatorPage: React.FC = () => {
  const navigate = useNavigate()

  const handleGoToAbout = () => {
    navigate("/about")
    window.scrollTo({ top: 0, left: 0, behavior: "instant" })
  }

  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col pt-16 font-sans">
      {/* Editorial Page Header */}
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-8 pb-4 text-left">
        <div className="border-b border-[#262626] pb-5 space-y-2">
          <h1 className="font-sans text-3xl sm:text-5xl font-black text-[#F7F7F5] uppercase tracking-tight">
            ENVIRONMENT SIMULATOR
          </h1>
          <p className="text-base sm:text-xl font-bold text-[#D4D4D0] max-w-3xl leading-relaxed">
            Simulate how solar elevation angle, scale disparity ratios, and sensor noise variances alter lunar terrain visibility in real-time.
          </p>
        </div>
      </div>

      {/* Main Simulator Component Section */}
      <SimulatorSection />

      {/* Editorial Light Section: Experimental Parameter Notes & About CTA */}
      <section className="relative py-20 bg-[#F7F7F5] text-[#111111] border-t border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          
          <div className="pb-6 border-b border-[#E2E2DE] space-y-2">
            <h2 className="font-sans text-2xl sm:text-3xl font-extrabold text-[#111111] tracking-tight">
              Environmental & Radiometric Variance Principles
            </h2>
            <p className="text-base sm:text-lg font-semibold text-[#111111] max-w-3xl font-sans leading-relaxed">
              Synthetic parameters reproduce spaceborne CCD linear detector responses, sub-solar shadow dynamics, and octave blur disparities encountered across Chandrayaan-2 orbits.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm font-mono-tech">
              <div className="text-[10px] text-[#777774] uppercase font-semibold tracking-wider">01 / SOLAR ELEVATION VARIANCE</div>
              <div className="text-lg font-bold text-[#111111] font-sans">Shadow Geometry Shifting</div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                At 1.8° sun elevation, polar crater rim shadows extend 10x longer than at 15°, causing
                naive template matchers to track moving shadow edges rather than geological rock surface.
              </p>
              <div className="pt-2 border-t border-[#E2E2DE] text-xs font-mono-tech text-[#8C5E13] font-semibold">
                Solution: Phase-congruency structural filters
              </div>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm font-mono-tech">
              <div className="text-[10px] text-[#777774] uppercase font-semibold tracking-wider">02 / OCTAVE SCALE PYRAMID</div>
              <div className="text-lg font-bold text-[#111111] font-sans">Gaussian Blur Equalization</div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Progressive downsampling with scale-space σ smoothing allows descriptors extracted from
                0.25 m/px OHRC images to maintain mathematical scale invariance when matched against 5.0 m/px TMC-2.
              </p>
              <div className="pt-2 border-t border-[#E2E2DE] text-xs font-mono-tech text-[#246327] font-semibold">
                Scale Gap Range: 20:1 up to 320:1
              </div>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm font-mono-tech">
              <div className="text-[10px] text-[#777774] uppercase font-semibold tracking-wider">03 / DETECTOR NOISE (DSNU)</div>
              <div className="text-lg font-bold text-[#111111] font-sans">Non-Local Means Filtering</div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Dark-signal non-uniformity (DSNU) across linear CCD arrays is normalized prior to
                gradient computation to prevent false keypoint triggers along sensor stripes.
              </p>
              <div className="pt-2 border-t border-[#E2E2DE] text-xs font-mono-tech text-[#111111] font-semibold">
                Pre-processing: Fast NLM + CLAHE clip 3.2
              </div>
            </div>
          </div>

          {/* Action Launch Bar to About Page */}
          <div className="p-6 sm:p-8 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] flex flex-col sm:flex-row items-center justify-between gap-6 shadow-sm">
            <div className="space-y-1">
              <div className="font-sans text-xl sm:text-2xl font-bold text-[#111111]">
                Mission Significance & Computer-Vision Methodology
              </div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] font-sans max-w-xl">
                Explore how subpixel co-registration enables safe landing hazard mapping and volatile
                ice characterization in permanently shadowed lunar craters.
              </p>
            </div>
            <button
              onClick={handleGoToAbout}
              className="flex items-center gap-2 px-6 py-3 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#111111] text-[#F7F7F5] hover:bg-[#222222] transition-colors shrink-0"
            >
              <BookOpen className="h-4 w-4" />
              <span>READ METHODOLOGY</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </section>

      {/* Global Footer */}
      <GlobalFooter />
    </div>
  )
}

export default SimulatorPage
