from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser

#This class will add to Django's default user model. The new fields will be 'uuid' and 'user_type'. 
class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )

    def __str__(self):
        return self.username
    
#This class will create our Product table.

class Product(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=50, unique=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


#This class will create our reviews table. 

class Review(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"
