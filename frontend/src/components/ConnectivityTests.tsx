import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  FormControlLabel,
  Switch,
  Divider,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  Add as AddIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  Computer as ComputerIcon,
  Storage as StorageIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon,
  NetworkCheck as NetworkCheckIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Info as InfoIcon,
  PlayArrow as PlayArrowIcon,
  Done as DoneIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { connectivityTestsApi, bulkScansApi } from '../services/api';
import { BulkScan, BulkScanResult, BulkScanResponse } from '../types';

interface ScanResult {
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

const ConnectivityTests: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [ipInput, setIpInput] = useState('');
  const [scanName, setScanName] = useState('');
  const [timeout, setTimeout] = useState(5);
  const [saveResults, setSaveResults] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState<BulkScanResponse | null>(null);
  const [bulkScans, setBulkScans] = useState<BulkScan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanProgress, setScanProgress] = useState(0);

  // Fetch bulk scans history
  const fetchBulkScans = async () => {
    try {
      setLoading(true);
      const response = await bulkScansApi.getAll();
      // Handle paginated response from Django REST Framework
      const scans = response.data.results || response.data;
      setBulkScans(Array.isArray(scans) ? scans : []);
    } catch (err) {
      setError('Failed to fetch bulk scans');
      console.error('Error fetching bulk scans:', err);
      // Ensure state remains as an array even on error
      setBulkScans([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBulkScans();
  }, []);

  const handleBulkScan = async () => {
    if (!ipInput.trim()) {
      setError('Please enter at least one IP address');
      return;
    }

    setIsScanning(true);
    setError(null);
    setScanProgress(0);

    try {
      const response = await connectivityTestsApi.bulkScan({
        ip_input: ipInput,
        name: scanName || 'Bulk Scan',
        timeout: timeout,
        save_results: saveResults
      });

      setScanResults(response.data);
      setIsModalOpen(false);
      setIpInput('');
      setScanName('');
      
      // Refresh bulk scans to show the new scan
      fetchBulkScans();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to perform bulk scan');
      console.error('Error performing bulk scan:', err);
    } finally {
      setIsScanning(false);
      setScanProgress(0);
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
      case 'pending':
        return <InfoIcon sx={{ color: '#ff9800' }} />;
      default:
        return <InfoIcon sx={{ color: '#666' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getResultStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon sx={{ color: '#4CAF50' }} />;
      case 'failed':
        return <CancelIcon sx={{ color: '#f44336' }} />;
      case 'error':
        return <WarningIcon sx={{ color: '#ff9800' }} />;
      default:
        return <WarningIcon sx={{ color: '#666' }} />;
    }
  };

  const getResultStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
        return 'error';
      case 'error':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatResponseTime = (time?: number) => {
    if (!time) return 'N/A';
    return `${time.toFixed(2)}ms`;
  };

  const renderPortTest = (port: number, result: any, portType: string) => {
    const isOpen = result.success;
    const icon = isOpen ? <CheckCircleIcon sx={{ color: '#4CAF50', fontSize: 16 }} /> : <CancelIcon sx={{ color: '#f44336', fontSize: 16 }} />;
    
    return (
      <Box key={port} sx={{ display: 'flex', alignItems: 'center', gap: 1, my: 0.5 }}>
        {icon}
        <Typography variant="body2">
          {portType} ({port}): {isOpen ? 'Open' : 'Closed'}
          {result.response_time && ` - ${formatResponseTime(result.response_time)}`}
        </Typography>
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Connectivity Tests
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsModalOpen(true)}
        >
          New Bulk Scan
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Latest Scan Results Section */}
      {scanResults && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Latest Scan Results - {scanResults.name || scanResults.scan_id}
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {scanResults.total_ips}
                    </Typography>
                    <Typography variant="body2">Total IPs</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main">
                      {scanResults.successful_scans}
                    </Typography>
                    <Typography variant="body2">Successful</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="error.main">
                      {scanResults.failed_scans}
                    </Typography>
                    <Typography variant="body2">Failed</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="warning.main">
                      {scanResults.error_scans}
                    </Typography>
                    <Typography variant="body2">Errors</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* System Type Summary */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                System Types Detected:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {Object.entries(scanResults.system_types).map(([type, count]) => (
                  <Chip
                    key={type}
                    icon={getSystemIcon(type)}
                    label={`${type.toUpperCase()}: ${count}`}
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Bulk Scans History */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Bulk Scan History
            </Typography>
            <IconButton onClick={fetchBulkScans}>
              <RefreshIcon />
            </IconButton>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Scan Name</TableCell>
                    <TableCell>IPs Scanned</TableCell>
                    <TableCell>Success Rate</TableCell>
                    <TableCell>System Types</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Array.isArray(bulkScans) && bulkScans.length > 0 ? (
                    bulkScans.map((scan) => (
                      <TableRow key={scan.id}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {scan.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {scan.scan_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                            {/* <Typography variant="body2">{scan.total_ips}</Typography> */}
                            {/* <Badge badgeContent={scan.successful_scans} color="success" /> */}
                            <Badge badgeContent={scan.total_ips} color="success" />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {scan.success_rate.toFixed(1)}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {Object.entries(scan.system_types).map(([type, count]) => (
                              <Chip
                                key={type}
                                icon={getSystemIcon(type)}
                                label={`${type}: ${count}`}
                                size="small"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(scan.status)}
                            label={scan.status}
                            color={getStatusColor(scan.status) as any}
                            size="small"
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
                        <TableCell>
                          <Accordion>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography variant="body2">View Details</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              <TableContainer component={Paper}>
                                <Table size="small">
                                  <TableHead>
                                    <TableRow>
                                      <TableCell>IP Address</TableCell>
                                      <TableCell>System Type</TableCell>
                                      <TableCell>Status</TableCell>
                                      <TableCell>Open Ports</TableCell>
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    {scan.scan_results.map((result: BulkScanResult, index: number) => (
                                      <TableRow key={index}>
                                        <TableCell>{result.ip_address}</TableCell>
                                        <TableCell>
                                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {getSystemIcon(result.system_type)}
                                            <Typography variant="body2">
                                              {result.system_type.toUpperCase()}
                                            </Typography>
                                          </Box>
                                        </TableCell>
                                        <TableCell>
                                          <Chip
                                            icon={getResultStatusIcon(result.overall_status)}
                                            label={result.overall_status}
                                            color={getResultStatusColor(result.overall_status) as any}
                                            size="small"
                                          />
                                        </TableCell>
                                        <TableCell>
                                          <Typography variant="body2">
                                            {result.open_ports.length > 0 ? result.open_ports.join(', ') : 'None'}
                                          </Typography>
                                        </TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </AccordionDetails>
                          </Accordion>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        <Typography variant="body2" color="text.secondary">
                          {loading ? 'Loading...' : 'No bulk scans found. Start your first scan!'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Bulk Scan Modal */}
      <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Bulk IP Scan</Typography>
            <IconButton onClick={() => setIsModalOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Scan Name"
              fullWidth
              value={scanName}
              onChange={(e) => setScanName(e.target.value)}
              placeholder="Enter a name for this scan (e.g., Project Alpha, Network Audit)"
              helperText="Custom name to identify this scan"
              sx={{ mb: 2 }}
            />
            
            <TextField
              label="IP Addresses"
              multiline
              rows={6}
              fullWidth
              value={ipInput}
              onChange={(e) => setIpInput(e.target.value)}
              placeholder="Enter IP addresses (comma-separated or one per line):&#10;192.168.1.1,192.168.1.2&#10;192.168.1.3&#10;10.0.0.1"
              helperText="Enter IP addresses separated by commas or on separate lines"
              sx={{ mb: 2 }}
            />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Timeout (seconds)"
                  type="number"
                  value={timeout}
                  onChange={(e) => setTimeout(parseInt(e.target.value))}
                  inputProps={{ min: 1, max: 30 }}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={saveResults}
                      onChange={(e) => setSaveResults(e.target.checked)}
                    />
                  }
                  label="Save results to database"
                />
              </Grid>
            </Grid>

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                This scan will test:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <NetworkCheckIcon />
                  </ListItemIcon>
                  <ListItemText primary="ICMP Ping test" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText primary="SSH ports (22, 2222) - Unix/Linux detection" />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <StorageIcon />
                  </ListItemIcon>
                  <ListItemText primary="SMB ports (139, 445) - Windows detection" />
                </ListItem>
              </List>
            </Box>
          </Box>
          
          {isScanning && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Scanning in progress...
              </Typography>
              <LinearProgress />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsModalOpen(false)} disabled={isScanning}>
            Cancel
          </Button>
          <Button
            onClick={handleBulkScan}
            variant="contained"
            disabled={isScanning || !ipInput.trim()}
            startIcon={isScanning ? <CircularProgress size={20} /> : <NetworkCheckIcon />}
          >
            {isScanning ? 'Scanning...' : 'Start Scan'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConnectivityTests; 