from django.contrib import admin
from .models import ProvenanceBlock


@admin.register(ProvenanceBlock)
class ProvenanceBlockAdmin(admin.ModelAdmin):
    """
    Read-only admin for provenance blocks
    Admins can VIEW but NOT EDIT blocks (immutability)
    """
    
    list_display = [
        'block_number',
        'listing_title',
        'action',
        'actor_name',
        'actor_role',
        'timestamp',
        'hash_preview',
        'is_valid_icon',
    ]
    
    list_filter = [
        'action',
        'actor_role',
        'status',
        'is_valid',
        'timestamp',
    ]
    
    search_fields = [
        'listing__title',
        'actor_name',
        'current_hash',
        'notes',
    ]
    
    readonly_fields = [
        'listing',
        'block_number',
        'previous_hash',
        'current_hash',
        'action',
        'actor',
        'actor_name',
        'actor_role',
        'status',
        'timestamp',
        'metadata',
        'notes',
        'is_valid',
        'hash_validation',
        'previous_block_link',
        'next_block_link',
    ]
    
    fieldsets = (
        ('Block Information', {
            'fields': (
                'listing',
                'block_number',
                'action',
                'timestamp',
                'status',
            )
        }),
        ('Actor Details', {
            'fields': (
                'actor',
                'actor_name',
                'actor_role',
            )
        }),
        ('Blockchain Hashes', {
            'fields': (
                'previous_hash',
                'current_hash',
                'hash_validation',
            ),
            'classes': ('collapse',),
        }),
        ('Chain Navigation', {
            'fields': (
                'previous_block_link',
                'next_block_link',
            )
        }),
        ('Additional Data', {
            'fields': (
                'metadata',
                'notes',
            ),
            'classes': ('collapse',),
        }),
    )
    
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Prevent manual creation of blocks"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of blocks"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of blocks"""
        return False
    
    def listing_title(self, obj):
        """Display listing title"""
        return obj.listing.title[:50]
    listing_title.short_description = 'Listing'
    
    def hash_preview(self, obj):
        """Display first 12 chars of current hash"""
        return f"{obj.current_hash[:12]}..."
    hash_preview.short_description = 'Hash Preview'
    
    def is_valid_icon(self, obj):
        """Visual indicator of validation status"""
        if obj.is_valid:
            return '✅ Valid'
        return '❌ Invalid'
    is_valid_icon.short_description = 'Status'
    
    def hash_validation(self, obj):
        """Real-time hash validation"""
        calculated = obj.calculate_hash()
        stored = obj.current_hash
        
        if calculated == stored:
            return f'✅ VALID - Hash matches\n\nCalculated: {calculated}\nStored: {stored}'
        else:
            return f'❌ TAMPERED - Hash mismatch!\n\nCalculated: {calculated}\nStored: {stored}'
    hash_validation.short_description = 'Hash Validation'
    
    def previous_block_link(self, obj):
        """Link to previous block"""
        prev = obj.get_previous_block()
        if prev:
            from django.utils.html import format_html
            from django.urls import reverse
            url = reverse('admin:provenance_provenanceblock_change', args=[prev.id])
            return format_html('<a href="{}">← Block #{}</a>', url, prev.block_number)
        return 'Genesis Block (No Previous)'
    previous_block_link.short_description = 'Previous Block'
    
    def next_block_link(self, obj):
        """Link to next block"""
        next_block = obj.get_next_block()
        if next_block:
            from django.utils.html import format_html
            from django.urls import reverse
            url = reverse('admin:provenance_provenanceblock_change', args=[next_block.id])
            return format_html('<a href="{}">Block #{} →</a>', url, next_block.block_number)
        return 'Latest Block (No Next)'
    next_block_link.short_description = 'Next Block'
