from rest_framework import serializers
from .models import TargetSystem, ConnectivityTest, CredentialTest, TestSession, BulkScan


class TargetSystemSerializer(serializers.ModelSerializer):
    """Serializer for TargetSystem model"""
    
    class Meta:
        model = TargetSystem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_ip_address(self, value):
        """Validate IP address format"""
        try:
            import ipaddress
            ipaddress.ip_address(value)
            return value
        except ValueError:
            raise serializers.ValidationError("Invalid IP address format")


class BulkScanSerializer(serializers.ModelSerializer):
    """Serializer for BulkScan model"""
    
    duration = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = BulkScan
        fields = '__all__'
        read_only_fields = ('created_at', 'completed_at', 'scan_id')
    
    def to_representation(self, instance):
        """Custom representation to format timestamps and duration"""
        data = super().to_representation(instance)
        
        # Format duration for display
        if instance.duration:
            duration_seconds = instance.duration.total_seconds()
            if duration_seconds < 60:
                data['duration_display'] = f"{duration_seconds:.1f}s"
            elif duration_seconds < 3600:
                data['duration_display'] = f"{duration_seconds/60:.1f}m"
            else:
                data['duration_display'] = f"{duration_seconds/3600:.1f}h"
        else:
            data['duration_display'] = "In Progress"
        
        return data


class ConnectivityTestSerializer(serializers.ModelSerializer):
    """Serializer for ConnectivityTest model"""
    
    target_system_name = serializers.CharField(source='target_system.name', read_only=True)
    target_system_ip = serializers.CharField(source='target_system.ip_address', read_only=True)
    bulk_scan_id = serializers.CharField(source='bulk_scan.scan_id', read_only=True)
    
    class Meta:
        model = ConnectivityTest
        fields = '__all__'
        read_only_fields = ('started_at', 'completed_at', 'response_time', 'test_output')


class CredentialTestSerializer(serializers.ModelSerializer):
    """Serializer for CredentialTest model"""
    
    target_system_name = serializers.CharField(source='target_system.name', read_only=True)
    target_system_ip = serializers.CharField(source='target_system.ip_address', read_only=True)
    password = serializers.CharField(write_only=True, required=False, help_text="Password for authentication (not stored)")
    ssh_key = serializers.CharField(write_only=True, required=False, help_text="SSH private key content (not stored)")
    
    class Meta:
        model = CredentialTest
        fields = '__all__'
        read_only_fields = ('started_at', 'completed_at', 'test_output')
        extra_kwargs = {
            'password': {'write_only': True},
            'ssh_key': {'write_only': True},
        }
    
    def validate(self, data):
        """Validate that required auth data is provided based on auth method"""
        auth_method = data.get('auth_method', 'password')
        
        if auth_method == 'password' and not data.get('password'):
            raise serializers.ValidationError("Password is required for password authentication")
        elif auth_method == 'ssh_key' and not data.get('ssh_key'):
            raise serializers.ValidationError("SSH key is required for SSH key authentication")
        
        return data


class TestSessionSerializer(serializers.ModelSerializer):
    """Serializer for TestSession model"""
    
    target_systems = TargetSystemSerializer(many=True, read_only=True)
    target_system_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of target system IDs to include in this session"
    )
    total_tests = serializers.ReadOnlyField()
    successful_tests = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = TestSession
        fields = '__all__'
        read_only_fields = ('created_at', 'completed_at', 'created_by')
    
    def create(self, validated_data):
        """Create test session with target systems"""
        target_system_ids = validated_data.pop('target_system_ids', [])
        test_session = TestSession.objects.create(**validated_data)
        
        if target_system_ids:
            target_systems = TargetSystem.objects.filter(id__in=target_system_ids)
            test_session.target_systems.set(target_systems)
        
        return test_session


class ConnectivityTestRequestSerializer(serializers.Serializer):
    """Serializer for connectivity test requests"""
    
    target_system_id = serializers.IntegerField(help_text="ID of the target system")
    test_type = serializers.ChoiceField(
        choices=['ping', 'tcp_connect', 'port_scan'],
        default='ping',
        help_text="Type of connectivity test to perform"
    )
    port = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=65535,
        help_text="Port number for TCP/port-specific tests"
    )
    timeout = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=30,
        help_text="Timeout in seconds for the test"
    )
    
    def validate(self, data):
        """Validate that port is provided for port-specific tests"""
        test_type = data.get('test_type')
        port = data.get('port')
        
        if test_type in ['tcp_connect', 'port_scan'] and not port:
            raise serializers.ValidationError("Port is required for TCP/port-specific tests")
        
        return data


class CredentialTestRequestSerializer(serializers.Serializer):
    """Serializer for credential test requests"""
    
    target_system_id = serializers.IntegerField(help_text="ID of the target system")
    username = serializers.CharField(max_length=255, help_text="Username for authentication")
    password = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Password for authentication"
    )
    auth_method = serializers.ChoiceField(
        choices=['password', 'ssh_key', 'kerberos', 'ntlm'],
        default='password',
        help_text="Authentication method to use"
    )
    ssh_key = serializers.CharField(
        write_only=True,
        required=False,
        help_text="SSH private key content"
    )
    port = serializers.IntegerField(
        default=22,
        min_value=1,
        max_value=65535,
        help_text="Port number for SSH/RDP connections"
    )
    timeout = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=60,
        help_text="Timeout in seconds for the test"
    )
    
    def validate(self, data):
        """Validate authentication data based on method"""
        auth_method = data.get('auth_method', 'password')
        
        if auth_method == 'password' and not data.get('password'):
            raise serializers.ValidationError("Password is required for password authentication")
        elif auth_method == 'ssh_key' and not data.get('ssh_key'):
            raise serializers.ValidationError("SSH key is required for SSH key authentication")
        
        # Set default ports based on OS and auth method
        target_system_id = data.get('target_system_id')
        if target_system_id:
            try:
                target_system = TargetSystem.objects.get(id=target_system_id)
                if not data.get('port'):
                    if target_system.operating_system == 'windows':
                        data['port'] = 3389 if auth_method in ['password', 'ntlm'] else 22
                    else:
                        data['port'] = 22
            except TargetSystem.DoesNotExist:
                raise serializers.ValidationError("Target system not found")
        
        return data 