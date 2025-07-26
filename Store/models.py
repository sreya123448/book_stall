from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='books')
    publishing_date = models.DateField(default=timezone.now)
    publisher = models.CharField(max_length=255)
    edition = models.PositiveIntegerField(default=1)
    number_of_pages = models.PositiveIntegerField()
    language = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)

    original_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_offer = models.BooleanField(default=False)
    offer_tag = models.CharField(max_length=100, blank=True)  # e.g., "Under ₹199", "BOGO", etc.
    offer_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def is_offer_active(self):
        return self.is_offer and (self.offer_expiry is None or self.offer_expiry > timezone.now())

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.available = self.stock > 0
        super().save(*args, **kwargs)
    