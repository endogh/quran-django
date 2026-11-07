from django.contrib import admin

from .models import AccessLog, IPGeoCache


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'masked_ip', 'country_name', 'path')
    list_filter = ('country_code', 'created_at')
    search_fields = ('ip', 'path', 'country_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('ip', 'country_code', 'country_name', 'path', 'user_agent', 'created_at')

    def has_add_permission(self, request):
        return False

    @admin.display(description='IP')
    def masked_ip(self, obj):
        parts = obj.ip.split('.')
        if len(parts) == 4:
            return '.'.join(parts[:3] + ['xxx'])
        return obj.ip


@admin.register(IPGeoCache)
class IPGeoCacheAdmin(admin.ModelAdmin):
    list_display = ('ip', 'country_name', 'country_code', 'resolved_at')
    list_filter = ('country_code',)
    search_fields = ('ip', 'country_name')
    readonly_fields = ('ip', 'country_code', 'country_name', 'resolved_at')

    def has_add_permission(self, request):
        return False
