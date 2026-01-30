from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    """
    Custom User Model for CircuTrade AI
    Extends Django's AbstractUser to add role-based functionality
    """
    
    ROLE_CHOICES = [
        ('GENERATOR', 'Waste Generator'),
        ('BUYER', 'Buyer/Manufacturer'),
        ('WORKER', 'Informal Worker'),
    ]
    
    # Core Fields
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='GENERATOR',
        help_text="User role in the circular economy ecosystem"
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Contact number for workers and notifications"
    )
    
    # Location Fields for Smart Matching
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Karma/Reputation System (for Generators)
    karma_score = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        help_text="Reputation score (0-1000). Higher score = better visibility"
    )
    
    # Profile Metadata
    company_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Company or organization name"
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Short description about the user/company"
    )
    
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    
    # Verification Status
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user has been verified by admin"
    )
    
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time of verification"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['karma_score']),
            models.Index(fields=['city', 'state']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.get_full_name()} ({self.company_name}) - {self.get_role_display()}"
        return f"{self.get_full_name()} - {self.get_role_display()}"
    
    def get_full_name(self):
        """Return full name or username if name not set"""
        full_name = super().get_full_name()
        return full_name if full_name else self.username
    
    def get_location(self):
        """Return formatted location string"""
        parts = [self.city, self.state, self.pincode]
        return ', '.join(filter(None, parts)) or 'Location not set'
    
    def can_list_waste(self):
        """Check if user can create waste listings"""
        return self.role == 'GENERATOR'
    
    def can_purchase(self):
        """Check if user can purchase waste"""
        return self.role == 'BUYER'
    
    def update_karma(self, points, reason=""):
        """
        Update karma score with validation
        :param points: Points to add (positive) or subtract (negative)
        :param reason: Optional reason for karma change
        """
        new_score = self.karma_score + points
        self.karma_score = max(0, min(1000, new_score))  # Clamp between 0-1000
        self.save()
        
        # Log karma change (could be expanded to a separate KarmaLog model)
        print(f"Karma updated for {self.username}: {points:+d} points. Reason: {reason}")
        
        return self.karma_score
    
    @property
    def karma_level(self):
        """Return karma level badge"""
        if self.karma_score >= 800:
            return "Platinum"
        elif self.karma_score >= 600:
            return "Gold"
        elif self.karma_score >= 400:
            return "Silver"
        elif self.karma_score >= 200:
            return "Bronze"
        else:
            return "Starter"
    
    @property
    def total_listings(self):
        """Get total waste listings created by this generator"""
        if self.role == 'GENERATOR':
            return self.waste_listings.count()
        return 0
    
    @property
    def total_purchases(self):
        """Get total purchases made by this buyer"""
        # TODO: Implement in Phase 5 with Transaction model
        # if self.role == 'BUYER':
        #     return self.buyer_transactions.count()
        return 0
    
    @property
    def total_sales(self):
        """Get total sales made by this generator"""
        # TODO: Implement in Phase 5 with Transaction model
        # if self.role == 'GENERATOR':
        #     return self.seller_transactions.filter(payment_status='COMPLETED').count()
        return 0
