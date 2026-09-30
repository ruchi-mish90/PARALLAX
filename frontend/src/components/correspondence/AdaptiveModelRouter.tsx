import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { ModelId } from '../../types/correspondence';
import { GitBranch, CheckCircle2, ChevronRight, Zap } from 'lucide-react';

export const AdaptiveModelRouter: React.FC = () => {
  const { 
    modelCandidates, 
    selectedModelId, 
    setSelectedModelId, 
    selectedModel,
    isAnmsActive,
    toggleAnms,
    isSubpixelRefined,
    toggleSubpixelRefinement,
    runModelTest,
    explainMode,
    setCursorLabel 
  } = useParallax();

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="p-5 sm:p-6 rounded-none sm:rounded-sm border border-[#E2E2DE] bg-[#FFFFFF] space-y-4 text-left shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EAEAE6] pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <GitBranch className="h-4 w-4 text-[#111111]" />
              <span className="font-mono-tech text-xs text-[#666666] uppercase tracking-wider font-semibold">
                ADAPTIVE MODEL ROUTER // CANDIDATE RANKING
              </span>
            </div>
            <h3 className="font-sans text-lg sm:text-xl font-bold text-[#111111]">
              {explainMode ? 'Matching Strategy Selected For This Pair' : 'Ranked Correspondence Model Candidates'}
            </h3>
            <p className="text-xs text-[#555555] font-sans max-w-2xl leading-relaxed">
              {explainMode
                ? 'PARALLAX evaluates the difficulty of this image pair and ranks the models. You can test alternate strategies below.'
                : 'Adaptive model ranking heuristic scores interchangeable correspondence engines based on diagnosed scale disparity and radiometric modality.'}
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="font-mono-tech text-[10px] text-[#777775] uppercase">MODEL BANK:</span>
            <span className="px-2 py-0.5 rounded-none bg-[#F7F7F5] border border-[#E2E2DE] font-mono-tech text-xs text-[#111111] font-semibold">
              6 CANDIDATES EVALUATED
            </span>
          </div>
        </div>

        {/* Top Selected Model Highlight Banner (Crisp Dark Block for High-Contrast Focal Rhythm) */}
        <div className="p-4 rounded-none sm:rounded-sm border border-[#262626] bg-[#111111] text-[#F7F7F5] flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-3xl">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-none text-[10px] font-mono-tech font-bold bg-[#1A2E1C] text-[#86D88E] border border-[#2E5E32] flex items-center gap-1">
                RANK #1 RECOMMENDED STRATEGY
              </span>
              <span className="font-mono-tech text-xs text-[#A0A0A0]">
                Category: <strong className="text-[#F7F7F5] font-semibold">{selectedModel.category}</strong>
              </span>
            </div>
            <h4 className="font-sans text-base sm:text-lg font-bold text-[#F7F7F5] flex items-center gap-2">
              <span>{selectedModel.name}</span>
              <span className="font-mono-tech text-xs text-[#86D88E] font-semibold">
                [{selectedModel.suitabilityScore}% Suitability]
              </span>
            </h4>
            <p className="text-xs text-[#A0A0A0] font-sans leading-relaxed">
              <strong className="text-[#F7F7F5]">Selection Rationale:</strong> {selectedModel.selectionRationale}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {/* ANMS Global Dispersion Toggle */}
            <button
              onClick={toggleAnms}
              title="Adaptive Non-Maximal Suppression enforces global spatial spread"
              className={`px-3 py-1.5 rounded-none font-mono-tech text-xs border transition-colors flex items-center gap-1.5 ${
                isAnmsActive
                  ? 'bg-[#1A2E1C] border-[#2E5E32] text-[#86D88E] font-semibold'
                  : 'bg-[#161616] border-[#333333] text-[#A0A0A0] hover:text-[#FFFFFF]'
              }`}
            >
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>ANMS SPATIAL COVERAGE: {isAnmsActive ? 'ENFORCED' : 'OFF'}</span>
            </button>

            {/* Sub-Pixel ECC Refinement Toggle */}
            <button
              onClick={toggleSubpixelRefinement}
              title="Enhanced Correlation Coefficient sub-pixel local refinement"
              className={`px-3 py-1.5 rounded-none font-mono-tech text-xs border transition-colors flex items-center gap-1.5 ${
                isSubpixelRefined
                  ? 'bg-[#1E1E1E] border-[#383838] text-[#F7F7F5] font-semibold'
                  : 'bg-[#161616] border-[#333333] text-[#A0A0A0] hover:text-[#FFFFFF]'
              }`}
            >
              <Zap className="h-3.5 w-3.5" />
              <span>ECC SUB-PIXEL: {isSubpixelRefined ? 'ON' : 'OFF'}</span>
            </button>
          </div>
        </div>

        {/* 6 Ranked Candidate Model Cards (White Cards with subtle hover) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
          {modelCandidates.map((candidate) => {
            const isSelected = selectedModelId === candidate.id;

            return (
              <div
                key={candidate.id}
                onClick={() => setSelectedModelId(candidate.id as ModelId)}
                onMouseEnter={() => setCursorLabel(`INSPECT ${candidate.id}`)}
                onMouseLeave={() => setCursorLabel('')}
                className={`p-4 rounded-none sm:rounded-sm border text-left cursor-pointer transition-colors duration-150 flex flex-col justify-between space-y-3 ${
                  isSelected
                    ? 'bg-[#F7F7F5] border-2 border-[#111111] shadow-sm'
                    : 'bg-[#FFFFFF] border border-[#E2E2DE] hover:border-[#BFBFB8]'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono-tech text-[10px] text-[#777775] font-bold uppercase tracking-wider">
                      RANK #{candidate.rank}
                    </span>
                    <span className={`px-2 py-0.5 rounded-none font-mono-tech text-[10px] font-semibold border ${
                      candidate.suitabilityScore >= 90 ? 'bg-[#E8F3E8] border-[#A8D3A9] text-[#246327]' :
                      candidate.suitabilityScore >= 75 ? 'bg-[#FBF3E4] border-[#DEC085] text-[#8C5E13]' :
                      'bg-[#F7F7F5] border-[#E2E2DE] text-[#666666]'
                    }`}>
                      {candidate.suitabilityScore}% MATCH
                    </span>
                  </div>

                  <h5 className="font-sans text-sm font-bold text-[#111111] leading-tight">
                    {candidate.name.split('(')[0]}
                  </h5>
                  <div className="text-[10px] font-mono-tech text-[#666666] uppercase">
                    {candidate.category}
                  </div>
                  <p className="text-xs text-[#555555] font-sans leading-relaxed line-clamp-2">
                    {candidate.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-[#EAEAE6] flex items-center justify-between text-[11px] font-mono-tech gap-2">
                  <span className={isSelected ? 'text-[#111111] font-bold' : 'text-[#777775]'}>
                    {isSelected ? '● ACTIVE ENGINE' : 'SELECT ENGINE'}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        runModelTest(candidate.id as ModelId);
                      }}
                      className="px-2 py-0.5 rounded-none text-[9.5px] font-mono-tech bg-[#111111] text-[#F7F7F5] hover:bg-[#262626] border border-[#262626] transition-colors"
                      title={`Run individual test for ${candidate.name}`}
                    >
                      TEST MODEL
                    </button>
                    <ChevronRight className={`h-3.5 w-3.5 ${isSelected ? 'text-[#111111]' : 'text-[#999999]'}`} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
