import React from "react"
import { useNavigate } from "react-router-dom"
import { HeroSection } from "../sections/HeroSection"
import { ProblemNarrative } from "../sections/ProblemNarrative"
import { GlobalFooter } from "../components/common/GlobalFooter"
import { 
  Compass, 
  ArrowRight, 
  Sliders, 
  Layers, 
  ShieldCheck, 
  GitBranch, 
  Maximize2, 
  Target,
  ArrowRightCircle
} from "lucide-react"

export const HomePage: React.FC = () => {
  const navigate = useNavigate()

  const handleNavigate = (path: string) => {
    navigate(path)
    window.scrollTo({ top: 0, left: 0, behavior: "instant" })
  }

  const workflowSteps = [
    { num: '01', title: 'Input', subtitle: 'Orbital Imagery' },
    { num: '02', title: 'Pair Formation', subtitle: 'Footprint Intersect' },
    { num: '03', title: 'Physics Preprocessing', subtitle: 'NLM & CLAHE' },
    { num: '04', title: 'Pair Characterization', subtitle: 'GSD & Modality Gap' },
    { num: '05', title: 'Adaptive Router', subtitle: 'Rank Model Bank' },
    { num: '06', title: 'Correspondence', subtitle: 'Phase/Gradient Match' },
    { num: '07', title: 'RANSAC / MSAC', subtitle: 'Geometric Inliers' },
    { num: '08', title: 'Spatial ANMS', subtitle: 'Cluster Suppression' },
    { num: '09', title: 'Sub-Pixel Refine', subtitle: 'ECC Local Tuning' },
    { num: '10', title: 'Quality & Output', subtitle: 'RMSE & Uncertainty' },
  ];

  const innovations = [
    {
      num: '01',
      title: 'Pair-Aware Adaptive Model Selection',
      summary: 'Different pair → different difficulty → ranked/selectable correspondence strategy.',
      details: 'Instead of forcing a single algorithm onto every lunar observation, PARALLAX diagnoses pair difficulty and selects from structural (RIFT/HOPC), gradient (CFOG), learned (SuperPoint+LightGlue), or dense (LoFTR) engines.',
      icon: <GitBranch className="h-4 w-4 text-[#111111]" />,
      tag: 'CORE DIFFERENTIATOR'
    },
    {
      num: '02',
      title: 'TMC-2 Intermediate Scale Bridge',
      summary: 'Conditional OHRC → TMC-2 → IIRS strategy for extreme scale/modality gaps.',
      details: 'When matching ultra-high-resolution OHRC (0.25 m/px) directly against hyperspectral IIRS (80 m/px), the 320:1 scale disparity degrades direct matching. PARALLAX proposes an intermediate 5 m/px stereo bridge to secure reliable registration.',
      icon: <Layers className="h-4 w-4 text-[#8C5E13]" />,
      tag: 'CONDITIONAL STRATEGY'
    },
    {
      num: '03',
      title: 'Physics-Aware Lunar Preprocessing',
      summary: 'Illumination, solar geometry and shadow-aware preprocessing.',
      details: 'Integrates Non-Local Means (NLM) de-striping, dark-signal non-uniformity (DSNU) filtering, and Rayleigh-distributed CLAHE to recover micro-relief hidden in pitch-black polar crater shadows.',
      icon: <Sliders className="h-4 w-4 text-[#555555]" />,
      tag: 'SENSOR-AWARE'
    },
    {
      num: '04',
      title: 'Spatially Distributed Correspondences',
      summary: 'ANMS/coverage logic avoids unstable clusters of matches.',
      details: 'Adaptive Non-Maximal Suppression (ANMS) enforces global geometric spread across the entire observation footprint, preventing all keypoints from bunching onto a single sunlit crater rim.',
      icon: <Maximize2 className="h-4 w-4 text-[#246327]" />,
      tag: 'GLOBAL DISPERSION'
    },
    {
      num: '05',
      title: 'Sub-Pixel + Uncertainty-Aware Validation',
      summary: 'Robust geometry → local refinement → error, coverage, confidence and uncertainty.',
      details: 'Following MSAC inlier consensus, Enhanced Correlation Coefficient (ECC) optimization fine-tunes coordinates to sub-pixel precision while reporting 1-sigma uncertainty bounds and target quality gate status.',
      icon: <ShieldCheck className="h-4 w-4 text-[#555555]" />,
      tag: 'SCIENTIFIC RIGOR'
    }
  ];

  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col font-sans">
      {/* 01: Master Landing Hero (BLACK SECTION #111111) */}
      <HeroSection />

      {/* 02: Problem Narrative ("Observed Through Different Eyes") (LIGHT SECTION #F7F7F5) */}
      <ProblemNarrative />

      {/* 03: Complete 10-Step Adaptive Workflow Visual (BLACK SECTION #111111) */}
      <section className="relative py-20 bg-[#111111] text-[#F7F7F5] border-b border-[#262626] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="space-y-2">
            <h2 className="font-sans text-2xl sm:text-4xl font-extrabold text-[#F7F7F5] uppercase tracking-tight">
              Adaptive Registration Pipeline Flow
            </h2>
            <p className="text-base sm:text-lg font-semibold text-[#D4D4D0] max-w-3xl font-sans leading-relaxed">
              PARALLAX replaces rigid one-size-fits-all matchers with an end-to-end adaptive framework. The pipeline characterizes difficulty, routes to optimal models, verifies geometry, and guarantees spatial coverage.
            </p>
          </div>

          {/* 10-Step Flow Graphic */}
          <div className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] overflow-x-auto">
            <div className="min-w-[980px] grid grid-cols-10 gap-2 items-center">
              {workflowSteps.map((step, idx) => (
                <div key={step.num} className="relative flex flex-col items-center text-center p-2.5 rounded-none border border-[#262626] bg-[#111111] hover:border-[#383838] transition-colors">
                  <span className="font-mono-tech text-[10px] text-[#A0A0A0] font-bold">{step.num}</span>
                  <span className="font-sans text-xs font-bold text-[#F7F7F5] mt-1 leading-tight">{step.title}</span>
                  <span className="font-mono-tech text-[9px] text-[#8C8C89] mt-1">{step.subtitle}</span>
                  {idx < workflowSteps.length - 1 && (
                    <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-[#383838]">
                      <ArrowRightCircle className="h-3 w-3 text-[#3E3E3E]" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 04: The 5 Innovation Cards ("Why PARALLAX Is Different") (LIGHT SECTION #F7F7F5) */}
      <section className="relative py-24 bg-[#F7F7F5] text-[#111111] border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="max-w-3xl space-y-2">
            <h2 className="font-sans text-2xl sm:text-4xl font-black tracking-tight text-[#111111] uppercase">
              WHY PARALLAX IS DIFFERENT
            </h2>
            <p className="text-base sm:text-lg font-semibold text-[#111111] leading-relaxed font-sans">
              Five architectural pillars that distinguish PARALLAX from conventional fixed-pipeline planetary tools.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {innovations.map((item) => (
              <div 
                key={item.num}
                className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] hover:border-[#BFBFB8] transition-colors flex flex-col justify-between space-y-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)]"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="p-2 rounded-none bg-[#F7F7F5] border border-[#E2E2DE]">
                      {item.icon}
                    </div>
                    <span className="font-mono-tech text-[9px] px-2 py-0.5 rounded-none bg-[#F7F7F5] border border-[#E2E2DE] text-[#666666] font-semibold uppercase tracking-wider">
                      {item.tag}
                    </span>
                  </div>

                  <div className="font-mono-tech text-[10px] text-[#888885] font-bold">PILLAR {item.num}</div>
                  <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
                    {item.title}
                  </h3>
                  <div className="font-mono-tech text-xs sm:text-sm text-[#111111] font-bold pb-1 border-b border-[#EAEAE6]">
                    {item.summary}
                  </div>
                  <p className="text-sm sm:text-base font-semibold text-[#222222] font-sans leading-relaxed">
                    {item.details}
                  </p>
                </div>
              </div>
            ))}

            {/* Sixth Interactive CTA Card (Crisp Dark Accent in Light Grid) */}
            <div className="p-6 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111] text-[#F7F7F5] flex flex-col justify-between space-y-4 shadow-md">
              <div className="space-y-2">
                <div className="font-mono-tech text-xs text-[#86D88E] uppercase tracking-wider font-semibold">
                  TRY THE ADAPTIVE ENGINE
                </div>
                <h3 className="font-sans text-lg sm:text-xl font-bold text-[#F7F7F5]">
                  Experience Pair-Aware Registration in Real Time
                </h3>
                <p className="text-sm sm:text-base font-medium text-[#D4D4D0] font-sans leading-relaxed">
                  Select any two Chandrayaan-2 sensors, inspect the characterized difficulty profile, see candidate models ranked, and verify sub-pixel alignment.
                </p>
              </div>

              <div className="space-y-2 pt-2">
                <button
                  onClick={() => handleNavigate("/correspondence")}
                  className="w-full flex items-center justify-center gap-2 px-5 py-2.5 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#F7F7F5] text-[#111111] hover:bg-[#FFFFFF] transition-colors"
                >
                  <span>LAUNCH STUDIO DEMO</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => handleNavigate("/simulator")}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-none font-mono-tech text-xs tracking-wider text-[#A0A0A0] hover:text-[#FFFFFF] border border-[#262626] bg-[#161616] hover:bg-[#222222] transition-colors"
                >
                  <Sliders className="h-3.5 w-3.5 text-[#E0A855]" />
                  <span>STRESS-TEST IN SIMULATOR</span>
                </button>
              </div>
            </div>
          </div>

          {/* Direct Launchpad Strip (White Editorial Card) */}
          <div className="p-6 sm:p-8 rounded-none sm:rounded-sm border border-[#D4D4D0] bg-[#FFFFFF] shadow-[0_2px_8px_rgba(0,0,0,0.04)] flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-1">
              <div className="font-sans text-xl sm:text-2xl font-bold text-[#111111]">
                Inspect 3D Lunar Craters & Characterize Payloads
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => handleNavigate("/explore")}
                className="flex items-center gap-2 px-5 py-2.5 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#111111] text-[#F7F7F5] hover:bg-[#222222] transition-colors"
              >
                <Compass className="h-3.5 w-3.5 text-[#F7F7F5]" />
                <span>LAUNCH EXPLORER</span>
              </button>
              <button
                onClick={() => handleNavigate("/instruments")}
                className="flex items-center gap-2 px-4 py-2.5 rounded-none font-mono-tech text-xs tracking-wider text-[#111111] border border-[#D4D4D0] bg-[#F7F7F5] hover:bg-[#EFEFEA] transition-colors"
              >
                <span>INSTRUMENT LAB</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 05: Global Mission Footer (BLACK SECTION #111111) */}
      <GlobalFooter />
    </div>
  )
}

export default HomePage
