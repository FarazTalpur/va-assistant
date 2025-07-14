import React from 'react';
import { Box, Typography } from '@mui/material';

const BatchTesting: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Batch Testing
      </Typography>
      <Typography variant="body1">
        This page will allow you to run multiple tests across multiple target systems simultaneously.
        Ideal for pre-scan validation of large environments.
      </Typography>
    </Box>
  );
};

export default BatchTesting; 