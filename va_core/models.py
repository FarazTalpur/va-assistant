from django.db import models
from django.contrib.auth.models import User
import json


class TargetSystem(models.Model):
    """Model to store target system information"""
    
    OS_CHOICES = [
        ('windows', 'Windows'),
        ('linux', 'Linux'),
        ('unix', 'Unix'),
    ]
    
    name = models.CharField(max_length=255, help_text="Friendly name for the target system")
    ip_address = models.GenericIPAddressField(help_text="IP address of the target system")
    hostname = models.CharField(max_length=255, blank=True, null=True, help_text="Hostname of the target system")
    operating_system = models.CharField(max_length=20, choices=OS_CHOICES, help_text="Operating system type")
    description = models.TextField(blank=True, null=True, help_text="Additional description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'ip_address']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class BulkScan(models.Model):
    """Model to track bulk IP scan operations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    scan_id = models.CharField(max_length=100, unique=True, help_text="Unique identifier for the bulk scan")
    name = models.CharField(max_length=255, default="Bulk Scan", help_text="Custom name for the bulk scan (e.g., project name)")
    ip_input = models.TextField(help_text="Original IP input string")
    total_ips = models.IntegerField(help_text="Total number of IPs scanned")
    successful_scans = models.IntegerField(default=0, help_text="Number of successful IP scans")
    failed_scans = models.IntegerField(default=0, help_text="Number of failed IP scans")
    error_scans = models.IntegerField(default=0, help_text="Number of error IP scans")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timeout_setting = models.IntegerField(default=5, help_text="Timeout setting used for the scan")
    system_types = models.JSONField(default=dict, help_text="Summary of detected system types")
    scan_results = models.JSONField(default=list, help_text="Detailed scan results for each IP")
    created_systems = models.IntegerField(default=0, help_text="Number of target systems created")
    saved_tests = models.IntegerField(default=0, help_text="Number of individual tests saved")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.scan_id}) - {self.total_ips} IPs"
    
    @property
    def duration(self):
        """Calculate scan duration"""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_ips > 0:
            return (self.successful_scans / self.total_ips) * 100
        return 0


class ConnectivityTest(models.Model):
    """Model to store network connectivity test results"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]
    
    target_system = models.ForeignKey(TargetSystem, on_delete=models.CASCADE, related_name='connectivity_tests')
    bulk_scan = models.ForeignKey(BulkScan, on_delete=models.CASCADE, related_name='connectivity_tests', null=True, blank=True)
    test_type = models.CharField(max_length=50, default='ping', help_text="Type of connectivity test (ping, port_scan, etc.)")
    port = models.IntegerField(null=True, blank=True, help_text="Port number for port-specific tests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in milliseconds")
    error_message = models.TextField(blank=True, null=True)
    test_output = models.JSONField(default=dict, help_text="Detailed test output")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.target_system.name} - {self.test_type} ({self.status})"


class CredentialTest(models.Model):
    """Model to store credential validation test results"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('unauthorized', 'Unauthorized'),
        ('connection_error', 'Connection Error'),
    ]
    
    AUTH_METHODS = [
        ('password', 'Username/Password'),
        ('ssh_key', 'SSH Key'),
        ('kerberos', 'Kerberos'),
        ('ntlm', 'NTLM'),
    ]
    
    target_system = models.ForeignKey(TargetSystem, on_delete=models.CASCADE, related_name='credential_tests')
    username = models.CharField(max_length=255, help_text="Username for authentication")
    auth_method = models.CharField(max_length=20, choices=AUTH_METHODS, default='password')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    test_output = models.JSONField(default=dict, help_text="Detailed test output (excluding sensitive data)")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.auth_method} test for {self.username}@{self.target_system.name} - {self.status}"


class TestSession(models.Model):
    """Model to group related tests in a session"""
    
    name = models.CharField(max_length=255, help_text="Session name")
    description = models.TextField(blank=True, null=True)
    target_systems = models.ManyToManyField(TargetSystem, related_name='test_sessions')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Test Session: {self.name}"
    
    @property
    def is_completed(self):
        return self.completed_at is not None
    
    @property
    def total_tests(self):
        connectivity_count = ConnectivityTest.objects.filter(target_system__in=self.target_systems.all()).count()
        credential_count = CredentialTest.objects.filter(target_system__in=self.target_systems.all()).count()
        return connectivity_count + credential_count
    
    @property
    def successful_tests(self):
        connectivity_success = ConnectivityTest.objects.filter(
            target_system__in=self.target_systems.all(),
            status='success'
        ).count()
        credential_success = CredentialTest.objects.filter(
            target_system__in=self.target_systems.all(),
            status='success'
        ).count()
        return connectivity_success + credential_success 