from django.shortcuts import render, redirect
from . models import Item, Inventory, Quantity
from plant_gallery.models import Bank
from django.contrib import messages as dj_msg
from django.contrib.auth.decorators import login_required

"""
    Views necessary to complete functions of the item_system app.

    Author: Joseph Salinas
    GitHub: plantonmars
"""


@login_required
def shop(request):
    """Allows all items in the database to be shown inside the shop"""

    context = {}

    try:
        items = Item.objects.all()
        context['items'] = items
    except:
        pass

    return render(request, 'item_system/shop.html', context)


@login_required
def purchase_item(request, item_id):
    """Logic for handling the purchase of an item"""

    item = Item.objects.get(id =item_id)
    my_bank = Bank.objects.get(owner=request.user)
    my_inventory = Inventory.objects.get(owner=request.user)

    # Checks if user has enough currency
    if my_bank.balance >= item.cost:
        # Checks if relation has been created yet through the intermediate table
        try:
            quantity = Quantity.objects.get(inventory=my_inventory, item=item)
            quantity.quantity += 1
            quantity.save()
        except:
            quantity = Quantity(inventory=my_inventory, item=item)
            quantity.quantity += 1
            quantity.save()

        my_bank.balance -= item.cost
        my_bank.save()
        my_inventory.items.add(item)
        dj_msg.success(request, f"{item.name} has been added to your inventory!")
        return redirect('item_system:shop')
    else:
        dj_msg.warning(request, f"Uh oh! You don't have enough funds to purchase {item.name}!")
        return redirect('item_system:shop')


@login_required
def inventory(request):
    """Shows all items within the user's inventory"""

    context = {}

    try:
        item_data = Quantity.objects.filter(inventory__owner=request.user)
        context['items'] = item_data
    except:
        pass

    return render(request, 'item_system/inventory.html', context)
