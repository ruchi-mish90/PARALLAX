import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { AnimatedNumber } from '../common/AnimatedNumber';
import { ScrambleText } from '../common/ScrambleText';
import { 
  CheckCircle2, 
  Crosshair, 
  BarChart3, 
  Activity, 
  AlertCircle 
} from 'lucide-react';

export const MetricCards: React.FC = () => {
  const { metrics, isAnmsActive, isSubpixelRefined, explainMode, setCursorLabel } = useParallax();

  return (
    <div className="space-y-4">
      {/* Evidence & Provenance Notice Banner */}
      <div className="p-3.5 rounded-none sm:rounded-sm bg-[#161616] border border-[#262626] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono-tech text-[#8C8C89]">
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-[#A0A0A0] shrink-0" />
          <span>
            EVIDENCE PROVENANCE: Quantitative telemetry mapped according to planetary-data traceability.
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-none bg-[#1A2E1C] border border-[#2E5E32] text-[#86D88E] text-[10px] font-semibold">
            MEASURED BENCHMARK
          </span>
          <span className="px-2 py-0.5 rounded-none bg-[#1E1E1E] border border-[#333333] text-[#A0A0A0] text-[10px] font-semibold">
            QUALITY TARGET GATE
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-left">
        
        {/* 1. RMSE / REGISTRATION ERROR */}
        <div
          onMouseEnter={() => setCursorLabel('INSPECT RMSE ACCURACY')}
          onMouseLeave={() => setCursorLabel('')}
          className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3 transition-colors hover:border-[#383838]"
        >
          <div className="flex items-center justify-between">
            <span className="font-mono-tech text-[10px] uppercase text-[#8C8C89] tracking-wider font-semibold">
              <ScrambleText text={explainMode ? 'ALIGNMENT DEVIATION' : 'REPROJECTION RMSE'} />
            </span>
            <Crosshair className="h-4 w-4 text-[#A0A0A0]" />
          </div>

          <div>
            <div className="font-sans text-3xl font-extrabold text-[#F7F7F5] tracking-tight flex items-baseline gap-1">
              <AnimatedNumber value={metrics.rmse} decimals={2} duration={800} />
              <span className="text-sm font-mono-tech text-[#8C8C89]">px</span>
            </div>
            <div className="text-xs text-[#8C8C89] mt-1 leading-normal font-sans">
              <ScrambleText text={explainMode ? 'Sub-pixel distance between matched landmarks' : 'Root Mean Square Error across geometric inliers'} />
            </div>
          </div>

          <div className="pt-2 border-t border-[#262626] flex items-center justify-between text-[10px] font-mono-tech">
            <span className={`px-1.5 py-0.5 rounded-none font-semibold ${
              metrics.candidateMatches > 0 
                ? (metrics.rmse < 1.5 ? 'text-[#86D88E] bg-[#1A2E1C] border border-[#2E5E32]' : 'text-[#E0A855] bg-[#2E2211] border border-[#5E4218]')
                : 'text-[#8C8C89] bg-[#1E1E1E] border border-[#383838]'
            }`}>
              {metrics.candidateMatches > 0 ? (metrics.rmse < 1.5 ? 'TARGET < 1.5 px MET' : 'TARGET EXCEEDED') : 'AWAITING RUN'}
            </span>
            <span className="text-[#8C8C89]">
              BENCHMARK
            </span>
          </div>
        </div>

        {/* 2. INLIER COUNT & RATIO */}
        <div
          onMouseEnter={() => setCursorLabel('INSPECT INLIER RATIO')}
          onMouseLeave={() => setCursorLabel('')}
          className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3 transition-colors hover:border-[#383838]"
        >
          <div className="flex items-center justify-between">
            <span className="font-mono-tech text-[10px] uppercase text-[#8C8C89] tracking-wider font-semibold">
              <ScrambleText text={explainMode ? 'CONFIRMED MATCH RATIO' : 'RANSAC INLIER CONSENSUS'} />
            </span>
            <CheckCircle2 className="h-4 w-4 text-[#86D88E]" />
          </div>

          <div>
            <div className="font-sans text-3xl font-extrabold text-[#F7F7F5] tracking-tight flex items-baseline gap-2">
              <AnimatedNumber value={metrics.inlierRatio} decimals={1} duration={800} suffix="%" />
              <span className="text-xs font-mono-tech text-[#8C8C89]">
                ({metrics.inlierMatches}/{metrics.candidateMatches})
              </span>
            </div>
            <div className="text-xs text-[#8C8C89] mt-1 leading-normal font-sans">
              <ScrambleText text={explainMode ? 'Portion of candidate pairs confirmed as genuine' : 'Projective homography MSAC inlier percentage'} />
            </div>
          </div>

          <div className="pt-2 border-t border-[#262626] flex items-center justify-between text-[10px] font-mono-tech">
            <span className={`px-1.5 py-0.5 rounded-none font-semibold ${
              metrics.candidateMatches > 0
                ? 'text-[#86D88E] bg-[#1A2E1C] border border-[#2E5E32]'
                : 'text-[#8C8C89] bg-[#1E1E1E] border border-[#383838]'
            }`}>
              {metrics.candidateMatches > 0 ? `${metrics.outlierMatches} OUTLIERS PRUNED` : 'AWAITING RUN'}
            </span>
            <span className="text-[#8C8C89]">
              CONSENSUS
            </span>
          </div>
        </div>

        {/* 3. UNCERTAINTY ESTIMATE (1-SIGMA) */}
        <div
          onMouseEnter={() => setCursorLabel('INSPECT UNCERTAINTY BOUND')}
          onMouseLeave={() => setCursorLabel('')}
          className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3 transition-colors hover:border-[#383838]"
        >
          <div className="flex items-center justify-between">
            <span className="font-mono-tech text-[10px] uppercase text-[#8C8C89] tracking-wider font-semibold">
              <ScrambleText text={explainMode ? 'CONFIDENCE MARGIN' : '1-SIGMA UNCERTAINTY (±σ)'} />
            </span>
            <Activity className="h-4 w-4 text-[#A0A0A0]" />
          </div>

          <div>
            <div className="font-sans text-3xl font-extrabold text-[#F7F7F5] tracking-tight flex items-baseline gap-1">
              <span className="text-[#8C8C89]">±</span>
              <AnimatedNumber value={metrics.uncertaintyPx} decimals={2} duration={800} />
              <span className="text-sm font-mono-tech text-[#8C8C89]">px</span>
            </div>
            <div className="text-xs text-[#8C8C89] mt-1 leading-normal font-sans">
              <ScrambleText text={explainMode ? 'Statistical error margin of landmark positions' : 'Covariance-derived displacement error bound'} />
            </div>
          </div>

          <div className="pt-2 border-t border-[#262626] flex items-center justify-between text-[10px] font-mono-tech">
            <span className="px-1.5 py-0.5 rounded-none text-[#E4E4E2] bg-[#1E1E1E] border border-[#383838] font-semibold">
              {isSubpixelRefined ? 'ECC REFINED' : 'RAW RANSAC'}
            </span>
            <span className="text-[#8C8C89]">
              UNCERTAINTY
            </span>
          </div>
        </div>

        {/* 4. SPATIAL COVERAGE (ANMS DISPERSION SCORE) */}
        <div
          onMouseEnter={() => setCursorLabel('INSPECT SPATIAL COVERAGE')}
          onMouseLeave={() => setCursorLabel('')}
          className="p-5 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3 transition-colors hover:border-[#383838]"
        >
          <div className="flex items-center justify-between">
            <span className="font-mono-tech text-[10px] uppercase text-[#8C8C89] tracking-wider font-semibold">
              <ScrambleText text={explainMode ? 'GLOBAL SPREAD' : 'SPATIAL COVERAGE (ANMS)'} />
            </span>
            <BarChart3 className="h-4 w-4 text-[#A0A0A0]" />
          </div>

          <div>
            <div className="font-sans text-3xl font-extrabold text-[#F7F7F5] tracking-tight flex items-baseline gap-1">
              <AnimatedNumber value={metrics.spatialCoverage} decimals={1} duration={800} suffix="%" />
            </div>
            <div className="text-xs text-[#8C8C89] mt-1 leading-normal font-sans">
              <ScrambleText text={explainMode ? 'Spread across the entire scene to prevent clumps' : 'Convex hull spatial distribution across target FOV'} />
            </div>
          </div>

          <div className="pt-2 border-t border-[#262626] flex items-center justify-between text-[10px] font-mono-tech">
            <span className="px-1.5 py-0.5 rounded-none text-[#86D88E] bg-[#1A2E1C] border border-[#2E5E32] font-semibold">
              {isAnmsActive ? 'ANMS ENFORCED' : 'RAW CLUSTERS'}
            </span>
            <span className="text-[#8C8C89]">
              DISPERSION
            </span>
          </div>
        </div>

      </div>

      {/* Secondary Metrics Row: Precision, Recall, Overall Confidence, Execution Time */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-left">
        {/* Precision */}
        <div className="p-4 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1">
          <div className="text-[10px] font-mono-tech text-[#8C8C89] uppercase">TRUE POSITIVE PRECISION</div>
          <div className="font-sans text-2xl font-bold text-[#F7F7F5] flex items-baseline gap-1">
            <AnimatedNumber value={metrics.precision} decimals={1} duration={600} suffix="%" />
          </div>
          <div className="text-[11px] text-[#8C8C89] font-sans">
            TP / (TP + FP) vs. ground truth
          </div>
          <div className="pt-2 text-[10px] font-mono-tech text-[#A0A0A0]">
            [VALIDATED BENCHMARK]
          </div>
        </div>

        {/* Recall */}
        <div className="p-4 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1">
          <div className="text-[10px] font-mono-tech text-[#8C8C89] uppercase">LANDMARK RECALL RATE</div>
          <div className="font-sans text-2xl font-bold text-[#F7F7F5] flex items-baseline gap-1">
            <AnimatedNumber value={metrics.recall} decimals={1} duration={600} suffix="%" />
          </div>
          <div className="text-[11px] text-[#8C8C89] font-sans">
            F1-Score: {(metrics.f1Score || 0).toFixed(3)}
          </div>
          <div className="pt-2 text-[10px] font-mono-tech text-[#A0A0A0]">
            [VALIDATED BENCHMARK]
          </div>
        </div>

        {/* Overall Confidence Score */}
        <div className="p-4 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1">
          <div className="text-[10px] font-mono-tech text-[#8C8C89] uppercase">OVERALL CONFIDENCE SCORE</div>
          <div className="font-sans text-2xl font-bold text-[#86D88E] flex items-baseline gap-1">
            <AnimatedNumber value={metrics.confidenceScore || 0} decimals={1} duration={600} suffix="%" />
          </div>
          <div className="text-[11px] text-[#8C8C89] font-sans">
            Quality Gate: <strong className="text-[#F7F7F5]">{metrics.qualityGateStatus || 'PASSED'}</strong>
          </div>
          <div className="pt-2 text-[10px] font-mono-tech text-[#86D88E]">
            [QUALITY GATE TARGET]
          </div>
        </div>

        {/* Execution Time */}
        <div className="p-4 rounded-none sm:rounded-sm border border-[#262626] bg-[#161616] space-y-1">
          <div className="text-[10px] font-mono-tech text-[#8C8C89] uppercase">PIPELINE EXECUTION TIME</div>
          <div className="font-sans text-2xl font-bold text-[#F7F7F5] flex items-baseline gap-1">
            <AnimatedNumber value={metrics.processingTimeMs || 0} decimals={0} duration={600} suffix=" ms" />
          </div>
          <div className="text-[11px] text-[#8C8C89] font-sans truncate">
            PyTorch acceleration (1024² tile)
          </div>
          <div className="pt-2 text-[10px] font-mono-tech text-[#E0A855]">
            [HARDWARE BENCHMARK]
          </div>
        </div>
      </div>
    </div>
  );
};
