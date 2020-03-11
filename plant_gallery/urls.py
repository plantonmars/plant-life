"""URL patterns for plant_gallery"""

from django.urls import path
from . import views

app_name = 'plant_gallery'

urlpatterns = [
    path('', views.index, name='index'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/type/<str:type_id>/', views.gallery_type, name='gallery_type'),
    path('gallery/lighting/<str:lighting_id>/', views.gallery_light, name='gallery_light'),
    path('plant/<int:plant_id>/edit', views.edit_plant, name="edit_plant"),
    path('plant/<int:plant_id>/', views.plant, name="plant"),
    path('plant/<int:plant_id>/purchase', views.purchase_plant, name="purchase_plant"),
    path('plant/create', views.create_plant, name="create_plant"),
    path('plants/', views.my_plants, name="my_plants"),
    path('payment/new', views.add_funds, name="add_funds"),
]