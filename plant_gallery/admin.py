from django.contrib import admin

# Register your models here.
from .models import Lighting, Type, Plant

admin.site.register(Lighting)
admin.site.register(Type)
admin.site.register(Plant)