from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import UserRegistrationForm, CustomLoginForm, UserProfileUpdateForm
from .models import CustomUser


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    User registration view with role selection
    """
    if request.user.is_authenticated:
        return redirect('marketplace_feed')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the user in after registration
            login(request, user)
            
            # Success message based on role
            role_messages = {
                'GENERATOR': 'Welcome! You can now start listing your waste materials.',
                'BUYER': 'Welcome! Start exploring verified waste materials in the marketplace.',
                'WORKER': 'Welcome! Your simplified dashboard is ready.'
            }
            
            messages.success(
                request,
                f"Account created successfully! {role_messages.get(user.role, 'Welcome to CircuTrade AI!')}"
            )
            
            # Redirect based on role
            if user.role == 'GENERATOR':
                return redirect('generator_dashboard')
            elif user.role == 'BUYER':
                return redirect('buyer_dashboard')
            elif user.role == 'WORKER':
                return redirect('worker_dashboard')
            else:
                return redirect('marketplace_feed')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Join CircuTrade AI'
    }
    return render(request, 'accounts/register.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Custom login view
    """
    if request.user.is_authenticated:
        return redirect('marketplace_feed')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                # Redirect to appropriate dashboard
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                if user.role == 'GENERATOR':
                    return redirect('generator_dashboard')
                elif user.role == 'BUYER':
                    return redirect('buyer_dashboard')
                elif user.role == 'WORKER':
                    return redirect('worker_dashboard')
                else:
                    return redirect('marketplace_feed')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login to CircuTrade AI'
    }
    return render(request, 'accounts/login.html', context)


@login_required
@require_http_methods(["GET"])
def logout_view(request):
    """
    Logout view
    """
    username = request.user.get_full_name()
    logout(request)
    messages.info(request, f'Goodbye, {username}! You have been logged out successfully.')
    return redirect('marketplace_feed')


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """
    View and edit user profile
    """
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'My Profile',
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_http_methods(["GET"])
def profile_public_view(request, username):
    """
    View public profile of another user
    """
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('marketplace_feed')
    
    # Get user statistics
    stats = {
        'total_listings': user.total_listings if user.role == 'GENERATOR' else 0,
        'total_purchases': user.total_purchases if user.role == 'BUYER' else 0,
        'total_sales': user.total_sales if user.role == 'GENERATOR' else 0,
        'karma_level': user.karma_level if user.role == 'GENERATOR' else None,
    }
    
    context = {
        'profile_user': user,
        'stats': stats,
        'page_title': f"{user.get_full_name()} - Profile"
    }
    return render(request, 'accounts/profile_public.html', context)


@require_http_methods(["GET"])
def check_username_availability(request):
    """
    AJAX endpoint to check if username is available
    """
    username = request.GET.get('username', '')
    available = not CustomUser.objects.filter(username=username).exists()
    
    from django.http import JsonResponse
    return JsonResponse({
        'available': available,
        'message': 'Username available' if available else 'Username already taken'
    })


@require_http_methods(["GET"])
def check_email_availability(request):
    """
    AJAX endpoint to check if email is available
    """
    email = request.GET.get('email', '')
    available = not CustomUser.objects.filter(email=email).exists()
    
    from django.http import JsonResponse
    return JsonResponse({
        'available': available,
        'message': 'Email available' if available else 'Email already registered'
    })
