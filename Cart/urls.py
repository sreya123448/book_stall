from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart',views.view_cart, name='view_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('add_wishlist/<int:book_id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_item/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('view_wishlist', views.view_wishlist, name='view_wishlist'),
    path('checkout/cart/',views.checkout_cart,name='checkout_cart')

]