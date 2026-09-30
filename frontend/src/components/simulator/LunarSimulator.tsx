import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { AnimatedNumber } from '../common/AnimatedNumber';
import { ScrambleText } from '../common/ScrambleText';
import { 
  Sliders, 
  RefreshCw, 
  Sun, 
  Volume2, 
  ZoomIn, 
  Contrast, 
  GitBranch, 
  Star 
} from 'lucide-react';

export const LunarSimulator: React.FC = () => {
  const { 
    simulationParams, 
    updateSimulationParam, 
    resetSimulationParams, 
    pairCharacterization,
    modelCandidates,
    selectedModel,
    explainMode,
    setCursorLabel 
  } = useParallax();

  // Dynamic CSS filter styles representing the synthetic lunar sensor parameters
  const imageFilterStyle = {
    filter: `contrast(${100 + (simulationParams.claheClipLimit - 3) * 20}%) brightness(${
      80 + (simulationParams.sunElevationAngle / 80) * 40
    }%)`,
  };

  // Compute simulated quality gate outcome
  const getQualityGate = () => {
    if (simulationParams.spatialScaleRatio >= 22 || (simulationParams.sunElevationAngle < 8 && simulationParams.sensorNoiseSigma > 12)) {
      return { status: 'WARNING / HIGH UNCERTAINTY', color: 'text-[#E0A855] border-[#5E4218] bg-[#2E2211]', note: 'Extreme scale gap & shadow distortion; requires intermediate TMC-2 bridge.' };
    }
    if (simulationParams.sunElevationAngle < 10) {
      return { status: 'PHASE-CONGRUENCY LOCK', color: 'text-[#F7F7F5] border-[#383838] bg-[#1E1E1E]', note: 'Low-sun shadows detected. RIFT invariant structural matching maintains convergence.' };
    }
    return { status: 'QUALITY GATE PASSED (< 1.5 px)', color: 'text-[#86D88E] border-[#2E5E32] bg-[#1A2E1C]', note: 'Reprojection residuals well within sub-pixel registration bounds.' };
  };

  const qualityGate = getQualityGate();

  return (
    <div className="bg-[#161616] rounded-none sm:rounded-sm p-6 border border-[#262626] space-y-6 text-left">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#262626] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="h-4 w-4 text-[#A0A0A0]" />
            <span className="font-mono-tech text-xs text-[#8C8C89] tracking-wider uppercase font-semibold">
              <ScrambleText text={explainMode ? 'VIRTUAL SENSOR LABORATORY' : 'CONTROLLED MULTI-SENSOR STRESS BENCH'} />
            </span>
            <span className="px-2 py-0.5 rounded-none text-[10px] font-mono-tech bg-[#2E2211] border border-[#5E4218] text-[#E0A855] font-semibold">
              SYNTHETIC / SIMULATED
            </span>
          </div>
          <h3 className="font-sans text-xl font-bold text-[#F7F7F5] mt-1">
            <ScrambleText text={explainMode ? 'Synthetic Stress Testing & Model Reaction' : 'Synthetic Stress Testing: Adaptive Model Reaction'} />
          </h3>
          <p className="text-xs text-[#8C8C89] mt-1 max-w-3xl font-sans leading-relaxed">
            {explainMode
              ? 'SYNTHETIC / SIMULATED SANDBOX: Tweak parameters to test algorithm breaking points. This sandbox is for controlled demonstration, not actual Chandrayaan-2 flight measurements.'
              : 'SYNTHETIC / SIMULATED: Controlled stress-testing sandbox reproducing spaceborne CCD responses, shadow dynamics, and octave scale blur. Distinct from verified flight telemetry.'}
          </p>
        </div>

        <button
          onClick={resetSimulationParams}
          onMouseEnter={() => setCursorLabel('RESET PARAMETERS')}
          onMouseLeave={() => setCursorLabel('')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-none font-mono-tech text-xs text-[#8C8C89] hover:text-[#F7F7F5] border border-[#262626] bg-[#111111] hover:bg-[#1E1E1E] transition-colors self-start sm:self-auto shrink-0"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>RESET DEFAULTS</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        
        {/* Left: Synthetic Observation Preview Screen */}
        <div className="lg:col-span-7 relative min-h-[380px] rounded-none sm:rounded-sm overflow-hidden border border-[#262626] bg-[#111111] flex flex-col justify-between p-4">
          {/* Base Synthetic Crater Terrain */}
          <div 
            className="absolute inset-0 grayscale transition-all duration-200"
            style={{
              ...imageFilterStyle,
              backgroundImage: `radial-gradient(circle at ${simulationParams.sunAzimuthAngle / 3.6}% ${
                100 - simulationParams.sunElevationAngle
              }%, rgba(255,255,255,0.9) 0%, rgba(90,95,110,0.85) 45%, rgba(10,12,16,0.98) 95%)`
            }}
          />

          {/* Dynamic Shadow Layer influenced by Sun Elevation */}
          <div 
            className="absolute inset-0 pointer-events-none transition-opacity duration-200"
            style={{
              background: `linear-gradient(${simulationParams.sunAzimuthAngle}deg, rgba(0,0,0,${
                Math.max(0.2, (80 - simulationParams.sunElevationAngle) / 85)
              }) 0%, transparent 60%)`
            }}
          />

          {/* Sensor Noise Emulation Overlay */}
          <div 
            className="absolute inset-0 pointer-events-none opacity-30 mix-blend-screen"
            style={{
              backgroundImage: `repeating-radial-gradient(circle, rgba(255,255,255,0.15) 0, rgba(0,0,0,0.8) ${
                Math.max(1, simulationParams.sensorNoiseSigma)
              }px)`
            }}
          />

          {/* Reticle targeting HUD */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="h-40 w-40 rounded-none border border-dashed border-[#555555]/40 flex items-center justify-center">
              <div className="h-1.5 w-1.5 bg-[#F7F7F5]" />
            </div>
          </div>

          {/* Telemetry Overlay with animated live numbers */}
          <div className="relative z-10 font-mono-tech text-[10px] bg-[#111111]/90 px-3 py-2 rounded-none border border-[#262626] text-[#F7F7F5] space-y-1 self-start">
            <div className="flex justify-between gap-4">
              <span className="text-[#8C8C89]">SOLAR ELEVATION:</span>
              <strong className="text-[#F7F7F5]"><AnimatedNumber value={simulationParams.sunElevationAngle} suffix="°" duration={200} /></strong>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-[#8C8C89]">GSD SCALE DISPARITY:</span>
              <strong className="text-[#F7F7F5]"><AnimatedNumber value={simulationParams.spatialScaleRatio} suffix="×" duration={200} /></strong>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-[#8C8C89]">SENSOR NOISE (σ):</span>
              <strong className="text-[#F7F7F5]"><AnimatedNumber value={simulationParams.sensorNoiseSigma} decimals={1} duration={200} /></strong>
            </div>
          </div>

          <div className="relative z-10 flex items-center justify-between font-mono-tech text-[10px] bg-[#111111]/90 px-3 py-2 rounded-none border border-[#262626] text-[#8C8C89]">
            <span>SYNTHETIC SENSOR FEED</span>
            <span className="text-[#E0A855] font-semibold">[SIMULATED FOR EXPERIMENTATION]</span>
          </div>
        </div>

        {/* Right: Parameter Controls */}
        <div className="lg:col-span-5 space-y-3 flex flex-col justify-between">
          
          {/* Parameter 1: Sun Elevation */}
          <div className="space-y-1.5 p-3 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111]">
            <div className="flex items-center justify-between text-xs font-mono-tech">
              <div className="flex items-center gap-2 text-[#F7F7F5]">
                <Sun className="h-3.5 w-3.5 text-[#E0A855]" />
                <span><ScrambleText text={explainMode ? 'Sun Elevation Angle' : 'Solar Elevation Angle (β)'} /></span>
              </div>
              <span className="text-[#E0A855] font-semibold">
                <AnimatedNumber value={simulationParams.sunElevationAngle} suffix="°" duration={150} />
              </span>
            </div>
            <input
              type="range"
              min="5"
              max="80"
              value={simulationParams.sunElevationAngle}
              onChange={(e) => updateSimulationParam('sunElevationAngle', Number(e.target.value))}
              className="w-full accent-[#E0A855] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono-tech text-[#646462]">
              <span className="text-[#E57373]">5° (Extreme Polar Grazing)</span>
              <span>80° (High Sun)</span>
            </div>
          </div>

          {/* Parameter 2: Spatial Scale Ratio */}
          <div className="space-y-1.5 p-3 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111]">
            <div className="flex items-center justify-between text-xs font-mono-tech">
              <div className="flex items-center gap-2 text-[#F7F7F5]">
                <ZoomIn className="h-3.5 w-3.5 text-[#A0A0A0]" />
                <span><ScrambleText text={explainMode ? 'Scale / Zoom Gap' : 'Spatial Scale Ratio (GSD)'} /></span>
              </div>
              <span className="text-[#F7F7F5] font-semibold">
                <AnimatedNumber value={simulationParams.spatialScaleRatio} suffix="×" duration={150} />
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="25"
              value={simulationParams.spatialScaleRatio}
              onChange={(e) => updateSimulationParam('spatialScaleRatio', Number(e.target.value))}
              className="w-full accent-[#F7F7F5] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono-tech text-[#646462]">
              <span>1× (Identical Resolution)</span>
              <span className="text-[#F7F7F5]">20× (Nominal OHRC:TMC)</span>
              <span className="text-[#E57373]">25× (Extreme)</span>
            </div>
          </div>

          {/* Parameter 3: Sensor Noise */}
          <div className="space-y-1.5 p-3 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111]">
            <div className="flex items-center justify-between text-xs font-mono-tech">
              <div className="flex items-center gap-2 text-[#F7F7F5]">
                <Volume2 className="h-3.5 w-3.5 text-[#A0A0A0]" />
                <span><ScrambleText text={explainMode ? 'Detector Static / Noise' : 'Gaussian Noise Variance (σ)'} /></span>
              </div>
              <span className="text-[#F7F7F5] font-semibold">
                <AnimatedNumber value={simulationParams.sensorNoiseSigma} decimals={1} duration={150} />
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="20"
              step="0.5"
              value={simulationParams.sensorNoiseSigma}
              onChange={(e) => updateSimulationParam('sensorNoiseSigma', Number(e.target.value))}
              className="w-full accent-[#F7F7F5] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono-tech text-[#646462]">
              <span>0 (Pristine Detector)</span>
              <span className="text-[#E57373]">20 (High Dark-Current)</span>
            </div>
          </div>

          {/* Parameter 4: CLAHE Contrast */}
          <div className="space-y-1.5 p-3 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111]">
            <div className="flex items-center justify-between text-xs font-mono-tech">
              <div className="flex items-center gap-2 text-[#F7F7F5]">
                <Contrast className="h-3.5 w-3.5 text-[#86D88E]" />
                <span><ScrambleText text={explainMode ? 'Shadow Contrast (CLAHE)' : 'CLAHE Clip Limit'} /></span>
              </div>
              <span className="text-[#86D88E] font-semibold">
                <AnimatedNumber value={simulationParams.claheClipLimit} decimals={1} duration={150} />
              </span>
            </div>
            <input
              type="range"
              min="1.0"
              max="5.0"
              step="0.2"
              value={simulationParams.claheClipLimit}
              onChange={(e) => updateSimulationParam('claheClipLimit', Number(e.target.value))}
              className="w-full accent-[#86D88E] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono-tech text-[#646462]">
              <span>1.0 (Flat)</span>
              <span className="text-[#86D88E]">3.2 (Calibrated)</span>
              <span>5.0 (Extreme)</span>
            </div>
          </div>

        </div>
      </div>

      {/* ─── LIVE ADAPTIVE REACTION PROOF PANEL ─── */}
      <div className="p-6 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#262626] pb-3">
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-[#A0A0A0]" />
            <h4 className="font-sans text-sm font-bold text-[#F7F7F5] uppercase">
              LIVE ADAPTIVE ROUTER REACTION TO CURRENT SIMULATED CONDITIONS
            </h4>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono-tech text-[#8C8C89] uppercase">DIAGNOSED DIFFICULTY:</span>
            <span className={`px-2 py-0.5 rounded-none font-mono-tech text-xs font-semibold uppercase ${
              pairCharacterization.overallDifficulty === 'Hard'
                ? 'bg-[#2E1616] text-[#E57373] border border-[#5E2424]'
                : pairCharacterization.overallDifficulty === 'Medium'
                ? 'bg-[#2E2211] text-[#E0A855] border border-[#5E4218]'
                : 'bg-[#1A2E1C] text-[#86D88E] border border-[#2E5E32]'
            }`}>
              {pairCharacterization.overallDifficulty}
            </span>
          </div>
        </div>

        {/* Selected Strategy & Environmental Stress Impact */}
        <div className="p-4 rounded-none border border-[#262626] bg-[#161616] flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-left">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-none text-[10px] font-mono-tech font-semibold bg-[#1E1E1E] text-[#F7F7F5] border border-[#383838] flex items-center gap-1">
                <Star className="h-3 w-3 fill-[#F7F7F5]" />
                ADAPTIVE CANDIDATE
              </span>
              <span className="font-mono-tech text-xs text-[#86D88E] font-semibold">
                {selectedModel.name}
              </span>
            </div>
            <p className="text-xs text-[#8C8C89] font-sans leading-relaxed">
              <strong className="text-[#F7F7F5]">Simulated Stress Impact: </strong>
              {simulationParams.sunElevationAngle < 8
                ? 'Grazing sun angle creates extreme crater shadows. Multi-scale phase congruency required to prevent false shadow edge tracking.'
                : simulationParams.sensorNoiseSigma > 10
                ? 'Elevated sensor noise degrades intensity gradients. Fast NLM and CLAHE filtering engaged.'
                : 'Nominal simulated stress parameters within registration operating envelope.'}
            </p>
          </div>
          <div className="shrink-0 font-mono-tech text-[10px] text-[#A0A0A0] bg-[#111111] px-3 py-2 border border-[#262626]">
            <div>STRESS MODE: ACTIVE</div>
            <div className="text-[#86D88E]">SIMULATION PREVIEW ONLY</div>
          </div>
        </div>
      </div>
    </div>
  );
};
