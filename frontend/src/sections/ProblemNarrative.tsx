import React from 'react';
import { useParallax } from '../state/ParallaxContext';
import { Eye, Layers, Sun, Scale } from 'lucide-react';

export const ProblemNarrative: React.FC = () => {
  const { explainMode, setCursorLabel } = useParallax();

  const challenges = [
    {
      id: 'scale',
      title: explainMode ? 'Scale Octave Disparity' : 'Large Spatial Scale Differences',
      desc: explainMode 
        ? 'OHRC zooms in to ~0.25 m/px to see individual boulders, while TMC-2 views at 5 m/px and IIRS at 80 m/px across a 320:1 scale gap.'
        : 'OHRC (~0.25–0.32 m/px), TMC-2 (~5 m/px), and IIRS (~80 m/px) observe at vastly different ground sampling distances, causing severe feature descriptor aliasing.',
      icon: <Scale className="h-4 w-4 text-[#111111]" />,
      tag: '0.25 m vs 5 m vs 80 m'
    },
    {
      id: 'illumination',
      title: explainMode ? 'Shifting Polar Shadows' : 'Illumination & Shadow Variation',
      desc: explainMode
        ? 'Because the Sun stays low on the polar horizon (1°–5°), crater rim shadows stretch by hundreds of meters between orbits, deceiving naive matchers.'
        : 'Low solar elevation angles in polar and high-latitude scenes cause non-linear shadow migration, altering apparent surface morphology.',
      icon: <Sun className="h-4 w-4 text-[#966316]" />,
      tag: 'Low-Sun Horizon (0.8°–5°)'
    },
    {
      id: 'modality',
      title: explainMode ? 'Different Camera Sensors' : 'Different Radiometric Modalities',
      desc: explainMode
        ? 'One sensor measures visible black-and-white sunlight reflection, while another records 256 bands of invisible infrared absorption and minerals.'
        : 'Optical panchromatic detectors and 256-band hyperspectral infrared observations do not share identical radiometric or gradient appearance.',
      icon: <Layers className="h-4 w-4 text-[#444444]" />,
      tag: 'Visible vs 256-Band SWIR'
    }
  ];

  return (
    <section id="problem" className="relative py-24 bg-[#F7F7F5] text-[#111111] border-y border-[#E2E2DE]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Editorial Section Header */}
        <div className="max-w-3xl space-y-4 text-left">
          <h2 className="font-sans text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-[#111111] leading-tight">
            THE MOON HAS BEEN OBSERVED <br />
            <span className="text-[#666666]">THROUGH DIFFERENT EYES.</span>
          </h2>

          <p className="text-base sm:text-lg font-semibold text-[#111111] leading-relaxed font-sans">
            {explainMode
              ? 'When Chandrayaan-2 orbits the Moon, its cameras take photos at vastly different resolutions, sun angles, and wavelengths. Standard image matching fails because the photos look completely different even when pointing at the same spot.'
              : 'Establishing automated point correspondence across heterogeneous remote-sensing payloads is hindered by radiometric disparities, severe shadow morphology transitions, and extreme scale octave gaps.'}
          </p>
        </div>

        {/* 3 Challenge Pillars (Precision White Cards on #F7F7F5 surface) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-12 text-left">
          {challenges.map((c) => (
            <div
              key={c.id}
              onMouseEnter={() => setCursorLabel(`INSPECT ${c.id.toUpperCase()}`)}
              onMouseLeave={() => setCursorLabel('')}
              className="bg-[#FFFFFF] rounded-none sm:rounded-sm p-6 border border-[#E2E2DE] hover:border-[#BFBFB8] transition-colors group flex flex-col justify-between shadow-[0_1px_3px_rgba(0,0,0,0.03)]"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="p-2 rounded-none bg-[#F7F7F5] border border-[#E2E2DE]">
                    {c.icon}
                  </div>
                  <span className="font-mono-tech text-[10px] px-2 py-0.5 rounded-none bg-[#F7F7F5] border border-[#E2E2DE] text-[#666666] font-semibold">
                    {c.tag}
                  </span>
                </div>

                <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
                  {c.title}
                </h3>

                <p className="text-sm sm:text-base font-medium text-[#222222] font-sans leading-relaxed">
                  {c.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* The Core PARALLAX Insight Callout (Editorial White Document Box) */}
        <div className="mt-12 p-8 rounded-none sm:rounded-sm bg-[#FFFFFF] border border-[#D4D4D0] text-left space-y-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
          <div className="flex items-center justify-between border-b border-[#EAEAE6] pb-3">
            <span className="font-mono-tech text-[10px] tracking-widest uppercase text-[#666666] font-semibold">
              CORE PARALLAX TECHNICAL PRINCIPLE
            </span>
            <span className="font-mono-tech text-[10px] text-[#246327] font-semibold">
              SPECIFICATION ARCHITECTURE
            </span>
          </div>

          <h3 className="font-sans text-xl sm:text-2xl font-bold text-[#111111] uppercase tracking-tight">
            &ldquo;DO NOT FORCE EVERY PAIR THROUGH ONE MATCHER.&rdquo;
          </h3>

          <p className="text-base sm:text-lg font-semibold text-[#111111] font-sans max-w-3xl leading-relaxed">
            First form and characterize the pair. Then rank and select an appropriate correspondence strategy. Finally verify geometry, enforce spatial distribution, and quantify quality and uncertainty.
          </p>

          <div className="pt-2 border-t border-[#EAEAE6] flex items-center gap-2 font-mono-tech text-xs sm:text-sm text-[#8C5E13] font-semibold">
            <span className="h-1.5 w-1.5 bg-[#8C5E13]" />
            <span>PRIMARY INVARIANCE: Different image pair → different difficulty → different suitable correspondence strategy.</span>
          </div>
        </div>

      </div>
    </section>
  );
};
