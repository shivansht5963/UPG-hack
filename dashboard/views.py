from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from marketplace.models import WasteListing, Material
from marketplace.utils import get_material_statistics
from accounts.models import CustomUser


def landing_page(request):
    """
    Public landing page with impact stats and CTA
    """
    # Redirect authenticated users to their dashboard
    if request.user.is_authenticated:
        if request.user.role == 'GENERATOR':
            return redirect('generator_dashboard')
        elif request.user.role == 'BUYER':
            return redirect('buyer_dashboard')
        elif request.user.role == 'WORKER':
            return redirect('worker_dashboard')
    
    # Get marketplace statistics
    stats = get_material_statistics()
    
    # Get featured listings (top 6 verified listings)
    featured_listings = WasteListing.objects.filter(
        status='LISTED',
        is_verified=True
    ).select_related('material', 'seller').order_by('-trust_score', '-created_at')[:6]
    
    context = {
        'stats': stats,
        'featured_listings': featured_listings,
        'page_title': 'CircuTrade AI - Transforming Waste into Value'
    }
    
    return render(request, 'dashboard/landing.html', context)


@login_required
def generator_dashboard(request):
    """
    Dashboard for waste generators
    Shows: listings, sales stats, karma, recent activity
    """
    if request.user.role != 'GENERATOR':
        messages.warning(request, 'Access denied. This dashboard is for waste generators only.')
        return redirect('marketplace_feed')
    
    # Get user's listings
    my_listings = WasteListing.objects.filter(
        seller=request.user
    ).select_related('material').order_by('-created_at')
    
    # Statistics
    stats = {
        'total_listings': my_listings.count(),
        'active_listings': my_listings.filter(status='LISTED').count(),
        'sold_listings': my_listings.filter(status='SOLD').count(),
        'total_weight_listed': my_listings.aggregate(total=Sum('weight'))['total'] or 0,
        'total_co2_impact': my_listings.aggregate(total=Sum('co2_saved'))['total'] or 0,
        'average_trust_score': my_listings.aggregate(avg=Avg('trust_score'))['avg'] or 0,
        'verified_listings': my_listings.filter(is_verified=True).count(),
    }
    
    # Recent listings (last 5)
    recent_listings = my_listings[:5]
    
    # Karma progress (calculate percentage to next level)
    current_karma = request.user.karma_score
    karma_levels = {
        'Platinum': 800,
        'Gold': 600,
        'Silver': 400,
        'Bronze': 200,
        'Starter': 0
    }
    
    current_level = request.user.karma_level
    next_level = None
    karma_to_next = 0
    karma_progress = 0
    
    for level, threshold in sorted(karma_levels.items(), key=lambda x: x[1], reverse=True):
        if current_karma < threshold:
            next_level = level
            karma_to_next = threshold - current_karma
            # Calculate progress within current level
            if current_level == 'Starter':
                karma_progress = (current_karma / 200) * 100
            elif current_level == 'Bronze':
                karma_progress = ((current_karma - 200) / 200) * 100
            elif current_level == 'Silver':
                karma_progress = ((current_karma - 400) / 200) * 100
            elif current_level == 'Gold':
                karma_progress = ((current_karma - 600) / 200) * 100
            elif current_level == 'Platinum':
                karma_progress = 100
    
    context = {
        'stats': stats,
        'recent_listings': recent_listings,
        'karma_info': {
            'current_level': current_level,
            'next_level': next_level,
            'karma_to_next': karma_to_next,
            'karma_progress': min(100, karma_progress),
            'current_karma': current_karma
        },
        'page_title': 'Generator Dashboard - CircuTrade AI'
    }
    
    return render(request, 'dashboard/generator_dashboard.html', context)


@login_required
def buyer_dashboard(request):
    """
    Dashboard for buyers/manufacturers
    Shows: marketplace recommendations, purchase history, nearby listings
    """
    if request.user.role != 'BUYER':
        messages.warning(request, 'Access denied. This dashboard is for buyers only.')
        return redirect('marketplace_feed')
    
    # Get recommended listings (same location, verified)
    recommended_listings = WasteListing.objects.filter(
        status='LISTED',
        is_verified=True
    ).filter(
        city=request.user.city
    ).select_related('material', 'seller').order_by('-trust_score')[:6]
    
    # If no local listings, get from same state
    if not recommended_listings.exists():
        recommended_listings = WasteListing.objects.filter(
            status='LISTED',
            is_verified=True,
            state=request.user.state
        ).select_related('material', 'seller').order_by('-trust_score')[:6]
    
    # Statistics
    stats = {
        'available_listings': WasteListing.objects.filter(status='LISTED').count(),
        'verified_listings': WasteListing.objects.filter(status='LISTED', is_verified=True).count(),
        'nearby_listings': WasteListing.objects.filter(
            status='LISTED',
            city=request.user.city
        ).count(),
        'total_materials': Material.objects.filter(is_active=True).count(),
    }
    
    # Top materials by availability
    top_materials = Material.objects.filter(
        is_active=True,
        listings__status='LISTED'
    ).annotate(
        listing_count=Count('listings')
    ).order_by('-listing_count')[:5]
    
    context = {
        'stats': stats,
        'recommended_listings': recommended_listings,
        'top_materials': top_materials,
        'page_title': 'Buyer Dashboard - CircuTrade AI'
    }
    
    return render(request, 'dashboard/buyer_dashboard.html', context)


@login_required
def worker_dashboard(request):
    """
    Dashboard for informal workers
    Shows: simple interface with available work, earnings potential
    """
    if request.user.role != 'WORKER':
        messages.warning(request, 'Access denied. This dashboard is for workers only.')
        return redirect('marketplace_feed')
    
    # Get nearby active listings (potential work opportunities)
    nearby_listings = WasteListing.objects.filter(
        status='LISTED',
        city=request.user.city
    ).select_related('material', 'seller').order_by('-created_at')[:10]
    
    # If no local listings, expand to state
    if not nearby_listings.exists():
        nearby_listings = WasteListing.objects.filter(
            status='LISTED',
            state=request.user.state
        ).select_related('material', 'seller').order_by('-created_at')[:10]
    
    # Statistics
    stats = {
        'nearby_opportunities': nearby_listings.count(),
        'total_weight_available': nearby_listings.aggregate(total=Sum('weight'))['total'] or 0,
    }
    
    context = {
        'stats': stats,
        'nearby_listings': nearby_listings,
        'page_title': 'Worker Dashboard - CircuTrade AI'
    }
    
    return render(request, 'dashboard/worker_dashboard.html', context)


@login_required
def provenance_vault(request):
    """
    Provenance tracking vault
    Coming in Phase 4 - placeholder for now
    """
    messages.info(request, 'Provenance Vault coming soon in Phase 4!')
    return redirect('marketplace_feed')


@login_required
def esg_report(request):
    """
    ESG (Environmental, Social, Governance) report
    Shows environmental impact metrics
    """
    # Get user's impact based on role
    if request.user.role == 'GENERATOR':
        # Generator's direct impact from listings
        user_impact = WasteListing.objects.filter(
            seller=request.user
        ).aggregate(
            total_co2=Sum('co2_saved'),
            total_weight=Sum('weight')
        )
    elif request.user.role == 'BUYER':
        # Buyer's impact from purchases (Phase 5)
        user_impact = {
            'total_co2': 0,
            'total_weight': 0
        }
        messages.info(request, 'Purchase-based ESG metrics coming in Phase 5!')
    else:
        user_impact = {
            'total_co2': 0,
            'total_weight': 0
        }
    
    # Platform-wide impact
    platform_impact = get_material_statistics()
    
    context = {
        'user_impact': user_impact,
        'platform_impact': platform_impact,
        'page_title': 'ESG Report - CircuTrade AI'
    }
    
    return render(request, 'dashboard/esg_report.html', context)
