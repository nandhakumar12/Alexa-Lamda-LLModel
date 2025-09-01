import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { Auth } from 'aws-amplify';
import toast from 'react-hot-toast';

// Types
interface ChatMessage {
  message: string;
  type: 'text' | 'voice';
  session_id: string;
  audio_data?: string; // base64 encoded audio
}

interface ChatResponse {
  response: string;
  intent: string;
  session_id: string;
  conversation_id: string;
  audio_url?: string;
}

interface AuthRequest {
  action: 'login' | 'register' | 'refresh' | 'validate' | 'logout';
  email?: string;
  password?: string;
  refresh_token?: string;
  token?: string;
  session_id?: string;
  user_attributes?: Record<string, string>;
}

interface AuthResponse {
  success: boolean;
  user_id?: string;
  email?: string;
  token?: string;
  session_id?: string;
  error?: string;
  error_code?: string;
  cognito_tokens?: {
    access_token: string;
    id_token: string;
    refresh_token?: string;
  };
}

interface HealthResponse {
  timestamp: string;
  environment: string;
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  components: Record<string, any>;
}

interface MetricsResponse {
  timestamp: string;
  time_range_minutes: number;
  metrics: Record<string, any>;
}

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_GATEWAY_URL || 'https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod';
const API_TIMEOUT = 15000; // 15 seconds

class ApiService {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
      // Disable preflight for simple requests
      withCredentials: false,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        try {
          // Get current session from Amplify
          const session = await Auth.currentSession();
          const token = session.getIdToken().getJwtToken();

          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        } catch (error) {
          // No valid session, continue without token
          console.debug('No valid session found');
        }

        // Don't add custom headers that trigger preflight
        // config.headers['X-Correlation-ID'] = this.generateCorrelationId();

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors (unauthorized)
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Try to refresh the session
            await Auth.currentSession();
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed, redirect to login
            console.error('Session refresh failed:', refreshError);
            toast.error('Session expired. Please log in again.');
            // You might want to trigger a logout here
            return Promise.reject(error);
          }
        }

        // Handle other errors
        this.handleApiError(error);
        return Promise.reject(error);
      }
    );
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private handleApiError(error: any) {
    const status = error.response?.status;
    const message = error.response?.data?.message || error.message;

    console.error('API Error:', {
      status,
      message,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data,
      code: error.code
    });

    // Don't show toast errors, let the calling code handle them
    // This prevents duplicate error messages
  }

  // Generic request method with retry
  private async request<T>(config: AxiosRequestConfig, retries: number = 2): Promise<T> {
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response: AxiosResponse<T> = await this.client(config);
        return response.data;
      } catch (error: any) {
        console.error(`API request attempt ${attempt + 1} failed:`, error);

        // If this is the last attempt, or it's not a network error, throw immediately
        if (attempt === retries || (error.response && error.response.status < 500)) {
          throw error;
        }

        // Wait before retrying (exponential backoff)
        const delay = Math.pow(2, attempt) * 1000;
        console.log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    throw new Error('Max retries exceeded');
  }

  // Chat API methods
  async sendMessage(data: ChatMessage): Promise<ChatResponse> {
    return this.request<ChatResponse>({
      method: 'POST',
      url: '/chatbot',
      data,
    });
  }

  async sendVoiceMessage(audioBlob: Blob, sessionId: string): Promise<ChatResponse> {
    // Convert blob to base64
    const base64Audio = await this.blobToBase64(audioBlob);
    
    return this.sendMessage({
      message: '',
      type: 'voice',
      session_id: sessionId,
      audio_data: base64Audio,
    });
  }

  // Authentication API methods
  async authenticate(data: AuthRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>({
      method: 'POST',
      url: '/auth',
      data,
    });
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    return this.authenticate({
      action: 'login',
      email,
      password,
    });
  }

  async register(email: string, password: string, userAttributes?: Record<string, string>): Promise<AuthResponse> {
    return this.authenticate({
      action: 'register',
      email,
      password,
      user_attributes: userAttributes,
    });
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    return this.authenticate({
      action: 'refresh',
      refresh_token: refreshToken,
    });
  }

  async validateToken(token: string): Promise<AuthResponse> {
    return this.authenticate({
      action: 'validate',
      token,
    });
  }

  async logout(sessionId: string): Promise<AuthResponse> {
    return this.authenticate({
      action: 'logout',
      session_id: sessionId,
    });
  }

  // Monitoring API methods
  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>({
      method: 'GET',
      url: '/health',
    });
  }

  async getMetrics(timeRangeMinutes: number = 60): Promise<MetricsResponse> {
    return this.request<MetricsResponse>({
      method: 'GET',
      url: '/metrics',
      params: { time_range_minutes: timeRangeMinutes },
    });
  }

  async getSystemStatus(): Promise<any> {
    return this.request<any>({
      method: 'GET',
      url: '/status',
    });
  }

  // Utility methods
  private async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix (data:audio/webm;base64,)
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // File upload methods
  async uploadFile(file: File, path: string): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', path);

    return this.request<{ url: string }>({
      method: 'POST',
      url: '/upload',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // WebSocket connection for real-time features
  createWebSocketConnection(onMessage: (data: any) => void): WebSocket | null {
    try {
      const wsUrl = API_BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://');
      const ws = new WebSocket(`${wsUrl}/ws`);

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };

      return ws;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      return null;
    }
  }
}

// Create singleton instance
const apiService = new ApiService();

// Export specific service instances
export const chatService = {
  sendMessage: (data: ChatMessage) => apiService.sendMessage(data),
  sendVoiceMessage: (audioBlob: Blob, sessionId: string) => apiService.sendVoiceMessage(audioBlob, sessionId),
};

export const authService = {
  login: (email: string, password: string) => apiService.login(email, password),
  register: (email: string, password: string, userAttributes?: Record<string, string>) => 
    apiService.register(email, password, userAttributes),
  refreshToken: (refreshToken: string) => apiService.refreshToken(refreshToken),
  validateToken: (token: string) => apiService.validateToken(token),
  logout: (sessionId: string) => apiService.logout(sessionId),
};

export const monitoringService = {
  getHealth: () => apiService.getHealth(),
  getMetrics: (timeRangeMinutes?: number) => apiService.getMetrics(timeRangeMinutes),
  getSystemStatus: () => apiService.getSystemStatus(),
};

export const fileService = {
  uploadFile: (file: File, path: string) => apiService.uploadFile(file, path),
};

export const websocketService = {
  createConnection: (onMessage: (data: any) => void) => apiService.createWebSocketConnection(onMessage),
};

export default apiService;
