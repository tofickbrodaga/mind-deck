export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type?: string;
}

export interface Deck {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface DeckCreate {
  title: string;
  description?: string | null;
}

export interface DeckUpdate {
  title?: string | null;
  description?: string | null;
}

export interface FSRSState {
  stability: number;
  difficulty: number;
  ease_factor: number;
  interval: number;
  review_count: number;
  last_review: string | null;
  due_date: string | null;
}

export interface Card {
  id: string;
  deck_id: string;
  front: string;
  back: string;
  audio_url: string | null;
  fsrs_state: FSRSState;
  created_at: string;
  updated_at: string;
}

export interface CardCreate {
  front: string;
  back: string;
}

export interface CardUpdate {
  front?: string | null;
  back?: string | null;
}

export interface ReviewCardRequest {
  quality: number; // 0-5
}

export type StudyMode = 'flashcards' | 'multiple_choice' | 'write' | 'match';

export interface StudySession {
  id: string;
  user_id: string;
  deck_id: string;
  mode: string;
  started_at: string;
  finished_at: string | null;
  cards_studied: number;
  cards_correct: number;
  cards_incorrect: number;
}

export interface StudySessionCreate {
  deck_id: string;
  mode: StudyMode;
}

export interface StudyFlashcardsResponse {
  cards: Card[];
}

export interface StudyMultipleChoiceResponse {
  card: Card;
  options: string[];
  correct_index: number;
}

export interface StudyWriteRequest {
  card_id: string;
  answer: string;
}

export interface StudyWriteResponse {
  is_correct: boolean;
  quality: number;
  correct_answer: string;
}

export interface StudyMatchResponse {
  terms: string[];
  definitions: string[];
  pairs: [string, string][];
}
