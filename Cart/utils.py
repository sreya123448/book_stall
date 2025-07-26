from decimal import Decimal

FREE_SHIPPING_THRESHOLD = Decimal('500.00')
FLAT_SHIPPING_FEE = Decimal('30.00')

def calculate_shipping(subtotal):
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal('0.00')
    return FLAT_SHIPPING_FEE

def get_shipping_message():
    return "Delivery time depends on stock and location"


from Orders.models import Order

def get_current_order(user):
    try:
        return Order.objects.filter(user=user, status=Order.Status.PROCESSING, is_paid=False).latest('created_at')
    except Order.DoesNotExist:
        return None