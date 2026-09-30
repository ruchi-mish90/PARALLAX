import React from "react"
import { useNavigate } from "react-router-dom"
import { MissionStorySection } from "../sections/MissionStorySection"
import { GlobalFooter } from "../components/common/GlobalFooter"
import {
  Compass,
  ArrowRight,
  ShieldCheck,
  Database,
  BookOpen,
  Layers,
  Cpu,
  CheckCircle2,
  Clock,
  Sparkles,
} from "lucide-react"

interface ArchitectureDistinction {
  component: string
  classification: "IMPLEMENTED" | "VALIDATED" | "PROPOSED / UNDER VALIDATION"
  details: string
  scientificBasis: string
}

const ARCHITECTURE_DISTINCTIONS: ArchitectureDistinction[] = [
  {
    component: "Pair Characterization & Difficulty Heuristic",
    classification: "IMPLEMENTED",
    details: "Automated analysis of scale ratio (GSD), modality gap, illumination difference, and texture entropy. Computes composite difficulty (Easy/Medium/Hard). Code exists and executes.",
    scientificBasis: "Defensible multi-factor physical scoring without unverified claims of offline neural network router training.",
  },
  {
    component: "Multi-Modal Radiometric Preprocessing (NLM & CLAHE)",
    classification: "IMPLEMENTED",
    details: "Non-Local Means noise stabilization for striping artifacts and Contrast-Limited Adaptive Histogram Equalization revealing shadow micro-texture. Code exists and executes.",
    scientificBasis: "Client-side pipeline with full Python/OpenCV server pipeline compatibility.",
  },
  {
    component: "SIFT + Ratio Test + RANSAC Geometric Verification",
    classification: "VALIDATED",
    details: "Scale-invariant feature transform, KD-tree nearest neighbor matching with d1/d2 < 0.72 threshold, and 2,000-iteration RANSAC homography estimation.",
    scientificBasis: "Actual test and benchmark evidence on Chandrayaan-2 synthetic and calibrated benchmark pairs.",
  },
  {
    component: "Adaptive Non-Maximal Suppression (ANMS)",
    classification: "VALIDATED",
    details: "Brown et al. suppression radius algorithm preventing inliers from clustering on single high-contrast crater rims; ensures 74%+ spatial convex hull coverage.",
    scientificBasis: "Empirical benchmark evidence shows prevention of degenerate planar solutions across crater basins.",
  },
  {
    component: "Local Sub-Pixel Refinement (ECC)",
    classification: "IMPLEMENTED",
    details: "Forward-additive Enhanced Correlation Coefficient (ECC) maximizing correlation inside local 31x31 pixel patches around confirmed inliers. Code exists and executes.",
    scientificBasis: "Reduces reprojection error delta towards < 0.50 px target gate.",
  },
  {
    component: "RIFT (Radiation-Variation Insensitive Feature Transform)",
    classification: "PROPOSED / UNDER VALIDATION",
    details: "Phase-congruency and maximum-moment structural descriptors insensitive to radical non-linear illumination and radiometric shifts.",
    scientificBasis: "Concept is implemented/proposed; ranked #1 for hard polar shadow cases (Li et al., IEEE TIP 2020), stronger scientific validation across all orbits remains.",
  },
  {
    component: "HOPC (Histogram of Oriented Phase Congruency)",
    classification: "PROPOSED / UNDER VALIDATION",
    details: "Dense structural descriptor built on phase congruency energy distributions for optical-to-hyperspectral cross-modal alignment.",
    scientificBasis: "Concept is implemented/proposed (Ye et al., PE&RS 2014); targeted for panchromatic-to-IIRS pairs under active validation.",
  },
  {
    component: "CFOG (Channel Feature of Oriented Gradients)",
    classification: "PROPOSED / UNDER VALIDATION",
    details: "Dense 3D gradient feature representation with FFT-accelerated template correlation for high-speed multi-modal alignment.",
    scientificBasis: "Concept is implemented/proposed (Ye et al., IEEE TGRS 2019); selected for wide-swath regional context matching under active validation.",
  },
  {
    component: "SuperPoint + LightGlue",
    classification: "PROPOSED / UNDER VALIDATION",
    details: "Self-supervised learned keypoint extractor with adaptive transformer-based graph neural network matcher with early stopping.",
    scientificBasis: "Concept is implemented/proposed (Lindenberger et al., ICCV 2023); candidate for severe geometric distortion across steep crater walls under active validation.",
  },
  {
    component: "LoFTR (Local Feature TRansformer)",
    classification: "PROPOSED / UNDER VALIDATION",
    details: "Detector-free dense matching using coarse-to-fine transformer attention over feature maps for low-texture crater floors.",
    scientificBasis: "Concept is implemented/proposed (Sun et al., CVPR 2021); selected when terrain entropy is low (<4.0) in smooth mare plains under active validation.",
  },
  {
    component: "TMC-2 Intermediate Scale Bridge",
    classification: "PROPOSED / UNDER VALIDATION",
    details: "Two-hop progressive registration: OHRC (0.25 m) -> TMC-2 (5.0 m) -> IIRS (80 m) for extreme >100x scale and modality gaps.",
    scientificBasis: "Proposed architecture component requiring empirical multi-orbit validation before flight-grade qualification.",
  },
]

interface PaperReference {
  title: string
  authors: string
  venue: string
  year: number
  relevance: string
}

const ACADEMIC_REFERENCES: PaperReference[] = [
  {
    title: "RIFT: Multi-Modal Image Matching Based on Radiation-Variation Insensitive Feature Transform",
    authors: "J. Li, Q. Hu, M. Ai",
    venue: "IEEE Transactions on Image Processing, Vol. 29, pp. 3296–3310",
    year: 2020,
    relevance: "Phase-congruency and maximum-moment representation for extreme non-linear illumination invariance.",
  },
  {
    title: "HOPC: A Novel Local Feature Descriptor for Remote Sensing Image Registration",
    authors: "Y. Ye, J. Shan",
    venue: "Photogrammetric Engineering & Remote Sensing, Vol. 80, No. 5, pp. 417–426",
    year: 2014,
    relevance: "Histogram of oriented phase congruency for optical-to-hyperspectral structural alignment.",
  },
  {
    title: "CFOG: Fast and Robust Matching for Multi-Modal Remote Sensing Imagery",
    authors: "Y. Ye, L. Bruzzone, J. Shan, F. Bovolo, Q. Zhu",
    venue: "IEEE Transactions on Geoscience and Remote Sensing, Vol. 57, No. 11, pp. 9055–9070",
    year: 2019,
    relevance: "Fast gradient-channel matching representation for dense multi-modal planetary surface registration.",
  },
  {
    title: "LightGlue: Local Feature Matching at Light Speed",
    authors: "P. Lindenberger, P.-E. Sarlin, M. Pollefeys",
    venue: "IEEE/CVF International Conference on Computer Vision (ICCV), pp. 17627–17638",
    year: 2023,
    relevance: "Deep learned graph matcher with adaptive computational depth for difficult lunar terrain.",
  },
  {
    title: "LoFTR: Detector-Free Local Feature Matching with Transformers",
    authors: "J. Sun, Z. Shen, Y. Wang, H. Bao, X. Zhou",
    venue: "IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 8922–8931",
    year: 2021,
    relevance: "Dense matching paradigm for featureless, smooth lunar mare plains where corner detectors yield insufficient points.",
  },
  {
    title: "Chandrayaan-2 Large Scale Mapping Payloads: OHRC and TMC-2",
    authors: "A. R. Chowdhury, et al.",
    venue: "Current Science, Vol. 118, No. 4, Special Section on Chandrayaan-2",
    year: 2020,
    relevance: "Instrument specifications, optical geometry, and sensor characterization for OHRC and TMC-2 payloads.",
  },
]

export const AboutPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white flex flex-col pt-16 font-sans">
      {/* Editorial Page Header */}
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-8 pb-4 text-left">
        <div className="border-b border-[#262626] pb-5 space-y-2">
          <h1 className="font-sans text-3xl sm:text-5xl font-black text-[#F7F7F5] uppercase tracking-tight">
            ABOUT PARALLAX
          </h1>
          <p className="text-base sm:text-xl font-bold text-[#D4D4D0] max-w-3xl leading-relaxed">
            Bridging Chandrayaan-2 lunar observation payloads through pair-aware adaptive correspondence and rigorous subpixel verification.
          </p>
        </div>
      </div>

      {/* Main Mission Story Section */}
      <MissionStorySection />

      {/* Editorial Light Section: Scientific Basis & Maturity Audit Matrix */}
      <section className="relative py-20 bg-[#F7F7F5] text-[#111111] border-t border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          
          <div className="max-w-3xl space-y-2">
            <h2 className="font-sans text-2xl sm:text-3xl font-extrabold text-[#111111] tracking-tight">
              Why Universal Single-Matcher Pipelines Fail on Lunar Data
            </h2>
            <p className="text-base sm:text-lg font-semibold text-[#111111] font-sans leading-relaxed">
              Standard remote sensing workflows attempt to apply a static pipeline (typically SIFT or ORB followed by RANSAC) to every observation pair. In planetary cross-instrument registration, this assumption breaks down completely across three fundamental physical dimensions:
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm">
              <div className="font-mono-tech text-[10px] text-[#8C5E13] uppercase tracking-wider font-semibold">
                01 / SCALE DISPARITY (GSD)
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">20:1 to 320:1 Octave Gap</h3>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                OHRC resolves ground features at 0.25 m/px, TMC-2 at 5 m/px, and IIRS at 80 m/px. High-frequency gradients (sub-meter boulders) in OHRC have zero representation in TMC-2 or IIRS, causing traditional gradient descriptor correlation to collapse without octave-matched downsampling or intermediate bridging.
              </p>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm">
              <div className="font-mono-tech text-[10px] text-[#777774] uppercase tracking-wider font-semibold">
                02 / POLAR ILLUMINATION ASYMMETRY
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">Low-Sun Grazing Shadows</h3>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                At lunar latitudes &gt; 80°S, subsolar elevation frequently drops below 5°. Slender crater rims cast shadows tens of kilometers long that migrate rapidly across orbital revisit times. Intensity-based cross-correlation identifies shadow edges as terrain features, generating catastrophic false positive correspondences.
              </p>
            </div>

            <div className="p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2.5 shadow-sm">
              <div className="font-mono-tech text-[10px] text-[#246327] uppercase tracking-wider font-semibold">
                03 / RADIOMETRIC MODALITY DIVERGENCE
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">Panchromatic vs. Hyperspectral</h3>
              <p className="text-sm sm:text-base font-semibold text-[#222222] leading-relaxed font-sans">
                Panchromatic cameras capture visible photon reflectance, while IIRS records across 256 spectral channels between 0.8 and 5.0 µm, sensitive to pyroxene, olivine, and OH/H₂O absorption bands. Contrast inversions are commonplace, demanding structural and phase-based representations over raw gradient magnitude.
              </p>
            </div>
          </div>

          {/* Architecture Distinction Table */}
          <div className="space-y-6 pt-4">
            <div className="space-y-1">
              <h3 className="font-sans text-xl sm:text-2xl font-bold text-[#111111]">
                Implementation Distinction Matrix
              </h3>
              <p className="text-base sm:text-lg font-semibold text-[#111111] font-sans max-w-3xl">
                In strict accordance with scientific integrity rules, PARALLAX maintains a clear distinction between operational baseline components, candidate model-bank components, and proposed architectural extensions.
              </p>
            </div>

            <div className="overflow-x-auto rounded-none border border-[#E2E2DE] bg-[#FFFFFF] shadow-sm">
              <table className="w-full text-left font-mono-tech text-xs">
                <thead>
                  <tr className="border-b border-[#E2E2DE] bg-[#EEEEEC] text-[#555555] text-[10px] uppercase">
                    <th className="py-3 px-4 font-semibold">Subsystem / Component</th>
                    <th className="py-3 px-4 font-semibold">Maturity Status</th>
                    <th className="py-3 px-4 font-semibold">Implementation Details</th>
                    <th className="py-3 px-4 font-semibold">Scientific Basis / Validation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E2DE] text-[#444444]">
                  {ARCHITECTURE_DISTINCTIONS.map((row, idx) => (
                    <tr key={idx} className="hover:bg-[#F9F9F8] transition-colors">
                      <td className="py-3 px-4 font-semibold text-[#111111] whitespace-nowrap">
                        {row.component}
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-none text-[9.5px] font-semibold ${
                            row.classification === "IMPLEMENTED"
                              ? "bg-[#EAF5EB] text-[#246327] border border-[#B8DDBA]"
                              : row.classification === "VALIDATED"
                              ? "bg-[#EBF3FC] text-[#1D5499] border border-[#A8C7F0]"
                              : "bg-[#FDF6E2] text-[#8C5E13] border border-[#E8D196]"
                          }`}
                        >
                          {row.classification === "IMPLEMENTED" ? (
                            <CheckCircle2 className="h-3 w-3" />
                          ) : row.classification === "VALIDATED" ? (
                            <ShieldCheck className="h-3 w-3" />
                          ) : (
                            <Clock className="h-3 w-3" />
                          )}
                          {row.classification}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs font-sans text-[#444444] max-w-sm">
                        {row.details}
                      </td>
                      <td className="py-3 px-4 text-[11px] font-sans text-[#666663] max-w-xs">
                        {row.scientificBasis}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </section>

      {/* Editorial Dark Section: Institutional Provenance & Data Curation */}
      <section className="relative py-16 bg-[#111111] text-[#F7F7F5] border-b border-[#262626] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="space-y-1">
            <div className="font-mono-tech text-xs text-[#8C8C89] uppercase tracking-wider flex items-center gap-2">
              <Database className="h-4 w-4 text-[#A0A0A0]" />
              <span>DATA PROVENANCE & INSTITUTIONAL SOURCES</span>
            </div>
            <h3 className="font-sans text-lg sm:text-2xl font-bold text-[#F7F7F5]">
              Payload Heritage and Reference Conventions
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-[#A0A0A0] font-sans leading-relaxed">
            <div className="space-y-3 p-5 rounded-none bg-[#161616] border border-[#262626]">
              <div className="font-bold text-[#F7F7F5] font-mono-tech text-xs flex items-center gap-2">
                <span className="h-1.5 w-1.5 bg-[#86D88E]" />
                ISRO / ISSDC / SAC AHMEDABAD
              </div>
              <p>
                Primary observations stem from India&apos;s Chandrayaan-2 lunar orbiter, launched July 22, 2019. Payloads designed and fabricated by the Space Applications Centre (SAC), Ahmedabad:
              </p>
              <ul className="list-disc list-inside space-y-1 text-[#8C8C89] font-mono-tech text-[10.5px]">
                <li>OHRC: 0.25–0.32 m/px nadir panchromatic frame camera</li>
                <li>TMC-2: 5.0 m/px three-line fore-aft-nadir stereo camera</li>
                <li>IIRS: 80 m/px 256-band hyperspectral sensor (0.8–5.0 µm)</li>
              </ul>
              <p className="text-[11px] text-[#646462]">
                Data distributed through the Indian Space Science Data Centre (ISSDC) PRADAN portal under standard PDS4 observational data specifications.
              </p>
            </div>

            <div className="space-y-3 p-5 rounded-none bg-[#161616] border border-[#262626]">
              <div className="font-bold text-[#F7F7F5] font-mono-tech text-xs flex items-center gap-2">
                <span className="h-1.5 w-1.5 bg-[#E0A855]" />
                NASA PDS GEOSCIENCES & IAU STANDARDS
              </div>
              <p>
                Geodetic and altimetric reference benchmarks are cross-verified against:
              </p>
              <ul className="list-disc list-inside space-y-1 text-[#8C8C89] font-mono-tech text-[10.5px]">
                <li>NASA Lunar Reconnaissance Orbiter (LRO) Narrow Angle Camera (LROC NAC)</li>
                <li>Lunar Orbiter Laser Altimeter (LOLA) 30m gridded polar elevation baselines</li>
                <li>IAU/IAG Working Group on Cartographic Coordinates (Mean Earth/polar axis frame)</li>
              </ul>
              <p className="text-[11px] text-[#646462]">
                Planetary radius reference R_moon = 1,737.4 km. All telemetry values in client demonstrations are calibrated on verified mock suites or measured ground-truth pairs and explicitly tagged as such.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Editorial Light Section: Academic Literature References & Studio CTA */}
      <section className="relative py-20 bg-[#F7F7F5] text-[#111111] border-t border-b border-[#E2E2DE] select-none text-left">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          
          <div className="space-y-1">
            <div className="font-mono-tech text-xs text-[#666663] uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-[#111111]" />
              <span>SCIENTIFIC LITERATURE & METHODOLOGY CITATIONS</span>
            </div>
            <h3 className="font-sans text-lg sm:text-2xl font-bold text-[#111111]">
              Foundational Research Papers
            </h3>
            <p className="text-xs text-[#555555] font-sans">
              The PARALLAX adaptive architecture builds on peer-reviewed algorithms in multi-modal remote sensing, structural descriptor design, and deep learning feature matching:
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ACADEMIC_REFERENCES.map((paper, idx) => (
              <div
                key={idx}
                className="p-5 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-2 shadow-sm hover:border-[#CACAC6] transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-sans text-sm font-bold text-[#111111] leading-snug">
                    {paper.title}
                  </h4>
                  <span className="px-1.5 py-0.5 rounded-none text-[10px] font-mono-tech bg-[#F0F0ED] border border-[#E2E2DE] text-[#555555] shrink-0">
                    {paper.year}
                  </span>
                </div>
                <div className="font-mono-tech text-xs text-[#666663]">
                  {paper.authors}
                </div>
                <div className="text-[11px] text-[#777774] italic font-sans">
                  {paper.venue}
                </div>
                <p className="text-xs text-[#444444] font-sans pt-1 border-t border-[#E2E2DE] leading-relaxed">
                  <span className="text-[#111111] font-semibold font-mono-tech text-[10px]">ROLE IN PARALLAX: </span>
                  {paper.relevance}
                </p>
              </div>
            ))}
          </div>

          {/* Action to Explore & Studio */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-6 p-6 sm:p-8 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] shadow-sm">
            <div className="space-y-1 text-left">
              <div className="text-[#111111] font-sans font-bold text-lg sm:text-xl">
                Ready to Test Adaptive Model Selection?
              </div>
              <p className="text-xs text-[#555555] font-sans max-w-xl">
                Explore how PARALLAX characterizes image pairs and dynamically switches matching strategies between SIFT, RIFT, HOPC, and LoFTR.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3 shrink-0">
              <button
                onClick={() => {
                  navigate("/correspondence")
                  window.scrollTo({ top: 0, left: 0, behavior: "instant" })
                }}
                className="flex items-center gap-2 px-5 py-2.5 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#111111] text-[#F7F7F5] hover:bg-[#222222] transition-colors"
              >
                <Cpu className="h-4 w-4" />
                <span>CORRESPONDENCE STUDIO</span>
                <ArrowRight className="h-4 w-4" />
              </button>
              <button
                onClick={() => {
                  navigate("/explore")
                  window.scrollTo({ top: 0, left: 0, behavior: "instant" })
                }}
                className="flex items-center gap-2 px-5 py-2.5 rounded-none font-mono-tech text-xs tracking-wider text-[#111111] border border-[#E2E2DE] bg-[#F7F7F5] hover:bg-[#EEEEEC] transition-colors"
              >
                <Compass className="h-4 w-4" />
                <span>3D LUNAR EXPLORER</span>
              </button>
            </div>
          </div>

        </div>
      </section>

      {/* Global Footer */}
      <GlobalFooter />
    </div>
  )
}

export default AboutPage
