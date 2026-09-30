import { SimulationParams } from "../types/state";
import { apiClient } from "./apiClient";

export interface SimulatorStressResponse {
  status: "success" | "simulated";
  degradedInlierRatio: number;
  estimatedRmse: number;
  syntheticNoiseSnrDb: number;
  shadowPixelPercentage: number;
  recommendedModelOverride?: string;
  warningNotice?: string;
}

/**
 * Service to execute backend lunar environment stress simulation.
 * Falls back locally if backend is offline.
 */
export async function evaluateSimulatorStress(
  params: SimulationParams
): Promise<SimulatorStressResponse> {
  if (apiClient.isLiveApiEnabled()) {
    try {
      const response = await apiClient.post<SimulatorStressResponse>(
        "/simulator/evaluate",
        params
      );
      if (response && response.status === "success") {
        return response;
      }
    } catch {
      // Offline fallback
    }
  }

  // Realistic synthetic calculation based on lunar physics formulas
  const elevationFactor = Math.sin((params.sunElevationAngle * Math.PI) / 180);
  const noiseFactor = params.sensorNoiseSigma / 25;
  const scaleDisparityFactor = params.spatialScaleRatio / 20;

  const estimatedRmse = Number(
    (1.1 + (1 - elevationFactor) * 1.4 + noiseFactor * 0.9 + scaleDisparityFactor * 0.7).toFixed(2)
  );

  const degradedInlierRatio = Number(
    Math.max(22, Math.min(94, 88 - (1 - elevationFactor) * 35 - noiseFactor * 25 - (scaleDisparityFactor - 1) * 10)).toFixed(1)
  );

  return {
    status: "simulated",
    degradedInlierRatio,
    estimatedRmse,
    syntheticNoiseSnrDb: Number((42 - params.sensorNoiseSigma * 1.2).toFixed(1)),
    shadowPixelPercentage: Number((Math.max(5, (1 - elevationFactor) * 65)).toFixed(1)),
    warningNotice:
      params.sunElevationAngle < 8
        ? "Extreme grazing shadow: high risk of shadow-edge hallucination without multi-scale phase congruency."
        : undefined,
  };
}

export const simulatorService = {
  evaluateSimulatorStress,
};
