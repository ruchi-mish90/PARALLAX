export type InstrumentId = 'OHRC' | 'TMC-2' | 'IIRS';

export interface InstrumentSpec {
  id: InstrumentId;
  name: string;
  fullName: string;
  payloadType: string;
  modality: string;
  spectralBand: string;
  groundResolution: string;
  swathWidth: string;
  stereoCapability: boolean;
  purpose: string;
  description: string;
  registrationChallenge: string;
  scientificRoleInParallax: string;
  acquisitionExample: string;
  sensorCharacteristics: {
    spectralChannels: number;
    radiometricResolution: string;
    focalLength: string;
    detectorType: string;
  };
}

