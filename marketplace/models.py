from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from accounts.models import CustomUser


class Material(models.Model):
    """
    Material types with base pricing and grade multipliers
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Material name (e.g., PET Plastic, Cotton Waste, E-Waste)"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of the material type"
    )
    
    # Pricing
    base_price_per_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price per kilogram in ₹"
    )
    
    # Grade Multipliers
    grade_a_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.5,
        validators=[MinValueValidator(0)],
        help_text="Price multiplier for Grade A (e.g., 1.5 = 150% of base)"
    )
    
    grade_b_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0)],
        help_text="Price multiplier for Grade B (e.g., 1.0 = 100% of base)"
    )
    
    grade_c_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.7,
        validators=[MinValueValidator(0)],
        help_text="Price multiplier for Grade C (e.g., 0.7 = 70% of base)"
    )
    
    # Environmental Impact
    co2_saved_per_kg = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        help_text="CO2 saved per kg when recycled (in kg CO2)"
    )
    
    # Metadata
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="bi-recycle",
        help_text="Bootstrap icon class (e.g., bi-recycle)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this material is currently accepting listings"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} (₹{self.base_price_per_kg}/kg)"
    
    def get_price_for_grade(self, grade):
        """Calculate price for a specific grade"""
        multipliers = {
            'A': self.grade_a_multiplier,
            'B': self.grade_b_multiplier,
            'C': self.grade_c_multiplier,
        }
        return float(self.base_price_per_kg) * float(multipliers.get(grade, 1.0))


class WasteListing(models.Model):
    """
    Waste listings created by generators
    """
    
    STATUS_CHOICES = [
        ('LISTED', 'Listed'),
        ('MATCHED', 'Matched with Buyer'),
        ('SOLD', 'Sold'),
        ('SHIPPED', 'Shipped'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    GRADE_CHOICES = [
        ('A', 'Grade A - Premium Quality'),
        ('B', 'Grade B - Standard Quality'),
        ('C', 'Grade C - Basic Quality'),
    ]
    
    # Core Fields
    title = models.CharField(
        max_length=200,
        help_text="Short title for the listing"
    )
    
    description = models.TextField(
        help_text="Detailed description of the waste material"
    )
    
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name='listings',
        help_text="Type of material"
    )
    
    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='waste_listings',
        limit_choices_to={'role': 'GENERATOR'},
        help_text="User who created this listing"
    )
    
    # Quantity and Pricing
    weight = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Weight in kilograms"
    )
    
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price for the entire lot in ₹"
    )
    
    # Quality Verification (From OpenCV or Manual)
    grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        default='B',
        help_text="Quality grade"
    )
    
    trust_score = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Verification trust score (0-100) from OpenCV"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether listing has been verified (trust >= 50%)"
    )
    
    verification_notes = models.TextField(
        blank=True,
        help_text="Notes from verification process"
    )
    
    # Images/Videos
    image1 = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Primary image"
    )
    
    image2 = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Additional image"
    )
    
    image3 = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Additional image"
    )
    
    image4 = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Additional image (for Gemini grading)"
    )
    
    image5 = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Additional image (for Gemini grading)"
    )
    
    # Gemini AI Grading Result
    gemini_grading_result = models.JSONField(
        blank=True,
        null=True,
        help_text="Gemini AI quality grading response"
    )
    
    video = models.FileField(
        upload_to='listings/videos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov'])],
        help_text="Video demonstration (optional)"
    )
    
    # Location (for smart matching)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address = models.TextField(
        blank=True,
        help_text="Detailed pickup address"
    )
    
    # Geolocation coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Latitude coordinate from geolocation"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Longitude coordinate from geolocation"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='LISTED',
        help_text="Current listing status"
    )
    
    # Sustainability Metrics
    co2_saved = models.FloatField(
        default=0.0,
        help_text="Total CO2 that will be saved if recycled (kg)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this listing expires"
    )
    
    class Meta:
        verbose_name = "Waste Listing"
        verbose_name_plural = "Waste Listings"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_verified']),
            models.Index(fields=['material', 'grade']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['seller']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.material.name} ({self.weight}kg, Grade {self.grade})"
    
    def save(self, *args, **kwargs):
        """Auto-calculate CO2 saved and verify status"""
        # Calculate CO2 saved using formula: Weight × CO2 Saving Factor
        # Example: 10kg plastic × 1.5 kg CO2/kg = 15kg CO2 saved
        self.co2_saved = self.weight * self.material.co2_saved_per_kg
        
        # Log CO2 calculation for debugging
        print(f"💚 CO2 Calculation: {self.weight}kg × {self.material.co2_saved_per_kg} kg CO2/kg = {self.co2_saved} kg CO2 saved")
        
        # Auto-verify if trust score >= 50
        self.is_verified = self.trust_score >= 50
        
        # Set default location from seller if not provided
        if not self.city and self.seller:
            self.city = self.seller.city or ''
            self.state = self.seller.state or ''
            self.pincode = self.seller.pincode or ''
        
        super().save(*args, **kwargs)
    
    @property
    def calculated_price(self):
        """Get calculated price based on grade and weight"""
        price_per_kg = self.material.get_price_for_grade(self.grade)
        return price_per_kg * self.weight
    
    @property
    def is_active(self):
        """Check if listing is still active"""
        return self.status == 'LISTED' and (
            self.expires_at is None or self.expires_at > timezone.now()
        )
    
    @property
    def images(self):
        """Get all uploaded images"""
        return [img for img in [self.image1, self.image2, self.image3, self.image4, self.image5] if img]
    
    @property
    def location_display(self):
        """Return formatted location"""
        parts = [self.city, self.state, self.pincode]
        return ', '.join(filter(None, parts))
    
    def get_matched_buyers(self, limit=5):
        """Get potential buyers based on location and preferences"""
        from django.db.models import Q
        
        buyers = CustomUser.objects.filter(
            role='BUYER',
            is_active=True
        ).filter(
            Q(city=self.city) | Q(state=self.state)
        )[:limit]
        
        return buyers
