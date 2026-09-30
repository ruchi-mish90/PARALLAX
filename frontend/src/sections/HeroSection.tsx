import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useParallax } from '../state/ParallaxContext';
import { Compass } from 'lucide-react';

export const HeroSection: React.FC = () => {
  const { setCursorLabel, explainMode } = useParallax();
  const navigate = useNavigate();

  const handleExploreClick = () => {
    navigate('/explore');
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  };

  return (
    <section id="hero" className="relative h-screen w-full flex flex-col justify-between overflow-hidden bg-[#111111] select-none text-left">
      
      {/* BACKGROUND VIDEO LAYER */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <video
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          className="w-full h-full object-cover scale-[1.28] origin-[40%_35%] opacity-90 filter brightness-100 contrast-105"
        >
          <source src="/hero-background.mp4" type="video/mp4" />
        </video>
      </div>

      {/* RESTRAINED EDITORIAL FADES (Crisp near-black #111111 transitions) */}
      <div className="absolute top-0 left-0 right-0 h-36 z-[1] pointer-events-none bg-gradient-to-b from-[#111111] via-[#111111]/40 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-44 z-[1] pointer-events-none bg-gradient-to-t from-[#111111] via-[#111111]/60 to-transparent" />

      {/* Seamless Floating Right-Aligned Editorial Typography Layer */}
      <div className="relative z-20 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 my-auto flex justify-end">
        <div className="w-full max-w-xl lg:max-w-2xl text-left sm:text-right space-y-6 pointer-events-auto">
          
          {/* Master Single Headline: Clean, Bold, Authoritative Inter Headline */}
          <h1 className="font-sans text-6xl sm:text-7xl lg:text-8xl font-black tracking-tight text-[#FFFFFF] uppercase leading-none drop-shadow-[0_4px_24px_rgba(0,0,0,0.9)]">
            PARALLAX
          </h1>

          {/* Sub-Context: Clean, Elegant, Legible without being overly chunky/bold */}
          <p className="text-lg sm:text-xl lg:text-2xl font-normal sm:font-medium text-[#EDEDEA] leading-relaxed drop-shadow-[0_2px_12px_rgba(0,0,0,0.95)] max-w-xl sm:ml-auto">
            {explainMode
              ? 'Adapts the registration strategy to each lunar image pair instead of forcing every pair through the same matcher.'
              : 'Adaptive multi-modal registration for reliable correspondence across heterogeneous Chandrayaan-2 lunar observations.'}
          </p>



          {/* Action Controls: Primary CTA & Secondary CTA */}
          <div className="flex flex-wrap items-center sm:justify-end gap-3 pt-2">
            <button
              onClick={() => {
                navigate('/correspondence');
                window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
              }}
              onMouseEnter={() => setCursorLabel('OPEN CORRESPONDENCE STUDIO')}
              onMouseLeave={() => setCursorLabel('')}
              className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#F7F7F5] text-[#111111] hover:bg-[#FFFFFF] transition-colors shadow-lg"
            >
              <Compass className="h-4 w-4" />
              <span>CORRESPONDENCE STUDIO</span>
            </button>

            <button
              onClick={handleExploreClick}
              onMouseEnter={() => setCursorLabel('TARGET LUNAR SITES')}
              onMouseLeave={() => setCursorLabel('')}
              className="flex items-center justify-center gap-2 px-5 py-3.5 rounded-none font-mono-tech text-xs tracking-wider text-[#F7F7F5] border border-[#333333] bg-[#161616]/90 hover:bg-[#222222] transition-colors"
            >
              <span>EXPLORE THE MOON</span>
            </button>
          </div>

        </div>
      </div>
    </section>
  );
};
