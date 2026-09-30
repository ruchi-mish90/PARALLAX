import React from "react"
import { useNavigate } from "react-router-dom"
import { CorrespondenceStudioSection } from "../sections/CorrespondenceStudioSection"
import { GlobalFooter } from "../components/common/GlobalFooter"
import { Scan, ArrowRight, Activity, BarChart2 } from "lucide-react"
import { useParallax } from "../state/ParallaxContext"

export const CorrespondencePage: React.FC = () => {
  const navigate = useNavigate()
  const { sourceInstrument, targetInstrument, selectedRegion, metrics } = useParallax()

  const handleRunAnalysis = () => {
    navigate("/analysis")
    window.scrollTo({ top: 0, left: 0, behavior: "instant" })
  }

  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col pt-14 font-sans">
      {/* ─── BAND 1 (BLACK #111111): Page Header & Top Setup ─── */}
      <div className="bg-[#111111] border-b border-[#262626]">
        <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-8 pb-5 text-left">
          <div className="space-y-2">
            <h1 className="font-sans text-3xl sm:text-5xl font-black text-[#F7F7F5] uppercase tracking-tight">
              CORRESPONDENCE STUDIO
            </h1>
            <p className="text-base sm:text-xl font-bold text-[#D4D4D0] max-w-3xl leading-relaxed">
              Diagnose pair difficulty, rank adaptive correspondence models, eliminate false shadows with geometry, and verify sub-pixel alignment.
            </p>
          </div>
        </div>
      </div>

      {/* Main Correspondence Studio Section with Alternating Dark & Light Bands */}
      <CorrespondenceStudioSection />

      {/* ─── BAND 5 (LIGHT #F7F7F5): Verification Launchpad ─── */}
      <section className="relative py-12 bg-[#F7F7F5] text-[#111111] border-b border-[#E2E2DE] select-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-6 sm:p-8 rounded-none sm:rounded-sm border border-[#D4D4D0] bg-[#FFFFFF] shadow-[0_2px_8px_rgba(0,0,0,0.04)] flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1 text-left">
              <div className="font-mono-tech text-xs text-[#246327] uppercase tracking-wider flex items-center gap-2 font-semibold">
                <span className="h-2 w-2 bg-[#246327]" />
                <span>PIPELINE EXECUTION READY</span>
              </div>
              <div className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
                Inspect Mathematical Homography & Error Residuals
              </div>
              <p className="text-xs text-[#555555] font-sans max-w-xl">
                Review estimated 3×3 projective transformation matrix H, {metrics.candidateMatches > 0 ? `${metrics.rmse.toFixed(2)} px RMSE distribution` : 'reprojection residual error distribution'},
                and Lowe ratio rejection histograms.
              </p>
            </div>
            <button
              onClick={handleRunAnalysis}
              className="flex items-center gap-2.5 px-6 py-3 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#111111] text-[#F7F7F5] hover:bg-[#222222] transition-colors shrink-0"
            >
              <BarChart2 className="h-4 w-4" />
              <span>RUN VERIFICATION & ANALYSIS</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </section>

      {/* ─── BAND 6 (BLACK #111111): Global Footer ─── */}
      <GlobalFooter />
    </div>
  )
}

export default CorrespondencePage
