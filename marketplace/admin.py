from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Material, WasteListing


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Admin interface for Material model
    """
    
    list_display = [
        'name',
        'base_price_display',
        'grade_multipliers_display',
        'co2_saved_per_kg',
        'total_listings',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'icon', 'is_active')
        }),
        ('Pricing', {
            'fields': ('base_price_per_kg', 'grade_a_multiplier', 'grade_b_multiplier', 'grade_c_multiplier'),
            'description': 'Set base price and multipliers for each grade'
        }),
        ('Environmental Impact', {
            'fields': ('co2_saved_per_kg',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_materials', 'deactivate_materials']
    
    def base_price_display(self, obj):
        """Display formatted price"""
        return f"₹{obj.base_price_per_kg}/kg"
    base_price_display.short_description = "Base Price"
    
    def grade_multipliers_display(self, obj):
        """Display all grade multipliers"""
        return format_html(
            '<span class="badge" style="background-color: #10b981;">A: {}x</span> '
            '<span class="badge" style="background-color: #3b82f6;">B: {}x</span> '
            '<span class="badge" style="background-color: #f59e0b;">C: {}x</span>',
            obj.grade_a_multiplier,
            obj.grade_b_multiplier,
            obj.grade_c_multiplier
        )
    grade_multipliers_display.short_description = "Grade Multipliers"
    
    def total_listings(self, obj):
        """Count of active listings for this material"""
        count = obj.listings.filter(status='LISTED').count()
        return count
    total_listings.short_description = "Active Listings"
    
    def activate_materials(self, request, queryset):
        """Bulk activate materials"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} material(s) activated.')
    activate_materials.short_description = "Activate selected materials"
    
    def deactivate_materials(self, request, queryset):
        """Bulk deactivate materials"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} material(s) deactivated.')
    deactivate_materials.short_description = "Deactivate selected materials"


@admin.register(WasteListing)
class WasteListingAdmin(admin.ModelAdmin):
    """
    Admin interface for WasteListing model
    """
    
    list_display = [
        'title',
        'material',
        'seller_display',
        'weight',
        'grade_badge',
        'trust_score_display',
        'verification_badge',
        'price_display',
        'status_badge',
        'location_short',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'grade',
        'is_verified',
        'material',
        'created_at',
        'state'
    ]
    
    search_fields = [
        'title',
        'description',
        'seller__username',
        'seller__company_name',
        'city',
        'pincode'
    ]
    
    readonly_fields = [
        'co2_saved',
        'is_verified',
        'created_at',
        'updated_at',
        'calculated_price_display',
        'image_preview'
    ]
    
    autocomplete_fields = ['seller']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'material', 'seller')
        }),
        ('Quantity & Pricing', {
            'fields': ('weight', 'base_price', 'calculated_price_display')
        }),
        ('Quality & Verification', {
            'fields': ('grade', 'trust_score', 'is_verified', 'verification_notes'),
            'description': 'Verification details from OpenCV or manual review'
        }),
        ('Media', {
            'fields': ('image1', 'image2', 'image3', 'video', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Location', {
            'fields': ('city', 'state', 'pincode', 'address')
        }),
        ('Status & Sustainability', {
            'fields': ('status', 'co2_saved', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_listings', 'mark_as_sold', 'cancel_listings']
    
    def seller_display(self, obj):
        """Display seller with company name"""
        if obj.seller.company_name:
            return f"{obj.seller.get_full_name()} ({obj.seller.company_name})"
        return obj.seller.get_full_name()
    seller_display.short_description = "Seller"
    
    def grade_badge(self, obj):
        """Display grade as colored badge"""
        colors = {
            'A': '#10b981',
            'B': '#3b82f6',
            'C': '#f59e0b'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">Grade {}</span>',
            colors.get(obj.grade, '#6b7280'),
            obj.grade
        )
    grade_badge.short_description = "Grade"
    
    def trust_score_display(self, obj):
        """Display trust score with color coding"""
        if obj.trust_score >= 70:
            color = '#10b981'
        elif obj.trust_score >= 50:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            obj.trust_score
        )
    trust_score_display.short_description = "Trust Score"
    
    def verification_badge(self, obj):
        """Display verification status as badge"""
        if obj.is_verified:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 3px;">✓ Verified</span>'
            )
        return format_html(
            '<span style="background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 3px;">✗ Unverified</span>'
        )
    verification_badge.short_description = "Verification"
    
    def price_display(self, obj):
        """Display calculated price"""
        return f"₹{obj.calculated_price:,.2f}"
    price_display.short_description = "Calculated Price"
    
    def calculated_price_display(self, obj):
        """Readonly calculated price field"""
        return f"₹{obj.calculated_price:,.2f} (based on {obj.weight}kg × Grade {obj.grade} rate)"
    calculated_price_display.short_description = "Auto-Calculated Price"
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'LISTED': '#3b82f6',
            'MATCHED': '#8b5cf6',
            'SOLD': '#10b981',
            'SHIPPED': '#06b6d4',
            'COMPLETED': '#22c55e',
            'CANCELLED': '#ef4444'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def location_short(self, obj):
        """Display shortened location"""
        return f"{obj.city}, {obj.state}"
    location_short.short_description = "Location"
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.image1:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.image1.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def verify_listings(self, request, queryset):
        """Bulk verify listings"""
        count = queryset.update(is_verified=True, trust_score=100)
        self.message_user(request, f'{count} listing(s) verified.')
    verify_listings.short_description = "Verify selected listings"
    
    def mark_as_sold(self, request, queryset):
        """Bulk mark as sold"""
        count = queryset.update(status='SOLD')
        self.message_user(request, f'{count} listing(s) marked as sold.')
    mark_as_sold.short_description = "Mark as sold"
    
    def cancel_listings(self, request, queryset):
        """Bulk cancel listings"""
        count = queryset.update(status='CANCELLED')
        self.message_user(request, f'{count} listing(s) cancelled.')
    cancel_listings.short_description = "Cancel selected listings"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('material', 'seller')
