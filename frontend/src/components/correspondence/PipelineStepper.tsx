import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { PIPELINE_STAGES } from '../../data/correspondenceMockData';
import { AnimatedNumber } from '../common/AnimatedNumber';
import { ScrambleText } from '../common/ScrambleText';
import { Play, CheckCircle2, Loader2, Sparkles } from 'lucide-react';

export const PipelineStepper: React.FC = () => {
  const { 
    explainMode, 
    isProcessing, 
    pipelineProgress, 
    currentStageIndex, 
    runCorrespondence,
    setCursorLabel 
  } = useParallax();

  return (
    <div className="bg-[#FFFFFF] rounded-none sm:rounded-sm p-5 border border-[#E2E2DE] space-y-4 shadow-[0_1px_3px_rgba(0,0,0,0.03)] text-left">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EAEAE6] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono-tech text-xs text-[#666666] uppercase tracking-wider">
              <ScrambleText text={explainMode ? 'STEP-BY-STEP ADAPTIVE PROCESS' : 'END-TO-END ADAPTIVE PIPELINE'} />
            </span>
            <span className="px-2 py-0.5 rounded-none text-[10px] font-mono-tech bg-[#F7F7F5] text-[#111111] border border-[#E2E2DE] font-semibold">
              10 STAGES
            </span>
          </div>
          <h3 className="font-sans text-base sm:text-lg font-bold text-[#111111] mt-0.5">
            <ScrambleText 
              text={explainMode 
                ? 'How PARALLAX Characterizes, Routes & Aligns the Pair' 
                : 'Pair-Aware Adaptive Registration Execution Flow'} 
            />
          </h3>
        </div>

        {/* Action Trigger Button (Dark Accent on Light surface) */}
        <button
          onClick={runCorrespondence}
          disabled={isProcessing}
          onMouseEnter={() => setCursorLabel('EXECUTE ADAPTIVE PIPELINE')}
          onMouseLeave={() => setCursorLabel('')}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-none font-mono-tech text-xs tracking-wider font-semibold transition-colors ${
            isProcessing
              ? 'bg-[#EFEFEA] text-[#111111] cursor-not-allowed border border-[#D4D4D0]'
              : 'bg-[#111111] text-[#F7F7F5] hover:bg-[#222222]'
          }`}
        >
          {isProcessing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-[#111111]" />
              <span>
                EXECUTING (<AnimatedNumber value={pipelineProgress} duration={300} suffix="%" />)
              </span>
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>RUN REGISTRATION</span>
            </>
          )}
        </button>
      </div>

      {/* Progress Line */}
      <div className="w-full bg-[#EAEAE6] h-1.5 overflow-hidden">
        <div 
          className="bg-[#111111] h-full transition-all duration-300 ease-out"
          style={{ width: `${pipelineProgress}%` }}
        />
      </div>

      {/* 10-Stage Grid Display */}
      <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2 pt-2">
        {PIPELINE_STAGES.map((stage, idx) => {
          const isDone = idx < currentStageIndex || (!isProcessing && pipelineProgress === 100);
          const isCurrent = isProcessing && idx === currentStageIndex;

          return (
            <div
              key={stage.id}
              className={`p-2 rounded-none border transition-colors text-left flex flex-col justify-between space-y-1 ${
                isCurrent 
                  ? 'bg-[#F7F7F5] border-2 border-[#111111] text-[#111111]' 
                  : isDone 
                  ? 'bg-[#F7F7F5] border border-[#E2E2DE] text-[#111111]' 
                  : 'bg-[#FFFFFF] border border-[#EAEAE6] text-[#888885]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`font-mono-tech text-[10px] font-bold ${
                  isCurrent ? 'text-[#111111]' : isDone ? 'text-[#246327]' : 'text-[#888885]'
                }`}>
                  {stage.stageNumber}
                </span>
                {isDone && <CheckCircle2 className="h-3 w-3 text-[#246327] shrink-0" />}
                {isCurrent && <Loader2 className="h-3 w-3 text-[#111111] animate-spin shrink-0" />}
              </div>

              <div className="font-sans text-xs font-bold text-[#111111] line-clamp-1">
                {stage.explainTitle}
              </div>

              <div className="text-[9px] font-mono-tech text-[#666666] line-clamp-2">
                {stage.algorithm.split(' ')[0]}
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Stage Callout */}
      {currentStageIndex < PIPELINE_STAGES.length && (
        <div className="p-3 rounded-none bg-[#F7F7F5] border border-[#E2E2DE] flex items-start gap-3 text-left">
          <Sparkles className="h-4 w-4 text-[#111111] shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <div className="text-xs font-mono-tech font-bold text-[#111111]">
              STAGE {PIPELINE_STAGES[currentStageIndex].stageNumber}: {PIPELINE_STAGES[currentStageIndex].scientificTitle}
            </div>
            <p className="text-xs text-[#555555] font-sans">
              {explainMode 
                ? PIPELINE_STAGES[currentStageIndex].explainDescription 
                : PIPELINE_STAGES[currentStageIndex].scientificDescription}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
