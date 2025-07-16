# VA Assistant - Vulnerability Analysis Assistant

A comprehensive web application for pre-scan validation in vulnerability assessment workflows. The VA Assistant helps verify network connectivity and credential validation before running vulnerability scans on target systems.

## 🎯 Purpose

The VA Assistant is designed for vulnerability assessment teams to perform two critical pre-scan checks:

1. **Network Connectivity Testing** - Verify that target systems are reachable
2. **Credential Validation** - Ensure authentication credentials work properly

This tool is specifically designed for deployment on standalone, airgapped vulnerability assessment machines.

## ✨ Features

- **Modern Web Interface** - Built with React and Material UI for an intuitive user experience
- **Network Connectivity Tests**:
  - ICMP Ping tests
  - TCP connection tests
  - Port scanning capabilities
- **Credential Validation**:
  - SSH password authentication
  - SSH key-based authentication  
  - Windows credential testing (RDP/WinRM simulation)
  - Support for multiple authentication methods
- **Batch Testing** - Run tests across multiple target systems simultaneously
- **Test Sessions** - Group and manage related tests
- **Real-time Results** - Live status updates during test execution
- **Comprehensive Logging** - Detailed test results and system logs
- **REST API** - Full programmatic access to all functionality
- **Airgapped Deployment** - Designed for isolated security environments

## 🏗️ Architecture

### Backend (Django)
- **Django 4.2** - Web framework
- **Django REST Framework** - API layer
- **SQLite** - Database (file-based for portability)
- **Paramiko** - SSH connectivity
- **Threading** - Asynchronous test execution

### Frontend (React)
- **React 18** - UI framework
- **Material UI** - Component library
- **TypeScript** - Type safety
- **Axios** - HTTP client
- **React Router** - Navigation

## 📋 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / RHEL 8+
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM
- **Storage**: 5GB free space
- **Network**: Access to target systems for testing

### Recommended Requirements
- **Memory**: 4GB RAM
- **CPU**: 2+ cores
- **Storage**: 10GB free space

### Dependencies
- Python 3.8+
- Node.js 16+ (for frontend build)
- Git
- Build tools (gcc, python3-dev)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

1. **Download the application**:
```bash
git clone <repository-url>
cd va-assistant
```

2. **Run the setup script**:
```bash
chmod +x setup.sh
./setup.sh
```

3. **Access the application**:
   - Open your browser to `http://localhost:8000`
   - Or `http://localhost` if Nginx was configured

### Option 2: Docker Deployment

1. **Using Docker Compose**:
```bash
docker-compose up -d
```

2. **Access the application**:
   - Open your browser to `http://localhost:8000`

### Option 3: Manual Installation

1. **Install system dependencies**:
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip nodejs npm build-essential git curl
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Build frontend**:
```bash
cd frontend
npm install
npm run build
cd ..
```

5. **Setup Django**:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # Optional
```

6. **Run the application**:
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🎮 Usage Guide

### Dashboard
The main dashboard provides an overview of:
- Total target systems configured
- Recent test activity
- Success rates for connectivity and credential tests
- System statistics by operating system

### Target Systems Management
1. Navigate to **Target Systems**
2. Click **Add Target System**
3. Fill in the required information:
   - Name (friendly identifier)
   - IP Address
   - Hostname (optional)
   - Operating System (Windows/Linux/Unix)
   - Description (optional)

### Running Connectivity Tests
1. Go to **Connectivity Tests**
2. Select a target system
3. Choose test type:
   - **Ping**: Basic ICMP connectivity
   - **TCP Connect**: Test specific port connectivity
   - **Port Scan**: Scan range of ports
4. Configure timeout and other parameters
5. Click **Run Test**

### Running Credential Tests
1. Go to **Credential Tests**
2. Select a target system
3. Choose authentication method:
   - **Password**: Username/password authentication
   - **SSH Key**: Private key authentication
4. Enter credentials (not stored permanently)
5. Click **Run Test**

### Batch Testing
1. Navigate to **Batch Testing**
2. Select multiple target systems
3. Choose test types to run
4. Optionally provide credentials for credential testing
5. Execute batch tests across all selected systems

### Test Sessions
1. Go to **Test Sessions**
2. Create a new session with a descriptive name
3. Add target systems to the session
4. Use sessions to group related testing activities

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-super-secret-django-key-here
DEBUG=False

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///va_assistant.db

# Allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip

# Logging
LOG_LEVEL=INFO
```

### Django Settings
Key settings can be modified in `va_assistant/settings.py`:

- **ALLOWED_HOSTS**: Configure allowed IP addresses/domains
- **CORS_ALLOWED_ORIGINS**: Configure frontend CORS origins
- **LOGGING**: Adjust logging levels and destinations
- **REST_FRAMEWORK**: API configuration

## 🔒 Security Considerations

### For Airgapped Environments
- All credentials are processed in memory only
- No external network connections required
- SQLite database for minimal attack surface
- Local authentication only

### Network Security
- Configure firewall rules appropriately
- Use HTTPS in production (configure reverse proxy)
- Regular security updates
- Monitor access logs

### Credential Handling
- Credentials are never stored in the database
- Transmitted over HTTPS only
- Memory is cleared after test execution
- Consider using SSH keys instead of passwords

## 📊 API Documentation

### Base URL
```
http://your-server:8000/api/
```

### Main Endpoints

#### Target Systems
- `GET /api/target-systems/` - List all target systems
- `POST /api/target-systems/` - Create new target system
- `GET /api/target-systems/{id}/` - Get specific target system
- `PATCH /api/target-systems/{id}/` - Update target system
- `DELETE /api/target-systems/{id}/` - Delete target system

#### Connectivity Tests
- `GET /api/connectivity-tests/` - List connectivity tests
- `POST /api/connectivity-tests/run/` - Run connectivity test
- `GET /api/connectivity-tests/{id}/` - Get test details

#### Credential Tests
- `GET /api/credential-tests/` - List credential tests
- `POST /api/credential-tests/run/` - Run credential test
- `GET /api/credential-tests/{id}/` - Get test details

#### Batch Testing
- `POST /api/batch-test/` - Run batch tests

#### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/health/` - System health check

### Example API Usage

**Create Target System**:
```bash
curl -X POST http://localhost:8000/api/target-systems/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Web Server 1",
    "ip_address": "192.168.1.100",
    "operating_system": "linux"
  }'
```

**Run Connectivity Test**:
```bash
curl -X POST http://localhost:8000/api/connectivity-tests/run/ \
  -H "Content-Type: application/json" \
  -d '{
    "target_system_id": 1,
    "test_type": "ping",
    "timeout": 5
  }'
```

## 🔍 Monitoring and Troubleshooting

### Service Management
```bash
# Check service status
sudo systemctl status va-assistant

# View logs
journalctl -u va-assistant -f

# Restart service
sudo systemctl restart va-assistant
```

### Log Files
- Application logs: `/var/log/va-assistant/`
- Django logs: Check `va_assistant.log` in the project directory
- Web server logs: `/var/log/nginx/` (if using Nginx)

### Common Issues

**Service won't start**:
- Check Python virtual environment path
- Verify database permissions
- Check port availability (8000)

**Tests failing**:
- Verify network connectivity to targets
- Check firewall rules
- Validate credentials
- Review target system configurations

**Frontend not loading**:
- Ensure frontend was built (`npm run build`)
- Check static files were collected
- Verify web server configuration

## 🔄 Backup and Maintenance

### Backup
Use the included backup script:
```bash
/opt/va-assistant/backup.sh
```

Or manually backup important files:
- Database: `db.sqlite3`
- Configuration: `.env`, `va_assistant/settings.py`
- Logs: `/var/log/va-assistant/`

### Updates
1. Stop the service: `sudo systemctl stop va-assistant`
2. Backup current installation
3. Update code files
4. Install new dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Collect static files: `python manage.py collectstatic --noinput`
7. Start service: `sudo systemctl start va-assistant`

### Log Rotation
Log rotation is automatically configured via `/etc/logrotate.d/va-assistant`.

## 🤝 Contributing

This application is designed for internal vulnerability assessment use. If you need to modify or extend functionality:

1. Backend changes: Modify Django models, views, and serializers
2. Frontend changes: Update React components in the `frontend/src/` directory
3. API changes: Update both backend serializers and frontend TypeScript types

## 📄 License

This project is designed for internal use in vulnerability assessment environments. Please ensure compliance with your organization's software policies.

## 🆘 Support

For technical support:
1. Check the troubleshooting section above
2. Review application logs
3. Verify system requirements
4. Check network connectivity

## 📚 Technical Details

### Database Schema
- **TargetSystem**: Stores target system information
- **ConnectivityTest**: Records connectivity test results
- **CredentialTest**: Records credential test results (no credentials stored)
- **TestSession**: Groups related tests together

### Test Execution Flow
1. User initiates test via web interface or API
2. Test record created in database with "pending" status
3. Background thread executes actual test
4. Results updated in real-time
5. Frontend polls for status updates

### Supported Test Types
- **Ping**: ICMP echo requests
- **TCP Connect**: TCP socket connections
- **Port Scan**: Multiple port connectivity checks
- **SSH Password**: SSH authentication with password
- **SSH Key**: SSH authentication with private key
- **Windows**: Basic Windows service connectivity

---

**VA Assistant** - Making vulnerability assessment more efficient and reliable. #   v a - a s s i s t a n t 
