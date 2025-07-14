import React from 'react';
import { Box, Typography } from '@mui/material';

const TestSessions: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Test Sessions
      </Typography>
      <Typography variant="body1">
        This page will manage test sessions to group and track multiple tests across different target systems.
      </Typography>
    </Box>
  );
};

export default TestSessions; 