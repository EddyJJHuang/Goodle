import { Pet, MapMarker } from '../types';

export const mockPets: Pet[] = [
  {
    id: '1',
    name: 'Buddy',
    breed: 'Golden Retriever',
    age: '2 yrs',
    gender: 'Male',
    distance: '2.5 km',
    image: 'https://images.unsplash.com/photo-1552053831-71594a27632d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
    images: [
      'https://images.unsplash.com/photo-1552053831-71594a27632d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1633722715463-d30f4f325e24?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
    ],
    tags: ['Playful', 'Friendly', 'High Energy'],
    description: 'Buddy is an energetic ball of sunshine! He loves playing fetch, long walks on the beach, and cuddles. Looking for a playdate partner who can keep up! 🐕💨',
    location: 'San Francisco, CA',
    ownerName: 'Sarah Jenkins',
    ownerImage: 'https://i.pravatar.cc/150?u=sarah',
    status: 'Available',
    health: { vaccinated: true, neutered: true, dewormed: true }
  },
  {
    id: '2',
    name: 'Luna',
    breed: 'Husky Mix',
    age: '1 yr',
    gender: 'Female',
    distance: '5 km',
    image: 'https://images.unsplash.com/photo-1605568427561-40dd23c2acea?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
    images: ['https://images.unsplash.com/photo-1605568427561-40dd23c2acea?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
    tags: ['Vocal', 'Smart', 'Escape Artist'],
    description: 'Luna is a beautiful Husky mix with a lot of personality. She loves to sing and run.',
    location: 'Oakland, CA',
    status: 'Available',
    health: { vaccinated: true, neutered: true, dewormed: true }
  },
  {
    id: '3',
    name: 'Milo',
    breed: 'Tabby Cat',
    age: '3 yrs',
    gender: 'Male',
    distance: '10 km',
    image: 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
    images: ['https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
    tags: ['Independent', 'Curious', 'Chill'],
    description: 'Milo is a curious explorer who loves high places. He is independent but enjoys evening lap time.',
    location: 'Fremont, CA',
    status: 'Available',
    health: { vaccinated: true, neutered: true, dewormed: false }
  },
  {
    id: '4',
    name: 'Bella',
    breed: 'Beagle',
    age: '5 mos',
    gender: 'Female',
    distance: '12 km',
    image: 'https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
    images: ['https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
    tags: ['Gentle', 'Quiet', 'Puppy'],
    description: 'A sweet little soul looking for a patient owner. Bella is a bit shy at first but warms up quickly.',
    location: 'San Jose, CA',
    status: 'Available',
    health: { vaccinated: true, neutered: false, dewormed: true }
  },
  {
    id: '5',
    name: 'Rocky',
    breed: 'Pug',
    age: '4 yrs',
    gender: 'Male',
    distance: '3 km',
    image: 'https://images.unsplash.com/photo-1517849845537-4d257902454a?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
    images: ['https://images.unsplash.com/photo-1517849845537-4d257902454a?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
    tags: ['Chill', 'Apartment Friendly', 'Foodie'],
    description: 'Rocky is a couch potato king. Ideal for apartment living. He snores a little but it adds to his charm.',
    location: 'San Francisco, CA',
    status: 'Available',
    health: { vaccinated: true, neutered: true, dewormed: true }
  }
];

export const mockMapMarkers: MapMarker[] = [
  {
    id: 'm1',
    lat: 35,
    lng: 45,
    type: 'lost',
    petName: 'Max',
    description: 'Lost near Central Park. Wearing red collar.',
    timeAgo: '2h ago',
    image: 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'm2',
    lat: 60,
    lng: 70,
    type: 'stray',
    description: 'Spotted running near the highway.',
    timeAgo: '15m ago',
    image: 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'm3',
    lat: 25,
    lng: 20,
    type: 'stray',
    description: 'Small kitten hiding under a car.',
    timeAgo: '1d ago',
    image: 'https://images.unsplash.com/photo-1573865526739-10659fec78a5?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
  }
];
