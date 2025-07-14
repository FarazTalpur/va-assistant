import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Computer as ComputerIcon,
  NetworkCheck as NetworkCheckIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  Scanner as ScannerIcon,
  Storage as StorageIcon,
  ExpandMore as ExpandMoreIcon,
  Done as DoneIcon,
  PlayArrow as PlayArrowIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { dashboardApi, apiUtils } from '../services/api';
import { DashboardStats, BulkScan } from '../types';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardApi.getStats();
      setStats(response.data);
    } catch (error) {
      setError(apiUtils.formatErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const getSystemIcon = (systemType: string) => {
    switch (systemType) {
      case 'windows':
        return <ComputerIcon sx={{ color: '#00A4EF' }} />;
      case 'unix':
        return <StorageIcon sx={{ color: '#E95420' }} />;
      default:
        return <ComputerIcon sx={{ color: '#666' }} />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <DoneIcon sx={{ color: '#4CAF50' }} />;
      case 'running':
        return <PlayArrowIcon sx={{ color: '#2196F3' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return <ScannerIcon sx={{ color: '#666' }} />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Failed to load dashboard: {error}
      </Alert>
    );
  }

  if (!stats) {
    return (
      <Alert severity="info">
        No dashboard data available
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <ComputerIcon color="primary" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                    {stats.total_systems}
                  </Typography>
                  <Typography color="text.secondary">
                    Target Systems
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <ScannerIcon color="info" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                    {stats.total_bulk_scans}
                  </Typography>
                  <Typography color="text.secondary">
                    Bulk Scans
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <SecurityIcon color="warning" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                    {stats.total_credential_tests}
                  </Typography>
                  <Typography color="text.secondary">
                    Credential Tests
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <TrendingUpIcon color="success" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                    {stats.recent_tests.successful_ips}
                  </Typography>
                  <Typography color="text.secondary">
                    IPs Discovered (24h)
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Recent Activity Summary */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity (24h)
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box>
                    <Typography variant="h5" color="primary">
                      {stats.recent_tests.bulk_scans}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Bulk Scans
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box>
                    <Typography variant="h5" color="info.main">
                      {stats.recent_tests.ips_scanned}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      IPs Scanned
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box>
                    <Typography variant="h5" color="warning.main">
                      {stats.recent_tests.credentials}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Credential Tests
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box>
                    <Typography variant="h5" color="success.main">
                      {stats.success_rates.bulk_scans.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Scan Success Rate
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Bulk Scan Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Bulk Scan Status
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <DoneIcon sx={{ color: '#4CAF50' }} />
                    <Box>
                      <Typography variant="h5">
                        {stats.bulk_scan_stats.completed_scans}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Completed
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PlayArrowIcon sx={{ color: '#2196F3' }} />
                    <Box>
                      <Typography variant="h5">
                        {stats.bulk_scan_stats.running_scans}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Running
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <ErrorIcon sx={{ color: '#f44336' }} />
                    <Box>
                      <Typography variant="h5">
                        {stats.bulk_scan_stats.failed_scans}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Failed
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <ScannerIcon color="primary" />
                    <Box>
                      <Typography variant="h5">
                        {stats.bulk_scan_stats.total_scans}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Breakdown and Recent Discoveries */}
      <Grid container spacing={3}>
        {/* Systems by OS */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Target Systems by OS
              </Typography>
              {Object.entries(stats.systems_by_os).map(([os, count]) => (
                <Box key={os} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getSystemIcon(os)}
                      <Typography variant="body1">
                        {os.charAt(0).toUpperCase() + os.slice(1)}
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="bold">
                      {count}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(count / stats.total_systems) * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent System Types Discovered */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Discoveries (24h)
              </Typography>
              {Object.keys(stats.recent_system_types).length > 0 ? (
                Object.entries(stats.recent_system_types).map(([type, count]) => (
                  <Box key={type} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        {getSystemIcon(type)}
                        <Typography variant="body1">
                          {type.charAt(0).toUpperCase() + type.slice(1)} Systems
                        </Typography>
                      </Box>
                      <Chip 
                        label={`+${count}`} 
                        color="success" 
                        size="small" 
                      />
                    </Box>
                  </Box>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No new systems discovered in the last 24 hours
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity Details */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Bulk Scans
              </Typography>
              {stats.recent_activity.bulk_scans.length > 0 ? (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Scan ID</TableCell>
                        <TableCell>IPs Scanned</TableCell>
                        <TableCell>Success Rate</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Duration</TableCell>
                        <TableCell>Created</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {stats.recent_activity.bulk_scans.map((scan: BulkScan) => (
                        <TableRow key={scan.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="bold">
                              {scan.scan_id}
                            </Typography>
                          </TableCell>
                          <TableCell>{scan.total_ips}</TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {scan.success_rate.toFixed(1)}%
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              icon={getStatusIcon(scan.status)}
                              label={scan.status}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {scan.duration_display}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(scan.created_at).toLocaleString()}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recent bulk scans
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 