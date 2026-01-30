from django.db.models.signals import post_save
from django.dispatch import receiver
from marketplace.models import WasteListing
from .models import ProvenanceBlock


@receiver(post_save, sender=WasteListing)
def create_provenance_blocks(sender, instance, created, **kwargs):
    """
    Automatically create provenance blocks when listing is created or updated
    """
    if created:
        # Create genesis block for new listing
        ProvenanceBlock.create_genesis_block(
            listing=instance,
            actor=instance.seller
        )
        
        # If listing is already verified, add verification block
        if instance.is_verified:
            ProvenanceBlock.add_block(
                listing=instance,
                action='VERIFIED',
                actor=None,  # System action
                metadata={
                    'trust_score': instance.trust_score,
                    'grade': instance.grade,
                    'verified_at': instance.updated_at.isoformat() if instance.updated_at else None
                },
                notes='AI quality verification completed'
            )
        
        # If listing is already in LISTED status, add listed block
        if instance.status == 'LISTED':
            ProvenanceBlock.add_block(
                listing=instance,
                action='LISTED',
                actor=instance.seller,
                metadata={
                    'price': float(instance.calculated_price),
                    'weight': float(instance.weight),
                },
                notes='Listing made available on marketplace'
            )
    else:
        # Handle status changes for existing listings
        
        # Check if status changed to SOLD
        if instance.status == 'SOLD':
            # Check if we already have a PURCHASED block
            existing_purchase = ProvenanceBlock.objects.filter(
                listing=instance,
                action='PURCHASED'
            ).exists()
            
            if not existing_purchase:
                ProvenanceBlock.add_block(
                    listing=instance,
                    action='PURCHASED',
                    actor=None,  # Buyer info will be in Phase 5
                    metadata={
                        'price': float(instance.calculated_price),
                        'sold_at': instance.updated_at.isoformat() if instance.updated_at else None
                    },
                    notes='Material purchased by buyer'
                )
        
        # Check if verification status changed
        if instance.is_verified:
            existing_verification = ProvenanceBlock.objects.filter(
                listing=instance,
                action='VERIFIED'
            ).exists()
            
            if not existing_verification:
                ProvenanceBlock.add_block(
                    listing=instance,
                    action='VERIFIED',
                    actor=None,
                    metadata={
                        'trust_score': instance.trust_score,
                        'grade': instance.grade,
                    },
                    notes='AI quality verification completed'
                )
