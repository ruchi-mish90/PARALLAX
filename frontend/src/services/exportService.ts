import { AlignmentMetrics, HomographyMatrix, MatchPair } from "../types/correspondence";
import { apiClient } from "./apiClient";

export interface GeoTiffExportRequest {
  sourceProductId: string;
  targetProductId: string;
  homography: HomographyMatrix;
  regionId: string;
}

export interface GeoTiffExportResponse {
  downloadUrl: string;
  projection: string;
  dimensions: { width: number; height: number };
  pixelScale: [number, number, number];
}

/**
 * Service to handle data export, transformation serialization, and GeoTIFF generation.
 */
export async function downloadHomographyJson(
  homography: HomographyMatrix,
  metrics: AlignmentMetrics,
  sourceLabel: string,
  targetLabel: string
) {
  const exportPayload = {
    metadata: {
      platform: "PARALLAX Chandrayaan-2 Registration Framework",
      source: sourceLabel,
      target: targetLabel,
      timestamp: new Date().toISOString(),
      rmse: metrics.rmse,
      uncertaintyPx: metrics.uncertaintyPx,
      qualityGateStatus: metrics.qualityGateStatus,
    },
    homographyMatrix: homography,
    metrics,
  };

  const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `PARALLAX_${sourceLabel}_to_${targetLabel}_Transform_${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function downloadResidualsCsv(matches: MatchPair[]) {
  const headers = "MatchId,SourceX,SourceY,TargetX,TargetY,Distance,Confidence,IsRansacInlier,ResidualErrorPx\n";
  const rows = matches
    .map(
      (m) =>
        `${m.id},${m.sourceKeypoint.x.toFixed(4)},${m.sourceKeypoint.y.toFixed(4)},${m.targetKeypoint.x.toFixed(4)},${m.targetKeypoint.y.toFixed(4)},${m.distance.toFixed(4)},${m.confidence.toFixed(4)},${m.isRansacInlier},${m.residualError.toFixed(4)}`
    )
    .join("\n");

  const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `PARALLAX_Residuals_${Date.now()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function requestGeoTiffExport(
  req: GeoTiffExportRequest
): Promise<GeoTiffExportResponse | null> {
  if (!apiClient.isLiveApiEnabled()) return null;
  try {
    return await apiClient.post<GeoTiffExportResponse>("/export/geotiff", req);
  } catch {
    return null;
  }
}

export const exportService = {
  downloadHomographyJson,
  downloadResidualsCsv,
  requestGeoTiffExport,
};
