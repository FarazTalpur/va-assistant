from django.contrib import admin
from .models import TargetSystem, ConnectivityTest, CredentialTest, TestSession, BulkScan


@admin.register(TargetSystem)
class TargetSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'hostname', 'operating_system', 'created_at')
    list_filter = ('operating_system', 'created_at')
    search_fields = ('name', 'ip_address', 'hostname')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'ip_address', 'hostname', 'operating_system')
        }),
        ('Additional Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BulkScan)
class BulkScanAdmin(admin.ModelAdmin):
    list_display = ['name', 'scan_id', 'total_ips', 'successful_scans', 'failed_scans', 'status', 'success_rate', 'duration_display', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'scan_id', 'ip_input']
    readonly_fields = ['created_at', 'completed_at', 'duration', 'success_rate']
    
    fieldsets = (
        ('Scan Information', {
            'fields': ('name', 'scan_id', 'ip_input', 'status', 'timeout_setting')
        }),
        ('Results Summary', {
            'fields': ('total_ips', 'successful_scans', 'failed_scans', 'error_scans', 'success_rate', 'system_types', 'created_systems', 'saved_tests')
        }),
        ('Detailed Results', {
            'fields': ('scan_results',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'duration')
        })
    )
    
    def duration_display(self, obj):
        if obj.duration:
            duration_seconds = obj.duration.total_seconds()
            if duration_seconds < 60:
                return f"{duration_seconds:.1f}s"
            elif duration_seconds < 3600:
                return f"{duration_seconds/60:.1f}m"
            else:
                return f"{duration_seconds/3600:.1f}h"
        return "In Progress"
    duration_display.short_description = "Duration"


@admin.register(ConnectivityTest)
class ConnectivityTestAdmin(admin.ModelAdmin):
    list_display = ('target_system', 'bulk_scan', 'test_type', 'status', 'response_time', 'started_at', 'completed_at')
    list_filter = ('test_type', 'status', 'started_at')
    search_fields = ('target_system__name', 'target_system__ip_address', 'bulk_scan__scan_id')
    readonly_fields = ('started_at', 'completed_at', 'response_time', 'test_output')
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Test Information', {
            'fields': ('target_system', 'test_type', 'port', 'status')
        }),
        ('Results', {
            'fields': ('response_time', 'error_message', 'test_output')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('target_system')


@admin.register(CredentialTest)
class CredentialTestAdmin(admin.ModelAdmin):
    list_display = ('target_system', 'username', 'auth_method', 'status', 'started_at', 'completed_at')
    list_filter = ('auth_method', 'status', 'started_at')
    search_fields = ('target_system__name', 'target_system__ip_address', 'username')
    readonly_fields = ('started_at', 'completed_at', 'test_output')
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Test Information', {
            'fields': ('target_system', 'username', 'auth_method', 'status')
        }),
        ('Results', {
            'fields': ('error_message', 'test_output')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('target_system')


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'total_systems', 'created_at', 'completed_at', 'is_completed')
    list_filter = ('created_at', 'completed_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'completed_at', 'total_tests', 'successful_tests')
    filter_horizontal = ('target_systems',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Target Systems', {
            'fields': ('target_systems',)
        }),
        ('Statistics', {
            'fields': ('total_tests', 'successful_tests'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_systems(self, obj):
        return obj.target_systems.count()
    total_systems.short_description = 'Total Systems'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('target_systems')


# Customize the admin site header and title
admin.site.site_header = 'VA Assistant Administration'
admin.site.site_title = 'VA Assistant Admin'
admin.site.index_title = 'Welcome to VA Assistant Administration' 