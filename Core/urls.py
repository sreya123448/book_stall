from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('base', views.Base, name='base'),
    path('', views.Index, name='index'),
    path('user_home', views.User_Home, name='user_home'),
    path('shop', views.Shop, name='shop'),
    path('book/<int:id>/', views.Book_Detail, name='book_detail'),
    path('arrivals', views.New_Arrivals, name='arrivals'),
    path('featured', views.Featured, name='featured'),
    path('about', views.About_Us, name='about'),
    path('trending', views.Trending, name='trending'),
    path('search/', views.search_view, name='search'),
    path('category/<int:id>/', views.Categories, name='category'),    
    path('offer_zone/', views.OfferZone, name='offer_zone'),

]