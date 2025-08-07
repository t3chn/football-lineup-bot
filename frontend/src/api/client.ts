import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'test-api-key',
  },
  timeout: 10000, // 10 seconds timeout
  withCredentials: false, // Explicitly disable credentials for CORS
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('Request:', config.method?.toUpperCase(), config.url, config.headers);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
apiClient.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('Full error object:', error);
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout!');
      console.error('Check if backend is accessible at:', API_BASE_URL);
    } else if (error.response) {
      console.error('Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('No response received. Request object:', error.request);
      console.error('Request readyState:', error.request.readyState);
      console.error('Request status:', error.request.status);
      console.error('Request responseURL:', error.request.responseURL);
      console.error('Error message:', error.message);
    } else {
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

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
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  },

  predictLineup: async (team: string): Promise<PredictionResponse> => {
    console.log('Requesting prediction for:', team);
    try {
      const response = await apiClient.get<PredictionResponse>(`/api/predict/${team}`);
      console.log('API response received:', response.data);
      console.log('Lineup players:', response.data?.lineup);
      return response.data;
    } catch (error) {
      console.error('predictLineup error:', error);
      throw error;
    }
  },
};
