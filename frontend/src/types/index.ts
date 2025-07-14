// Target System Types
export interface TargetSystem {
  id: number;
  name: string;
  ip_address: string;
  hostname?: string;
  operating_system: 'windows' | 'linux' | 'unix';
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTargetSystem {
  name: string;
  ip_address: string;
  hostname?: string;
  operating_system: 'windows' | 'linux' | 'unix';
  description?: string;
}

// Pagination Types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Test Types
export type TestStatus = 'pending' | 'running' | 'success' | 'failed' | 'timeout' | 'unauthorized' | 'connection_error';

export interface ConnectivityTest {
  id: number;
  target_system: number;
  target_system_name: string;
  target_system_ip: string;
  test_type: 'ping' | 'tcp_connect' | 'port_scan';
  port?: number;
  status: TestStatus;
  response_time?: number;
  error_message?: string;
  test_output: Record<string, any>;
  started_at: string;
  completed_at?: string;
}

export interface CredentialTest {
  id: number;
  target_system: number;
  target_system_name: string;
  target_system_ip: string;
  username: string;
  auth_method: 'password' | 'ssh_key' | 'kerberos' | 'ntlm';
  status: TestStatus;
  error_message?: string;
  test_output: Record<string, any>;
  started_at: string;
  completed_at?: string;
}

export interface TestSession {
  id: number;
  name: string;
  description?: string;
  target_systems: TargetSystem[];
  created_by?: number;
  created_at: string;
  completed_at?: string;
  total_tests: number;
  successful_tests: number;
  is_completed: boolean;
}

// Bulk IP Scan Types
export interface BulkScanResult {
  ip_address: string;
  ping_result: {
    success: boolean;
    response_time?: number;
    error?: string;
  };
  ssh_ports: {
    [key: number]: {
      success: boolean;
      response_time?: number;
      error?: string;
    };
  };
  smb_ports: {
    [key: number]: {
      success: boolean;
      response_time?: number;
      error?: string;
    };
  };
  system_type: 'windows' | 'unix' | 'unknown';
  open_ports: number[];
  overall_status: 'success' | 'failed' | 'error';
  scan_timestamp: string;
  error?: string;
}

export interface BulkScanResponse {
  scan_id: string;
  name: string;
  total_ips: number;
  successful_scans: number;
  failed_scans: number;
  error_scans: number;
  scan_results: BulkScanResult[];
  created_systems: number;
  saved_tests: number;
  system_types: {
    [key: string]: number;
  };
  scan_timestamp: string;
}

export interface BulkScanRequest {
  ip_input: string;
  name?: string;
  timeout?: number;
  save_results?: boolean;
}

// Bulk Scan Model Types
export interface BulkScan {
  id: number;
  scan_id: string;
  name: string;
  ip_input: string;
  total_ips: number;
  successful_scans: number;
  failed_scans: number;
  error_scans: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  timeout_setting: number;
  system_types: {
    [key: string]: number;
  };
  scan_results: BulkScanResult[];
  created_systems: number;
  saved_tests: number;
  created_at: string;
  completed_at?: string;
  duration?: number;
  success_rate: number;
  duration_display: string;
}

// Request Types
export interface ConnectivityTestRequest {
  target_system_id: number;
  test_type: 'ping' | 'tcp_connect' | 'port_scan';
  port?: number;
  timeout?: number;
}

export interface CredentialTestRequest {
  target_system_id: number;
  username: string;
  password?: string;
  auth_method: 'password' | 'ssh_key' | 'kerberos' | 'ntlm';
  ssh_key?: string;
  port?: number;
  timeout?: number;
}

export interface BatchTestRequest {
  target_system_ids: number[];
  test_types: string[];
  credentials?: {
    username: string;
    password?: string;
    auth_method?: string;
    ssh_key?: string;
  };
}

// Dashboard Types
export interface DashboardStats {
  total_systems: number;
  total_bulk_scans: number;
  total_credential_tests: number;
  recent_tests: {
    bulk_scans: number;
    credentials: number;
    ips_scanned: number;
    successful_ips: number;
  };
  success_rates: {
    bulk_scans: number;
    credentials: number;
  };
  systems_by_os: Record<string, number>;
  recent_system_types: Record<string, number>;
  bulk_scan_stats: {
    total_scans: number;
    completed_scans: number;
    running_scans: number;
    failed_scans: number;
  };
  recent_activity: {
    bulk_scans: BulkScan[];
    credential_tests: CredentialTest[];
  };
}

export interface SystemHealth {
  status: 'healthy' | 'unhealthy';
  database: 'healthy' | 'unhealthy';
  recent_activity: number;
  timestamp: string;
  version: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface TestResponse {
  test_id: number;
  status: string;
  message: string;
  test_details: ConnectivityTest | CredentialTest;
}

export interface BatchTestResponse {
  connectivity_tests: Array<{
    test_id: number;
    target_system: string;
    test_type: string;
    status: string;
  }>;
  credential_tests: Array<{
    test_id: number;
    target_system: string;
    username: string;
    status: string;
  }>;
  errors: string[];
}

// Form Types
export interface TargetSystemFormData {
  name: string;
  ip_address: string;
  hostname: string;
  operating_system: 'windows' | 'linux' | 'unix';
  description: string;
}

export interface ConnectivityTestFormData {
  target_system_id: number;
  test_type: 'ping' | 'tcp_connect' | 'port_scan';
  port: string;
  timeout: number;
}

export interface CredentialTestFormData {
  target_system_id: number;
  username: string;
  password: string;
  auth_method: 'password' | 'ssh_key' | 'kerberos' | 'ntlm';
  ssh_key: string;
  port: string;
  timeout: number;
} 