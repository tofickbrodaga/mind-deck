import axios from 'axios';
import type {
  User,
  UserCreate,
  UserLogin,
  TokenResponse,
  Deck,
  DeckCreate,
  DeckUpdate,
  Card,
  CardCreate,
  CardUpdate,
  ReviewCardRequest,
  StudySession,
  StudySessionCreate,
  StudyFlashcardsResponse,
  StudyMultipleChoiceResponse,
  StudyWriteRequest,
  StudyWriteResponse,
  StudyMatchResponse,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен к каждому запросу
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обрабатываем ошибки авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (data: UserCreate): Promise<User> => {
    const response = await api.post<User>('/users/register', data);
    return response.data;
  },

  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/users/login', data);
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },
};

// Decks API
export const decksAPI = {
  getAll: async (): Promise<Deck[]> => {
    const response = await api.get<Deck[]>('/decks');
    return response.data;
  },

  getById: async (id: string): Promise<Deck> => {
    const response = await api.get<Deck>(`/decks/${id}`);
    return response.data;
  },

  create: async (data: DeckCreate): Promise<Deck> => {
    const response = await api.post<Deck>('/decks', data);
    return response.data;
  },

  update: async (id: string, data: DeckUpdate): Promise<Deck> => {
    const response = await api.put<Deck>(`/decks/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/decks/${id}`);
  },
};

// Cards API
export const cardsAPI = {
  getByDeck: async (deckId: string): Promise<Card[]> => {
    const response = await api.get<Card[]>(`/cards/deck/${deckId}`);
    return response.data;
  },

  getDueCards: async (deckId: string, limit?: number): Promise<Card[]> => {
    const params = limit ? { limit } : {};
    const response = await api.get<Card[]>(`/cards/deck/${deckId}/due`, { params });
    return response.data;
  },

  getById: async (id: string): Promise<Card> => {
    const response = await api.get<Card>(`/cards/${id}`);
    return response.data;
  },

  create: async (deckId: string, data: CardCreate): Promise<Card> => {
    const response = await api.post<Card>(`/cards/deck/${deckId}`, data);
    return response.data;
  },

  update: async (id: string, data: CardUpdate): Promise<Card> => {
    const response = await api.put<Card>(`/cards/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/cards/${id}`);
  },

  review: async (id: string, data: ReviewCardRequest): Promise<Card> => {
    const response = await api.post<Card>(`/cards/${id}/review`, data);
    return response.data;
  },
};

// Study API
export const studyAPI = {
  startSession: async (data: StudySessionCreate): Promise<StudySession> => {
    const response = await api.post<StudySession>('/study/session', data);
    return response.data;
  },

  finishSession: async (sessionId: string): Promise<StudySession> => {
    const response = await api.post<StudySession>(`/study/session/${sessionId}/finish`);
    return response.data;
  },

  getFlashcards: async (deckId: string, limit: number = 20): Promise<StudyFlashcardsResponse> => {
    const response = await api.get<StudyFlashcardsResponse>(`/study/flashcards/${deckId}`, {
      params: { limit },
    });
    return response.data;
  },

  getMultipleChoice: async (
    deckId: string,
    cardId: string
  ): Promise<StudyMultipleChoiceResponse> => {
    const response = await api.get<StudyMultipleChoiceResponse>(
      `/study/multiple-choice/${deckId}/${cardId}`
    );
    return response.data;
  },

  checkWrite: async (data: StudyWriteRequest): Promise<StudyWriteResponse> => {
    const response = await api.post<StudyWriteResponse>('/study/write/check', data);
    return response.data;
  },

  getMatch: async (deckId: string, limit: number = 10): Promise<StudyMatchResponse> => {
    const response = await api.get<StudyMatchResponse>(`/study/match/${deckId}`, {
      params: { limit },
    });
    return response.data;
  },
};

// Import API
export const importAPI = {
  importFromWord: async (deckId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/import/word/${deckId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  importFromExcel: async (deckId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/import/excel/${deckId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  importFromImage: async (deckId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/import/image/${deckId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;
