import React from "react"
import { MoonExplorerSection } from "../sections/MoonExplorerSection"
import { GlobalFooter } from "../components/common/GlobalFooter"
import { Crosshair, MapPin, Eye, Compass } from "lucide-react"

export const ExplorePage: React.FC = () => {
  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col pt-16 font-sans">
      {/* Editorial Page Introduction Banner */}
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-8 pb-4 text-left">
        <div className="border-b border-[#262626] pb-5 space-y-2">
          <h1 className="font-sans text-3xl sm:text-5xl font-black text-[#F7F7F5] uppercase tracking-tight">
            LUNAR REGION EXPLORER
          </h1>
          <p className="text-base sm:text-xl font-bold text-[#D4D4D0] max-w-3xl leading-relaxed">
            Target authentic Chandrayaan-2 lunar observation corridors across heterogeneous orbital imaging passes.
          </p>
        </div>
      </div>

      {/* Main 3D Lunar Explorer Stage */}
      <MoonExplorerSection />

      {/* Editorial Light Section: Selenodetic Ground Standards & Calibrated Corridors */}
      <section className="relative py-20 bg-[#F7F7F5] text-[#111111] border-t border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          
          <div className="pb-6 border-b border-[#E2E2DE] space-y-2">
            <h2 className="font-sans text-2xl sm:text-3xl font-extrabold text-[#111111] tracking-tight">
              Selenodetic Ground Control & Orbital Geometry
            </h2>
            <p className="text-base sm:text-lg font-semibold text-[#111111] max-w-3xl font-sans leading-relaxed">
              Planetary co-registration demands rigorous geodetic anchoring against verified laser altimetry baselines and retro-reflector coordinates before multi-modal feature matching.
            </p>
          </div>

          {/* 3 Editorial Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm">
              <div className="text-[10px] text-[#777774] font-mono-tech uppercase font-semibold tracking-wider">
                01 / COORDINATE SYSTEM
              </div>
              <div className="text-lg font-bold text-[#111111] font-sans">
                Mean Earth/Polar Axis (ME)
              </div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Standard IAU/IAG selenographic reference frame with lunar radius R = 1,737.4 km, with coordinates anchored by Apollo and Lunokhod lunar laser retro-reflectors.
              </p>
              <div className="pt-2 border-t border-[#E2E2DE] text-xs font-mono-tech text-[#666663] font-semibold">
                Zero Meridian: Mean Earth Direction
              </div>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm">
              <div className="text-[10px] text-[#8C5E13] font-mono-tech uppercase font-semibold tracking-wider">
                02 / ILLUMINATION REGIME
              </div>
              <div className="text-lg font-bold text-[#111111] font-sans">
                Glancing Solar Angles (1°–5°)
              </div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Polar craters experience grazing sunlight creating perpetual shadows inside crater floors interspersed with razor-sharp sunlit rims that migrate non-linearly.
              </p>
              <div className="pt-2 border-t border-[#E2E2DE] text-xs font-mono-tech text-[#8C5E13] font-semibold">
                Requires: Phase Congruency / RIFT
              </div>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm">
              <div className="text-[10px] text-[#246327] font-mono-tech uppercase font-semibold tracking-wider">
                03 / MISSION APPLICATION
              </div>
              <div className="text-lg font-bold text-[#111111] font-sans">
                Volatiles & Hazard Avoidance
              </div>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Selected target sites represent priority locations for water-ice prospecting and safe automated touch-down corridors for Chandrayaan and Artemis missions.
              </p>
              <div className="pt-2 border-t border-[#E2E2DE] text-xs font-mono-tech text-[#246327] font-semibold">
                Subpixel Tolerance: &lt; 0.50 px
              </div>
            </div>
          </div>

          {/* Geodetic Benchmark Table */}
          <div className="space-y-4">
            <div className="space-y-1">
              <div className="font-mono-tech text-xs text-[#666663] uppercase tracking-wider">
                CALIBRATED POLAR OBSERVATION TARGETS
              </div>
              <h3 className="font-sans text-lg font-bold text-[#111111]">
                Target Site Reference Catalogue
              </h3>
            </div>

            <div className="overflow-x-auto border border-[#E2E2DE] bg-[#FFFFFF] shadow-sm">
              <table className="w-full text-left font-mono-tech text-xs">
                <thead>
                  <tr className="border-b border-[#E2E2DE] bg-[#EEEEEC] text-[#555555] text-[10px] uppercase">
                    <th className="py-3 px-4 font-semibold">Target Site</th>
                    <th className="py-3 px-4 font-semibold">Coordinates</th>
                    <th className="py-3 px-4 font-semibold">Solar Elevation</th>
                    <th className="py-3 px-4 font-semibold">Primary Sensor Gap</th>
                    <th className="py-3 px-4 font-semibold">Primary Match Strategy</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E2DE] text-[#444444]">
                  <tr className="hover:bg-[#F9F9F8] transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#111111]">Shackleton Ridge</td>
                    <td className="py-3 px-4">89.9°S, 0.0°E</td>
                    <td className="py-3 px-4 text-[#8C5E13]">1.5° (Grazing)</td>
                    <td className="py-3 px-4">OHRC ↔ TMC-2 (20:1)</td>
                    <td className="py-3 px-4 text-[#246327] font-semibold">RIFT + RANSAC</td>
                  </tr>
                  <tr className="hover:bg-[#F9F9F8] transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#111111]">Faustini Basin</td>
                    <td className="py-3 px-4">87.3°S, 77.0°E</td>
                    <td className="py-3 px-4 text-[#9E2A27]">0.8° (PSR Shadow)</td>
                    <td className="py-3 px-4">OHRC ↔ IIRS (320:1)</td>
                    <td className="py-3 px-4 text-[#246327] font-semibold">LoFTR + Scale Bridge</td>
                  </tr>
                  <tr className="hover:bg-[#F9F9F8] transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#111111]">Boguslawsky E</td>
                    <td className="py-3 px-4">74.2°S, 53.6°E</td>
                    <td className="py-3 px-4 text-[#246327]">8.4° (Moderate)</td>
                    <td className="py-3 px-4">OHRC ↔ TMC-2 (20:1)</td>
                    <td className="py-3 px-4 text-[#246327] font-semibold">SIFT + ANMS + ECC</td>
                  </tr>
                  <tr className="hover:bg-[#F9F9F8] transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#111111]">Shiv Shakti Point</td>
                    <td className="py-3 px-4">69.37°S, 32.35°E</td>
                    <td className="py-3 px-4 text-[#246327]">11.2° (Equatorward)</td>
                    <td className="py-3 px-4">TMC-2 ↔ IIRS (16:1)</td>
                    <td className="py-3 px-4 text-[#246327] font-semibold">LightGlue Graph</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </section>

      {/* Global Footer */}
      <GlobalFooter />
    </div>
  )
}

export default ExplorePage
