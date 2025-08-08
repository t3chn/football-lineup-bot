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
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  predictLineup: async (team: string): Promise<PredictionResponse> => {
    console.log('Requesting prediction for:', team);
    try {
      const response = await apiClient.get<PredictionResponse>(`/predict/${team}`);
      console.log('API response received:', response.data);
      console.log('Lineup players:', response.data?.lineup);
      return response.data;
    } catch (error) {
      console.error('predictLineup error:', error);
      throw error;
    }
  },

  // New API methods for enhanced features
  getTeamInjuries: async (teamName: string) => {
    try {
      const response = await apiClient.get(`/analytics/injuries/${encodeURIComponent(teamName)}`);
      return response.data;
    } catch (error) {
      console.error('getTeamInjuries error:', error);
      throw error;
    }
  },

  analyzeTeamNews: async (teamName: string) => {
    try {
      const response = await apiClient.get(`/analytics/news/${encodeURIComponent(teamName)}`);
      return response.data;
    } catch (error) {
      console.error('analyzeTeamNews error:', error);
      throw error;
    }
  },

  getTeamFixtures: async (teamName: string) => {
    try {
      // Note: This would need team ID mapping in production
      const response = await apiClient.get('/schedule/fixtures', {
        params: { limit: 10 }
      });

      // Mock filter by team name
      return {
        matches: response.data.fixtures?.slice(0, 5).map((f: any) => ({
          ...f,
          is_home: Math.random() > 0.5,
          opponent: f.home_team || f.away_team,
        })) || []
      };
    } catch (error) {
      console.error('getTeamFixtures error:', error);
      throw error;
    }
  },

  checkPlayerAvailability: async (teamName: string, playerName: string) => {
    try {
      const response = await apiClient.get(
        `/analytics/player-availability/${encodeURIComponent(teamName)}/${encodeURIComponent(playerName)}`
      );
      return response.data;
    } catch (error) {
      console.error('checkPlayerAvailability error:', error);
      throw error;
    }
  },
};
