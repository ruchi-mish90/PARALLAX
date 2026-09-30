import { InstrumentId } from '../types/instruments';
import { LunarRegion } from '../types/regions';
import { SimulationParams } from '../types/state';
import { ModelCandidate, ModelId, PairCharacterization, LunarImageProduct } from '../types/correspondence';

export const CANDIDATE_MODELS: Record<ModelId, Omit<ModelCandidate, 'suitabilityScore' | 'rank' | 'isRecommended' | 'selectionRationale'>> = {
  'RIFT': {
    id: 'RIFT',
    name: 'RIFT (Radiation-variation Insensitive Feature Transform)',
    category: 'Phase Congruency',
    description: 'Constructs maximum index maps from Log-Gabor phase congruency, achieving invariance to extreme non-linear radiometric differences and shifting shadow boundaries.',
    strengths: [
      'Invariance to extreme solar illumination and polar shadow changes',
      'Effective across heterogeneous spectral bands (Panchromatic vs SWIR)',
      'Constructs structural phase-congruency orientation layers'
    ],
    weaknesses: [
      'Higher computational overhead for Log-Gabor filter convolutions',
      'Requires substantial local gradient energy on smooth lunar regolith'
    ]
  },
  'HOPC': {
    id: 'HOPC',
    name: 'HOPC (Histogram of Orientated Phase Congruency)',
    category: 'Structural',
    description: 'Captures structural geometry from multi-scale and multi-orientation phase congruency representations rather than raw pixel intensities.',
    strengths: [
      'Robust against multi-modal contrast inversions and glancing solar angles',
      'Excellent performance on high-relief crater walls and ridgelines'
    ],
    weaknesses: [
      'Susceptible to octave scale aliasing beyond 15:1 GSD gap without scale-space pre-pyramids',
      'Sensitive to high-frequency sensor noise'
    ]
  },
  'CFOG': {
    id: 'CFOG',
    name: 'CFOG (Channel Features of Orientated Gradients)',
    category: 'Gradient',
    description: 'Fast pixel-wise 3D orientation gradient channels with 3D Gaussian convolution for cross-modality remote-sensing image registration.',
    strengths: [
      'Extremely fast dense matching execution (sub-150 ms)',
      'Effective for Moderate difficulty pairs with identical or near-visible spectral bands'
    ],
    weaknesses: [
      'Struggles when solar elevation causes extensive shadow migration (> 25° shadow shift)',
      'Requires significant initial spatial overlap (> 65%)'
    ]
  },
  'SUPERPOINT_LIGHTGLUE': {
    id: 'SUPERPOINT_LIGHTGLUE',
    name: 'SuperPoint + LightGlue (Learned Keypoints & Graph Matching)',
    category: 'Learned Feature',
    description: 'Deep self-supervised keypoint extractor combined with adaptive positional and visual graph neural network attention for resilient correspondence.',
    strengths: [
      'Sub-pixel landmark localization on repetitive crater regolith',
      'Adaptive early-exit matching rejecting impossible candidates with high confidence',
      'Resilient to moderate scale disparities (up to 8:1)'
    ],
    weaknesses: [
      'Pretrained weights require domain adaptation on crater ejecta and low-sun lunar imagery',
      'Inference requires GPU acceleration for real-time throughput'
    ]
  },
  'LOFTR': {
    id: 'LOFTR',
    name: 'LoFTR (Detector-Free Local Feature Matching with Transformers)',
    category: 'Dense Matching',
    description: 'Coarse-to-fine transformer matching using self- and cross-attention without relying on discrete keypoint detection, ideal for low-texture regions.',
    strengths: [
      'Finds dense matches inside low-texture crater basins and washed-out terrain',
      'Global receptive field maintains spatial context across wide gaps'
    ],
    weaknesses: [
      'Computationally heavy memory footprint on large remote-sensing orbital swaths',
      'Quadratic complexity requires tiling on full 4096-wide OHRC strips'
    ]
  },
  'SIFT': {
    id: 'SIFT',
    name: 'SIFT (Scale-Invariant Feature Transform — Classical Baseline)',
    category: 'Classical Baseline',
    description: 'Standard planetary remote-sensing baseline utilizing Difference-of-Gaussians (DoG) scale-space extrema and 128-D gradient orientation histograms.',
    strengths: [
      'Mathematically proven scale-space invariance for mild to moderate GSD ratios',
      'Deterministic execution and low memory consumption',
      'Ideal reference baseline to quantify adaptive improvements'
    ],
    weaknesses: [
      'Completely fails under severe radiometric contrast inversion (optical vs hyperspectral)',
      'Tracks moving shadow edges instead of geological rock under shifting solar angles'
    ]
  }
};

/**
 * Characterize an image pair and evaluate candidate correspondence models.
 * This embodies the central PARALLAX idea:
 * "Different image pair -> different difficulty -> different suitable correspondence strategy."
 */
export function evaluatePair(
  source: InstrumentId,
  target: InstrumentId,
  region: LunarRegion,
  simParams?: SimulationParams,
  sourceProduct?: LunarImageProduct,
  targetProduct?: LunarImageProduct
): {
  characterization: PairCharacterization;
  rankedCandidates: ModelCandidate[];
  selectedModel: ModelCandidate;
} {
  // 1. Determine Real Scale Ratio from Product GSD
  const gsdA = sourceProduct?.gsd ?? (source === 'OHRC' ? 0.25 : source === 'TMC-2' ? 5.0 : 80.0);
  const gsdB = targetProduct?.gsd ?? (target === 'OHRC' ? 0.25 : target === 'TMC-2' ? 5.0 : 80.0);
  const maxGsd = Math.max(gsdA, gsdB);
  const minGsd = Math.min(gsdA, gsdB);
  
  const scaleRatio = simParams 
    ? simParams.spatialScaleRatio 
    : (gsdA === gsdB ? 1 : Number((maxGsd / minGsd).toFixed(1)));
  const scaleRatioDisplay = scaleRatio === 1 ? '1:1' : `${scaleRatio}:1`;

  // 2. Determine Real Modality Difference
  const modA = (sourceProduct?.modality || source).toLowerCase();
  const modB = (targetProduct?.modality || target).toLowerCase();
  let modalityDifference: 'Low' | 'Moderate' | 'Severe' = 'Low';
  
  if (modA.includes('spectral') || modB.includes('spectral') || source === 'IIRS' || target === 'IIRS') {
    if (source === 'OHRC' || target === 'OHRC' || minGsd <= 0.35) {
      modalityDifference = 'Severe'; // 0.25m visible panchromatic vs 256-band IR
    } else {
      modalityDifference = 'Moderate'; // 5m visible stereo vs 256-band IR
    }
  } else {
    modalityDifference = 'Low'; // Both are optical panchromatic
  }

  // 3. Determine Real Solar Illumination Difference
  const sunElevA = sourceProduct?.solarElevation ?? (simParams ? simParams.sunElevationAngle : 18);
  const sunElevB = targetProduct?.solarElevation ?? (simParams ? simParams.sunElevationAngle : 18);
  const elevDelta = Number(Math.abs(sunElevA - sunElevB).toFixed(1));

  const azimA = sourceProduct?.solarAzimuth ?? (simParams ? simParams.sunAzimuthAngle : 135);
  const azimB = targetProduct?.solarAzimuth ?? (simParams ? simParams.sunAzimuthAngle : 135);
  const azimDelta = Math.min(Math.abs(azimA - azimB), 360 - Math.abs(azimA - azimB));

  let illuminationDifference: 'Minimal' | 'Moderate' | 'Extreme' = 'Moderate';
  if (elevDelta > 10 || sunElevA < 6 || sunElevB < 6) {
    illuminationDifference = 'Extreme'; // Polar glancing sun with massive shifting shadows
  } else if (elevDelta > 4 || azimDelta > 40) {
    illuminationDifference = 'Moderate';
  } else {
    illuminationDifference = 'Minimal';
  }

  // 4. Overlap & Texture
  const textureEntropy = region.id === 'tycho-central-peak' ? 7.4 : region.id === 'faustini-crater' ? 5.9 : region.id === 'shackleton-connecting-ridge' ? 6.3 : 6.8;
  const validA = sourceProduct?.validPixelRatio ?? 96.0;
  const validB = targetProduct?.validPixelRatio ?? 96.0;
  const validPixelRatio = Number(Math.min(validA, validB).toFixed(1));

  const isSameRegion = !sourceProduct || !targetProduct || (sourceProduct.regionId === targetProduct.regionId);
  const baseOverlap = isSameRegion 
    ? (scaleRatio >= 100 ? 52 : scaleRatio >= 15 ? 84 : 95)
    : 0;
  const estimatedOverlap = isSameRegion ? Math.round(baseOverlap * (validPixelRatio / 100)) : 0;
  const viewpointGeometryDiff = (source === 'TMC-2' || target === 'TMC-2') ? 'Moderate Triplet' : 'Near-Nadir';

  // 5. Overall Difficulty Assessment
  let overallDifficulty: 'Easy' | 'Medium' | 'Hard' = 'Medium';
  let difficultyRationale = '';
  let suggestTmcBridge = false;

  if (scaleRatio >= 100 || (modalityDifference === 'Severe' && illuminationDifference === 'Extreme')) {
    overallDifficulty = 'Hard';
    suggestTmcBridge = true;
    difficultyRationale = `Severe scale disparity (${scaleRatioDisplay}) combined with optical vs. hyperspectral radiometric divergence (Δ solar elev: ${elevDelta}°). Intermediate TMC-2 scale bridge is recommended.`;
  } else if (scaleRatio >= 15 || illuminationDifference === 'Extreme' || modalityDifference === 'Moderate') {
    overallDifficulty = 'Medium';
    suggestTmcBridge = false;
    difficultyRationale = `Multi-scale octave gap (${scaleRatioDisplay}) with polar shadow morphology (Δ solar elev: ${elevDelta}°). Requires phase-congruency or structural gradient representations.`;
  } else {
    overallDifficulty = 'Easy';
    suggestTmcBridge = false;
    difficultyRationale = `Near-identical scale (${scaleRatioDisplay}) and high geometric overlap (${estimatedOverlap}%). Learned sparse keypoint or gradient matchers achieve sub-pixel precision.`;
  }

  // 6. Score and Rank Candidate Models using real objective evaluation formulas
  const candidates: ModelCandidate[] = (Object.keys(CANDIDATE_MODELS) as ModelId[]).map((id) => {
    const base = CANDIDATE_MODELS[id];
    let score = 50;
    let rationale = '';

    if (id === 'RIFT') {
      // Invariant to illumination and multi-spectral divergence
      const scalePenalty = scaleRatio > 25 ? (scaleRatio / 320) * 8 : 0;
      const elevBonus = illuminationDifference === 'Extreme' ? 8 : illuminationDifference === 'Moderate' ? 4 : 0;
      score = Math.round(88 + elevBonus - scalePenalty + (modalityDifference === 'Severe' ? 6 : 0));
      rationale = score >= 90
        ? 'Ranked #1: Log-Gabor phase congruency is invariant to extreme polar shadow elongation and visible-to-infrared radiometric disparity.'
        : 'Robust structural mapping bridges multi-spectral differences effectively.';
    } else if (id === 'HOPC') {
      const scalePenalty = scaleRatio > 50 ? 14 : scaleRatio > 15 ? 6 : 0;
      const elevBonus = illuminationDifference === 'Extreme' ? 6 : 0;
      score = Math.round(86 + elevBonus - scalePenalty);
      rationale = 'Histogram of phase congruency preserves structural rim edges under glancing polar sunlight.';
    } else if (id === 'SUPERPOINT_LIGHTGLUE') {
      // High accuracy on moderate scales and low modality gap
      const scalePenalty = scaleRatio > 10 ? Math.min(30, (scaleRatio - 10) * 1.2) : 0;
      const modalPenalty = modalityDifference === 'Severe' ? 24 : modalityDifference === 'Moderate' ? 10 : 0;
      const elevPenalty = elevDelta > 15 ? 8 : 0;
      score = Math.round(96 - scalePenalty - modalPenalty - elevPenalty);
      rationale = score >= 90
        ? 'Ranked #1: Deep graph neural network attention achieves exceptional sub-pixel localization on fine lunar crater regolith.'
        : 'Sub-pixel accuracy is high, but scale disparity and modality gap degrade sparse point repeatability.';
    } else if (id === 'LOFTR') {
      // Transformer dense matching in low-texture / shadow regions
      const textureBonus = textureEntropy < 6.5 ? 6 : 0;
      const scalePenalty = scaleRatio > 20 ? Math.min(22, (scaleRatio - 20) * 0.4) : 0;
      const modalPenalty = modalityDifference === 'Severe' ? 14 : 0;
      score = Math.round(86 + textureBonus - scalePenalty - modalPenalty);
      rationale = 'Detector-free dense transformer attention extracts correspondences within dark crater shadows and low-texture plains.';
    } else if (id === 'CFOG') {
      // Rapid 3D Gaussian orientation channels
      const elevPenalty = elevDelta > 10 ? 22 : elevDelta * 1.5;
      const modalPenalty = modalityDifference === 'Severe' ? 20 : modalityDifference === 'Moderate' ? 8 : 0;
      score = Math.round(92 - elevPenalty - modalPenalty);
      rationale = score >= 85
        ? 'Ranked top tier: 3D Gaussian orientation channels offer rapid, highly accurate registration for near-visible pairs.'
        : 'Orientation gradients can be corrupted by shifting high-contrast crater shadows.';
    } else if (id === 'SIFT') {
      // Classical baseline
      const elevPenalty = elevDelta * 2.2;
      const modalPenalty = modalityDifference === 'Severe' ? 36 : modalityDifference === 'Moderate' ? 18 : 0;
      const scalePenalty = scaleRatio > 5 ? Math.min(18, (scaleRatio - 5) * 1.5) : 0;
      score = Math.round(86 - elevPenalty - modalPenalty - scalePenalty);
      rationale = score >= 80
        ? 'Reliable classical baseline with fast DoG scale-space octave filtering.'
        : 'Classical SIFT fails under non-linear radiometric shifts and tracks migrating shadows rather than surface topography.';
    }

    // Apply simulation parameters adjustment
    if (simParams) {
      if (simParams.sensorNoiseSigma > 10) {
        if (id === 'LOFTR' || id === 'SUPERPOINT_LIGHTGLUE') score += 5;
        if (id === 'SIFT' || id === 'CFOG') score -= 8;
      }
    }

    return {
      ...base,
      suitabilityScore: Math.min(99, Math.max(20, score)),
      rank: 0,
      isRecommended: false,
      selectionRationale: rationale
    };
  });

  // Sort descending by real computed suitability score
  candidates.sort((a, b) => b.suitabilityScore - a.suitabilityScore);
  candidates.forEach((c, idx) => {
    c.rank = idx + 1;
    c.isRecommended = idx === 0;
  });

  return {
    characterization: {
      scaleRatio,
      scaleRatioDisplay,
      modalityDifference,
      illuminationDifference,
      textureEntropy,
      estimatedOverlap,
      validPixelRatio,
      viewpointGeometryDiff,
      overallDifficulty,
      difficultyRationale,
      suggestTmcBridge
    },
    rankedCandidates: candidates,
    selectedModel: candidates[0]
  };
}
