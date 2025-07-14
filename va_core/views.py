from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import threading
import logging

from .models import TargetSystem, ConnectivityTest, CredentialTest, TestSession, BulkScan
from .serializers import (
    TargetSystemSerializer, ConnectivityTestSerializer, CredentialTestSerializer,
    TestSessionSerializer, ConnectivityTestRequestSerializer, CredentialTestRequestSerializer,
    BulkScanSerializer
)
from .utils import (
    run_connectivity_test, run_credential_test, BulkIPScanner, parse_ip_input,
    create_target_systems_from_scan, save_connectivity_tests_from_scan
)

logger = logging.getLogger(__name__)


class TargetSystemListCreateView(generics.ListCreateAPIView):
    """List all target systems or create a new one"""
    queryset = TargetSystem.objects.all()
    serializer_class = TargetSystemSerializer
    permission_classes = [permissions.AllowAny]


class TargetSystemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a target system"""
    queryset = TargetSystem.objects.all()
    serializer_class = TargetSystemSerializer
    permission_classes = [permissions.AllowAny]


class BulkScanListView(generics.ListAPIView):
    """List all bulk scans"""
    queryset = BulkScan.objects.all()
    serializer_class = BulkScanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = BulkScan.objects.all()
        status_filter = self.request.query_params.get('status')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class BulkScanDetailView(generics.RetrieveAPIView):
    """Retrieve a specific bulk scan"""
    queryset = BulkScan.objects.all()
    serializer_class = BulkScanSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'scan_id'  # Use scan_id instead of pk


class ConnectivityTestListView(generics.ListAPIView):
    """List all connectivity tests"""
    queryset = ConnectivityTest.objects.all()
    serializer_class = ConnectivityTestSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = ConnectivityTest.objects.all()
        target_system_id = self.request.query_params.get('target_system_id')
        status_filter = self.request.query_params.get('status')
        
        if target_system_id:
            queryset = queryset.filter(target_system_id=target_system_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-started_at')


class ConnectivityTestDetailView(generics.RetrieveAPIView):
    """Retrieve a specific connectivity test"""
    queryset = ConnectivityTest.objects.all()
    serializer_class = ConnectivityTestSerializer
    permission_classes = [permissions.AllowAny]


class CredentialTestListView(generics.ListAPIView):
    """List all credential tests"""
    queryset = CredentialTest.objects.all()
    serializer_class = CredentialTestSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = CredentialTest.objects.all()
        target_system_id = self.request.query_params.get('target_system_id')
        status_filter = self.request.query_params.get('status')
        
        if target_system_id:
            queryset = queryset.filter(target_system_id=target_system_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-started_at')


class CredentialTestDetailView(generics.RetrieveAPIView):
    """Retrieve a specific credential test"""
    queryset = CredentialTest.objects.all()
    serializer_class = CredentialTestSerializer
    permission_classes = [permissions.AllowAny]


class TestSessionListCreateView(generics.ListCreateAPIView):
    """List all test sessions or create a new one"""
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer
    permission_classes = [permissions.AllowAny]


class TestSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a test session"""
    queryset = TestSession.objects.all()
    serializer_class = TestSessionSerializer
    permission_classes = [permissions.AllowAny]


class RunConnectivityTestView(APIView):
    """Run a connectivity test"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ConnectivityTestRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                target_system = TargetSystem.objects.get(id=data['target_system_id'])
                
                # Create connectivity test record
                connectivity_test = ConnectivityTest.objects.create(
                    target_system=target_system,
                    test_type=data['test_type'],
                    port=data.get('port'),
                    status='pending'
                )
                
                # Run test in background thread
                thread = threading.Thread(
                    target=run_connectivity_test, 
                    args=(connectivity_test.id,)
                )
                thread.daemon = True
                thread.start()
                
                # Return immediate response
                return Response({
                    'test_id': connectivity_test.id,
                    'status': 'started',
                    'message': f'Connectivity test started for {target_system.name}',
                    'test_details': ConnectivityTestSerializer(connectivity_test).data
                }, status=status.HTTP_201_CREATED)
                
            except TargetSystem.DoesNotExist:
                return Response(
                    {'error': 'Target system not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error starting connectivity test: {str(e)}")
                return Response(
                    {'error': f'Failed to start connectivity test: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RunCredentialTestView(APIView):
    """Run a credential test"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = CredentialTestRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                target_system = TargetSystem.objects.get(id=data['target_system_id'])
                
                # Create credential test record
                credential_test = CredentialTest.objects.create(
                    target_system=target_system,
                    username=data['username'],
                    auth_method=data['auth_method'],
                    status='pending'
                )
                
                # Prepare credentials (don't store sensitive data)
                credentials = {
                    'password': data.get('password'),
                    'ssh_key': data.get('ssh_key'),
                    'port': data.get('port'),
                    'timeout': data.get('timeout', 10)
                }
                
                # Run test in background thread
                thread = threading.Thread(
                    target=run_credential_test, 
                    args=(credential_test.id, credentials)
                )
                thread.daemon = True
                thread.start()
                
                # Return immediate response (without sensitive data)
                response_data = CredentialTestSerializer(credential_test).data
                response_data.pop('password', None)
                response_data.pop('ssh_key', None)
                
                return Response({
                    'test_id': credential_test.id,
                    'status': 'started',
                    'message': f'Credential test started for {data["username"]}@{target_system.name}',
                    'test_details': response_data
                }, status=status.HTTP_201_CREATED)
                
            except TargetSystem.DoesNotExist:
                return Response(
                    {'error': 'Target system not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error starting credential test: {str(e)}")
                return Response(
                    {'error': f'Failed to start credential test: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchTestView(APIView):
    """Run batch tests on multiple target systems"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        target_system_ids = request.data.get('target_system_ids', [])
        test_types = request.data.get('test_types', ['ping'])
        credentials = request.data.get('credentials', {})
        
        if not target_system_ids:
            return Response(
                {'error': 'target_system_ids is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'connectivity_tests': [],
            'credential_tests': [],
            'errors': []
        }
        
        for target_id in target_system_ids:
            try:
                target_system = TargetSystem.objects.get(id=target_id)
                
                # Run connectivity tests
                for test_type in test_types:
                    if test_type in ['ping', 'tcp_connect', 'port_scan']:
                        connectivity_test = ConnectivityTest.objects.create(
                            target_system=target_system,
                            test_type=test_type,
                            status='pending'
                        )
                        
                        # Start test in background
                        thread = threading.Thread(
                            target=run_connectivity_test, 
                            args=(connectivity_test.id,)
                        )
                        thread.daemon = True
                        thread.start()
                        
                        results['connectivity_tests'].append({
                            'test_id': connectivity_test.id,
                            'target_system': target_system.name,
                            'test_type': test_type,
                            'status': 'started'
                        })
                
                # Run credential tests if credentials are provided
                if credentials.get('username'):
                    credential_test = CredentialTest.objects.create(
                        target_system=target_system,
                        username=credentials['username'],
                        auth_method=credentials.get('auth_method', 'password'),
                        status='pending'
                    )
                    
                    # Start test in background
                    thread = threading.Thread(
                        target=run_credential_test, 
                        args=(credential_test.id, credentials)
                    )
                    thread.daemon = True
                    thread.start()
                    
                    results['credential_tests'].append({
                        'test_id': credential_test.id,
                        'target_system': target_system.name,
                        'username': credentials['username'],
                        'status': 'started'
                    })
                    
            except TargetSystem.DoesNotExist:
                results['errors'].append(f'Target system with ID {target_id} not found')
            except Exception as e:
                results['errors'].append(f'Error processing target {target_id}: {str(e)}')
        
        return Response(results, status=status.HTTP_201_CREATED)


class BulkIPScanView(APIView):
    """Bulk IP scanning with system classification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Perform bulk IP scanning
        Expected payload: {
            "ip_input": "192.168.1.1,192.168.1.2\n192.168.1.3",
            "timeout": 5,
            "save_results": true,
            "name": "Project Name"
        }
        """
        try:
            # Parse request data
            ip_input = request.data.get('ip_input', '')
            timeout = request.data.get('timeout', 5)
            save_results = request.data.get('save_results', True)
            name = request.data.get('name', 'Bulk Scan')
            
            if not ip_input:
                return Response(
                    {'error': 'IP input is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse IP addresses
            ip_addresses = parse_ip_input(ip_input)
            
            if not ip_addresses:
                return Response(
                    {'error': 'No valid IP addresses found in input'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(ip_addresses) > 100:  # Limit to prevent abuse
                return Response(
                    {'error': 'Maximum 100 IP addresses allowed per scan'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create bulk scan record
            scan_id = f"bulk_scan_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            bulk_scan = BulkScan.objects.create(
                scan_id=scan_id,
                name=name,
                ip_input=ip_input,
                total_ips=len(ip_addresses),
                status='running',
                timeout_setting=timeout
            )
            
            # Perform bulk scanning
            logger.info(f"Starting bulk IP scan {scan_id} for {len(ip_addresses)} addresses")
            scan_results = BulkIPScanner.scan_multiple_ips(ip_addresses, timeout)
            
            # Calculate summary statistics
            successful_scans = len([r for r in scan_results if r.get('overall_status') == 'success'])
            failed_scans = len([r for r in scan_results if r.get('overall_status') == 'failed'])
            error_scans = len([r for r in scan_results if r.get('overall_status') == 'error'])
            
            # System type summary
            system_types = {}
            for result in scan_results:
                if result.get('overall_status') == 'success':
                    sys_type = result.get('system_type', 'unknown')
                    system_types[sys_type] = system_types.get(sys_type, 0) + 1
            
            # Save results to database if requested
            created_systems = []
            saved_tests = []
            
            if save_results:
                created_systems = create_target_systems_from_scan(scan_results)
                # Note: We're not saving individual connectivity tests for bulk scans
                # The detailed results are stored in the bulk_scan.scan_results field
            
            # Update bulk scan record
            bulk_scan.successful_scans = successful_scans
            bulk_scan.failed_scans = failed_scans
            bulk_scan.error_scans = error_scans
            bulk_scan.system_types = system_types
            bulk_scan.scan_results = scan_results
            bulk_scan.created_systems = len(created_systems)
            bulk_scan.saved_tests = len(saved_tests)
            bulk_scan.status = 'completed'
            bulk_scan.completed_at = timezone.now()
            bulk_scan.save()
            
            # Prepare response
            response_data = {
                'scan_id': scan_id,
                'name': name,
                'total_ips': len(ip_addresses),
                'successful_scans': successful_scans,
                'failed_scans': failed_scans,
                'error_scans': error_scans,
                'scan_results': scan_results,
                'created_systems': len(created_systems),
                'saved_tests': len(saved_tests),
                'system_types': system_types,
                'scan_timestamp': timezone.now().isoformat(),
                'success_rate': bulk_scan.success_rate
            }
            
            logger.info(f"Bulk IP scan {scan_id} completed: {successful_scans}/{len(ip_addresses)} successful")
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in bulk IP scan: {str(e)}")
            # Update bulk scan status to failed if it exists
            if 'bulk_scan' in locals():
                bulk_scan.status = 'failed'
                bulk_scan.completed_at = timezone.now()
                bulk_scan.save()
            
            return Response(
                {'error': f'Bulk IP scan failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        total_systems = TargetSystem.objects.count()
        total_bulk_scans = BulkScan.objects.count()
        total_credential_tests = CredentialTest.objects.count()
        
        # Recent test stats (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = timezone.now() - timedelta(days=1)
        
        recent_bulk_scans = BulkScan.objects.filter(created_at__gte=yesterday)
        recent_credentials = CredentialTest.objects.filter(started_at__gte=yesterday)
        
        # Bulk scan success rate (based on completed scans)
        bulk_scan_success_rate = 0
        completed_bulk_scans = recent_bulk_scans.filter(status='completed')
        if completed_bulk_scans.count() > 0:
            total_success_rate = sum([scan.success_rate for scan in completed_bulk_scans])
            bulk_scan_success_rate = total_success_rate / completed_bulk_scans.count()
        
        credential_success_rate = 0
        if recent_credentials.count() > 0:
            credential_success_rate = (
                recent_credentials.filter(status='success').count() / 
                recent_credentials.count() * 100
            )
        
        # System breakdown by OS
        systems_by_os = {}
        for system in TargetSystem.objects.all():
            os_type = system.operating_system
            systems_by_os[os_type] = systems_by_os.get(os_type, 0) + 1
        
        # Bulk scan statistics
        bulk_scan_stats = {
            'total_scans': total_bulk_scans,
            'completed_scans': BulkScan.objects.filter(status='completed').count(),
            'running_scans': BulkScan.objects.filter(status='running').count(),
            'failed_scans': BulkScan.objects.filter(status='failed').count(),
        }
        
        # Recent bulk scans summary
        total_ips_scanned = sum([scan.total_ips for scan in recent_bulk_scans])
        total_successful_ips = sum([scan.successful_scans for scan in recent_bulk_scans])
        
        # System types detected in recent scans
        recent_system_types = {}
        for scan in recent_bulk_scans.filter(status='completed'):
            for sys_type, count in scan.system_types.items():
                recent_system_types[sys_type] = recent_system_types.get(sys_type, 0) + count
        
        return Response({
            'total_systems': total_systems,
            'total_bulk_scans': total_bulk_scans,
            'total_credential_tests': total_credential_tests,
            'recent_tests': {
                'bulk_scans': recent_bulk_scans.count(),
                'credentials': recent_credentials.count(),
                'ips_scanned': total_ips_scanned,
                'successful_ips': total_successful_ips,
            },
            'success_rates': {
                'bulk_scans': round(bulk_scan_success_rate, 2),
                'credentials': round(credential_success_rate, 2),
            },
            'systems_by_os': systems_by_os,
            'recent_system_types': recent_system_types,
            'bulk_scan_stats': bulk_scan_stats,
            'recent_activity': {
                'bulk_scans': BulkScanSerializer(
                    recent_bulk_scans.order_by('-created_at')[:5], many=True
                ).data,
                'credential_tests': CredentialTestSerializer(
                    recent_credentials.order_by('-started_at')[:5], many=True
                ).data,
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return Response(
            {'error': f'Failed to get dashboard statistics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def system_health_check(request):
    """Check the health of the VA Assistant system"""
    try:
        # Check database connectivity
        db_status = 'healthy'
        try:
            TargetSystem.objects.count()
        except Exception:
            db_status = 'unhealthy'
        
        # Check recent test activity
        from datetime import datetime, timedelta
        last_hour = timezone.now() - timedelta(hours=1)
        
        recent_tests = (
            ConnectivityTest.objects.filter(started_at__gte=last_hour).count() +
            CredentialTest.objects.filter(started_at__gte=last_hour).count()
        )
        
        return Response({
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'database': db_status,
            'recent_activity': recent_tests,
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })
    
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 