from django.shortcuts import render,redirect    
from Store.models import *
from Cart.models import *
from .models import *
from .forms import *
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages


def Base(request):
    return render(request,'Core/base.html')

# def Index(request):
#     if request.user.is_authenticated:
#         return redirect('core:user_home')
#     categories = Category.objects.annotate(book_count=Count('books')).order_by('-book_count')
    
#     thirty_days_ago = timezone.now().date() - timedelta(days=30)
#     new_arrivals = Book.objects.filter(
#         available=True,
#         publishing_date__gte=thirty_days_ago
#     ).order_by('-publishing_date')[:8]
#     if not new_arrivals:
#        new_arrivals = Book.objects.filter(available=True).order_by('-publishing_date')[:8]
    
#     now_trending = Book.objects.filter(available=True).order_by('-stock')[:8]
    
#     offer_books = Book.objects.filter(
#         is_offer=True,
#         available=True
#     ).filter(
#         models.Q(offer_expiry__isnull=True) | models.Q(offer_expiry__gt=timezone.now())
#     )[:8]  

#     for book in offer_books:
#         if book.original_price and book.original_price > book.price:
#             discount = ((book.original_price - book.price) / book.original_price) * 100
#             book.discount_percent = round(discount)
#         else:
#             book.discount_percent = 0

#     featured_books = Book.objects.filter(available=True, featured=True)[:8]
#     banners = Banner.objects.all()[:4] 
#     return render(request, 'Core/index.html', {
#         'categories': categories,
#         'new_arrivals': new_arrivals,
#         'now_trending': now_trending,
#         'featured_books': featured_books,
#         'banners': banners,
#         'offer_books': offer_books,
#         'now': timezone.now(), 
#     })

def Index(request):
    if request.user.is_authenticated:
        return redirect('core:user_home')

    # Top categories by book count
    categories = Category.objects.annotate(book_count=Count('books')).order_by('-book_count')[:6]

    # New Arrivals - Last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    new_arrivals = Book.objects.filter(
        available=True,
        publishing_date__gte=thirty_days_ago
    ).order_by('-publishing_date')[:8]

    if not new_arrivals.exists():
        new_arrivals = Book.objects.filter(available=True).order_by('-publishing_date')[:8]

    # Trending Books by stock (fallback if no sales tracking)
    now_trending = Book.objects.filter(available=True).order_by('-stock')[:8]

    # Offer Books - with valid expiry
    offer_books = Book.objects.filter(
        is_offer=True,
        available=True
    ).filter(
        Q(offer_expiry__isnull=True) | Q(offer_expiry__gt=timezone.now())
    )[:8]

    for book in offer_books:
        if book.original_price and book.original_price > book.price:
            discount = ((book.original_price - book.price) / book.original_price) * 100
            book.discount_percent = round(discount)
        else:
            book.discount_percent = 0

    # Featured Books
    featured_books = Book.objects.filter(available=True, featured=True)[:8]
    if not featured_books.exists():
        featured_books = Book.objects.filter(available=True).order_by('?')[:8]

    # Banners (top 4)
    banners = Banner.objects.all()[:4]

    return render(request, 'Core/index.html', {
        'categories': categories,
        'new_arrivals': new_arrivals,
        'now_trending': now_trending,
        'featured_books': featured_books,
        'banners': banners,
        'offer_books': offer_books,
        'now': timezone.now(),
    })


@login_required
def User_Home(request):
    categories = Category.objects.annotate(book_count=Count('books')).order_by('-book_count')
    
    # New arrivals (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    new_arrivals = Book.objects.filter(
        publishing_date__gte=thirty_days_ago, 
        available=True
    ).order_by('-publishing_date')[:8]  # Get 8 newest books
    
    # Trending (by stock)
    now_trending = Book.objects.filter(available=True).order_by('-stock')[:8]
    
    offer_books = Book.objects.filter(
        is_offer=True,
        available=True
    ).filter(
        models.Q(offer_expiry__isnull=True) | models.Q(offer_expiry__gt=timezone.now())
    )[:8]  

    for book in offer_books:
        if book.original_price and book.original_price > book.price:
            discount = ((book.original_price - book.price) / book.original_price) * 100
            book.discount_percent = round(discount)
        else:
            book.discount_percent = 0

    # Featured books
    featured_books = Book.objects.filter(available=True, featured=True)[:8]
    banners = Banner.objects.all()[:4] 

    context = {
        'categories': categories,
        'new_arrivals': new_arrivals,
        'now_trending': now_trending,
        'featured_books': featured_books,
        'banners': banners,
        'offer_books': offer_books,
        'now': timezone.now(), 
    }
    return render(request, 'Core/user_home.html', context)

def Shop(request):
    # books = Book.objects.filter(available=True)
    books = Book.objects.all()

    # Apply filters
    price_max = request.GET.get('price_max')
    if price_max:
        books = books.filter(price__lte=float(price_max))
    
    categories = request.GET.getlist('categories')
    if categories:
        books = books.filter(categories__id__in=categories).distinct()

    languages = request.GET.getlist('languages')
    if languages:
        books = books.filter(language__in=languages)    
    
    in_stock = request.GET.get('in_stock')
    if in_stock:
        books = books.filter(stock__gt=0)
    
    # Apply sorting
    sort = request.GET.get('sort', 'price_asc')
    if sort == 'price_asc':
        books = books.order_by('price')
    elif sort == 'price_desc':
        books = books.order_by('-price')
    elif sort == 'newest':
        books = books.order_by('-publishing_date')
    elif sort == 'popular':
        books = books.order_by('-stock')
    
    # Pagination
    paginator = Paginator(books, 12)  # Show 12 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    selected_categories = request.GET.getlist('categories')

    context = {
        'books': page_obj,
        'selected_categories': selected_categories,
        'selected_languages': languages,
        'categories': Category.objects.annotate(book_count=Count('books')).filter(book_count__gt=0),
        'all_languages': Book.objects.values_list('language', flat=True).distinct().order_by('language'),

    }
    return render(request, 'Core/shop.html', context)

def Book_Detail(request, id):
    book = get_object_or_404(Book, id=id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')

        if rating and content:
            Review.objects.create(
                book=book,
                user=request.user,
                rating=rating,
                text=content
            )
            messages.success(request, "Your review has been submitted.")
            return redirect('core:book_detail', id=book.id)
        else:
            messages.error(request, "Please provide both rating and review.")

    is_offer_valid = book.is_offer and (not book.offer_expiry or book.offer_expiry > timezone.now())

    discount_percent = 0
    if is_offer_valid and book.original_price and book.original_price > book.price:
        discount_percent = round(((book.original_price - book.price) / book.original_price) * 100)

    # Fetch related books (same categories, exclude self)
    categories = book.categories.all()
    related_books = Book.objects.filter(categories__in=categories).exclude(id=book.id).distinct()[:8]
    # Fetch reviews
    reviews = Review.objects.filter(book=book).order_by('-created_at')
    return render(request, 'Core/book_details.html', {
        'book': book,
        'is_offer_valid': is_offer_valid,
        'discount_percent': discount_percent,
        'related_books': related_books,
        'reviews': reviews,
    })

def New_Arrivals(request):
    latest_books = Book.objects.filter(available=True).order_by('-publishing_date')[:20]  # last 20 books
    return render(request,'Core/new_arrivals.html', {'latest_books': latest_books})

def Featured(request):
    featuredbooks = Book.objects.filter(available=True, featured=True)
    return render(request, 'Core/featured.html', {
        'featuredbooks': featuredbooks
    })    

def About_Us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for contacting us! We'll get back to you soon.")
            return redirect('core:about')  # or use reverse() if needed
    else:
        form = ContactForm()
    return render(request,'Core/about.html', {'form': form})
    

def Trending(request):
    trending_books = Book.objects.filter(available=True).order_by('-stock')[:20]
    return render(request,'Core/trending.html', {
        'trending_books': trending_books
    })    


def search_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()

    return render(request, 'Core/search_results.html', {
        'query': query,
        'results': results
    })

def Categories(request, id):
    category = get_object_or_404(Category, id=id)
    books = Book.objects.filter(categories=category)
    return render(request, 'Core/category.html', {
        'category': category,
        'books': books
    })

def OfferZone(request):
    offer_books = Book.objects.filter(
        is_offer=True,
        available=True
    ).filter(
        models.Q(offer_expiry__isnull=True) | models.Q(offer_expiry__gt=timezone.now())
    )[:8]  

    for book in offer_books:
        if book.original_price and book.original_price > book.price:
            discount = ((book.original_price - book.price) / book.original_price) * 100
            book.discount_percent = round(discount)
        else:
            book.discount_percent = 0

    return render(request,'Core/offer_zone.html',{'offer_books': offer_books,
        'now': timezone.now(), 
    })