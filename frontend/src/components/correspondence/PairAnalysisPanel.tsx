import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { Activity, AlertTriangle, Scale, Sun, Layers, HelpCircle, GitFork } from 'lucide-react';

export const PairAnalysisPanel: React.FC = () => {
  const { 
    sourceInstrument, 
    targetInstrument, 
    sourceProduct,
    targetProduct,
    pairCharacterization, 
    useTmcBridge, 
    toggleTmcBridge, 
    explainMode 
  } = useParallax();

  const getDifficultyColor = (diff: string) => {
    switch (diff) {
      case 'Easy':
        return 'text-[#246327] bg-[#E8F3E8] border-[#A8D3A9]';
      case 'Medium':
        return 'text-[#8C5E13] bg-[#FBF3E4] border-[#DEC085]';
      case 'Hard':
      default:
        return 'text-[#9E2A27] bg-[#FCEAE9] border-[#E8A5A3]';
    }
  };

  return (
    <div className="space-y-4">
      {/* Main Analysis Card (Crisp White Card on #F7F7F5 Surface) */}
      <div className="p-5 sm:p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-5 text-left shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#EAEAE6] pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-[#111111]" />
              <span className="font-mono-tech text-xs text-[#666666] uppercase tracking-wider font-semibold">
                PAIR CHARACTERIZATION & DIAGNOSIS
              </span>
            </div>
            <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
              {explainMode ? 'How Difficult Is This Pair To Match?' : 'Heterogeneous Sensor Difficulty Characterization'}
            </h3>
          </div>

          <div className="flex items-center gap-3">
            <span className="font-mono-tech text-xs text-[#666666]">OVERALL DIFFICULTY:</span>
            <span className={`px-3 py-0.5 rounded-none font-mono-tech text-xs font-semibold uppercase border ${getDifficultyColor(pairCharacterization.overallDifficulty)}`}>
              {pairCharacterization.overallDifficulty}
            </span>
          </div>
        </div>

        {/* 6 Diagnostic Telemetry Gauges */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Scale Ratio */}
          <div className="p-3 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] space-y-1">
            <div className="flex items-center gap-1.5 text-[10px] font-mono-tech text-[#666666] uppercase">
              <Scale className="h-3 w-3 text-[#111111]" />
              <span>SCALE RATIO</span>
            </div>
            <div className="font-mono-tech text-sm font-bold text-[#111111]">
              {pairCharacterization.scaleRatioDisplay}
            </div>
            <div className="text-[10px] text-[#777775] font-mono-tech">
              {pairCharacterization.scaleRatio > 50 ? 'Severe Disparity' : pairCharacterization.scaleRatio > 10 ? 'High Gap' : 'Nominal'}
            </div>
          </div>

          {/* Modality Difference */}
          <div className="p-3 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] space-y-1">
            <div className="flex items-center gap-1.5 text-[10px] font-mono-tech text-[#666666] uppercase">
              <Layers className="h-3 w-3 text-[#111111]" />
              <span>MODALITY GAP</span>
            </div>
            <div className={`font-mono-tech text-sm font-bold ${
              pairCharacterization.modalityDifference === 'Severe' ? 'text-[#9E2A27]' :
              pairCharacterization.modalityDifference === 'Moderate' ? 'text-[#8C5E13]' : 'text-[#246327]'
            }`}>
              {pairCharacterization.modalityDifference}
            </div>
            <div className="text-[10px] text-[#777775] font-mono-tech truncate" title={`${sourceProduct?.label || sourceInstrument} × ${targetProduct?.label || targetProduct?.productId || targetInstrument}`}>
              {sourceProduct?.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : sourceInstrument} × {targetProduct?.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : targetInstrument}
            </div>
          </div>

          {/* Illumination Difference */}
          <div className="p-3 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] space-y-1">
            <div className="flex items-center gap-1.5 text-[10px] font-mono-tech text-[#666666] uppercase">
              <Sun className="h-3 w-3 text-[#8C5E13]" />
              <span>ILLUMINATION</span>
            </div>
            <div className={`font-mono-tech text-sm font-bold ${
              pairCharacterization.illuminationDifference === 'Extreme' ? 'text-[#9E2A27]' :
              pairCharacterization.illuminationDifference === 'Moderate' ? 'text-[#8C5E13]' : 'text-[#246327]'
            }`}>
              {pairCharacterization.illuminationDifference}
            </div>
            <div className="text-[10px] text-[#777775] font-mono-tech">
              Low-Angle Polar Sun
            </div>
          </div>

          {/* Texture Entropy */}
          <div className="p-3 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] space-y-1">
            <div className="text-[10px] font-mono-tech text-[#666666] uppercase">
              TEXTURE ENTROPY
            </div>
            <div className="font-mono-tech text-sm font-bold text-[#111111]">
              {pairCharacterization.textureEntropy} <span className="text-[10px] text-[#777775] font-normal">/ 8.0</span>
            </div>
            <div className="text-[10px] text-[#777775] font-mono-tech">
              Regolith Roughness
            </div>
          </div>

          {/* Estimated Overlap */}
          <div className="p-3 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] space-y-1">
            <div className="text-[10px] font-mono-tech text-[#666666] uppercase">
              EST. OVERLAP
            </div>
            <div className="font-mono-tech text-sm font-bold text-[#246327]">
              {pairCharacterization.estimatedOverlap}%
            </div>
            <div className="text-[10px] text-[#777775] font-mono-tech">
              Spatial Intersect
            </div>
          </div>

          {/* Valid Pixel Ratio */}
          <div className="p-3 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] space-y-1">
            <div className="text-[10px] font-mono-tech text-[#666666] uppercase">
              VALID PIXELS
            </div>
            <div className="font-mono-tech text-sm font-bold text-[#111111]">
              {pairCharacterization.validPixelRatio}%
            </div>
            <div className="text-[10px] text-[#777775] font-mono-tech">
              Excluding Shadows
            </div>
          </div>
        </div>

        {/* Diagnosis Rationale Callout */}
        <div className="p-3.5 rounded-none sm:rounded-sm bg-[#F7F7F5] border border-[#E2E2DE] flex items-start gap-3 text-xs leading-relaxed">
          <HelpCircle className="h-4 w-4 text-[#111111] shrink-0 mt-0.5" />
          <div className="space-y-1 text-[#555555]">
            <span className="font-mono-tech font-semibold text-[#111111]">PAIR DIAGNOSIS: </span>
            <span>{pairCharacterization.difficultyRationale}</span>
          </div>
        </div>

        {/* CONDITIONAL TMC-2 INTERMEDIATE BRIDGE PROPOSAL BANNER */}
        {pairCharacterization.suggestTmcBridge && (
          <div className="p-4 rounded-none sm:rounded-sm border border-[#DEC085] bg-[#FBF3E4] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-[#8C5E13] font-mono-tech text-xs font-bold uppercase">
                <AlertTriangle className="h-4 w-4 text-[#8C5E13] shrink-0" />
                <span>CONDITIONAL STRATEGY: TMC-2 INTERMEDIATE SCALE BRIDGE</span>
                <span className="px-1.5 py-0.2 rounded-none text-[9px] bg-[#FFFFFF] text-[#8C5E13] border border-[#DEC085]">
                  PROPOSED STRATEGY
                </span>
              </div>
              <p className="text-xs text-[#555555] font-sans leading-relaxed">
                Direct matching across a 320:1 GSD gap (OHRC ~0.25 m vs IIRS ~80 m) risks severe descriptor aliasing. PARALLAX proposes an intermediate bridge route: <strong className="text-[#111111]">OHRC (0.25 m) → TMC-2 (5.0 m) → IIRS (80 m)</strong>.
              </p>
            </div>

            <button
              onClick={toggleTmcBridge}
              className={`px-4 py-2 rounded-none font-mono-tech text-xs font-bold tracking-wider transition-colors flex items-center gap-2 shrink-0 ${
                useTmcBridge
                  ? 'bg-[#8C5E13] text-[#FFFFFF]'
                  : 'bg-[#FFFFFF] border border-[#DEC085] text-[#8C5E13] hover:bg-[#F7F7F5]'
              }`}
            >
              <GitFork className="h-3.5 w-3.5" />
              <span>{useTmcBridge ? 'BRIDGE ACTIVE (OHRC→TMC→IIRS)' : 'ENGAGE TMC-2 BRIDGE'}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
