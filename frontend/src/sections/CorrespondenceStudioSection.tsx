import React from 'react';
import { useParallax } from '../state/ParallaxContext';
import { DualImageComparator } from '../components/correspondence/DualImageComparator';
import { PipelineStepper } from '../components/correspondence/PipelineStepper';
import { FilterToggle } from '../components/correspondence/FilterToggle';
import { PairAnalysisPanel } from '../components/correspondence/PairAnalysisPanel';
import { AdaptiveModelRouter } from '../components/correspondence/AdaptiveModelRouter';
import { PairSelectionControlArea } from '../components/correspondence/PairSelectionControlArea';
import { Scan, MapPin } from 'lucide-react';

export const CorrespondenceStudioSection: React.FC = () => {
  const { 
    selectedRegion, 
    selectedModel,
    explainMode,
  } = useParallax();

  return (
    <div id="correspondence" className="w-full flex flex-col select-none">
      
      {/* ─── BAND 1: PAIR SELECTION & OBSERVATION SETUP (BLACK SECTION #111111) ─── */}
      <section className="relative py-10 bg-[#111111] text-[#F7F7F5] border-b border-[#262626]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-6">
          {/* 3-Column Top Control Area (Source A | Router Setup | Target B) */}
          <PairSelectionControlArea />
        </div>
      </section>

      {/* ─── BAND 2: PAIR CHARACTERIZATION & ADAPTIVE MODEL BANK (LIGHT SECTION #F7F7F5) ─── */}
      <section className="relative py-16 bg-[#F7F7F5] text-[#111111] border-b border-[#E2E2DE]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-6">
          <h2 className="font-sans text-xl sm:text-3xl font-extrabold text-[#111111] tracking-tight">
            Pair Difficulty Characterization & Model Bank
          </h2>

          {/* Part B: Pair Analysis Panel */}
          <PairAnalysisPanel />

          {/* Part C: Adaptive Model Router */}
          <AdaptiveModelRouter />
        </div>
      </section>

      {/* ─── BAND 3: DUAL IMAGE COMPARATOR STAGE (BLACK SECTION #111111) ─── */}
      <section className="relative py-16 bg-[#111111] text-[#F7F7F5] border-b border-[#262626]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#262626] pb-3">
            <div className="font-sans text-base sm:text-lg font-bold text-[#F7F7F5] flex items-center gap-2">
              <span>VISUAL ALIGNMENT & SUBPIXEL CORRESPONDENCE STAGE</span>
              <span className="font-mono-tech text-xs font-normal text-[#86D88E]">
                [ENGINE: {selectedModel.name.split('(')[0]}]
              </span>
            </div>
            <div className="font-mono-tech text-xs text-[#8C8C89]">
              INSPECT RESIDUAL VECTOR DISPLACEMENTS IN REAL TIME
            </div>
          </div>

          {/* Part D & E: Dual Image Comparator with Canvas */}
          <DualImageComparator />

          {/* Interactive Match Vector Filters */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
            <FilterToggle />

            <div className="font-mono-tech text-[11px] text-[#8C8C89]">
              CLICK ANY MATCH VECTOR TO INSPECT REPROJECTION RESIDUAL
            </div>
          </div>
        </div>
      </section>

      {/* ─── BAND 4: 10-STAGE PIPELINE STEPPER (LIGHT SECTION #F7F7F5) ─── */}
      <section className="relative py-16 bg-[#F7F7F5] text-[#111111] border-b border-[#E2E2DE]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-6">
          <h2 className="font-sans text-xl sm:text-3xl font-extrabold text-[#111111] tracking-tight">
            End-to-End Registration Execution Stepper
          </h2>

          {/* Part F: 10-Stage Pipeline Stepper */}
          <PipelineStepper />
        </div>
      </section>

    </div>
  );
};
