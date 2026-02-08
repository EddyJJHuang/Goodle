export interface Pet {
  id: string;
  name: string;
  breed: string;
  age: string; // e.g., "2 yrs", "5 mos"
  gender: 'Male' | 'Female';
  distance: string;
  image: string;
  images: string[];
  tags: string[]; // e.g., "Playful", "Vaccinated"
  description: string;
  location: string;
  ownerName?: string;
  ownerImage?: string;
  status: 'Available' | 'Adopted' | 'Lost' | 'Found';
  health?: {
    vaccinated: boolean;
    neutered: boolean;
    dewormed: boolean;
  };
}

export interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  type: 'lost' | 'stray';
  petName?: string;
  description?: string;
  timeAgo: string;
  image: string;
}

export enum ViewMode {
    HOME = 'HOME',
    MATCH = 'MATCH',
    LOST_FOUND = 'LOST_FOUND',
    ADOPTION = 'ADOPTION',
    DETAILS = 'DETAILS',
    POST = 'POST'
}