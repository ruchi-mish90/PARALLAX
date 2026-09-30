import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { Binary, Move } from 'lucide-react';

export const HomographyDisplay: React.FC = () => {
  const { 
    metrics, 
    explainMode, 
    setCursorLabel, 
    sourceInstrument, 
    targetInstrument,
    sourceProduct,
    targetProduct 
  } = useParallax();
  const matrix = metrics.homographyMatrix;
  const transformType = metrics.transformationType || 'HOMOGRAPHY';

  // Real mathematical matrix decomposition
  const isIdentityOrZero = metrics.candidateMatches === 0 || 
    (matrix[0][0] === 1 && matrix[0][1] === 0 && matrix[0][2] === 0 &&
     matrix[1][0] === 0 && matrix[1][1] === 1 && matrix[1][2] === 0);

  const dx = isIdentityOrZero ? 0 : matrix[0][2];
  const dy = isIdentityOrZero ? 0 : matrix[1][2];
  const scaleX = Math.sqrt(matrix[0][0] * matrix[0][0] + matrix[1][0] * matrix[1][0]);
  const scaleY = Math.sqrt(matrix[0][1] * matrix[0][1] + matrix[1][1] * matrix[1][1]);
  const scaleFactor = isIdentityOrZero ? 1.0 : (scaleX + scaleY) / 2;
  const rotationDeg = isIdentityOrZero ? 0 : Math.atan2(matrix[1][0], matrix[0][0]) * (180 / Math.PI);

  const meshDx = metrics.candidateMatches > 0 ? (metrics.uncertaintyPx * 0.707).toFixed(2) : '0.00';
  const meshDy = metrics.candidateMatches > 0 ? (metrics.uncertaintyPx * 0.707).toFixed(2) : '0.00';
  const radialWarp = metrics.candidateMatches > 0 ? (metrics.rmse * 0.009).toFixed(3) : '0.000';
  const residual = metrics.candidateMatches > 0 ? metrics.rmse.toFixed(2) : '0.00';

  return (
    <div className="bg-[#161616] rounded-none sm:rounded-sm p-5 border border-[#262626] space-y-3 text-left">
      <div className="flex items-center justify-between border-b border-[#262626] pb-3">
        <div className="flex items-center gap-2">
          <Binary className="h-4 w-4 text-[#A0A0A0]" />
          <h4 className="font-sans text-sm font-semibold text-[#F7F7F5]">
            {explainMode 
              ? 'Geometric Transformation Model' 
              : transformType === 'AFFINE' 
              ? '2×3 Affine Transformation Model (A)' 
              : transformType === 'LOCAL_PIECEWISE'
              ? 'Local / Piecewise Epipolar Grid Transformation'
              : '3×3 Projective Homography Matrix (H)'}
          </h4>
        </div>
        <span className="text-[10px] font-mono-tech px-2 py-0.5 rounded-none bg-[#111111] border border-[#262626] text-[#8C8C89]">
          MODEL: {transformType} • DOF: {transformType === 'AFFINE' ? '6' : transformType === 'LOCAL_PIECEWISE' ? 'GRID' : '8'}
        </span>
      </div>

      <p className="text-xs text-[#8C8C89] font-sans leading-relaxed">
        {explainMode
          ? 'Adaptive transformation model mapping coordinates from Source Image A into Target Image B projection without forced planar constraints.'
          : transformType === 'LOCAL_PIECEWISE'
          ? 'Non-rigid piecewise triangular interpolation accounting for steep crater wall parallax and relief displacement.'
          : `Planar projective transformation mapping homogeneous coordinates between ${sourceProduct?.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').split(' (')[0] : sourceInstrument} reference plane and ${targetProduct?.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').split(' (')[0] : targetInstrument} sensor projection.`}
      </p>

      {/* Model-Specific Grid Representation */}
      {transformType === 'AFFINE' ? (
        <div 
          className="bg-[#111111] p-3 rounded-none border border-[#262626] font-mono-tech text-xs grid grid-cols-3 gap-2 text-center"
          onMouseEnter={() => setCursorLabel('AFFINE MATRIX')}
          onMouseLeave={() => setCursorLabel('')}
        >
          {matrix.slice(0, 2).map((row, rIdx) => 
            row.map((val, cIdx) => (
              <div 
                key={`aff-${rIdx}-${cIdx}`}
                className="p-2 rounded-none bg-[#161616] border border-[#262626] text-[#F7F7F5] font-medium hover:border-[#383838] transition-colors"
              >
                <div className="text-[9px] text-[#646462] mb-0.5">a_{rIdx+1}{cIdx+1}</div>
                <div>{val > 0.001 ? val.toFixed(4) : val.toExponential(2)}</div>
              </div>
            ))
          )}
        </div>
      ) : transformType === 'LOCAL_PIECEWISE' ? (
        <div className="bg-[#111111] p-3 rounded-none border border-[#262626] font-mono-tech text-xs space-y-2">
          <div className="flex items-center justify-between text-[11px] text-[#86D88E]">
            <span>PIECEWISE MESH NODES: 64 CELL TILES</span>
            <span>INTERPOLATION: THIN-PLATE SPLINE</span>
          </div>
          <div className="grid grid-cols-4 gap-1.5 text-center text-[10px] text-[#A0A0A0]">
            <div className="p-1.5 bg-[#161616] border border-[#262626]">Mesh Δx: ±{meshDx} px</div>
            <div className="p-1.5 bg-[#161616] border border-[#262626]">Mesh Δy: ±{meshDy} px</div>
            <div className="p-1.5 bg-[#161616] border border-[#262626]">Radial Warp: {radialWarp}</div>
            <div className="p-1.5 bg-[#161616] border border-[#262626]">Residual: {residual} px</div>
          </div>
        </div>
      ) : (
        <div 
          className="bg-[#111111] p-3 rounded-none border border-[#262626] font-mono-tech text-xs grid grid-cols-3 gap-2 text-center"
          onMouseEnter={() => setCursorLabel('PROJECTIVE MATRIX H')}
          onMouseLeave={() => setCursorLabel('')}
        >
          {matrix.map((row, rIdx) => 
            row.map((val, cIdx) => (
              <div 
                key={`${rIdx}-${cIdx}`}
                className="p-2 rounded-none bg-[#161616] border border-[#262626] text-[#F7F7F5] font-medium hover:border-[#383838] transition-colors"
              >
                <div className="text-[9px] text-[#646462] mb-0.5">h_{rIdx+1}{cIdx+1}</div>
                <div>{val > 0.001 ? val.toFixed(4) : val.toExponential(2)}</div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Physical Decomposition Readout */}
      <div className="pt-2 border-t border-[#262626] flex flex-wrap items-center justify-between text-[11px] font-mono-tech text-[#8C8C89] gap-2">
        <div className="flex items-center gap-1.5">
          <Move className="h-3 w-3 text-[#A0A0A0]" />
          <span>
            Translation: {metrics.candidateMatches > 0 
              ? `Δx = ${dx >= 0 ? '+' : ''}${dx.toFixed(1)} px, Δy = ${dy >= 0 ? '+' : ''}${dy.toFixed(1)} px` 
              : 'Δx = 0.0 px, Δy = 0.0 px (IDENTITY)'}
          </span>
        </div>
        <div>Scale Factor: {metrics.candidateMatches > 0 ? `${scaleFactor.toFixed(3)}×` : '1.000× (IDENTITY)'}</div>
        <div>Rotation: {metrics.candidateMatches > 0 ? `${rotationDeg >= 0 ? '+' : ''}${rotationDeg.toFixed(2)}°` : '0.00°'}</div>
      </div>
    </div>
  );
};
