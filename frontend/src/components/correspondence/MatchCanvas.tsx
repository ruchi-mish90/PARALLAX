import React from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { MatchPair } from '../../types/correspondence';

interface MatchCanvasProps {
  containerWidth: number;
  containerHeight: number;
}

export const MatchCanvas: React.FC<MatchCanvasProps> = ({ containerWidth, containerHeight }) => {
  const { 
    filteredMatches, 
    sourceKeypoints, 
    targetKeypoints, 
    matchFilter, 
    hoveredMatch, 
    setHoveredMatch, 
    setCursorLabel, 
    explainMode 
  } = useParallax();

  // Coordinates mapping:
  // Left image occupies 0% to 50% width
  // Right image occupies 50% to 100% width
  const halfWidth = containerWidth / 2;

  // NASA-inspired muted semantic functional colors
  const COLOR_INLIER = '#4E9A51'; // Muted sage for ACCEPT
  const COLOR_OUTLIER = '#C64343'; // Muted rust for REJECT

  return (
    <svg
      className="absolute inset-0 pointer-events-auto w-full h-full z-20"
      viewBox={`0 0 ${containerWidth} ${containerHeight}`}
    >
      {/* MATCH LINES */}
      {matchFilter !== 'ALL_FEATURES' && filteredMatches.map((pair: MatchPair) => {
        // Source point on Left Panel
        const x1 = (pair.sourceKeypoint.x / 100) * halfWidth;
        const y1 = (pair.sourceKeypoint.y / 100) * containerHeight;

        // Target point on Right Panel
        const x2 = halfWidth + (pair.targetKeypoint.x / 100) * halfWidth;
        const y2 = (pair.targetKeypoint.y / 100) * containerHeight;

        const isHovered = hoveredMatch?.id === pair.id;
        const strokeColor = pair.isRansacInlier ? COLOR_INLIER : COLOR_OUTLIER;

        // Subtle curve through center gap
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2;

        return (
          <g key={pair.id} className="cursor-pointer transition-opacity duration-150">
            {/* Wider transparent hit-area for easy mouse hover */}
            <path
              d={`M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}`}
              fill="none"
              stroke="transparent"
              strokeWidth="14"
              onMouseEnter={() => {
                setHoveredMatch(pair);
                setCursorLabel(
                  pair.isRansacInlier 
                    ? `INLIER #${pair.id} • RESIDUAL: ${pair.residualError.toFixed(2)}px` 
                    : `OUTLIER #${pair.id} • REJECTED BY RANSAC`
                );
              }}
              onMouseLeave={() => {
                setHoveredMatch(null);
                setCursorLabel('');
              }}
            />

            {/* Visual match vector line - Sharp, crisp 1px scientific vector */}
            <path
              d={`M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}`}
              fill="none"
              stroke={strokeColor}
              strokeWidth={isHovered ? 2.0 : pair.isRansacInlier ? 1.0 : 0.8}
              strokeDasharray={pair.isRansacInlier ? 'none' : '3 3'}
              opacity={
                hoveredMatch
                  ? isHovered ? 1.0 : 0.15
                  : pair.isRansacInlier ? 0.75 : 0.35
              }
            />
          </g>
        );
      })}

      {/* SOURCE KEYPOINTS (Left Panel) */}
      {sourceKeypoints.map((kp) => {
        const cx = (kp.x / 100) * halfWidth;
        const cy = (kp.y / 100) * containerHeight;
        const isAssociated = hoveredMatch?.sourceKeypoint.id === kp.id;

        return (
          <g key={`src-${kp.id}`}>
            <circle
              cx={cx}
              cy={cy}
              r={isAssociated ? 4.5 : 2.5}
              fill="#F7F7F5"
              fillOpacity={isAssociated ? 1.0 : 0.8}
              stroke="#111111"
              strokeWidth="1"
            />
            {isAssociated && (
              <circle
                cx={cx}
                cy={cy}
                r="7"
                fill="none"
                stroke="#F7F7F5"
                strokeWidth="1"
              />
            )}
          </g>
        );
      })}

      {/* TARGET KEYPOINTS (Right Panel) */}
      {targetKeypoints.map((kp) => {
        const cx = halfWidth + (kp.x / 100) * halfWidth;
        const cy = (kp.y / 100) * containerHeight;
        const isAssociated = hoveredMatch?.targetKeypoint.id === kp.id;

        return (
          <g key={`tgt-${kp.id}`}>
            <circle
              cx={cx}
              cy={cy}
              r={isAssociated ? 4.5 : 2.5}
              fill="#C0C0BD"
              fillOpacity={isAssociated ? 1.0 : 0.8}
              stroke="#111111"
              strokeWidth="1"
            />
            {isAssociated && (
              <circle
                cx={cx}
                cy={cy}
                r="7"
                fill="none"
                stroke="#C0C0BD"
                strokeWidth="1"
              />
            )}
          </g>
        );
      })}

      {/* HOVERED MATCH METADATA TOOLTIP */}
      {hoveredMatch && (
        <g>
          <rect
            x={halfWidth - 95}
            y={24}
            width="190"
            height="52"
            fill="#161616"
            stroke={hoveredMatch.isRansacInlier ? COLOR_INLIER : COLOR_OUTLIER}
            strokeWidth="1"
          />
          <text
            x={halfWidth}
            y={42}
            textAnchor="middle"
            fill="#F7F7F5"
            fontFamily="Inter, sans-serif"
            fontSize="11"
            fontWeight="600"
          >
            {hoveredMatch.isRansacInlier 
              ? (explainMode ? '✓ Verified Correspondence' : `✓ RANSAC Inlier #${hoveredMatch.id}`)
              : (explainMode ? '✗ Misaligned Outlier' : `✗ Outlier #${hoveredMatch.id}`)}
          </text>
          <text
            x={halfWidth}
            y={60}
            textAnchor="middle"
            fill="#8C8C89"
            fontFamily="IBM Plex Mono, monospace"
            fontSize="9.5"
          >
            Res: {hoveredMatch.residualError.toFixed(2)} px • Conf: {(hoveredMatch.confidence * 100).toFixed(0)}%
          </text>
        </g>
      )}
    </svg>
  );
};
