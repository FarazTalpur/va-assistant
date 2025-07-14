import subprocess
import socket
import time
import platform
import paramiko
import logging
import threading
import concurrent.futures
from django.utils import timezone
from .models import ConnectivityTest, CredentialTest, TargetSystem

logger = logging.getLogger(__name__)


class ConnectivityTester:
    """Utility class for network connectivity testing"""
    
    @staticmethod
    def ping_test(ip_address, timeout=5):
        """
        Perform ping test to check basic connectivity
        """
        try:
            # Determine ping command based on OS
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip_address]
            else:
                cmd = ['ping', '-c', '1', '-W', str(timeout), ip_address]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'response_time': response_time,
                    'output': result.stdout,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response_time': None,
                    'output': result.stdout,
                    'error': result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'Ping timeout after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': str(e)
            }
    
    @staticmethod
    def tcp_connect_test(ip_address, port, timeout=5):
        """
        Test TCP connectivity to a specific port
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((ip_address, port))
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            sock.close()
            
            if result == 0:
                return {
                    'success': True,
                    'response_time': response_time,
                    'output': f'Successfully connected to {ip_address}:{port}',
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response_time': None,
                    'output': '',
                    'error': f'Connection failed to {ip_address}:{port}'
                }
        
        except socket.timeout:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'Connection timeout to {ip_address}:{port} after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': str(e)
            }
    
    @staticmethod
    def port_scan_test(ip_address, port_range=(1, 1024), timeout=1):
        """
        Scan multiple ports to check which are open
        """
        open_ports = []
        closed_ports = []
        
        if isinstance(port_range, int):
            ports_to_scan = [port_range]
        elif isinstance(port_range, tuple) and len(port_range) == 2:
            ports_to_scan = range(port_range[0], port_range[1] + 1)
        else:
            ports_to_scan = range(1, 1025)  # Default scan
        
        for port in ports_to_scan:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                else:
                    closed_ports.append(port)
            
            except Exception:
                closed_ports.append(port)
        
        return {
            'success': len(open_ports) > 0,
            'response_time': None,
            'output': f'Open ports: {open_ports[:10]}{"..." if len(open_ports) > 10 else ""}',
            'error': None if open_ports else f'No open ports found in range {port_range}',
            'open_ports': open_ports,
            'total_scanned': len(list(ports_to_scan))
        }


class BulkIPScanner:
    """Utility class for bulk IP scanning with system classification"""
    
    @staticmethod
    def classify_system(open_ports):
        """
        Classify system type based on open ports
        Returns: ('windows', 'unix', 'unknown')
        """
        # Windows indicators: SMB ports 139, 445
        windows_ports = [139, 445]
        # Unix/Linux indicators: SSH ports 22, 2222
        unix_ports = [22, 2222]
        
        has_windows_ports = any(port in open_ports for port in windows_ports)
        has_unix_ports = any(port in open_ports for port in unix_ports)
        
        if has_windows_ports and has_unix_ports:
            # Both detected, prioritize Windows if both SMB ports are open
            if 139 in open_ports and 445 in open_ports:
                return 'windows'
            else:
                return 'unix'
        elif has_windows_ports:
            return 'windows'
        elif has_unix_ports:
            return 'unix'
        else:
            return 'unknown'
    
    @staticmethod
    def scan_single_ip(ip_address, timeout=5):
        """
        Perform comprehensive scan on a single IP address
        Tests: ping, SSH ports (22, 2222), SMB ports (139, 445)
        """
        results = {
            'ip_address': ip_address,
            'ping_result': None,
            'ssh_ports': {},
            'smb_ports': {},
            'system_type': 'unknown',
            'open_ports': [],
            'scan_timestamp': timezone.now().isoformat()
        }
        
        try:
            # 1. Ping test
            results['ping_result'] = ConnectivityTester.ping_test(ip_address, timeout)
            
            # 2. SSH port tests (22, 2222)
            ssh_ports = [22, 2222]
            for port in ssh_ports:
                port_result = ConnectivityTester.tcp_connect_test(ip_address, port, timeout)
                results['ssh_ports'][port] = port_result
                if port_result['success']:
                    results['open_ports'].append(port)
            
            # 3. SMB port tests (139, 445)
            smb_ports = [139, 445]
            for port in smb_ports:
                port_result = ConnectivityTester.tcp_connect_test(ip_address, port, timeout)
                results['smb_ports'][port] = port_result
                if port_result['success']:
                    results['open_ports'].append(port)
            
            # 4. System classification
            results['system_type'] = BulkIPScanner.classify_system(results['open_ports'])
            
            # 5. Overall status
            results['overall_status'] = 'success' if (
                results['ping_result']['success'] or 
                len(results['open_ports']) > 0
            ) else 'failed'
            
        except Exception as e:
            results['error'] = str(e)
            results['overall_status'] = 'error'
            logger.error(f"Error scanning IP {ip_address}: {str(e)}")
        
        return results
    
    @staticmethod
    def scan_multiple_ips(ip_addresses, timeout=5, max_workers=10):
        """
        Perform bulk IP scanning with parallel processing
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scanning tasks
            future_to_ip = {
                executor.submit(BulkIPScanner.scan_single_ip, ip, timeout): ip 
                for ip in ip_addresses
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error scanning IP {ip}: {str(e)}")
                    results.append({
                        'ip_address': ip,
                        'error': str(e),
                        'overall_status': 'error',
                        'scan_timestamp': timezone.now().isoformat()
                    })
        
        return results


def parse_ip_input(ip_input):
    """
    Parse IP input string (comma-separated or line-separated)
    Returns list of valid IP addresses
    """
    import ipaddress
    
    ips = []
    # Split by comma first, then by newlines
    raw_ips = []
    
    if ',' in ip_input:
        raw_ips = [ip.strip() for ip in ip_input.split(',')]
    else:
        raw_ips = [ip.strip() for ip in ip_input.split('\n')]
    
    for ip in raw_ips:
        if ip:  # Skip empty strings
            try:
                # Validate IP address
                ipaddress.ip_address(ip)
                ips.append(ip)
            except ValueError:
                logger.warning(f"Invalid IP address format: {ip}")
                continue
    
    return ips


def create_target_systems_from_scan(scan_results):
    """
    Create or update TargetSystem entries from scan results
    """
    created_systems = []
    
    for result in scan_results:
        if result.get('overall_status') == 'success':
            ip_address = result['ip_address']
            system_type = result.get('system_type', 'unknown')
            
            # Map system type to model choices
            os_mapping = {
                'windows': 'windows',
                'unix': 'unix',
                'unknown': 'unix'  # Default to unix if unknown
            }
            
            # Check if target system already exists
            target_system, created = TargetSystem.objects.get_or_create(
                ip_address=ip_address,
                defaults={
                    'name': f"{system_type.title()} System - {ip_address}",
                    'hostname': ip_address,
                    'operating_system': os_mapping.get(system_type, 'unix'),
                    'description': f"Auto-discovered {system_type} system with open ports: {result.get('open_ports', [])}"
                }
            )
            
            if not created:
                # Update existing system with new scan data
                target_system.operating_system = os_mapping.get(system_type, target_system.operating_system)
                target_system.description = f"Last scan: {result.get('scan_timestamp', 'Unknown')} - Open ports: {result.get('open_ports', [])}"
                target_system.save()
            
            created_systems.append({
                'target_system': target_system,
                'scan_result': result,
                'created': created
            })
    
    return created_systems


def save_connectivity_tests_from_scan(scan_results):
    """
    Save connectivity test results to database
    """
    saved_tests = []
    
    for result in scan_results:
        ip_address = result['ip_address']
        
        # Get or create target system
        try:
            target_system = TargetSystem.objects.get(ip_address=ip_address)
        except TargetSystem.DoesNotExist:
            # Create a basic target system if it doesn't exist
            target_system = TargetSystem.objects.create(
                name=f"System - {ip_address}",
                ip_address=ip_address,
                operating_system='unix',  # Default
                description="Auto-created during bulk IP scan"
            )
        
        # Save ping test result
        if result.get('ping_result'):
            ping_test = ConnectivityTest.objects.create(
                target_system=target_system,
                test_type='ping',
                status='success' if result['ping_result']['success'] else 'failed',
                response_time=result['ping_result'].get('response_time'),
                error_message=result['ping_result'].get('error'),
                test_output=result['ping_result'],
                completed_at=timezone.now()
            )
            saved_tests.append(ping_test)
        
        # Save SSH port test results
        for port, port_result in result.get('ssh_ports', {}).items():
            ssh_test = ConnectivityTest.objects.create(
                target_system=target_system,
                test_type='tcp_connect',
                port=port,
                status='success' if port_result['success'] else 'failed',
                response_time=port_result.get('response_time'),
                error_message=port_result.get('error'),
                test_output=port_result,
                completed_at=timezone.now()
            )
            saved_tests.append(ssh_test)
        
        # Save SMB port test results
        for port, port_result in result.get('smb_ports', {}).items():
            smb_test = ConnectivityTest.objects.create(
                target_system=target_system,
                test_type='tcp_connect',
                port=port,
                status='success' if port_result['success'] else 'failed',
                response_time=port_result.get('response_time'),
                error_message=port_result.get('error'),
                test_output=port_result,
                completed_at=timezone.now()
            )
            saved_tests.append(smb_test)
    
    return saved_tests


class CredentialTester:
    """Utility class for credential validation testing"""
    
    @staticmethod
    def ssh_password_test(ip_address, username, password, port=22, timeout=10):
        """
        Test SSH login with username/password
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            start_time = time.time()
            client.connect(
                hostname=ip_address,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                banner_timeout=timeout,
                auth_timeout=timeout
            )
            end_time = time.time()
            
            # Test command execution
            stdin, stdout, stderr = client.exec_command('whoami', timeout=5)
            whoami_result = stdout.read().decode().strip()
            
            client.close()
            
            return {
                'success': True,
                'response_time': (end_time - start_time) * 1000,
                'output': f'Successfully authenticated as {whoami_result}',
                'error': None,
                'user_info': whoami_result
            }
        
        except paramiko.AuthenticationException:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': 'Authentication failed - invalid credentials'
            }
        except paramiko.SSHException as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'SSH connection error: {str(e)}'
            }
        except socket.timeout:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'Connection timeout after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'Connection error: {str(e)}'
            }
    
    @staticmethod
    def ssh_key_test(ip_address, username, private_key_content, port=22, timeout=10):
        """
        Test SSH login with private key
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Load private key from string
            from io import StringIO
            private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_content))
            
            start_time = time.time()
            client.connect(
                hostname=ip_address,
                port=port,
                username=username,
                pkey=private_key,
                timeout=timeout,
                banner_timeout=timeout,
                auth_timeout=timeout
            )
            end_time = time.time()
            
            # Test command execution
            stdin, stdout, stderr = client.exec_command('whoami', timeout=5)
            whoami_result = stdout.read().decode().strip()
            
            client.close()
            
            return {
                'success': True,
                'response_time': (end_time - start_time) * 1000,
                'output': f'Successfully authenticated with SSH key as {whoami_result}',
                'error': None,
                'user_info': whoami_result
            }
        
        except paramiko.AuthenticationException:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': 'Authentication failed - invalid SSH key or username'
            }
        except paramiko.SSHException as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'SSH connection error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'SSH key authentication error: {str(e)}'
            }
    
    @staticmethod
    def windows_credential_test(ip_address, username, password, port=3389, timeout=10):
        """
        Test Windows credential using WinRM or RDP-like connection
        Note: This is a simplified test - in production you might want to use pywinrm
        """
        try:
            # For Windows systems, we'll try to establish a connection to common Windows ports
            # This is a basic connectivity test with credential validation simulation
            
            # Try RDP port (3389) or WinRM ports (5985/5986)
            test_ports = [3389, 5985, 5986] if port == 3389 else [port]
            
            for test_port in test_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((ip_address, test_port))
                    sock.close()
                    
                    if result == 0:
                        # Port is open, simulating credential validation
                        # In a real implementation, you would use pywinrm or similar
                        return {
                            'success': True,
                            'response_time': timeout * 1000,  # Simulated response time
                            'output': f'Windows service accessible on port {test_port}. Credential validation simulated.',
                            'error': None,
                            'note': 'This is a simulated test. Implement actual WinRM/RDP credential validation for production use.'
                        }
                except Exception:
                    continue
            
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'Windows services not accessible on {ip_address}. Ports {test_ports} are closed.'
            }
        
        except Exception as e:
            return {
                'success': False,
                'response_time': None,
                'output': '',
                'error': f'Windows credential test error: {str(e)}'
            }


def run_connectivity_test(test_id):
    """
    Run a connectivity test asynchronously
    """
    try:
        test = ConnectivityTest.objects.get(id=test_id)
        test.status = 'running'
        test.save()
        
        logger.info(f"Starting connectivity test {test_id} for {test.target_system.ip_address}")
        
        # Perform the actual test based on test type
        if test.test_type == 'ping':
            result = ConnectivityTester.ping_test(test.target_system.ip_address)
        elif test.test_type == 'tcp_connect':
            result = ConnectivityTester.tcp_connect_test(
                test.target_system.ip_address, 
                test.port or 80
            )
        elif test.test_type == 'port_scan':
            port_range = (test.port, test.port) if test.port else (1, 1024)
            result = ConnectivityTester.port_scan_test(
                test.target_system.ip_address,
                port_range
            )
        else:
            result = {'success': False, 'error': f'Unknown test type: {test.test_type}'}
        
        # Update test results
        test.status = 'success' if result['success'] else 'failed'
        test.response_time = result.get('response_time')
        test.error_message = result.get('error')
        test.test_output = result
        test.completed_at = timezone.now()
        test.save()
        
        logger.info(f"Completed connectivity test {test_id} with status: {test.status}")
        
    except ConnectivityTest.DoesNotExist:
        logger.error(f"Connectivity test {test_id} not found")
    except Exception as e:
        logger.error(f"Error running connectivity test {test_id}: {str(e)}")
        try:
            test = ConnectivityTest.objects.get(id=test_id)
            test.status = 'failed'
            test.error_message = str(e)
            test.completed_at = timezone.now()
            test.save()
        except:
            pass


def run_credential_test(test_id, credentials):
    """
    Run a credential test asynchronously
    """
    try:
        test = CredentialTest.objects.get(id=test_id)
        test.status = 'running'
        test.save()
        
        logger.info(f"Starting credential test {test_id} for {test.username}@{test.target_system.ip_address}")
        
        # Perform the actual test based on auth method and target OS
        if test.auth_method == 'password':
            if test.target_system.operating_system == 'windows':
                result = CredentialTester.windows_credential_test(
                    test.target_system.ip_address,
                    test.username,
                    credentials.get('password', ''),
                    port=credentials.get('port', 3389)
                )
            else:
                result = CredentialTester.ssh_password_test(
                    test.target_system.ip_address,
                    test.username,
                    credentials.get('password', ''),
                    port=credentials.get('port', 22)
                )
        elif test.auth_method == 'ssh_key':
            result = CredentialTester.ssh_key_test(
                test.target_system.ip_address,
                test.username,
                credentials.get('ssh_key', ''),
                port=credentials.get('port', 22)
            )
        else:
            result = {'success': False, 'error': f'Authentication method {test.auth_method} not implemented'}
        
        # Update test results
        if result['success']:
            test.status = 'success'
        elif 'Authentication failed' in result.get('error', ''):
            test.status = 'unauthorized'
        else:
            test.status = 'connection_error'
        
        test.error_message = result.get('error')
        test.test_output = {k: v for k, v in result.items() if k not in ['password', 'ssh_key']}
        test.completed_at = timezone.now()
        test.save()
        
        logger.info(f"Completed credential test {test_id} with status: {test.status}")
        
    except CredentialTest.DoesNotExist:
        logger.error(f"Credential test {test_id} not found")
    except Exception as e:
        logger.error(f"Error running credential test {test_id}: {str(e)}")
        try:
            test = CredentialTest.objects.get(id=test_id)
            test.status = 'failed'
            test.error_message = str(e)
            test.completed_at = timezone.now()
            test.save()
        except:
            pass 