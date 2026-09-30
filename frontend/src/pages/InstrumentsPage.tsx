import React from "react"
import { useNavigate } from "react-router-dom"
import { InstrumentLabSection } from "../sections/InstrumentLabSection"
import { GlobalFooter } from "../components/common/GlobalFooter"
import { Radio, ArrowRight } from "lucide-react"

export const InstrumentsPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col pt-14 font-sans">
      
      {/* ─── BAND 1 (LIGHT #F7F7F5): Editorial Header & Specification Matrix ─── */}
      <section className="relative py-12 bg-[#F7F7F5] text-[#111111] border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 space-y-8">
          {/* Header Title */}
          <div className="border-b border-[#EAEAE6] pb-5 space-y-2">
            <h1 className="font-sans text-3xl sm:text-5xl font-black text-[#111111] uppercase tracking-tight">
              INSTRUMENT LAB
            </h1>
            <p className="text-base sm:text-xl font-bold text-[#111111] max-w-3xl leading-relaxed">
              Verified sensor specifications, spectral bands, focal lengths, and ground sampling distances across heterogeneous lunar observation payloads.
            </p>
          </div>

          {/* Sensor Optics & Bandwidth Comparison Table */}
          <div className="space-y-4">
            <h2 className="font-sans text-xl sm:text-2xl font-bold text-[#111111]">
              Heterogeneous Observation Physics
            </h2>

            <div className="overflow-x-auto rounded-none border border-[#E2E2DE] bg-[#FFFFFF] shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
              <table className="w-full text-left font-mono-tech text-xs">
                <thead className="bg-[#EFEFEA] text-[#111111] border-b border-[#E2E2DE]">
                  <tr>
                    <th className="p-3">INSTRUMENT</th>
                    <th className="p-3">GSD</th>
                    <th className="p-3">MODALITY</th>
                    <th className="p-3">PRIMARY ROLE</th>
                    <th className="p-3">REGISTRATION CHALLENGE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAEAE6] text-[#444444]">
                  <tr className="hover:bg-[#F7F7F5] transition-colors">
                    <td className="p-3 text-[#111111] font-bold flex items-center gap-2">
                      <span className="h-1.5 w-1.5 bg-[#111111]" />
                      <span>OHRC</span>
                    </td>
                    <td className="p-3 text-[#111111] font-bold">~0.25–0.32 m/px</td>
                    <td className="p-3">Optical/panchromatic</td>
                    <td className="p-3 text-[#111111]">Fine terrain detail & hazard verification</td>
                    <td className="p-3 text-[#8C5E13] font-semibold">Very high spatial detail causing severe scale aliasing</td>
                  </tr>
                  <tr className="hover:bg-[#F7F7F5] transition-colors">
                    <td className="p-3 text-[#111111] font-bold flex items-center gap-2">
                      <span className="h-1.5 w-1.5 bg-[#666666]" />
                      <span>TMC-2</span>
                    </td>
                    <td className="p-3 text-[#111111] font-bold">~5 m/px</td>
                    <td className="p-3">Visible panchromatic + stereo</td>
                    <td className="p-3 text-[#111111]">Regional terrain / 3D DEM context</td>
                    <td className="p-3 text-[#246327] font-semibold">Intermediate scale bridge for extreme pairs</td>
                  </tr>
                  <tr className="hover:bg-[#F7F7F5] transition-colors">
                    <td className="p-3 text-[#111111] font-bold flex items-center gap-2">
                      <span className="h-1.5 w-1.5 bg-[#8C5E13]" />
                      <span>IIRS</span>
                    </td>
                    <td className="p-3 text-[#8C5E13] font-bold">~80 m/px</td>
                    <td className="p-3 text-[#8C5E13]">Hyperspectral (256 bands)</td>
                    <td className="p-3 text-[#111111]">Spectral / mineralogical & water hydration mapping</td>
                    <td className="p-3 text-[#9E2A27] font-semibold">Extreme scale + modality gap; requires phase congruency or bridge</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ─── BAND 2 (BLACK #111111): Interactive Sensor Lab Workbench ─── */}
      <InstrumentLabSection />

      {/* ─── BAND 3 (LIGHT #F7F7F5): Action Launchpad ─── */}
      <section className="relative py-12 bg-[#F7F7F5] text-[#111111] border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-6 sm:p-8 rounded-none sm:rounded-sm border border-[#D4D4D0] bg-[#FFFFFF] shadow-[0_2px_8px_rgba(0,0,0,0.04)] flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <div className="text-[#111111] font-sans font-bold text-base sm:text-lg">
                Proceed to Image Correspondence Studio
              </div>
              <p className="text-xs text-[#555555] font-sans">
                Pair OHRC with TMC-2 or IIRS to extract multi-modal landmark homographies.
              </p>
            </div>
            <button
              onClick={() => {
                navigate("/correspondence")
                window.scrollTo({ top: 0, left: 0, behavior: "instant" })
              }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#111111] text-[#F7F7F5] hover:bg-[#222222] transition-colors shrink-0"
            >
              <span>LAUNCH STUDIO</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </section>

      {/* ─── BAND 4 (BLACK #111111): Global Footer ─── */}
      <GlobalFooter />
    </div>
  )
}

export default InstrumentsPage
