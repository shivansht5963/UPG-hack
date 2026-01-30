from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin with CircuTrade AI specific fields
    """
    
    # List display
    list_display = [
        'username',
        'email',
        'role',
        'karma_score',
        'city',
        'is_verified',
        'is_active',
        'created_at'
    ]
    
    # List filters
    list_filter = [
        'role',
        'is_verified',
        'is_active',
        'is_staff',
        'created_at',
        'state'
    ]
    
    # Search fields
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'company_name',
        'phone_number',
        'city'
    ]
    
    # Ordering
    ordering = ['-created_at']
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    # Fieldsets for detail view
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Role & Profile', {
            'fields': ('role', 'company_name', 'bio', 'profile_image')
        }),
        ('Location', {
            'fields': ('city', 'state', 'pincode')
        }),
        ('Karma & Verification', {
            'fields': ('karma_score', 'is_verified', 'verified_at'),
            'description': 'Reputation system and verification status'
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for add user
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
        ('Role & Info', {
            'classes': ('wide',),
            'fields': ('role', 'first_name', 'last_name', 'phone_number')
        }),
        ('Location', {
            'classes': ('wide',),
            'fields': ('city', 'state', 'pincode')
        }),
    )
    
    # Actions
    actions = ['verify_users', 'unverify_users', 'reset_karma']
    
    def verify_users(self, request, queryset):
        """Bulk verify users"""
        from django.utils import timezone
        count = queryset.update(is_verified=True, verified_at=timezone.now())
        self.message_user(request, f'{count} user(s) successfully verified.')
    verify_users.short_description = "Verify selected users"
    
    def unverify_users(self, request, queryset):
        """Bulk unverify users"""
        count = queryset.update(is_verified=False, verified_at=None)
        self.message_user(request, f'{count} user(s) unverified.')
    unverify_users.short_description = "Unverify selected users"
    
    def reset_karma(self, request, queryset):
        """Reset karma to default (100)"""
        count = queryset.update(karma_score=100)
        self.message_user(request, f'Karma reset to 100 for {count} user(s).')
    reset_karma.short_description = "Reset karma to 100"
    
    # Custom list display methods
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related()
    
    # Add custom CSS/JS if needed
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
