"""
Marketplace utility functions for CircuTrade AI
Includes pricing calculations, CO2 impact, and buyer matching algorithms
"""

from decimal import Decimal
from django.db.models import Q


def calculate_fair_price(material, weight, grade='B', location_distance=None):
    """
    Calculate fair price for waste materials based on multiple factors
    
    Args:
        material: Material instance
        weight: Weight in kilograms (float)
        grade: Quality grade ('A', 'B', or 'C')
        location_distance: Optional distance in km for transport cost adjustment
    
    Returns:
        dict with price breakdown
    """
    # Get base price per kg for the grade
    base_price_per_kg = material.get_price_for_grade(grade)
    
    # Calculate base total
    base_total = Decimal(str(base_price_per_kg)) * Decimal(str(weight))
    
    # Volume discount (for larger quantities)
    volume_discount = 0
    if weight >= 1000:  # 1 ton or more
        volume_discount = 0.10  # 10% discount
    elif weight >= 500:
        volume_discount = 0.05  # 5% discount
    
    # Location adjustment (if provided)
    location_adjustment = 0
    if location_distance:
        if location_distance > 100:
            location_adjustment = -0.05  # -5% for very far locations
        elif location_distance > 50:
            location_adjustment = -0.02  # -2% for moderate distance
    
    # Calculate final price
    total_discount = volume_discount + location_adjustment
    final_price = base_total * (Decimal('1.0') + Decimal(str(total_discount)))
    
    return {
        'base_price_per_kg': float(base_price_per_kg),
        'weight': float(weight),
        'base_total': float(base_total),
        'volume_discount_percent': volume_discount * 100,
        'location_adjustment_percent': location_adjustment * 100,
        'final_price': float(final_price),
        'savings': float(base_total - final_price) if final_price < base_total else 0,
        'currency': '₹'
    }


def calculate_co2_savings(material, weight):
    """
    Calculate CO2 emissions saved by recycling
    
    Args:
        material: Material instance
        weight: Weight in kilograms (float)
    
    Returns:
        dict with CO2 impact details
    """
    co2_saved_kg = material.co2_saved_per_kg * weight
    
    # Convert to meaningful comparisons
    trees_equivalent = co2_saved_kg / 21  # Average tree absorbs ~21kg CO2/year
    car_km_equivalent = co2_saved_kg / 0.12  # Average car emits ~0.12kg CO2/km
    
    return {
        'co2_saved_kg': round(co2_saved_kg, 2),
        'trees_equivalent': round(trees_equivalent, 1),
        'car_km_equivalent': round(car_km_equivalent, 0),
        'material_name': material.name,
        'weight': weight
    }


def match_buyers_to_listing(listing, limit=10):
    """
    Smart matching algorithm to find suitable buyers for a listing
    
    Matching criteria:
    1. Buyer role
    2. Same or nearby location (city/state)
    3. High karma score (if generator)
    4. Active users
    
    Args:
        listing: WasteListing instance
        limit: Maximum number of matches to return
    
    Returns:
        QuerySet of matched buyers with scoring
    """
    from accounts.models import CustomUser
    
    # Base query: Active buyers only
    buyers = CustomUser.objects.filter(
        role='BUYER',
        is_active=True
    )
    
    # Priority 1: Same city (highest priority)
    same_city_buyers = buyers.filter(city__iexact=listing.city)
    
    # Priority 2: Same state but different city
    same_state_buyers = buyers.filter(
        state__iexact=listing.state
    ).exclude(city__iexact=listing.city)
    
    # Priority 3: Other active buyers
    other_buyers = buyers.exclude(
        Q(city__iexact=listing.city) | Q(state__iexact=listing.state)
    )
    
    # Combine with priority (UNION in order)
    matched_buyers = list(same_city_buyers[:limit])
    
    if len(matched_buyers) < limit:
        remaining = limit - len(matched_buyers)
        matched_buyers.extend(list(same_state_buyers[:remaining]))
    
    if len(matched_buyers) < limit:
        remaining = limit - len(matched_buyers)
        matched_buyers.extend(list(other_buyers[:remaining]))
    
    return matched_buyers[:limit]


def get_listing_score(listing):
    """
    Calculate quality score for a listing (0-100)
    
    Factors:
    - Trust score (40%)
    - Seller karma (30%)
    - Completeness (images, description) (20%)
    - Verification status (10%)
    
    Args:
        listing: WasteListing instance
    
    Returns:
        int score (0-100)
    """
    score = 0
    
    # Trust score contribution (40%)
    score += (listing.trust_score * 0.4)
    
    # Seller karma contribution (30%)
    karma_normalized = (listing.seller.karma_score / 1000) * 100
    score += (karma_normalized * 0.3)
    
    # Completeness contribution (20%)
    completeness = 0
    if listing.image1:
        completeness += 5
    if listing.image2:
        completeness += 3
    if listing.image3:
        completeness += 2
    if listing.description and len(listing.description) > 50:
        completeness += 5
    if listing.video:
        completeness += 5
    # completeness is out of 20, normalize to percentage
    completeness_percent = (completeness / 20) * 100
    score += (completeness_percent * 0.2)
    
    # Verification bonus (10%)
    if listing.is_verified:
        score += 10
    
    return min(100, int(score))


def estimate_pickup_cost(listing, buyer_location):
    """
    Estimate logistics/pickup cost based on distance and weight
    
    Args:
        listing: WasteListing instance
        buyer_location: dict with 'city', 'state', 'pincode'
    
    Returns:
        dict with cost estimate
    """
    # Mock distance calculation (in real app, use Google Maps API)
    # For now, use simple heuristic
    same_city = listing.city.lower() == buyer_location.get('city', '').lower()
    same_state = listing.state.lower() == buyer_location.get('state', '').lower()
    
    if same_city:
        distance_km = 20  # Assume 20km within city
        cost_per_km = 5
    elif same_state:
        distance_km = 150  # Assume 150km within state
        cost_per_km = 4
    else:
        distance_km = 500  # Assume 500km inter-state
        cost_per_km = 3.5
    
    # Weight factor (heavier = more cost per km)
    weight_multiplier = 1.0
    if listing.weight > 1000:
        weight_multiplier = 1.5
    elif listing.weight > 500:
        weight_multiplier = 1.2
    
    base_cost = distance_km * cost_per_km * weight_multiplier
    
    # Add handling fee
    handling_fee = listing.weight * 0.5  # ₹0.5 per kg
    
    total_cost = base_cost + handling_fee
    
    return {
        'distance_km': distance_km,
        'cost_per_km': cost_per_km,
        'weight_multiplier': weight_multiplier,
        'base_transport_cost': round(base_cost, 2),
        'handling_fee': round(handling_fee, 2),
        'total_estimated_cost': round(total_cost, 2),
        'currency': '₹'
    }


def get_material_statistics():
    """
    Get aggregated statistics for all materials and listings
    
    Returns:
        dict with marketplace statistics
    """
    from marketplace.models import Material, WasteListing
    from django.db.models import Sum, Count, Avg
    
    stats = {
        'total_materials': Material.objects.filter(is_active=True).count(),
        'total_listings': WasteListing.objects.filter(status='LISTED').count(),
        'total_verified_listings': WasteListing.objects.filter(
            status='LISTED', 
            is_verified=True
        ).count(),
        'total_weight_available': WasteListing.objects.filter(
            status='LISTED'
        ).aggregate(total=Sum('weight'))['total'] or 0,
        'total_co2_potential': WasteListing.objects.filter(
            status='LISTED'
        ).aggregate(total=Sum('co2_saved'))['total'] or 0,
        'average_trust_score': WasteListing.objects.filter(
            status='LISTED'
        ).aggregate(avg=Avg('trust_score'))['avg'] or 0,
    }
    
    # Round values
    stats['total_weight_available'] = round(stats['total_weight_available'], 2)
    stats['total_co2_potential'] = round(stats['total_co2_potential'], 2)
    stats['average_trust_score'] = round(stats['average_trust_score'], 1)
    
    return stats
