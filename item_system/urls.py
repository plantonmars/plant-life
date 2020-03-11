from django.urls import path

from . import views

app_name = 'item_system'

urlpatterns = [

    path("shop/", views.shop, name="shop"),
    path("inventory/", views.inventory, name="inventory"),
    path("shop/purchase/<int:item_id>", views.purchase_item, name="purchase_item")

]