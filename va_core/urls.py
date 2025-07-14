from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'va_core'

urlpatterns = [
    # Target Systems
    path('target-systems/', views.TargetSystemListCreateView.as_view(), name='target-systems-list'),
    path('target-systems/<int:pk>/', views.TargetSystemDetailView.as_view(), name='target-systems-detail'),
    
    # Bulk Scans
    path('bulk-scans/', views.BulkScanListView.as_view(), name='bulk-scans-list'),
    path('bulk-scans/<str:scan_id>/', views.BulkScanDetailView.as_view(), name='bulk-scans-detail'),
    
    # Connectivity Tests
    path('connectivity-tests/', views.ConnectivityTestListView.as_view(), name='connectivity-tests-list'),
    path('connectivity-tests/<int:pk>/', views.ConnectivityTestDetailView.as_view(), name='connectivity-tests-detail'),
    path('connectivity-tests/run/', views.RunConnectivityTestView.as_view(), name='run-connectivity-test'),
    path('connectivity-tests/bulk-scan/', views.BulkIPScanView.as_view(), name='bulk-ip-scan'),
    
    # Credential Tests
    path('credential-tests/', views.CredentialTestListView.as_view(), name='credential-tests-list'),
    path('credential-tests/<int:pk>/', views.CredentialTestDetailView.as_view(), name='credential-tests-detail'),
    path('credential-tests/run/', views.RunCredentialTestView.as_view(), name='run-credential-test'),
    
    # Test Sessions
    path('test-sessions/', views.TestSessionListCreateView.as_view(), name='test-sessions-list'),
    path('test-sessions/<int:pk>/', views.TestSessionDetailView.as_view(), name='test-sessions-detail'),
    
    # Batch Operations
    path('batch-test/', views.BatchTestView.as_view(), name='batch-test'),
    
    # Dashboard and System Health
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('health/', views.system_health_check, name='system-health'),
] 