import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useParallax } from '../state/ParallaxContext';
import { LUNAR_REGIONS } from '../data/regionsData';
import { MoonCanvas } from '../components/three/MoonCanvas';
import { Compass, Crosshair, Sun, Mountain } from 'lucide-react';

export const MoonExplorerSection: React.FC = () => {
  const { selectedRegion, setSelectedRegion, setCursorLabel, explainMode } = useParallax();
  const navigate = useNavigate();

  const handleAnalyze = () => {
    navigate('/correspondence');
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  };

  return (
    <section id="explore" className="relative py-16 border-b border-[#262626] bg-[#111111] overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Region Target Bar Pills */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {LUNAR_REGIONS.map((region) => {
            const isSelected = selectedRegion.id === region.id;
            return (
              <button
                key={region.id}
                onClick={() => setSelectedRegion(region)}
                onMouseEnter={() => setCursorLabel(`TARGET ${region.name}`)}
                onMouseLeave={() => setCursorLabel('')}
                className={`p-3.5 text-left border transition-colors rounded-none sm:rounded-sm ${
                  isSelected
                    ? 'bg-[#1C1C1C] border-[#F7F7F5] text-[#F7F7F5]'
                    : 'bg-[#161616] border-[#262626] text-[#8C8C89] hover:text-[#F7F7F5] hover:border-[#383838]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-sans text-sm font-bold text-[#F7F7F5]">
                    {region.name}
                  </span>
                  <Crosshair className={`h-3.5 w-3.5 ${isSelected ? 'text-[#F7F7F5]' : 'text-[#646462]'}`} />
                </div>
                <div className="font-mono-tech text-[10px] text-[#8C8C89] mt-1">
                  {region.latDisplay} • {region.longDisplay}
                </div>
              </button>
            );
          })}
        </div>

        {/* Widescreen Interactive Explorer Console */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* 3D Lunar Globe Stage */}
          <div className="lg:col-span-8 relative min-h-[460px] rounded-none sm:rounded-sm overflow-hidden border border-[#262626] bg-[#161616]">
            <MoonCanvas
              onSelectRegion={(reg) => setSelectedRegion(reg)}
              className="w-full h-full min-h-[460px]"
            />
            {/* HUD Corner Reticles */}
            <div className="absolute top-4 left-4 font-mono-tech text-[10px] text-[#F7F7F5] bg-[#111111]/90 px-3 py-1 rounded-none border border-[#262626]">
              SELENOGRAPHIC RETICLE: {selectedRegion.name.toUpperCase()}
            </div>

            <div className="absolute bottom-4 right-4 font-mono-tech text-[10px] text-[#8C8C89] bg-[#111111]/90 px-3 py-1 rounded-none border border-[#262626]">
              ROTATION: INTERACTIVE ORBITAL CONTROL
            </div>
          </div>

          {/* Active Target Telemetry Panel */}
          <div className="lg:col-span-4 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] p-6 flex flex-col justify-between text-left space-y-5">
            <div className="space-y-4">
              <div className="border-b border-[#262626] pb-3">
                <span className="font-mono-tech text-[10px] text-[#8C8C89] uppercase tracking-wider block">
                  SELECTED OBSERVATION SITE
                </span>
                <h3 className="font-sans text-xl font-bold text-[#F7F7F5] mt-1">
                  {selectedRegion.name}
                </h3>
                <p className="text-xs text-[#8C8C89] font-mono-tech mt-0.5">
                  {selectedRegion.subTitle}
                </p>
              </div>

              {/* Coordinates */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono-tech">
                <div className="p-2.5 rounded-none bg-[#111111] border border-[#262626]">
                  <span className="text-[#646462] block text-[9.5px] uppercase">LATITUDE</span>
                  <span className="text-[#F7F7F5] font-semibold">{selectedRegion.latDisplay}</span>
                </div>
                <div className="p-2.5 rounded-none bg-[#111111] border border-[#262626]">
                  <span className="text-[#646462] block text-[9.5px] uppercase">LONGITUDE</span>
                  <span className="text-[#F7F7F5] font-semibold">{selectedRegion.longDisplay}</span>
                </div>
              </div>

              {/* Topographic Relief & Illumination */}
              <div className="space-y-1.5 text-xs text-[#A0A0A0]">
                <div className="flex items-center gap-2 p-2 rounded-none bg-[#111111] border border-[#262626]">
                  <Mountain className="h-3.5 w-3.5 text-[#8C8C89] shrink-0" />
                  <span>Relief: {selectedRegion.elevationProfile}</span>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-none bg-[#111111] border border-[#262626]">
                  <Sun className="h-3.5 w-3.5 text-[#E0A855] shrink-0" />
                  <span>Illumination: {selectedRegion.lightingCondition}</span>
                </div>
              </div>

              <p className="text-sm sm:text-base font-medium text-[#D4D4D0] leading-relaxed pt-1 font-sans">
                {selectedRegion.featureDescription}
              </p>

              {/* Target Difficulty Preview */}
              <div className="p-3 rounded-none bg-[#111111] border border-[#262626] space-y-1 text-left font-mono-tech">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-[#8C8C89] uppercase">REGISTRATION DIFFICULTY:</span>
                  <span className={`px-2 py-0.5 text-[9.5px] font-semibold ${
                    selectedRegion.id === 'faustini-crater' || selectedRegion.id === 'shackleton-connecting-ridge'
                      ? 'bg-[#2E2211] text-[#E0A855] border border-[#5E4218]'
                      : 'bg-[#1A2E1C] text-[#86D88E] border border-[#2E5E32]'
                  }`}>
                    {selectedRegion.id === 'faustini-crater' || selectedRegion.id === 'shackleton-connecting-ridge' ? 'HIGH (LOW SUN)' : 'MODERATE'}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-[#CCCCCC] font-sans leading-normal">
                  {selectedRegion.id === 'faustini-crater'
                    ? 'Permanent shadow boundaries require RIFT phase congruency or LoFTR dense matching.'
                    : 'High contrast topography suitable for SIFT baseline or learned LightGlue graph matching.'}
                </p>
              </div>
            </div>

            {/* Launch Correspondence Actions */}
            <div className="space-y-3 pt-3 border-t border-[#262626]">
              {/* Region-to-Observation Product Discovery */}
              <div className="space-y-2">
                <div className="flex items-center justify-between font-mono-tech text-[10px] text-[#8C8C89]">
                  <span className="uppercase tracking-wider">AVAILABLE OBSERVATIONS ({selectedRegion.name.toUpperCase()}):</span>
                  <span className="text-[#86D88E] font-semibold">CATALOGUE MATCH</span>
                </div>
                <div className="grid grid-cols-3 gap-1.5 font-mono-tech text-[10px]">
                  {selectedRegion.availableInstruments.map(inst => (
                    <div key={inst} className="p-1.5 bg-[#111111] border border-[#262626] text-center space-y-0.5">
                      <div className="text-[#F7F7F5] font-bold">{inst}</div>
                      <div className="text-[9px] text-[#8C8C89]">
                        {inst === 'OHRC' ? '0.25 m/px' : inst === 'TMC-2' ? '5.0 m/px' : '80 m/px'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                <button
                  onClick={() => {
                    navigate('/instruments');
                    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
                  }}
                  className="flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-none font-mono-tech text-xs tracking-wider text-[#A0A0A0] hover:text-[#F7F7F5] border border-[#262626] hover:border-[#383838] bg-[#111111] hover:bg-[#161616] transition-colors"
                >
                  <span>VIEW SENSORS</span>
                </button>
                <button
                  onClick={handleAnalyze}
                  onMouseEnter={() => setCursorLabel(`REGISTER ${selectedRegion.name.toUpperCase()}`)}
                  onMouseLeave={() => setCursorLabel('')}
                  className="flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-none font-mono-tech text-xs tracking-wider font-bold bg-[#F7F7F5] text-[#111111] hover:bg-[#FFFFFF] transition-colors"
                >
                  <span>CREATE PAIR →</span>
                </button>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
};
