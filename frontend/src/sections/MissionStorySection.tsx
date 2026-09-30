import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useParallax } from '../state/ParallaxContext';

export const MissionStorySection: React.FC = () => {
  const { setCursorLabel } = useParallax();
  const navigate = useNavigate();

  const scrollToHero = () => {
    navigate('/');
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  };

  const scrollToCorrespondence = () => {
    navigate('/correspondence');
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  };

  return (
    <section id="mission" className="relative py-16 bg-[#111111] border-b border-[#262626]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-12">
        
        {/* Storytelling Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          
          <div className="lg:col-span-6 space-y-5">
            <h2 className="font-sans text-xl sm:text-3xl font-extrabold tracking-tight text-[#F7F7F5] uppercase">
              The Cross-Instrument Challenge
            </h2>

            <div className="space-y-4 text-sm sm:text-base font-medium text-[#D4D4D0] leading-relaxed font-sans">
              <p>
                India&apos;s Chandrayaan-2 orbiter carries some of the most sophisticated planetary cameras in human history. Its Orbiter High Resolution Camera (OHRC) captures features as small as 25 cm, while the Terrain Mapping Camera-2 (TMC-2) generates continuous 3D digital elevation models, and the Imaging Infrared Spectrometer (IIRS) maps water ice and lunar minerals.
              </p>
              <p>
                However, each sensor operates in a different orbit pass, with differing solar angles, resolutions, and spectral sensitivities. Without automated subpixel co-registration, scientific findings from OHRC cannot be reliably projected onto TMC-2 elevation models or combined with IIRS mineral maps.
              </p>
              <p className="font-bold text-[#FFFFFF]">
                PARALLAX bridges this gap through pair-aware adaptive correspondence—characterizing difficulty across scale, illumination, and radiometric modalities, then routing each observation pair to the optimal registration strategy.
              </p>
            </div>
          </div>

          <div className="lg:col-span-6 space-y-4">
            <div className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1.5">
              <div className="font-mono-tech text-[10px] text-[#A0A0A0] uppercase font-semibold">01 / UNIFIED LUNAR CARTOGRAPHY</div>
              <h3 className="font-sans text-lg font-bold text-[#F7F7F5]">Subpixel Georeferencing</h3>
              <p className="text-sm sm:text-base font-medium text-[#D4D4D0] leading-relaxed font-sans">
                Reconciles 0.25 m/px boulders with 5.0 m/px regional elevation baselines, enabling precision hazard avoidance for landing craft.
              </p>
            </div>

            <div className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1.5">
              <div className="font-mono-tech text-[10px] text-[#E0A855] uppercase font-semibold">02 / VOLATILE ICE LOCALIZATION</div>
              <h3 className="font-sans text-lg font-bold text-[#F7F7F5]">Permanently Shadowed Regions (PSR)</h3>
              <p className="text-sm sm:text-base font-medium text-[#D4D4D0] leading-relaxed font-sans">
                Aligns visible micro-topography with 256-channel infrared water absorption features inside dark polar craters like Faustini and Shackleton.
              </p>
            </div>

            <div className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1.5">
              <div className="font-mono-tech text-[10px] text-[#86D88E] uppercase font-semibold">03 / OPEN SCIENCE ARCHITECTURE</div>
              <h3 className="font-sans text-lg font-bold text-[#F7F7F5]">Live Backend Readiness</h3>
              <p className="text-sm sm:text-base font-medium text-[#D4D4D0] leading-relaxed font-sans">
                Designed to interface seamlessly with Python/OpenCV/PyTorch server pipelines, with full transparency between verified demo datasets and live telemetry.
              </p>
            </div>
          </div>

        </div>

        {/* Editorial Architecture Statement */}
        <div className="p-6 sm:p-8 rounded-none sm:rounded-sm bg-[#161616] border border-[#262626] text-left space-y-4">
          <div className="border-b border-[#262626] pb-4">
            <h3 className="font-sans text-xl sm:text-2xl font-bold tracking-tight text-[#F7F7F5]">
              Pair-Aware Adaptive Registration Architecture
            </h3>
          </div>

          <p className="text-sm sm:text-base font-medium text-[#D4D4D0] font-sans leading-relaxed max-w-3xl">
            PARALLAX does not force every image pair through a rigid pipeline. By characterizing scale ratios, illumination disparity, and modality gaps upfront, the platform selects and parameterizes the exact algorithm required for convergence—from traditional SIFT with ANMS to deep structural RIFT and LoFTR dense transformers.
          </p>
        </div>

      </div>
    </section>
  );
};
