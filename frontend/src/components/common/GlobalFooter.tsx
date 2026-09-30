import React from "react"
import { useNavigate } from "react-router-dom"
import { Compass, ArrowUpRight, Globe2, ShieldCheck } from "lucide-react"

export const GlobalFooter: React.FC = () => {
  const navigate = useNavigate()

  const handleNav = (href: string) => {
    navigate(href)
    window.scrollTo({ top: 0, left: 0, behavior: "instant" })
  }

  return (
    <footer className="relative z-10 border-t border-[#262626] bg-[#111111] py-14 text-left select-none font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
          {/* Brand & Mission Statement */}
          <div className="md:col-span-6 space-y-3">
            <div className="flex items-center gap-3">
              <div className="h-6 w-6 rounded-none border border-[#333333] flex items-center justify-center bg-[#161616]">
                <Compass className="h-3.5 w-3.5 text-[#E4E4E2]" />
              </div>
              <span className="font-sans font-bold tracking-tight text-base text-[#F7F7F5]">
                PARALLAX
              </span>
              <span className="px-1.5 py-0.2 rounded-none text-[9px] font-mono-tech bg-[#1A1A1A] text-[#A0A0A0] border border-[#333333]">
                CHANDRAYAAN-2
              </span>
            </div>
            <p className="text-xs text-[#8C8C89] max-w-md leading-relaxed font-sans">
              An autonomous scale-invariant computer-vision platform for subpixel lunar image
              correspondence across heterogeneous remote-sensing instruments: OHRC, TMC-2, and IIRS.
            </p>
            <div className="flex items-center gap-4 text-[10px] font-mono-tech text-[#646462] pt-1">
              <span className="flex items-center gap-1.5 text-[#A0A0A0]">
                <Globe2 className="h-3 w-3" />
                <span>100 KM POLAR ORBIT</span>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 text-[#86D88E]">
                <ShieldCheck className="h-3 w-3" />
                <span>ISRO / ISSDC OPEN DATA</span>
              </span>
            </div>
          </div>

          {/* Directory Links */}
          <div className="md:col-span-3 space-y-2.5 font-mono-tech">
            <div className="text-[10px] uppercase text-[#8C8C89] tracking-wider font-semibold">
              PLATFORM DIRECTORY
            </div>
            <ul className="space-y-1.5 text-xs text-[#A0A0A0]">
              <li>
                <button
                  onClick={() => handleNav("/")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>01 MISSION OVERVIEW</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleNav("/explore")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>02 LUNAR EXPLORER</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleNav("/instruments")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>03 INSTRUMENT LAB</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleNav("/correspondence")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>04 CORRESPONDENCE STUDIO</span>
                </button>
              </li>
            </ul>
          </div>

          <div className="md:col-span-3 space-y-2.5 font-mono-tech">
            <div className="text-[10px] uppercase text-[#8C8C89] tracking-wider font-semibold">
              ANALYSIS & SCIENCE
            </div>
            <ul className="space-y-1.5 text-xs text-[#A0A0A0]">
              <li>
                <button
                  onClick={() => handleNav("/analysis")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>05 VERIFICATION METRICS</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleNav("/simulator")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>06 MULTI-SENSOR SIMULATOR</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleNav("/about")}
                  className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1"
                >
                  <span>07 METHODOLOGY & DATA</span>
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Baseline Bar */}
        <div className="pt-6 border-t border-[#262626] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono-tech text-[#646462]">
          <div>
            <span>© 2024 PARALLAX SCIENTIFIC CONSORTIUM • CHANDRAYAAN-2 SCIENCE DATA ARCHIVE</span>
          </div>
          <div className="flex items-center gap-4 text-[#8C8C89]">
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              className="hover:text-[#FFFFFF] transition-colors flex items-center gap-1 text-[11px]"
            >
              <span>BACK TO TOP</span>
              <ArrowUpRight className="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default GlobalFooter
