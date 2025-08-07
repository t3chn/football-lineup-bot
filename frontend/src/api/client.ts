import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Player {
  id?: number;
  name: string;
  number?: number;
  position: string;
  is_captain: boolean;
}

export interface PredictionResponse {
  team: string;
  match_date?: string;
  opponent?: string;
  formation?: string;
  lineup: Player[];
  confidence: number;
  source: string;
  cached: boolean;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export const api = {
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  predictLineup: async (team: string): Promise<PredictionResponse> => {
    const response = await apiClient.get<PredictionResponse>(`/predict/${team}`);
    return response.data;
  },
};
