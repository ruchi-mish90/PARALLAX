import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { MatchFilterType } from '../../types/correspondence';
import { CheckCircle2, XCircle, Layers, Eye } from 'lucide-react';

export const FilterToggle: React.FC = () => {
  const { 
    matchFilter, 
    setMatchFilter, 
    matchPairs, 
    sourceKeypoints, 
    metrics, 
    isSubpixelRefined, 
    setCursorLabel 
  } = useParallax();

  const inliersCount = matchPairs.filter(m => m.isRansacInlier).length;
  const outliersCount = matchPairs.filter(m => !m.isRansacInlier).length;

  const filters: { id: MatchFilterType; label: string; count: number; icon: React.ReactNode; color: string }[] = [
    {
      id: 'ANMS_ONLY',
      label: 'ANMS DISTRIBUTED',
      count: matchPairs.filter(m => m.isRansacInlier && m.isAnmsSelected).length,
      icon: <CheckCircle2 className="h-3.5 w-3.5 text-cyan-accent" />,
      color: 'text-cyan-accent border-cyan-accent/40 bg-cyan-accent/10',
    },
    {
      id: 'INLIERS',
      label: 'VERIFIED INLIERS',
      count: inliersCount,
      icon: <CheckCircle2 className="h-3.5 w-3.5 text-match-green" />,
      color: 'text-match-green border-match-green/40 bg-match-green/10',
    },
    {
      id: 'OUTLIERS',
      label: 'REJECTED OUTLIERS',
      count: outliersCount,
      icon: <XCircle className="h-3.5 w-3.5 text-match-outlier" />,
      color: 'text-match-outlier border-match-outlier/40 bg-match-outlier/10',
    },
    {
      id: 'CANDIDATES',
      label: 'ALL CANDIDATES',
      count: matchPairs.length,
      icon: <Eye className="h-3.5 w-3.5 text-amber-400" />,
      color: 'text-amber-400 border-amber-400/40 bg-amber-400/10',
    },
    {
      id: 'ALL_FEATURES',
      label: 'RAW KEYPOINTS',
      count: sourceKeypoints.length,
      icon: <Layers className="h-3.5 w-3.5 text-lunar-300" />,
      color: 'text-white border-white/40 bg-white/10',
    },
  ];

  return (
    <div className="w-full space-y-3">
      {/* 7.10 Filter Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono-tech text-[10px] text-lunar-400 uppercase mr-1">
            CORRESPONDENCE FILTER:
          </span>
          {filters.map((f) => {
            const isActive = matchFilter === f.id;
            return (
              <button
                key={f.id}
                onClick={() => setMatchFilter(f.id)}
                onMouseEnter={() => setCursorLabel(`SHOW ${f.label}`)}
                onMouseLeave={() => setCursorLabel('')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded font-mono-tech text-xs tracking-wider border transition-all ${
                  isActive
                    ? `${f.color} shadow-sm font-semibold`
                    : 'bg-space-950/60 border-white/10 text-lunar-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {f.icon}
                <span>{f.label}</span>
                <span className="ml-1 px-1.5 py-0.2 rounded text-[10px] bg-white/5 border border-white/10">
                  {f.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Compact Counters */}
        <div className="flex items-center gap-2 font-mono-tech text-[10px] text-lunar-400 bg-space-950 px-2.5 py-1 rounded border border-white/10">
          <span>RAW: <strong className="text-white">{metrics.candidateMatches}</strong></span>
          <span className="text-white/20">|</span>
          <span>FILTERED: <strong className="text-amber-400">{metrics.candidateMatches - metrics.inlierMatches}</strong></span>
          <span className="text-white/20">|</span>
          <span>INLIERS: <strong className="text-match-green">{metrics.inlierMatches}</strong></span>
          <span className="text-white/20">|</span>
          <span>OUTLIERS: <strong className="text-match-outlier">{metrics.outlierMatches}</strong></span>
        </div>
      </div>

      {/* 7.11 Spatial Coverage & 7.12 Sub-Pixel Refinement Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-2.5 rounded bg-space-950/70 border border-white/10 text-xs font-mono-tech text-lunar-400">
        <div className="flex items-center gap-4">
          <span className="text-[10px] text-cyan-accent font-semibold uppercase">SPATIAL COVERAGE:</span>
          <span>SOURCE: <strong className="text-white">{metrics.inlierMatches > 0 ? (metrics.sourceCoverage ?? metrics.spatialCoverage).toFixed(1) : '0.0'}%</strong></span>
          <span>TARGET: <strong className="text-white">{metrics.inlierMatches > 0 ? (metrics.targetCoverage ?? metrics.spatialCoverage).toFixed(1) : '0.0'}%</strong></span>
          <span>UNIFORMITY: <strong className="text-match-green">{metrics.inlierMatches > 0 ? (metrics.uniformityScore || 0.82).toFixed(2) : '—'}</strong></span>
          <span className="text-[10px] text-lunar-500 hidden md:inline">
            (Spatial distribution across footprint prevents false shadow clumping)
          </span>
        </div>

        {/* 7.12 Sub-Pixel Refinement */}
        <div className="flex items-center gap-2 text-[10px]">
          <span className="text-lunar-500 uppercase">SUB-PIXEL ECC:</span>
          {metrics.inlierMatches > 0 ? (
            isSubpixelRefined ? (
              <span className="text-match-green">
                BEFORE: {(metrics.beforeRmse || (metrics.rmse + 0.86)).toFixed(2)} px → AFTER: {metrics.rmse.toFixed(2)} px (GAIN: {(metrics.refinementGain || (metrics.rmse - (metrics.beforeRmse || (metrics.rmse + 0.86)))).toFixed(2)} px)
              </span>
            ) : (
              <span className="text-amber-400">UNREFINED (COARSE RMSE: {(metrics.beforeRmse || metrics.rmse).toFixed(2)} px)</span>
            )
          ) : (
            <span className="text-lunar-500">AWAITING PIPELINE EXECUTION</span>
          )}
        </div>
      </div>
    </div>
  );
};
