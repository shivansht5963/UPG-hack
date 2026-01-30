import hashlib
from django.db import models
from django.utils import timezone
from marketplace.models import WasteListing
from accounts.models import CustomUser


class ProvenanceBlock(models.Model):
    """
    Blockchain-like immutable record of waste material journey
    Each block is cryptographically linked to previous block via SHA-256 hash
    """
    
    ACTION_CHOICES = [
        ('CREATED', 'Listing Created'),
        ('VERIFIED', 'AI Quality Verified'),
        ('LISTED', 'Listed on Marketplace'),
        ('PURCHASED', 'Purchased by Buyer'),
        ('COLLECTED', 'Collected by Worker'),
        ('DELIVERED', 'Delivered to Buyer'),
        ('RECYCLED', 'Recycled/Processed'),
        ('CANCELLED', 'Listing Cancelled'),
        ('UPDATED', 'Listing Updated'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('INVALIDATED', 'Invalidated'),
    ]
    
    # Core blockchain fields
    listing = models.ForeignKey(
        WasteListing,
        on_delete=models.CASCADE,
        related_name='provenance_blocks',
        help_text='The waste listing this block belongs to'
    )
    block_number = models.PositiveIntegerField(
        help_text='Sequential block number (0 = genesis block)'
    )
    previous_hash = models.CharField(
        max_length=64,
        default='0' * 64,
        help_text='SHA-256 hash of previous block (genesis = all zeros)'
    )
    current_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text='SHA-256 hash of this block (calculated on save)'
    )
    
    # Action details
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='What action occurred'
    )
    actor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='provenance_actions',
        help_text='Who performed this action'
    )
    actor_name = models.CharField(
        max_length=200,
        help_text='Name of actor (preserved even if user deleted)'
    )
    actor_role = models.CharField(
        max_length=20,
        blank=True,
        help_text='Role of actor at time of action'
    )
    
    # Block status and metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMED'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When this block was created (immutable)'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional contextual data (trust_score, price, etc.)'
    )
    notes = models.TextField(
        blank=True,
        help_text='Optional notes about this action'
    )
    
    # Validation
    is_valid = models.BooleanField(
        default=True,
        help_text='Whether this block passes hash validation'
    )
    
    class Meta:
        ordering = ['listing', 'block_number']
        unique_together = [['listing', 'block_number']]
        indexes = [
            models.Index(fields=['listing', 'block_number']),
            models.Index(fields=['current_hash']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = 'Provenance Block'
        verbose_name_plural = 'Provenance Blocks'
    
    def __str__(self):
        return f"Block #{self.block_number} - {self.listing.title[:30]} - {self.action}"
    
    def calculate_hash(self):
        """
        Calculate SHA-256 hash of this block's data
        Hash includes: previous_hash + block_number + action + actor + timestamp
        """
        # Use current time if timestamp not yet set (auto_now_add hasn't run)
        timestamp_str = self.timestamp.isoformat() if self.timestamp else timezone.now().isoformat()
        
        hash_data = (
            f"{self.previous_hash}"
            f"{self.listing.id}"
            f"{self.block_number}"
            f"{self.action}"
            f"{self.actor_name}"
            f"{timestamp_str}"
            f"{str(self.metadata)}"
        )
        
        return hashlib.sha256(hash_data.encode('utf-8')).hexdigest()
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate current_hash
        """
        # Calculate hash before saving
        if not self.current_hash or self.current_hash == '':
            self.current_hash = self.calculate_hash()
        
        super().save(*args, **kwargs)
    
    def validate_chain(self):
        """
        Validate this block's hash matches its calculated hash
        Returns True if block is valid, False if tampered
        """
        calculated = self.calculate_hash()
        return self.current_hash == calculated
    
    def get_next_block(self):
        """Get the next block in the chain"""
        return ProvenanceBlock.objects.filter(
            listing=self.listing,
            block_number=self.block_number + 1
        ).first()
    
    def get_previous_block(self):
        """Get the previous block in the chain"""
        if self.block_number == 0:
            return None
        return ProvenanceBlock.objects.filter(
            listing=self.listing,
            block_number=self.block_number - 1
        ).first()
    
    @staticmethod
    def create_genesis_block(listing, actor=None):
        """
        Create the first block (genesis) for a listing
        """
        actor_name = actor.get_full_name() if actor else 'System'
        actor_role = actor.role if actor else 'SYSTEM'
        
        genesis = ProvenanceBlock.objects.create(
            listing=listing,
            block_number=0,
            previous_hash='0' * 64,  # Genesis has no previous
            action='CREATED',
            actor=actor,
            actor_name=actor_name,
            actor_role=actor_role,
            status='CONFIRMED',
            metadata={
                'material': listing.material.name,
                'weight': float(listing.weight),
                'grade': listing.grade,
                'city': listing.city,
                'state': listing.state,
            }
        )
        
        return genesis
    
    @staticmethod
    def add_block(listing, action, actor=None, metadata=None, notes=''):
        """
        Add a new block to the chain
        """
        # Get the last block in the chain
        last_block = ProvenanceBlock.objects.filter(
            listing=listing
        ).order_by('-block_number').first()
        
        if not last_block:
            # No chain exists, create genesis first
            last_block = ProvenanceBlock.create_genesis_block(listing, actor)
        
        # Create new block
        actor_name = actor.get_full_name() if actor else 'System'
        actor_role = actor.role if actor and hasattr(actor, 'role') else 'SYSTEM'
        
        new_block = ProvenanceBlock.objects.create(
            listing=listing,
            block_number=last_block.block_number + 1,
            previous_hash=last_block.current_hash,
            action=action,
            actor=actor,
            actor_name=actor_name,
            actor_role=actor_role,
            status='CONFIRMED',
            metadata=metadata or {},
            notes=notes
        )
        
        return new_block
    
    @staticmethod
    def validate_entire_chain(listing):
        """
        Validate entire provenance chain for a listing
        Returns (is_valid, broken_at_block)
        """
        blocks = ProvenanceBlock.objects.filter(
            listing=listing
        ).order_by('block_number')
        
        for i, block in enumerate(blocks):
            # Validate hash
            if not block.validate_chain():
                return False, block.block_number
            
            # Validate linkage (except genesis)
            if i > 0:
                previous_block = blocks[i - 1]
                if block.previous_hash != previous_block.current_hash:
                    return False, block.block_number
        
        return True, None
