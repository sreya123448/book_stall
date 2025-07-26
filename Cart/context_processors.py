from .models import CartItem, WishlistItem  # adjust import if in another app

def cart_and_wishlist_counts(request):
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        wishlist_count = WishlistItem.objects.filter(user=request.user).count()
        cart_count = CartItem.objects.filter(user=request.user).count()
    return {
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
