from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    name = models.CharField(max_length=50)
    item_img = models.CharField(max_length=300)
    description = models.CharField(max_length=250)
    cost = models.IntegerField()
    type = models.CharField(max_length=10)


class Inventory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='Quantity')


class Quantity(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)




