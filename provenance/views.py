from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from marketplace.models import WasteListing
from .models import ProvenanceBlock
from io import BytesIO
from datetime import datetime


@login_required
def provenance_detail(request, listing_id):
    """
    Display provenance timeline for a listing
    Shows visual blockchain timeline with all blocks
    """
    listing = get_object_or_404(WasteListing, id=listing_id)
    
    # Get all blocks for this listing
    blocks = ProvenanceBlock.objects.filter(
        listing=listing
    ).order_by('block_number')
    
    # Validate entire chain
    chain_valid, broken_at = ProvenanceBlock.validate_entire_chain(listing)
    
    # Get statistics
    stats = {
        'total_blocks': blocks.count(),
        'genesis_date': blocks.first().timestamp if blocks.exists() else None,
        'latest_action': blocks.last().action if blocks.exists() else None,
        'latest_date': blocks.last().timestamp if blocks.exists() else None,
        'chain_valid': chain_valid,
        'broken_at_block': broken_at,
    }
    
    context = {
        'listing': listing,
        'blocks': blocks,
        'stats': stats,
        'page_title': f'Provenance - {listing.title}'
    }
    
    return render(request, 'provenance/detail.html', context)


@login_required
def download_certificate(request, listing_id):
    """
    Generate and download PDF certificate of provenance
    """
    listing = get_object_or_404(WasteListing, id=listing_id)
    
    # Get all blocks
    blocks = ProvenanceBlock.objects.filter(
        listing=listing
    ).order_by('block_number')
    
    # Validate chain
    chain_valid, broken_at = ProvenanceBlock.validate_entire_chain(listing)
    
    # For now, render HTML certificate (PDF generation requires ReportLab)
    # We'll use a print-friendly HTML that can be printed to PDF via browser
    context = {
        'listing': listing,
        'blocks': blocks,
        'chain_valid': chain_valid,
        'broken_at_block': broken_at,
        'generated_date': datetime.now(),
        'total_blocks': blocks.count(),
        'genesis_hash': blocks.first().current_hash if blocks.exists() else None,
        'latest_hash': blocks.last().current_hash if blocks.exists() else None,
    }
    
    return render(request, 'provenance/certificate.html', context)


@login_required
def validate_chain_api(request, listing_id):
    """
    API endpoint to validate provenance chain
    Returns JSON with validation status
    """
    listing = get_object_or_404(WasteListing, id=listing_id)
    
    # Validate chain
    chain_valid, broken_at = ProvenanceBlock.validate_entire_chain(listing)
    
    blocks = ProvenanceBlock.objects.filter(listing=listing).order_by('block_number')
    
    return JsonResponse({
        'listing_id': listing_id,
        'listing_title': listing.title,
        'total_blocks': blocks.count(),
        'chain_valid': chain_valid,
        'broken_at_block': broken_at,
        'genesis_hash': blocks.first().current_hash if blocks.exists() else None,
        'latest_hash': blocks.last().current_hash if blocks.exists() else None,
        'message': 'Chain is valid ✓' if chain_valid else f'Chain broken at block #{broken_at}!'
    })
