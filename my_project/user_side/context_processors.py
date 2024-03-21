from .models import *
from django.db.models import Min,Max
from payment.models import CartItem
def get_filter(request):
    cats=Service.objects.distinct().values('category__category_name','category__id')
    types=Service.objects.distinct().values('type__type_name','type__id')
    provider_types=ServiceAttribute.objects.distinct().values('provider_type__provider_type_name','provider_type__id','provider_type__provider_type_code')
    min_max_price = ServiceAttribute.objects.aggregate(Min("price"),Max('price'))

    # Get cart and wishlist counts
    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_deleted=False)
        wishlist_items = WishlistItem.objects.filter(user=request.user)
        cart_count = cart_items.count()
        wishlist_count = wishlist_items.count()
    data = {
        'cats' : cats,
        'types' : types,
        'provider_types' : provider_types,
        'min_max_price':min_max_price,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,

    }
    return data

    
