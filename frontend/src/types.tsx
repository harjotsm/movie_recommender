export interface Movie {
  id: number;
  title: string;
  overview: string;
  score: number;
  genres: string;
  year: string;
  rating: number;
  runtime: number;
}

export interface AppOptions {
  genres: string[];
  moods: string[];
}

export interface UserPreferences {
  genre: string;
  mood: string;
  content: string;
  element: string;
}
