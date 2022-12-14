from django.contrib import admin
from .models import Product, Photo, Rating
# Register your models here.


admin.site.register(Product)
admin.site.register(Photo)
admin.site.register(Rating)