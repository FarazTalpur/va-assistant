import axios, { AxiosResponse } from 'axios';
import {
  TargetSystem,
  CreateTargetSystem,
  ConnectivityTest,
  CredentialTest,
  TestSession,
  ConnectivityTestRequest,
  CredentialTestRequest,
  BatchTestRequest,
  TestResponse,
  BatchTestResponse,
  DashboardStats,
  SystemHealth,
  BulkScanRequest,
  BulkScanResponse,
  BulkScan,
  PaginatedResponse,
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config: any) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: any) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: any) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: any) => {
    console.error('API Response Error:', error);
    if (error.response) {
      console.error('Error Status:', error.response.status);
      console.error('Error Data:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Target Systems API
export const targetSystemsApi = {
  // Get all target systems
  getAll: (): Promise<AxiosResponse<TargetSystem[]>> => {
    return api.get('/target-systems/');
  },

  // Get target system by ID
  getById: (id: number): Promise<AxiosResponse<TargetSystem>> => {
    return api.get(`/target-systems/${id}/`);
  },

  // Create new target system
  create: (data: CreateTargetSystem): Promise<AxiosResponse<TargetSystem>> => {
    return api.post('/target-systems/', data);
  },

  // Update target system
  update: (id: number, data: Partial<CreateTargetSystem>): Promise<AxiosResponse<TargetSystem>> => {
    return api.patch(`/target-systems/${id}/`, data);
  },

  // Delete target system
  delete: (id: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/target-systems/${id}/`);
  },
};

// Bulk Scans API
export const bulkScansApi = {
  // Get all bulk scans
  getAll: (params?: { status?: string }): Promise<AxiosResponse<PaginatedResponse<BulkScan>>> => {
    return api.get('/bulk-scans/', { params });
  },

  // Get bulk scan by scan_id
  getById: (scanId: string): Promise<AxiosResponse<BulkScan>> => {
    return api.get(`/bulk-scans/${scanId}/`);
  },
};

// Connectivity Tests API
export const connectivityTestsApi = {
  // Get all connectivity tests
  getAll: (params?: { target_system_id?: number; status?: string }): Promise<AxiosResponse<PaginatedResponse<ConnectivityTest>>> => {
    return api.get('/connectivity-tests/', { params });
  },

  // Get connectivity test by ID
  getById: (id: number): Promise<AxiosResponse<ConnectivityTest>> => {
    return api.get(`/connectivity-tests/${id}/`);
  },

  // Run connectivity test
  run: (data: ConnectivityTestRequest): Promise<AxiosResponse<TestResponse>> => {
    return api.post('/connectivity-tests/run/', data);
  },

  // Run bulk IP scan
  bulkScan: (data: BulkScanRequest): Promise<AxiosResponse<BulkScanResponse>> => {
    return api.post('/connectivity-tests/bulk-scan/', data);
  },
};

// Credential Tests API
export const credentialTestsApi = {
  // Get all credential tests
  getAll: (params?: { target_system_id?: number; status?: string }): Promise<AxiosResponse<CredentialTest[]>> => {
    return api.get('/credential-tests/', { params });
  },

  // Get credential test by ID
  getById: (id: number): Promise<AxiosResponse<CredentialTest>> => {
    return api.get(`/credential-tests/${id}/`);
  },

  // Run credential test
  run: (data: CredentialTestRequest): Promise<AxiosResponse<TestResponse>> => {
    return api.post('/credential-tests/run/', data);
  },
};

// Test Sessions API
export const testSessionsApi = {
  // Get all test sessions
  getAll: (): Promise<AxiosResponse<TestSession[]>> => {
    return api.get('/test-sessions/');
  },

  // Get test session by ID
  getById: (id: number): Promise<AxiosResponse<TestSession>> => {
    return api.get(`/test-sessions/${id}/`);
  },

  // Create new test session
  create: (data: { name: string; description?: string; target_system_ids: number[] }): Promise<AxiosResponse<TestSession>> => {
    return api.post('/test-sessions/', data);
  },

  // Update test session
  update: (id: number, data: Partial<{ name: string; description?: string; target_system_ids: number[] }>): Promise<AxiosResponse<TestSession>> => {
    return api.patch(`/test-sessions/${id}/`, data);
  },

  // Delete test session
  delete: (id: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/test-sessions/${id}/`);
  },
};

// Batch Testing API
export const batchTestApi = {
  // Run batch tests
  run: (data: BatchTestRequest): Promise<AxiosResponse<BatchTestResponse>> => {
    return api.post('/batch-test/', data);
  },
};

// Dashboard API
export const dashboardApi = {
  // Get dashboard statistics
  getStats: (): Promise<AxiosResponse<DashboardStats>> => {
    return api.get('/dashboard/stats/');
  },

  // Get system health
  getHealth: (): Promise<AxiosResponse<SystemHealth>> => {
    return api.get('/health/');
  },
};

// Utility functions for common operations
export const apiUtils = {
  // Refresh test status by polling
  pollTestStatus: async (
    testType: 'connectivity' | 'credential',
    testId: number,
    callback: (test: ConnectivityTest | CredentialTest) => void,
    maxAttempts: number = 30,
    interval: number = 2000
  ): Promise<void> => {
    let attempts = 0;
    
    const poll = async () => {
      try {
        attempts++;
        let response;
        
        if (testType === 'connectivity') {
          response = await connectivityTestsApi.getById(testId);
        } else {
          response = await credentialTestsApi.getById(testId);
        }
        
        const test = response.data;
        callback(test);
        
        // Continue polling if test is still running and we haven't exceeded max attempts
        if (test.status === 'running' || test.status === 'pending') {
          if (attempts < maxAttempts) {
            setTimeout(poll, interval);
          } else {
            console.warn(`Polling stopped after ${maxAttempts} attempts for ${testType} test ${testId}`);
          }
        }
      } catch (error) {
        console.error(`Error polling ${testType} test ${testId}:`, error);
        if (attempts < maxAttempts) {
          setTimeout(poll, interval);
        }
      }
    };
    
    poll();
  },

  // Format error message from API response
  formatErrorMessage: (error: any): string => {
    if (error.response?.data?.error) {
      return error.response.data.error;
    } else if (error.response?.data?.message) {
      return error.response.data.message;
    } else if (error.response?.data) {
      // Handle field-specific errors
      const errorData = error.response.data;
      const fieldErrors = [];
      
      for (const [field, messages] of Object.entries(errorData)) {
        if (Array.isArray(messages)) {
          fieldErrors.push(`${field}: ${messages.join(', ')}`);
        } else if (typeof messages === 'string') {
          fieldErrors.push(`${field}: ${messages}`);
        }
      }
      
      return fieldErrors.length > 0 ? fieldErrors.join('; ') : 'An error occurred';
    } else if (error.message) {
      return error.message;
    } else {
      return 'An unknown error occurred';
    }
  },

  // Validate IP address format
  isValidIpAddress: (ip: string): boolean => {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
  },

  // Get status color for display
  getStatusColor: (status: string): 'success' | 'error' | 'warning' | 'info' => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
      case 'timeout':
      case 'unauthorized':
      case 'connection_error':
        return 'error';
      case 'running':
        return 'info';
      case 'pending':
        return 'warning';
      default:
        return 'info';
    }
  },

  // Format timestamp for display
  formatTimestamp: (timestamp: string): string => {
    return new Date(timestamp).toLocaleString();
  },

  // Calculate duration between two timestamps
  calculateDuration: (startTime: string, endTime?: string): string => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const durationMs = end.getTime() - start.getTime();
    
    if (durationMs < 1000) {
      return `${durationMs}ms`;
    } else if (durationMs < 60000) {
      return `${(durationMs / 1000).toFixed(1)}s`;
    } else {
      return `${(durationMs / 60000).toFixed(1)}m`;
    }
  },
};

export default api; 