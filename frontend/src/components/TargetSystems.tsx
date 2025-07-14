import React from 'react';
import { Box, Typography } from '@mui/material';

const TargetSystems: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Target Systems Management
      </Typography>
      <Typography variant="body1">
        This page will allow you to manage target systems for vulnerability analysis.
        Features will include adding, editing, and deleting target systems.
      </Typography>
    </Box>
  );
};

export default TargetSystems; 