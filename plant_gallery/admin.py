from django.contrib import admin

# Register your models here.
from .models import Lighting, Type, Plant
from item_system.models import Item

admin.site.register(Lighting)
admin.site.register(Type)
admin.site.register(Plant)
admin.site.register(Item)