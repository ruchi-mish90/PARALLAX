import { InstrumentId } from './instruments';

export type DifficultyLevel = 'Easy' | 'Medium' | 'Hard';

export interface LunarImageProduct {
  id: string;
  productId: string;
  instrument: InstrumentId | 'LROC_NAC' | 'LOLA_DEM';
  instrumentLabel: string;
  label: string;
  gsd: number; // ground sampling distance in meters/px
  gsdDisplay: string;
  modality: string;
  orbitNumber?: number;
  solarElevation: number; // in degrees
  solarAzimuth: number; // in degrees
  acquisitionDate: string;
  thumbnailUrl: string;
  validPixelRatio: number; // percentage e.g. 98.4
  regionId: string;
  channelInfo?: string;
  sensorDescription: string;
}

export type PipelineStageId = 
  | '01_PAIR_FORMATION'
  | '02_PREPROCESSING'
  | '03_PAIR_CHARACTERIZATION'
  | '04_ADAPTIVE_ROUTER'
  | '05_CORRESPONDENCE'
  | '06_RANSAC_VERIFICATION'
  | '07_SPATIAL_ANMS'
  | '08_SUBPIXEL_REFINEMENT'
  | '09_QUALITY_UNCERTAINTY'
  | '10_REGISTERED_OUTPUT';

export interface PipelineStageInfo {
  id: PipelineStageId;
  stageNumber: string;
  scientificTitle: string;
  explainTitle: string;
  scientificDescription: string;
  explainDescription: string;
  algorithm: string;
  parameters: Record<string, string | number>;
  status: 'pending' | 'active' | 'completed';
}

export interface Keypoint {
  id: number;
  x: number; // normalized 0-100%
  y: number; // normalized 0-100%
  scale: number;
  orientation: number;
  response: number;
  instrument: InstrumentId;
  isAnmsSelected?: boolean; // filtered by Adaptive Non-Maximal Suppression
}

export interface MatchPair {
  id: number;
  sourceKeypoint: Keypoint;
  targetKeypoint: Keypoint;
  distance: number;
  confidence: number;
  isRansacInlier: boolean;
  isAnmsSelected: boolean; // meets spatial dispersion criteria
  residualError: number; // in pixels
}

export type ModelId = 
  | 'SIFT'
  | 'RIFT'
  | 'HOPC'
  | 'CFOG'
  | 'SUPERPOINT_LIGHTGLUE'
  | 'LOFTR';

export interface ModelCandidate {
  id: ModelId;
  name: string;
  category: 'Structural' | 'Phase Congruency' | 'Gradient' | 'Learned Feature' | 'Dense Matching' | 'Classical Baseline';
  description: string;
  suitabilityScore: number; // 0 - 100
  rank: number; // 1 to 6
  isRecommended: boolean;
  strengths: string[];
  weaknesses: string[];
  selectionRationale: string;
}

export interface PairCharacterization {
  scaleRatio: number; // e.g. 20, 320, 16, 1
  scaleRatioDisplay: string; // e.g. "20:1"
  modalityDifference: 'Low' | 'Moderate' | 'Severe';
  illuminationDifference: 'Minimal' | 'Moderate' | 'Extreme';
  textureEntropy: number; // e.g. 6.8 / 8.0 bits
  estimatedOverlap: number; // percentage e.g. 84%
  validPixelRatio: number; // percentage e.g. 96.5%
  viewpointGeometryDiff: 'Near-Nadir' | 'Moderate Triplet' | 'Wide Stereo';
  overallDifficulty: DifficultyLevel;
  difficultyRationale: string;
  suggestTmcBridge: boolean; // Proposed conditional OHRC -> TMC-2 -> IIRS intermediate bridge
}

export type EvidenceType = 'MEASURED_BENCHMARK' | 'TARGET_QUALITY_GATE' | 'SIMULATED_ILLUSTRATIVE';

export type QualityGateStatus = 'PASSED' | 'WARNING' | 'FAILED' | 'CONDITIONAL_BRIDGE';

export interface AlignmentMetrics {
  totalFeaturesSource: number;
  totalFeaturesTarget: number;
  candidateMatches: number;
  inlierMatches: number;
  outlierMatches: number;
  inlierRatio: number; // percentage e.g. 80.0%
  rmse: number; // root mean square error in pixels e.g. 1.28 px
  uncertaintyPx: number; // 1-sigma uncertainty e.g. +/- 0.14 px
  precision: number; // e.g. 92.4%
  recall: number; // e.g. 85.6%
  f1Score: number; // e.g. 0.888
  spatialCoverage: number; // e.g. 74.2% (ANMS dispersion score)
  confidenceScore: number; // e.g. 88.5%
  qualityGateStatus: QualityGateStatus;
  evidenceType: EvidenceType;
  selectedModelName: string;
  tmcBridgeActive: boolean;
  transformationType?: 'HOMOGRAPHY' | 'AFFINE' | 'LOCAL_PIECEWISE' | 'SPLINE';
  affineMatrix?: number[][]; // 2x3 matrix
  sourceCoverage?: number; // e.g. 78.4%
  targetCoverage?: number; // e.g. 71.9%
  uniformityScore?: number; // e.g. 0.82
  beforeRmse?: number; // e.g. 2.14 px
  afterRmse?: number; // e.g. 1.28 px
  refinementGain?: number; // e.g. -0.86 px
  meanError?: number;
  medianError?: number;
  maxError?: number;
}

export type ViewerState = 'ORIGINAL' | 'PREPROCESSED' | 'REGISTERED';

export type ObservabilityStatus = 'OBSERVABLE' | 'BLOCKED_NO_OVERLAP';

export type MatchFilterType = 'ALL_FEATURES' | 'CANDIDATES' | 'INLIERS' | 'OUTLIERS' | 'ANMS_ONLY';

export type ComparisonMode = 'SIDE_BY_SIDE' | 'OVERLAY' | 'SWIPE' | 'DIFFERENCE' | 'CORRESPONDENCE';

export type HomographyMatrix = number[][];

