from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
import json

from .models import Transaction
from marketplace.models import WasteListing
from provenance.models import ProvenanceBlock

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def create_offer(request, listing_id):
    """
    Create a new purchase offer (transaction)
    """
    if request.method != 'POST':
        return redirect('listing_detail', listing_id=listing_id)
    
    listing = get_object_or_404(WasteListing, id=listing_id)
    
    # Validate buyer role
    if request.user.role != 'BUYER':
        messages.error(request, 'Only buyers can make offers.')
        return redirect('listing_detail', listing_id=listing_id)
    
    # Validate listing is available
    if listing.status != 'LISTED':
        messages.error(request, 'This listing is no longer available.')
        return redirect('listing_detail', listing_id=listing_id)
    
    # Get form data
    offer_amount = request.POST.get('offer_amount')
    delivery_address = request.POST.get('delivery_address')
    contact_number = request.POST.get('contact_number')
    notes = request.POST.get('notes', '')
    
    # Create transaction
    transaction = Transaction.objects.create(
        listing=listing,
        buyer=request.user,
        seller=listing.seller,
        offer_amount=offer_amount,
        delivery_address=delivery_address,
        contact_number=contact_number,
        notes=notes,
        status='PENDING',
        payment_status='PENDING'
    )
    
    # Award karma for making offer
    request.user.update_karma(2, f"Made offer on {listing.title}")
    
    messages.success(request, f'✅ Your offer of ₹{offer_amount} has been sent to the seller!')
    return redirect('buyer_offers')


@login_required
def accept_offer(request, transaction_id):
    """
    Seller accepts an offer
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Validate seller
    if transaction.seller != request.user:
        messages.error(request, 'You are not authorized to accept this offer.')
        return redirect('dashboard')
    
    # Validate status
    if transaction.status != 'PENDING':
        messages.error(request, 'This offer has already been processed.')
        return redirect('seller_offers')
    
    # Accept offer
    seller_notes = request.POST.get('seller_notes', '')
    transaction.accept(seller_notes)
    
    # Add provenance block
    ProvenanceBlock.add_block(
        listing=transaction.listing,
        action='PURCHASED',
        actor=transaction.buyer,
        metadata={
            'price': float(transaction.offer_amount),
            'buyer': transaction.buyer.get_full_name(),
            'transaction_id': transaction.id,
        },
        notes=f'Purchase offer accepted by seller'
    )
    
    messages.success(request, f'✅ Offer accepted! Buyer has been notified.')
    return redirect('seller_offers')


@login_required
def reject_offer(request, transaction_id):
    """
    Seller rejects an offer
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Validate seller
    if transaction.seller != request.user:
        messages.error(request, 'You are not authorized to reject this offer.')
        return redirect('dashboard')
    
    # Validate status
    if transaction.status != 'PENDING':
        messages.error(request, 'This offer has already been processed.')
        return redirect('seller_offers')
    
    # Reject offer
    seller_notes = request.POST.get('seller_notes', 'Offer declined')
    transaction.reject(seller_notes)
    
    messages.success(request, 'Offer rejected.')
    return redirect('seller_offers')


@login_required
def create_razorpay_order(request, transaction_id):
    """
    Create Razorpay order for payment
    """
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Validate buyer
    if transaction.buyer != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Validate status
    if transaction.status != 'ACCEPTED':
        return JsonResponse({'error': 'Transaction not ready for payment'}, status=400)
    
    # Create Razorpay order
    amount_in_paise = int(float(transaction.offer_amount) * 100)  # Convert to paise
    
    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': 1,  # Auto capture
        'notes': {
            'transaction_id': transaction.id,
            'buyer_name': request.user.get_full_name(),
            'listing_title': transaction.listing.title,
        }
    }
    
    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        # Update transaction with Razorpay order ID
        transaction.payment_status = 'PROCESSING'
        transaction.save()
        
        return JsonResponse({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key_id': settings.RAZORPAY_KEY_ID,
            'buyer_name': request.user.get_full_name(),
            'buyer_email': request.user.email or '',
            'buyer_phone': transaction.contact_number,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def verify_payment(request):
    """
    Verify Razorpay payment signature and update transaction
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        transaction_id = data.get('transaction_id')
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Signature verified - Update transaction
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        # Update transaction
        transaction.status = 'CONFIRMED'
        transaction.payment_status = 'COMPLETED'
        transaction.transaction_hash = razorpay_payment_id
        transaction.save()
        
        # Update listing status
        transaction.listing.status = 'SOLD'
        transaction.listing.save()
        
        # Add provenance block
        ProvenanceBlock.add_block(
            listing=transaction.listing,
            action='PURCHASED',
            actor=transaction.buyer,
            metadata={
                'payment_confirmed': True,
                'amount': float(transaction.offer_amount),
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
            },
            notes=f'Payment confirmed via Razorpay - Transaction #{transaction.id}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Payment of ₹{transaction.offer_amount} confirmed!'
        })
        
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'error': 'Payment verification failed'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def buyer_offers(request):
    """
    View all offers made by the buyer
    """
    if request.user.role != 'BUYER':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    offers = Transaction.objects.filter(buyer=request.user).select_related('listing', 'seller')
    
    context = {
        'offers': offers,
        'page_title': 'My Offers',
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,  # Pass to template
    }
    
    return render(request, 'transactions/buyer_offers.html', context)


@login_required
def seller_offers(request):
    """
    View all offers received by the seller
    """
    if request.user.role != 'GENERATOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    offers = Transaction.objects.filter(seller=request.user).select_related('listing', 'buyer')
    
    context = {
        'offers': offers,
        'page_title': 'Received Offers'
    }
    
    return render(request, 'transactions/seller_offers.html', context)
