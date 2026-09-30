import React from "react"
import { useNavigate } from "react-router-dom"
import { AnalysisSection } from "../sections/AnalysisSection"
import { GlobalFooter } from "../components/common/GlobalFooter"
import { BarChart2, ArrowRight, Sliders, ShieldCheck } from "lucide-react"
import { useParallax } from "../state/ParallaxContext"

export const AnalysisPage: React.FC = () => {
  const navigate = useNavigate()
  const { 
    sourceInstrument, 
    targetInstrument, 
    sourceProduct,
    targetProduct,
    selectedRegion, 
    metrics 
  } = useParallax()

  const handleGoToSimulator = () => {
    navigate("/simulator")
    window.scrollTo({ top: 0, left: 0, behavior: "instant" })
  }

  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col pt-16 font-sans">
      {/* Editorial Page Header */}
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-8 pb-4 text-left">
        <div className="border-b border-[#262626] pb-5 space-y-2">
          <h1 className="font-sans text-3xl sm:text-5xl font-black text-[#F7F7F5] uppercase tracking-tight">
            CORRESPONDENCE ANALYSIS
          </h1>
          <p className="text-base sm:text-xl font-bold text-[#D4D4D0] max-w-3xl leading-relaxed">
            Quantitative evaluation of projective transformation matrix H, reprojection root-mean-square error (RMSE), and spatial distribution consistency.
          </p>
        </div>
      </div>

      {/* Main Analysis Section */}
      <AnalysisSection />

      {/* Editorial Light Section: Deep Mathematical Formulation & Outlier Audit */}
      <section className="relative py-20 bg-[#F7F7F5] text-[#111111] border-t border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          
          <div className="pb-6 border-b border-[#E2E2DE] space-y-2">
            <h2 className="font-sans text-2xl sm:text-3xl font-extrabold text-[#111111] tracking-tight">
              Planar Homography & Outlier Rejection Rationale
            </h2>
            <p className="text-base sm:text-lg font-semibold text-[#111111] max-w-3xl font-sans leading-relaxed">
              Mathematical proof of projective transformation validity at orbital altitude, coupled with adaptive spatial suppression criteria.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-3 font-mono-tech shadow-sm">
              <div className="text-[10px] text-[#777774] uppercase tracking-wider flex items-center justify-between">
                <span>MATHEMATICAL FORMULATION</span>
                <span className="text-[9px] text-[#999996]">PLANAR APPROXIMATION</span>
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
                Projective Transformation Validity
              </h3>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                The 8-degree-of-freedom planar homography matrix H maps homogeneous image coordinates
                x = (u, v, 1)ᵀ in the reference {sourceProduct?.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').split(' (')[0] : sourceInstrument} frame to corresponding coordinates x&apos; in {targetProduct?.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').split(' (')[0] : targetInstrument}:
              </p>
              <div className="p-3 rounded-none bg-[#F0F0ED] border border-[#E2E2DE] text-[#111111] text-xs font-semibold">
                x&apos; ~ H · x, where det(H) ≠ 0
              </div>
              <p className="text-xs sm:text-sm font-medium text-[#333333] font-sans leading-relaxed">
                <span className="text-[#8C5E13] font-mono-tech text-[10px] font-semibold">SCIENTIFIC CONTEXT: </span>
                Planar homography provides a sound local approximation at 100 km Chandrayaan-2 orbital altitude, where crater vertical relief (Δh ≈ 1–2 km) constitutes &lt;2% of sensor standoff distance. For steep crater central peaks with extreme parallax, piecewise thin-plate splines or DEM-assisted epipolar geometry are recommended.
              </p>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-3 font-mono-tech shadow-sm">
              <div className="text-[10px] text-[#777774] uppercase tracking-wider flex items-center justify-between">
                <span>REJECTED MATCH BREAKDOWN & ANMS</span>
                <span className="text-[9px] text-[#999996]">OUTLIER AUDIT</span>
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
                Geometry & Dispersion Consensus
              </h3>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Subsolar angle shifts cause polar boulder shadows to migrate non-linearly. Candidate matches failing the distance ratio d₁/d₂ &lt; 0.72 or exceeding the 2.5 px MSAC consensus threshold are rejected.
              </p>
              <div className="space-y-1.5 pt-2 border-t border-[#E2E2DE] text-xs text-[#444444]">
                <div className="flex items-center justify-between">
                  <span>CONFIRMED INLIERS:</span>
                  <span className="text-[#246327] font-bold">
                    {metrics.candidateMatches > 0
                      ? `${metrics.inlierMatches} MATCHES (${metrics.inlierRatio.toFixed(1)}%)`
                      : 'AWAITING PIPELINE RUN'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[#666663] text-[11px]">
                  <span>REJECTED OUTLIERS:</span>
                  <span className="text-[#9E2A27] font-semibold">
                    {metrics.candidateMatches > 0
                      ? `${metrics.outlierMatches} MATCHES (${(100 - metrics.inlierRatio).toFixed(1)}%)`
                      : '—'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[#111111] text-[11px]">
                  <span>ANMS CONVEX-HULL SPREAD:</span>
                  <span className="font-semibold text-[#246327]">
                    {metrics.candidateMatches > 0
                      ? `${metrics.spatialCoverage.toFixed(1)}% (TARGET > 60% ${metrics.spatialCoverage >= 60 ? 'MET' : 'PENDING'})`
                      : '—'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Action to Simulator */}
          <div className="p-6 sm:p-8 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] flex flex-col sm:flex-row items-center justify-between gap-6 shadow-sm">
            <div className="space-y-1">
              <div className="font-sans text-xl sm:text-2xl font-bold text-[#111111]">
                Open Parameter Simulator & Noise Sandbox
              </div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] font-sans max-w-xl">
                Simulate low solar illumination angles, synthetic detector noise, and extreme scale disparities
                to verify PARALLAX model stability under harsh operational conditions.
              </p>
            </div>
            <button
              onClick={handleGoToSimulator}
              className="flex items-center gap-2.5 px-6 py-3 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#111111] text-[#F7F7F5] hover:bg-[#222222] transition-colors shrink-0"
            >
              <Sliders className="h-4 w-4" />
              <span>LAUNCH SIMULATOR SANDBOX</span>
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

export default AnalysisPage
