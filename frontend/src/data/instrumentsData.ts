import { InstrumentSpec } from '../types/instruments';

export const CHANDRAYAAN_INSTRUMENTS: Record<string, InstrumentSpec> = {
  'OHRC': {
    id: 'OHRC',
    name: 'OHRC',
    fullName: 'Orbiter High Resolution Camera',
    payloadType: 'Ultra-High-Resolution Optical Imager',
    modality: 'Optical/panchromatic',
    spectralBand: 'Visible (0.45 – 0.68 µm)',
    groundResolution: '~0.25–0.32 m/px (from 100 km orbit)',
    swathWidth: '3.0 km × 12.0 km',
    stereoCapability: true,
    purpose: 'Hazard detection, landing site mapping, boulder identification, and high-resolution crater morphology.',
    description: 'OHRC captures ultra-fine spatial detail at sub-meter scales, discerning individual boulders, micro-craters, and shadow contours critical for landing hazard verification.',
    registrationChallenge: 'Very high spatial detail (~0.25–0.32 m/px) causing severe scale octave aliasing when registered directly against regional sensors.',
    scientificRoleInParallax: 'Acts as the ultra-fine reference (source) image with dense micro-textural landmarks.',
    acquisitionExample: 'CH2_OHR_NC_20191024T184512_001_A',
    sensorCharacteristics: {
      spectralChannels: 1,
      radiometricResolution: '12-bit / 4096 grey levels',
      focalLength: '1250 mm',
      detectorType: 'TDI-CCD Linear Array (4096 pixels)',
    }
  },
  'TMC-2': {
    id: 'TMC-2',
    name: 'TMC-2',
    fullName: 'Terrain Mapping Camera-2',
    payloadType: 'Panchromatic Triplet Stereo Imager',
    modality: 'Visible panchromatic + stereo',
    spectralBand: 'Visible (0.50 – 0.85 µm)',
    groundResolution: '~5 m/px (from 100 km orbit)',
    swathWidth: '20.0 km',
    stereoCapability: true,
    purpose: 'Digital Elevation Model (DEM) generation, regional topography, surface slope mapping, and crater morphology.',
    description: 'TMC-2 captures triplet views (Fore +26°, Nadir 0°, Aft -26°) along orbital tracks to generate 3D digital surface elevation models of the lunar terrain.',
    registrationChallenge: 'Acts as the essential intermediate scale bridge connecting ultra-fine OHRC features to regional terrain context and mineralogical observations.',
    scientificRoleInParallax: 'Provides regional contextual baseline (target) and serves as an intermediate scale bridge for extreme scale-gap pairs.',
    acquisitionExample: 'CH2_TMC_NC_20191024T184422_001_N',
    sensorCharacteristics: {
      spectralChannels: 1,
      radiometricResolution: '10-bit / 1024 grey levels',
      focalLength: '120 mm',
      detectorType: 'Linear CCD (4000 pixels × 3 cameras: Fore +26°, Nadir 0°, Aft -26°)',
    }
  },
  'IIRS': {
    id: 'IIRS',
    name: 'IIRS',
    fullName: 'Imaging Infrared Spectrometer',
    payloadType: 'Hyperspectral VNIR-SWIR Spectrometer',
    modality: 'Hyperspectral',
    spectralBand: 'Extended SWIR (0.80 – 5.0 µm in 256 contiguous bands)',
    groundResolution: '~80 m/px (from 100 km orbit)',
    swathWidth: '20.0 km',
    stereoCapability: false,
    purpose: 'Mineralogical mapping, signature detection of OH/H2O absorption features at 2.8–3.0 µm, and thermal emission correction.',
    description: 'IIRS maps mineral composition and surface hydroxyl/water hydration across 256 contiguous spectral bands spanning the visible to extended short-wave infrared.',
    registrationChallenge: 'Extreme scale + modality gap (320:1 GSD vs OHRC) combined with severe radiometric contrast differences between visible albedo and infrared absorption.',
    scientificRoleInParallax: 'Requires pair-aware phase-congruency structural matching (RIFT/HOPC) or an intermediate TMC-2 scale bridge for robust co-registration.',
    acquisitionExample: 'CH2_IIR_HY_20191102T041219_001_B',
    sensorCharacteristics: {
      spectralChannels: 256,
      radiometricResolution: '14-bit ADC',
      focalLength: '175 mm',
      detectorType: 'Staring HgCdTe Focal Plane Array with Grating Spectrometer',
    }
  }
};
