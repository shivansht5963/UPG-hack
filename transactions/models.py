from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from marketplace.models import WasteListing


class Transaction(models.Model):
    """
    Transaction/Offer model for purchase requests
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Seller Approval'),
        ('ACCEPTED', 'Accepted - Awaiting Payment'),
        ('CONFIRMED', 'Payment Confirmed'),
        ('REJECTED', 'Rejected by Seller'),
        ('CANCELLED', 'Cancelled by Buyer'),
        ('COMPLETED', 'Transaction Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Payment Pending'),
        ('PROCESSING', 'Processing Payment'),
        ('COMPLETED', 'Payment Completed'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Payment Refunded'),
    ]
    
    # Core fields
    listing = models.ForeignKey(
        WasteListing,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text='The listing being purchased'
    )
    buyer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='purchases',
        help_text='Buyer making the offer'
    )
    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sales',
        help_text='Seller receiving the offer'
    )
    
    # Offer details
    offer_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Buyer\'s offered price'
    )
    delivery_address = models.TextField(
        help_text='Delivery address provided by buyer'
    )
    contact_number = models.CharField(
        max_length=15,
        help_text='Buyer contact number'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes from buyer'
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    transaction_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text='Mock payment transaction hash'
    )
    seller_notes = models.TextField(
        blank=True,
        help_text='Notes from seller (reason for rejection, etc.)'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['listing', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Transaction #{self.id} - {self.listing.title[:30]} - {self.status}"
    
    def accept(self, seller_notes=''):
        """Accept the offer"""
        self.status = 'ACCEPTED'
        self.accepted_at = timezone.now()
        self.seller_notes = seller_notes
        self.save()
    
    def reject(self, seller_notes=''):
        """Reject the offer"""
        self.status = 'REJECTED'
        self.seller_notes = seller_notes
        self.save()
    
    def confirm_payment(self):
        """Buyer confirms payment (mocked)"""
        import hashlib
        import random
        
        self.status = 'CONFIRMED'
        self.payment_status = 'COMPLETED'
        self.paid_at = timezone.now()
        
        # Generate mock transaction hash
        hash_data = f"{self.id}{self.buyer.id}{self.offer_amount}{timezone.now().isoformat()}{random.randint(1000, 9999)}"
        self.transaction_hash = hashlib.sha256(hash_data.encode()).hexdigest()
        
        self.save()
        
        # Update listing status to SOLD
        self.listing.status = 'SOLD'
        self.listing.save()
    
    def complete(self):
        """Mark transaction as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()
