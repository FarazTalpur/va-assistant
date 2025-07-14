import React from 'react';
import { Box, Typography } from '@mui/material';

const CredentialTests: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Credential Tests
      </Typography>
      <Typography variant="body1">
        This page will manage credential validation tests for both Unix and Windows systems.
        Supports password, SSH key, Kerberos, and NTLM authentication methods.
      </Typography>
    </Box>
  );
};

export default CredentialTests; 