import { InstrumentId } from './instruments';
import { LunarRegion } from './regions';
import { 
  PipelineStageId, 
  MatchFilterType, 
  ComparisonMode, 
  AlignmentMetrics, 
  MatchPair, 
  Keypoint 
} from './correspondence';

export interface SimulationParams {
  sunElevationAngle: number; // 5 to 80 deg
  sunAzimuthAngle: number; // 0 to 360 deg
  spatialScaleRatio: number; // 1 to 20x
  sensorNoiseSigma: number; // 0 to 25
  claheClipLimit: number; // 1.0 to 5.0
  shadowThreshold: number; // 0 to 100
}

export type BackendConnectionStatus = 'connected' | 'disconnected' | 'checking';

export interface BackendInfo {
  status: 'ok' | 'degraded' | 'offline';
  service?: string;
  version?: string;
  device?: string; // e.g. "cuda:0 (NVIDIA RTX 4090)" or "cpu"
  torchVersion?: string;
  opencvVersion?: string;
  availableModels?: string[];
  uptimeSeconds?: number;
}

export interface ParallaxAppState {
  explainMode: boolean; // false = Scientific Mode, true = Explain Mode
  selectedRegion: LunarRegion;
  sourceInstrument: InstrumentId;
  targetInstrument: InstrumentId;
  activeComparisonMode: ComparisonMode;
  isProcessing: boolean;
  activePipelineStage: PipelineStageId | null;
  pipelineProgress: number; // 0 to 100
  matchFilter: MatchFilterType;
  showCoordinates: boolean;
  activeMatchPair: MatchPair | null;
  sourceFeatures: Keypoint[];
  targetFeatures: Keypoint[];
  matchPairs: MatchPair[];
  metrics: AlignmentMetrics;
  simulationParams: SimulationParams;
  cursorLabel: string;
  isDemoDataMode: boolean;
  backendStatus: BackendConnectionStatus;
  backendInfo: BackendInfo | null;
}

