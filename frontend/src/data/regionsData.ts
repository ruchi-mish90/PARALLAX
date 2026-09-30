import { LunarRegion } from '../types/regions';

export const LUNAR_REGIONS: LunarRegion[] = [
  {
    id: 'faustini-crater',
    name: 'Faustini Rim',
    subTitle: 'South Polar High Relief Rim',
    latitude: -87.18,
    longitude: 84.31,
    latDisplay: '87° 11\' S',
    longDisplay: '84° 19\' E',
    featureDescription: 'Permanently shadowed region (PSR) boundary with steep crater walls and extreme illumination contrast.',
    geologicalImportance: 'Key target for volatile water ice entrapment and low-sun elevation shadow morphology studies.',
    availableInstruments: ['OHRC', 'TMC-2', 'IIRS'],
    isDemoData: true,
    elevationProfile: '-1,420 m to +850 m',
    surfaceRoughness: 'High (Hurst exponent 0.62)',
    lightingCondition: 'Low solar elevation (1.8° – 4.5°)'
  },
  {
    id: 'boguslawsky-e',
    name: 'Boguslawsky-E',
    subTitle: 'Prime High-Latitude Landing Site',
    latitude: -70.9,
    longitude: 53.8,
    latDisplay: '70° 54\' S',
    longDisplay: '53° 48\' E',
    featureDescription: 'Relatively smooth highland crater floor flanked by ancient impact ejecta blankets and low-relief mounds.',
    geologicalImportance: 'Designated high-latitude landing corridor evaluated during Chandrayaan-2 and Chandrayaan-3 hazard avoidance passes.',
    availableInstruments: ['OHRC', 'TMC-2', 'IIRS'],
    isDemoData: true,
    elevationProfile: '-2,100 m floor datum',
    surfaceRoughness: 'Moderate (rms slope 6.8°)',
    lightingCondition: 'Nominal highland illumination (12.4° solar elevation)'
  },
  {
    id: 'shackleton-connecting-ridge',
    name: 'Shackleton Ridge',
    subTitle: 'Connecting Ridge / South Pole Peak',
    latitude: -89.65,
    longitude: 0.0,
    latDisplay: '89° 39\' S',
    longDisplay: '00° 00\' W',
    featureDescription: 'Narrow elevated ridge situated between Shackleton and de Gerlache craters enjoying near-permanent solar illumination.',
    geologicalImportance: 'Prime candidate site for solar power generation and long-duration lunar surface scientific payloads.',
    availableInstruments: ['OHRC', 'TMC-2', 'IIRS'],
    isDemoData: true,
    elevationProfile: '+1,120 m ridge crest',
    surfaceRoughness: 'Steep local gradients (>25°)',
    lightingCondition: 'Glancing polar illumination (0.8° – 2.2°)'
  },
  {
    id: 'tycho-central-peak',
    name: 'Tycho Peak',
    subTitle: 'Copernican-era Impact Landmark',
    latitude: -43.31,
    longitude: -11.36,
    latDisplay: '43° 18\' S',
    longDisplay: '11° 22\' W',
    featureDescription: 'Prominent, exceptionally crisp central peak complex rising 2 km above the floor of the 85 km diameter impact crater.',
    geologicalImportance: 'Standard planetary calibration landmark for optical reflectance and mineralogical absorption band indexing.',
    availableInstruments: ['OHRC', 'TMC-2', 'IIRS'],
    isDemoData: true,
    elevationProfile: '+1,980 m peak prominence',
    surfaceRoughness: 'Blocky boulder fields with high radar backscatter',
    lightingCondition: 'High solar elevation (45.0°)'
  }
];
