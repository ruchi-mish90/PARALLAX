import { InstrumentId } from './instruments';

export interface LunarRegion {
  id: string;
  name: string;
  subTitle: string;
  latitude: number; // in degrees (-90 to 90)
  longitude: number; // in degrees (-180 to 180)
  latDisplay: string;
  longDisplay: string;
  featureDescription: string;
  geologicalImportance: string;
  availableInstruments: InstrumentId[];
  isDemoData: boolean;
  elevationProfile: string;
  surfaceRoughness: string;
  lightingCondition: string;
}
