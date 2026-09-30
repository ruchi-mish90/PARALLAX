import { PipelineStageInfo, Keypoint, MatchPair, AlignmentMetrics, HomographyMatrix } from '../types/correspondence';

export const PIPELINE_STAGES: PipelineStageInfo[] = [
  {
    id: '01_PAIR_FORMATION',
    stageNumber: '01',
    scientificTitle: 'Pair Formation & Ingestion',
    explainTitle: 'Load Observation Pair',
    scientificDescription: 'Ingests orbital observation metadata, sensor ephemeris, camera geometry matrices, and establishes initial overlapping bounding footprints.',
    explainDescription: 'The system selects two satellite photos of the lunar surface and verifies that their viewing areas overlap.',
    algorithm: 'IAU/IAG Selenographic Coordinate Footprint Intersector',
    parameters: { footprintIntersection: '84.2%', coordinateDatum: 'Mean Earth/Polar Axis (ME)' },
    status: 'completed'
  },
  {
    id: '02_PREPROCESSING',
    stageNumber: '02',
    scientificTitle: 'Sensor & Physics-Aware Preprocessing',
    explainTitle: 'Calibrate & Balance Lighting',
    scientificDescription: 'Non-Local Means (NLM) de-striping, dark-signal non-uniformity (DSNU) normalization, and Rayleigh-distributed CLAHE to reveal micro-relief inside polar shadows.',
    explainDescription: 'Removes camera sensor lines and brightens deep crater shadows so rock features become clear without blowing out sunny ridges.',
    algorithm: 'NLM Denoising + CLAHE (Tile Grid: 16x16, Clip Limit: 3.2)',
    parameters: { clipLimit: 3.2, tilesX: 16, tilesY: 16, filterWindow: '7x7' },
    status: 'completed'
  },
  {
    id: '03_PAIR_CHARACTERIZATION',
    stageNumber: '03',
    scientificTitle: 'Pair Characterization & Difficulty Estimation',
    explainTitle: 'Diagnose Pair Difficulty',
    scientificDescription: 'Evaluates ground sampling distance ratio (GSD), multi-spectral modality gap, solar illumination difference, texture entropy, and determines overall pair difficulty.',
    explainDescription: 'The system checks how different the two photos are in zoom level, camera type, and sun angle to rate difficulty (Easy / Medium / Hard).',
    algorithm: 'Multi-Factor Remote-Sensing Difficulty Estimator',
    parameters: { gsdDisparityRatio: '20:1', modalityGap: 'Panchromatic vs Stereo', difficulty: 'Medium' },
    status: 'completed'
  },
  {
    id: '04_ADAPTIVE_ROUTER',
    stageNumber: '04',
    scientificTitle: 'Adaptive Model Router & Strategy Selection',
    explainTitle: 'Select Best Matching Tool',
    scientificDescription: 'Ranks model bank candidates (RIFT, HOPC, CFOG, SuperPoint+LightGlue, LoFTR, SIFT) and selects the optimal structural or feature matching engine.',
    explainDescription: 'Instead of forcing the same matching algorithm on every photo, PARALLAX picks the model best equipped for this specific pair.',
    algorithm: 'Pair-Aware Model Scoring & Strategy Selection Heuristic',
    parameters: { rankedTopCandidate: 'RIFT (Phase Congruency)', suitabilityScore: 96, confidenceMargin: '+12%' },
    status: 'completed'
  },
  {
    id: '05_CORRESPONDENCE',
    stageNumber: '05',
    scientificTitle: 'Feature Extraction & Candidate Matching',
    explainTitle: 'Extract & Pair Up Landmarks',
    scientificDescription: 'Executes the selected correspondence strategy (Log-Gabor phase congruency / scale-space pyramids) with nearest-neighbor indexing and ambiguity ratio tests.',
    explainDescription: 'Finds unique landmarks (crater edges, boulders, ridge bends) in both images and pairs them up with fingerprint matching.',
    algorithm: 'Phase Congruency Feature Mapping + Mutual Ratio Filtering',
    parameters: { rawExtracted: 0, initialCandidates: 0, ratioThreshold: 0.72 },
    status: 'pending'
  },
  {
    id: '06_RANSAC_VERIFICATION',
    stageNumber: '06',
    scientificTitle: 'Robust Geometric Verification (MSAC / RANSAC)',
    explainTitle: 'Filter False Matches with Geometry',
    scientificDescription: 'M-estimator Sample Consensus (MSAC) testing transformation hypotheses with reprojection threshold to eliminate false matches caused by migrating shadows.',
    explainDescription: 'Tests geometric formulas to find the single real perspective connecting true matches, throwing away misleading shadows.',
    algorithm: 'USAC / MSAC Projective Consensus (Max Iter: 2000)',
    parameters: { maxIterations: 2000, reprojectionThreshold: 2.5 },
    status: 'pending'
  },
  {
    id: '07_SPATIAL_ANMS',
    stageNumber: '07',
    scientificTitle: 'Spatial Distribution & ANMS Enforcement',
    explainTitle: 'Spread Out Landmarks Evenly',
    scientificDescription: 'Adaptive Non-Maximal Suppression (ANMS) enforces global spatial dispersion across the image footprint, preventing unstable point clustering on single crater rims.',
    explainDescription: 'Ensures landmarks are spread evenly across the whole scene rather than clumped in one tiny corner, making the alignment stable.',
    algorithm: 'Brown-Szeliski Adaptive Non-Maximal Suppression (ANMS)',
    parameters: { suppressionRadius: '120 px' },
    status: 'pending'
  },
  {
    id: '08_SUBPIXEL_REFINEMENT',
    stageNumber: '08',
    scientificTitle: 'Sub-Pixel Local Refinement (ECC)',
    explainTitle: 'Fine-Tune Alignment to Fractions of a Pixel',
    scientificDescription: 'Enhanced Correlation Coefficient (ECC) optimization iteratively adjusts projective matrix H coordinates to achieve sub-pixel spatial convergence.',
    explainDescription: 'Fine-tunes the mathematical alignment down to fractions of a single camera pixel for pinpoint accuracy.',
    algorithm: 'Enhanced Correlation Coefficient (ECC) Non-Linear Optimizer',
    parameters: { convergenceDelta: '1e-5', maxIterations: 50 },
    status: 'pending'
  },
  {
    id: '09_QUALITY_UNCERTAINTY',
    stageNumber: '09',
    scientificTitle: 'Quality Assessment & Uncertainty Quantification',
    explainTitle: 'Evaluate Alignment Trustworthiness',
    scientificDescription: 'Computes reprojection RMSE, 1-sigma uncertainty bounds, inlier ratio, and validates against target quality gates.',
    explainDescription: 'Checks whether the mathematical alignment passes quality safety standards before declaring success.',
    algorithm: 'Covariance-Based Uncertainty Estimator & Quality Gate Verifier',
    parameters: { qualityStatus: 'PENDING', targetThresholdMet: '< 1.5 px' },
    status: 'pending'
  },
  {
    id: '10_REGISTERED_OUTPUT',
    stageNumber: '10',
    scientificTitle: 'Orthorectified Co-Registered Output',
    explainTitle: 'Final Aligned Product Ready',
    scientificDescription: 'Generates warp-registered multi-sensor composite with pixel-accurate correspondence vectors ready for DEM projection and mineralogical mapping.',
    explainDescription: 'The two satellite images are now geometrically locked onto the exact same lunar terrain with subpixel accuracy.',
    algorithm: 'Bilinear Projective Image Warper & Composite Generator',
    parameters: { projectionFrame: 'IAU Moon 2000' },
    status: 'pending'
  }
];

// Clean Zero/Initial State (Populated exclusively by live backend telemetry)
export const INITIAL_SOURCE_KEYPOINTS: Keypoint[] = [];
export const INITIAL_TARGET_KEYPOINTS: Keypoint[] = [];
export const INITIAL_MATCH_PAIRS: MatchPair[] = [];

export const INITIAL_HOMOGRAPHY: HomographyMatrix = [
  [1.0, 0.0, 0.0],
  [0.0, 1.0, 0.0],
  [0.0, 0.0, 1.0]
];

export const INITIAL_ALIGNMENT_METRICS: AlignmentMetrics = {
  totalFeaturesSource: 0,
  totalFeaturesTarget: 0,
  candidateMatches: 0,
  inlierMatches: 0,
  outlierMatches: 0,
  inlierRatio: 0,
  rmse: 0,
  uncertaintyPx: 0,
  precision: 0,
  recall: 0,
  f1Score: 0,
  spatialCoverage: 0,
  confidenceScore: 0,
  qualityGateStatus: 'PASSED',
  evidenceType: 'MEASURED_BENCHMARK',
  selectedModelName: 'AUTO (PENDING RUN)',
  tmcBridgeActive: false,
  transformationType: 'HOMOGRAPHY',
  homographyMatrix: INITIAL_HOMOGRAPHY,
  sourceCoverage: 0,
  targetCoverage: 0,
  uniformityScore: 0,
  beforeRmse: 0,
  afterRmse: 0,
  refinementGain: 0,
  meanError: 0,
  medianError: 0,
  maxError: 0,
  processingTimeMs: 0,
};

// Aliases for clean backward-compatibility with live backend state
export const MOCK_SOURCE_KEYPOINTS = INITIAL_SOURCE_KEYPOINTS;
export const MOCK_TARGET_KEYPOINTS = INITIAL_TARGET_KEYPOINTS;
export const MOCK_MATCH_PAIRS = INITIAL_MATCH_PAIRS;
export const MOCK_ALIGNMENT_METRICS = INITIAL_ALIGNMENT_METRICS;
export const MOCK_HOMOGRAPHY = INITIAL_HOMOGRAPHY;
