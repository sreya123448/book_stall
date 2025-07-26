from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view,name="logout"),
    path('profile/',views.Myaccount,name="my_profile"),
    path('add-address/', views.add_address, name='add_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('orders/',views.My_Orders,name="my_orders"),
    path('order_details/<int:order_id>',views.Order_details,name="order_details"),
    path('order/<int:order_id>/invoice/', views.invoice_pdf, name='invoice_pdf'),



    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]