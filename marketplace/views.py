from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
import random
import hashlib
from .models import Material, WasteListing
from .forms import WasteListingForm, MarketplaceFilterForm, VerificationForm


@require_http_methods(["GET"])
def marketplace_feed(request):
    """
    Public marketplace feed with filtering
    """
    # Get all listed and verified waste listings
    listings = WasteListing.objects.filter(
        status='LISTED'
    ).select_related('material', 'seller')
    
    # Apply filters
    filter_form = MarketplaceFilterForm(request.GET)
    
    if filter_form.is_valid():
        # Material filter
        material = filter_form.cleaned_data.get('material')
        if material:
            listings = listings.filter(material=material)
        
        # Grade filter
        grade = filter_form.cleaned_data.get('grade')
        if grade:
            listings = listings.filter(grade=grade)
        
        # Weight range
        min_weight = filter_form.cleaned_data.get('min_weight')
        if min_weight:
            listings = listings.filter(weight__gte=min_weight)
        
        max_weight = filter_form.cleaned_data.get('max_weight')
        if max_weight:
            listings = listings.filter(weight__lte=max_weight)
        
        # Location filters
        city = filter_form.cleaned_data.get('city')
        if city:
            listings = listings.filter(city__icontains=city)
        
        state = filter_form.cleaned_data.get('state')
        if state:
            listings = listings.filter(state__icontains=state)
        
        # Verified only
        verified_only = filter_form.cleaned_data.get('verified_only')
        if verified_only:
            listings = listings.filter(is_verified=True)
        
        # Sorting
        sort_by = filter_form.cleaned_data.get('sort_by')
        if sort_by:
            listings = listings.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(listings, 12)  # 12 listings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'listings': page_obj,
        'filter_form': filter_form,
        'total_count': paginator.count,
        'page_title': 'Marketplace - CircuTrade AI',
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    
    return render(request, 'marketplace/feed.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_listing(request):
    """
    Create new waste listing (Generators only)
    """
    from .gemini_grading import apply_gemini_grading
    
    # Check if user is a generator
    if request.user.role != 'GENERATOR':
        messages.error(request, 'Only waste generators can create listings.')
        return redirect('marketplace_feed')
    
    if request.method == 'POST':
        form = WasteListingForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            
            # Calculate base price
            listing.base_price = listing.calculated_price
            
            # Save listing first to get file paths
            listing.save()
            
            # Apply Gemini AI grading (analyzes all 5 images)
            if any([listing.image1, listing.image2, listing.image3, listing.image4, listing.image5]):
                try:
                    grading_result = apply_gemini_grading(listing)
                    messages.success(
                        request,
                        f'🤖 Gemini AI Grading Complete! '
                        f'Material: {grading_result["material"]} | '
                        f'Grade: {grading_result["grade"]} | '
                        f'Confidence: {int(grading_result["confidence"]*100)}%'
                    )
                except Exception as e:
                    messages.warning(request, f'AI grading failed, using defaults: {str(e)}')
                    # Fallback to mock verification
                    if listing.image1:
                        verification_result = mock_opencv_verification(listing.image1, listing.material)
                        listing.trust_score = verification_result['trust_score']
                        listing.grade = verification_result['suggested_grade']
                        listing.verification_notes = verification_result['notes']
                        listing.save()
            else:
                messages.warning(request, 'No images uploaded. Using default grade.')
            
            # Update seller karma
            # Award karma for creating listing
            request.user.update_karma(5, "Created new waste listing")
            
            # Bonus karma based on grade quality
            if listing.grade == 'A':
                request.user.update_karma(10, "High quality Grade A waste")
            elif listing.grade == 'B':
                request.user.update_karma(5, "Good quality Grade B waste")

            
            return redirect('generator_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteListingForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': 'Create Waste Listing',
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'marketplace/create_listing.html', context)


@require_http_methods(["GET"])
def listing_detail(request, listing_id):
    """
    View detailed information about a listing
    """
    listing = get_object_or_404(
        WasteListing.objects.select_related('material', 'seller'),
        pk=listing_id
    )
    
    # Get similar listings
    similar_listings = WasteListing.objects.filter(
        material=listing.material,
        status='LISTED',
        is_verified=True
    ).exclude(pk=listing.pk).select_related('material', 'seller')[:4]
    
    context = {
        'listing': listing,
        'similar_listings': similar_listings,
        'page_title': f'{listing.title} - CircuTrade AI',
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'marketplace/listing_detail.html', context)


@login_required
@require_http_methods(["POST"])
def delete_listing(request, listing_id):
    """
    Delete a listing (only by owner)
    """
    listing = get_object_or_404(WasteListing, pk=listing_id, seller=request.user)
    
    if listing.status != 'LISTED':
        messages.error(request, 'Cannot delete listing that is already in progress.')
        return redirect('generator_dashboard')
    
    listing.status = 'CANCELLED'
    listing.save()
    
    messages.success(request, 'Listing cancelled successfully.')
    return redirect('generator_dashboard')


# ==================== 
# API Endpoints
# ====================

@require_http_methods(["POST"])
def calculate_price_api(request):
    """
    AJAX API endpoint for real-time price calculation
    """
    import json
    
    try:
        data = json.loads(request.body)
        material_id = data.get('material_id')
        grade = data.get('grade')
        weight = float(data.get('weight', 0))
        
        if not all([material_id, grade, weight]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        material = Material.objects.get(pk=material_id)
        price_per_kg = material.get_price_for_grade(grade)
        total_price = price_per_kg * weight
        co2_saved = material.co2_saved_per_kg * weight
        
        return JsonResponse({
            'price': total_price,
            'price_per_kg': price_per_kg,
            'co2_saved': co2_saved,
            'material_name': material.name
        })
    
    except Material.DoesNotExist:
        return JsonResponse({'error': 'Material not found'}, status=404)
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid data format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def mock_opencv_verification_api(request):
    """
    Mock OpenCV verification API endpoint
    
    In production, this would:
    1. Accept image upload
    2. Run OpenCV detection
    3. Use ML model to verify material type and quality
    4. Return trust score and suggested grade
    
    For MVP, we return randomized but realistic scores
    """
    import json
    from django.core.files.storage import default_storage
    
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image = request.FILES['image']
        material_id = request.POST.get('material_id')
        
        if not material_id:
            return JsonResponse({'error': 'Material ID required'}, status=400)
        
        material = Material.objects.get(pk=material_id)
        
        # Mock verification (in production, this would be actual OpenCV/ML)
        result = mock_opencv_verification(image, material)
        
        return JsonResponse({
            'success': True,
            'trust_score': result['trust_score'],
            'suggested_grade': result['suggested_grade'],
            'notes': result['notes'],
            'is_verified': result['trust_score'] >= 50,
            'message': f"Verification complete. Trust score: {result['trust_score']}%"
        })
    
    except Material.DoesNotExist:
        return JsonResponse({'error': 'Material not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== 
# Utility Functions
# ====================

def mock_opencv_verification(image, material):
    """
    Mock OpenCV verification logic
    
    In production, this would:
    - Use OpenCV for image analysis
    - Detect material characteristics
    - Use ML model for quality assessment
    - Return real trust score
    
    For MVP, we generate deterministic but realistic scores based on image hash
    """
    try:
        # Read image data
        image_data = image.read()
        image.seek(0)  # Reset file pointer
        
        # Generate deterministic hash from image
        image_hash = hashlib.md5(image_data).hexdigest()
        
        # Use hash to generate "realistic" but deterministic scores
        hash_int = int(image_hash[:8], 16)
        base_score = (hash_int % 40) + 50  # Score between 50-90
        
        # Add material-specific bonus
        material_bonus = (hash_int % 15) - 5  # -5 to +10
        trust_score = max(30, min(100, base_score + material_bonus))
        
        # Determine grade based on trust score
        if trust_score >= 80:
            suggested_grade = 'A'
        elif trust_score >= 60:
            suggested_grade = 'B'
        else:
            suggested_grade = 'C'
        
        # Generate notes
        notes_templates = [
            "Image quality: Good. Material appears to match {material}.",
            "Detected consistent material texture. Recommended as {material}.",
            "Visual inspection passed. Grade {grade} quality detected.",
            "Material composition verified. Minor contaminants detected.",
            "High confidence match for {material}. Grade {grade} recommended."
        ]
        
        notes = random.choice(notes_templates).format(
            material=material.name,
            grade=suggested_grade
        )
        
        return {
            'trust_score': trust_score,
            'suggested_grade': suggested_grade,
            'notes': notes,
            'image_hash': image_hash[:16]
        }
    
    except Exception as e:
        # Fallback in case of error
        return {
            'trust_score': 50,
            'suggested_grade': 'B',
            'notes': f'Automated verification unavailable. Manual review recommended. ({str(e)})',
            'image_hash': 'error'
        }
