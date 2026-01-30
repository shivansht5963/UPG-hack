from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'listing_title',
        'buyer_name',
        'seller_name',
        'offer_amount',
        'status',
        'payment_status',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'payment_status',
        'created_at',
    ]
    
    search_fields = [
        'listing__title',
        'buyer__username',
        'seller__username',
        'transaction_hash',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'accepted_at',
        'paid_at',
        'completed_at',
        'transaction_hash',
    ]
    
    fieldsets = (
        ('Transaction Info', {
            'fields': (
                'listing',
                'buyer',
                'seller',
                'offer_amount',
            )
        }),
        ('Delivery Details', {
            'fields': (
                'delivery_address',
                'contact_number',
                'notes',
            )
        }),
        ('Status', {
            'fields': (
                'status',
                'payment_status',
                'seller_notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'accepted_at',
                'paid_at',
                'completed_at',
            ),
            'classes': ('collapse',),
        }),
        ('Payment', {
            'fields': (
                'transaction_hash',
            )
        }),
    )
    
    def listing_title(self, obj):
        return obj.listing.title[:50]
    listing_title.short_description = 'Listing'
    
    def buyer_name(self, obj):
        return obj.buyer.get_full_name()
    buyer_name.short_description = 'Buyer'
    
    def seller_name(self, obj):
        return obj.seller.get_full_name()
    seller_name.short_description = 'Seller'
