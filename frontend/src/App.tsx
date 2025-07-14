import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from './theme';

// Import components
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import TargetSystems from './components/TargetSystems';
import ConnectivityTests from './components/ConnectivityTests';
import CredentialTests from './components/CredentialTests';
import TestSessions from './components/TestSessions';
import BatchTesting from './components/BatchTesting';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/target-systems" element={<TargetSystems />} />
            <Route path="/connectivity-tests" element={<ConnectivityTests />} />
            <Route path="/credential-tests" element={<CredentialTests />} />
            <Route path="/test-sessions" element={<TestSessions />} />
            <Route path="/batch-testing" element={<BatchTesting />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App; 