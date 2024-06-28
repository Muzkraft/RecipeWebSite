from django.contrib import admin
from .models import Category, Recipe

admin.site.site_title = 'Админка сайта рецептов'
admin.site.site_header = 'Админка сайта рецептов'

admin.site.register(Category)
admin.site.register(Recipe)
