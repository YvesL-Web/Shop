from django.db import models
from django.urls import reverse

from category.models import Category
from account.models import Account

# Create your models here.
def get_product_image_filepath(instance, filename):
    return 'gallery_image/{0}/{1}'.format(instance.product.name, filename)

class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    images = models.ImageField(upload_to="images/products/")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=models.Avg('rating'))
        avg=0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def count_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=models.Count('id'))
        count=0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def get_url(self):
        return reverse("product_detail", args=[self.category.slug, self.slug ])
    
    def __str__(self):
        return self.name


variration_cat_choice = {('color', 'color'), ('size', 'size')}

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_cat='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_cat='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_cat = models.CharField(max_length=100, choices=variration_cat_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to= get_product_image_filepath)

    class Meta:
        verbose_name_plural = "product gallery"

    def __str__(self):
        return self.product.name