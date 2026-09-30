import React, { useState } from 'react';
import { CHANDRAYAAN_INSTRUMENTS } from '../data/instrumentsData';
import { InstrumentId } from '../types/instruments';
import { useParallax } from '../state/ParallaxContext';
import { Camera, Sparkles } from 'lucide-react';

export const InstrumentLabSection: React.FC = () => {
  const { setSourceInstrument, setTargetInstrument, setCursorLabel, explainMode } = useParallax();
  const [selectedInst, setSelectedInst] = useState<InstrumentId>('OHRC');

  const activeSpec = CHANDRAYAAN_INSTRUMENTS[selectedInst];

  return (
    <section id="instruments" className="relative py-24 bg-space-900/40 border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left">
        
        {/* 3 Payload Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(Object.keys(CHANDRAYAAN_INSTRUMENTS) as InstrumentId[]).map((id) => {
            const inst = CHANDRAYAAN_INSTRUMENTS[id];
            const isSelected = selectedInst === id;

            return (
              <button
                key={id}
                onClick={() => setSelectedInst(id)}
                onMouseEnter={() => setCursorLabel(`INSPECT ${id}`)}
                onMouseLeave={() => setCursorLabel('')}
                className={`p-6 rounded-xl border text-left transition-all ${
                  isSelected
                    ? 'bg-space-850 border-cyan-accent shadow-[0_0_25px_rgba(100,210,255,0.15)] scale-[1.01]'
                    : 'bg-space-950 border-white/10 text-lunar-400 hover:text-white hover:border-white/25 hover:bg-space-900/60'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="font-display-tech text-2xl font-bold text-white">
                    {inst.name}
                  </span>
                  <span className={`px-2 py-0.5 rounded font-mono-tech text-[10px] border ${
                    id === 'OHRC' ? 'text-cyan-accent border-cyan-accent/30 bg-cyan-accent/10' :
                    id === 'TMC-2' ? 'text-amber-400 border-amber-400/30 bg-amber-400/10' :
                    'text-azure-accent border-azure-accent/30 bg-azure-accent/10'
                  }`}>
                    {inst.groundResolution.split(' ')[0]} {inst.groundResolution.split(' ')[1]}
                  </span>
                </div>

                <div className="font-display-tech text-base font-semibold text-white mb-2">
                  {inst.fullName}
                </div>

                <p className="text-sm font-medium text-lunar-200 line-clamp-3 leading-relaxed mb-4">
                  {inst.purpose}
                </p>

                <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[11px] font-mono-tech text-lunar-500">
                  <span>{inst.spectralBand.split('(')[0]}</span>
                  <span className="text-cyan-accent font-semibold">SELECT DOSSIER →</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Deep Dive Dossier on Active Instrument */}
        <div className="mt-8 hud-panel-active rounded-xl p-8 border border-white/15 space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 border-b border-white/10 pb-6">
            <div>
              <div className="font-mono-tech text-xs text-cyan-accent uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="h-3.5 w-3.5" />
                <span>PAYLOAD PROFILE DOSSIER</span>
              </div>
              <h3 className="font-display-tech text-3xl font-bold text-white mt-1">
                {activeSpec.fullName} ({activeSpec.name})
              </h3>
              <p className="text-xs text-lunar-400 mt-0.5">
                {activeSpec.payloadType} • CHANDRAYAAN-2 SCIENCE EXPERIMENT
              </p>
            </div>

            {/* Quick Pair Assign Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSourceInstrument(activeSpec.id)}
                className="px-3.5 py-2 rounded bg-cyan-accent/15 border border-cyan-accent/50 text-cyan-accent font-mono-tech text-xs hover:bg-cyan-accent hover:text-space-950 transition-all font-semibold"
              >
                SET AS SOURCE (A)
              </button>
              <button
                onClick={() => setTargetInstrument(activeSpec.id)}
                className="px-3.5 py-2 rounded bg-amber-400/15 border border-amber-400/50 text-amber-400 font-mono-tech text-xs hover:bg-amber-400 hover:text-space-950 transition-all font-semibold"
              >
                SET AS TARGET (B)
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-space-950 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono-tech text-lunar-500 uppercase">GROUND RESOLUTION</div>
              <div className="font-mono-tech text-sm font-bold text-white">{activeSpec.groundResolution}</div>
            </div>
            <div className="p-4 rounded-lg bg-space-950 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono-tech text-lunar-500 uppercase">MODALITY & BAND</div>
              <div className="font-mono-tech text-sm font-bold text-cyan-accent">{activeSpec.modality}</div>
            </div>
            <div className="p-4 rounded-lg bg-space-950 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono-tech text-lunar-500 uppercase">IMAGING SWATH</div>
              <div className="font-mono-tech text-sm font-bold text-white">{activeSpec.swathWidth}</div>
            </div>
            <div className="p-4 rounded-lg bg-space-950 border border-white/5 space-y-1">
              <div className="text-[10px] font-mono-tech text-lunar-500 uppercase">DETECTOR TYPE</div>
              <div className="font-mono-tech text-xs font-bold text-amber-300">{activeSpec.sensorCharacteristics.detectorType}</div>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="font-mono-tech text-xs text-amber-400 uppercase tracking-wider font-semibold">
              REGISTRATION CHALLENGE IN PARALLAX:
            </h4>
            <p className="text-sm sm:text-base font-medium text-white leading-relaxed max-w-4xl bg-space-950/70 p-4 rounded-lg border border-amber-500/20">
              {activeSpec.registrationChallenge}
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-mono-tech text-xs text-lunar-400 uppercase tracking-wider font-semibold">
              PRIMARY SCIENTIFIC ROLE & SENSOR PHYSICS:
            </h4>
            <p className="text-sm sm:text-base font-medium text-lunar-200 leading-relaxed max-w-4xl bg-space-950/70 p-4 rounded-lg border border-white/5">
              {activeSpec.scientificRoleInParallax} {activeSpec.description}
            </p>
          </div>

          {/* Pre-launch Pair Difficulty Diagnosis Box */}
          <div className="p-5 rounded-xl border border-cyan-accent/30 bg-gradient-to-r from-space-950 via-space-900 to-space-950 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <span className="font-mono-tech text-xs text-cyan-accent font-bold uppercase tracking-wider">
                  ACTIVE PAIR CONFIGURATION:
                </span>
                <span className="font-mono-tech text-xs text-white px-2 py-0.5 rounded bg-space-950 border border-white/15">
                  {useParallax().sourceInstrument} (A) × {useParallax().targetInstrument} (B)
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono-tech text-[10px] text-lunar-400 uppercase">PAIR DIFFICULTY:</span>
                <span className={`px-2 py-0.5 rounded font-mono-tech text-xs font-bold uppercase ${
                  useParallax().pairCharacterization.overallDifficulty === 'Hard'
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    : useParallax().pairCharacterization.overallDifficulty === 'Medium'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-match-green/20 text-match-green border border-match-green/40'
                }`}>
                  {useParallax().pairCharacterization.overallDifficulty}
                </span>
              </div>
            </div>

            {/* Structured Pair Diagnostics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs font-mono-tech">
              <div className="p-2.5 rounded bg-space-950/80 border border-white/10 space-y-0.5">
                <span className="text-lunar-400 text-[10px] uppercase block">GSD GAP:</span>
                <span className="text-white font-bold">~{useParallax().pairCharacterization.scaleRatio.toFixed(0)}× ({useParallax().pairCharacterization.scaleRatioDisplay})</span>
              </div>
              <div className="p-2.5 rounded bg-space-950/80 border border-white/10 space-y-0.5">
                <span className="text-lunar-400 text-[10px] uppercase block">MODALITY:</span>
                <span className="text-cyan-accent font-bold">
                  {useParallax().sourceInstrument === 'IIRS' ? 'Hyperspectral' : 'Panchromatic'} → {useParallax().targetInstrument === 'IIRS' ? 'Hyperspectral' : useParallax().targetInstrument === 'TMC-2' ? 'Visible Stereo' : 'Panchromatic'}
                </span>
              </div>
              <div className="p-2.5 rounded bg-space-950/80 border border-white/10 space-y-0.5">
                <span className="text-lunar-400 text-[10px] uppercase block">RECOMMENDED ENGINE:</span>
                <span className="text-match-green font-bold truncate block">{useParallax().selectedModel.name.split('(')[0]}</span>
              </div>
            </div>

            <p className="text-sm font-medium text-white font-sans leading-relaxed">
              {useParallax().pairCharacterization.difficultyRationale}
            </p>

            {/* Extreme scale bridge candidate strategy notice */}
            {useParallax().pairCharacterization.suggestTmcBridge && (
              <div className="p-3 rounded bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs font-mono-tech space-y-1">
                <div className="font-bold flex items-center gap-1.5 text-amber-400">
                  <span>TMC-2 INTERMEDIATE BRIDGE (CANDIDATE / PROPOSED STRATEGY)</span>
                </div>
                <p className="text-[11px] font-sans text-lunar-200">
                  Extreme scale disparity ({useParallax().pairCharacterization.scaleRatioDisplay}). A two-hop bridge (OHRC → TMC-2 → IIRS) is proposed as a candidate strategy requiring multi-orbit empirical validation; not scientifically proven for every pair.
                </p>
              </div>
            )}

            <div className="flex items-center justify-between pt-1">
              <span className="font-mono-tech text-[11px] text-cyan-300">
                Engine Suitability Score: {useParallax().selectedModel.suitabilityScore}/100
              </span>
              <button
                onClick={() => {
                  window.location.href = '/correspondence';
                }}
                className="flex items-center gap-1.5 px-4 py-2 rounded bg-cyan-accent text-space-950 font-mono-tech text-xs font-bold hover:bg-cyan-300 transition-all hover:scale-105"
              >
                <span>OPEN IN STUDIO →</span>
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between text-xs font-mono-tech text-lunar-500 pt-2 border-t border-white/10">
            <span>CALIBRATION ARCHIVE ID: {activeSpec.acquisitionExample}</span>
            <span>RADIOMETRIC RANGE: {activeSpec.sensorCharacteristics.radiometricResolution}</span>
          </div>
        </div>

      </div>
    </section>
  );
};
