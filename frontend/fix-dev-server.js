// Fix for React Scripts dev server allowedHosts issue
// This script creates the necessary .env file for the frontend

const fs = require('fs');
const path = require('path');

const envContent = `# React App Environment Variables
REACT_APP_API_URL=http://localhost:8000/api

# Development settings to fix webpack dev server issues
ESLINT_NO_DEV_ERRORS=true
GENERATE_SOURCEMAP=false
DANGEROUSLY_DISABLE_HOST_CHECK=true
FAST_REFRESH=false
`;

const envPath = path.join(__dirname, '.env');

try {
  fs.writeFileSync(envPath, envContent);
  console.log('✅ Created .env file for React frontend');
  console.log('📋 You can now run: npm start');
} catch (error) {
  console.error('❌ Error creating .env file:', error.message);
  console.log('\n📝 Please manually create a .env file in the frontend directory with this content:');
  console.log(envContent);
}

// Also check if node_modules exists
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.log('\n⚠️  node_modules not found. Please run: npm install');
} 