from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages as dj_msg
from . models import Plant, Bank, Lighting, Type
from . forms import LightingForm, TypeForm, PlantForm, PaymentForm
from plant_network.models import Inbox, Messages
from item_system.models import Item, Quantity, Inventory
import random

"""
    Views necessary to complete functions of the plant_gallery app.

    Author: Joseph Salinas
    GitHub: plantonmars
"""


def index(request):
    """Used to render the landing page for the website"""

    return render(request, 'plant_gallery/index.html')


def gallery(request):
    """Used to display all plants that are listed for sale"""

    plants = Plant.objects.filter(for_sale=True)

    context = {'plants': plants}
    search_dict(context)

    if request.GET:
        return search_redirect(request)

    return render(request, 'plant_gallery/gallery.html', context)


def gallery_type(request, type_id):
    """Used to display all plants that are listed for sale under a specified plant type"""

    isValid = Type.objects.filter(plant_type=type_id.title())

    if not isValid:
        dj_msg.warning(request, f"There was an error processing that request.")
        return redirect("plant_gallery:gallery")

    type_id = type_id.title()
    plants = Plant.objects.filter(plant_type__plant_type=type_id, for_sale=True)
    context = {'plants': plants, 'plant_type': type_id, 'isType': True}
    search_dict(context)

    if request.GET:
        return search_redirect(request)

    return render(request, 'plant_gallery/gallery.html', context)


def gallery_light(request, lighting_id):
    """Used to display all plants that are listed for sale under a specified lighting condition"""

    isValid = Lighting.objects.filter(lighting_condition=lighting_id.title())

    if not isValid:
        dj_msg.warning(request, f"There was an error processing that request.")
        return redirect('plant_gallery:gallery')

    lighting_id = lighting_id.title()
    plants = Plant.objects.filter(lighting__lighting_condition=lighting_id, for_sale=True)
    context = {'plants': plants, 'lighting': lighting_id, 'isLighting': True}
    search_dict(context)

    if request.GET:
        return search_redirect(request)

    return render(request, 'plant_gallery/gallery.html', context)


@login_required
def create_plant(request):
    """Determines if the user has the appropriate items to create a plant, then proceeds
    to create the desired plant specified by the user"""

    context = {}

    try:
        my_inventory = Inventory.objects.get(owner=request.user)
        context['seeds'] = my_inventory.items.filter(type='seeds')
        context['pot'] = my_inventory.items.filter(type='pot')
    except:
        pass

    # Plants the specified seeds, creates plant and adjusts the quantity of items used.
    if 'plant' in request.GET:
        seeds_quantity = Quantity.objects.get(inventory=my_inventory, item__name=request.GET['plant'])
        seeds_quantity.quantity -= 1
        seeds_quantity.save()

        if seeds_quantity.quantity == 0:
            remove_seeds = Item.objects.get(name=request.GET['plant'])
            my_inventory.items.remove(remove_seeds)

        pot_quantity = Quantity.objects.get(inventory=my_inventory, item__name='Pot')
        pot_quantity.quantity -= 1
        pot_quantity.save()

        if pot_quantity.quantity == 0:
            remove_pot = Item.objects.get(type="pot")
            my_inventory.items.remove(remove_pot)

        upload_plant(request)
        dj_msg.success(request, "Congrats on your new addition!")
        return redirect('plant_gallery:my_plants')

    return render(request, 'plant_gallery/create_plant.html', context)


@login_required
def plant(request, plant_id):
    """Displays the page of a plant that is listed for sale or belongs to their owner"""
    plant_searched = Plant.objects.get(id=plant_id)
    plant_visibility(plant_searched, request)
    context = {'plant': plant_searched}

    if 'discard' in request.GET:
        check_ownership(plant_searched, request)
        name = plant_searched.name
        plant_searched.delete()
        dj_msg.success(request, f"Bye bye! {name} was discarded.")
        return redirect("plant_gallery:my_plants")
    elif 'fertilize' in request.GET:
        check_ownership(plant_searched, request)

        if plant_searched.level == plant_searched.max_level:
            dj_msg.warning(request, "You can't fertilize a plant that has reached their max level!")
            return redirect('plant_gallery:plant', plant_id)
        try:

            my_inventory = Inventory.objects.get(owner=request.user)
            fertilizer = my_inventory.items.get(type="fertilizer")
            quantity = Quantity.objects.get(item=fertilizer, inventory=my_inventory)

            quantity.quantity -= 1
            quantity.save()

            if quantity.quantity == 0:
                my_inventory.items.remove(fertilizer)

            # Fertilizer will allow for a random range of exp gained from 100 to a half of the max_exp required
            exp_gained = random.randint(100, (plant_searched.max_exp / 2) + 1)
            plant_searched.exp += exp_gained

            if plant_searched.exp >= plant_searched.max_exp:
                remainder = plant_searched.exp - plant_searched.max_exp
                plant_searched.level += 1
                plant_searched.exp = remainder
                plant_searched.max_exp = exp_dict(plant_searched.level)
                plant_searched.img_url = evolution_dict(plant_searched.level, plant_searched.species)['img_url']
                plant_searched.save()
                dj_msg.success(request, f'You fertilized {plant_searched.name} and gained {exp_gained} exp and'
                                        f' your plant grew to level {plant_searched.level}!')
                return redirect("plant_gallery:plant", plant_id)

            else:
                plant_searched.save()
                dj_msg.success(request, f'You fertilized {plant_searched.name} and gained {exp_gained} exp!')
                return redirect("plant_gallery:plant", plant_id)


        except:
            dj_msg.warning(request, "Uh oh! It seems that you don't have fertilizer")
            return redirect("plant_gallery:plant", plant_id)

    return render(request, 'plant_gallery/plant.html', context)


@login_required
def purchase_plant(request, plant_id):
    """The purchase process of a plant, balances will be checked and updated and a
    notification will be sent as a message to the seller if their plant was bought"""

    plant_requested = Plant.objects.get(id=plant_id)
    context = {'plant': plant_requested, 'isAdopting': True}

    if plant_requested.owner == request.user:
        return redirect("plant_gallery:gallery")

    if request.GET:
        current_bank = Bank.objects.get(owner=request.user)
        other_bank = Bank.objects.get(owner=plant_requested.owner)
        # Compares current balance to plant cost
        if current_bank.balance >= plant_requested.cost:
            current_bank.balance -= plant_requested.cost
            current_bank.save()
            other_bank.balance += plant_requested.cost
            other_bank.save()

            # Create a message to be sent to the seller, knowing their plant was purchased
            subject = f"{request.user.username} bought your plant, {plant_requested.name}!"
            body = f"This message is to notify that another user by the name of {request.user.username} has purchased" \
                   " your plant!"
            sent_from = "PLANT ADMIN"
            inbox = Inbox.objects.get(owner=plant_requested.owner)
            notify_seller = Messages(subject=subject, body=body, sent_from=sent_from, inbox=inbox)
            notify_seller.save()

            plant_requested.owner = request.user
            plant_requested.save()

            # Redirects user to their plants to see their new addition
            dj_msg.success(request, f"Woohoo! {plant_requested.name} has joined your plant family.")
            return redirect('plant_gallery:my_plants')
        else:
            # Error message presented to show that user lacks funds
            dj_msg.warning(request, f"Whoops, It seems like you don't have enough funds!")
            return render(request, 'plant_gallery/plant.html', context)

    return render(request, 'plant_gallery/plant.html', context)


@login_required
def add_funds(request):
    """Presents an empty payment form, user must enter valid data for each section or
    they will be promoted with a ValidationError message"""

    if request.method != 'POST':
        # Blank Form
        form = PaymentForm()
    else:
        # Form with data
        form = PaymentForm(data=request.POST)

        if form.is_valid():
            # Update payment record
            new_payment = form.save(commit=False)
            new_payment.owner = request.user
            new_payment.save()

            # Update bank record
            current_bank = Bank.objects.get(owner=request.user)
            current_bank.balance += int(request.POST['amount'])
            current_bank.save()

            dj_msg.success(request, "Funds were added successfully.")
            return redirect('plant_gallery:add_funds')

    context = {'form': form}

    return render(request, 'plant_gallery/add_funds.html', context)


@login_required
def edit_plant(request, plant_id):
    """Allows a user to customize their plant"""

    plant_to_edit = Plant.objects.get(id=plant_id)
    check_ownership(plant_to_edit, request)

    if request.method != 'POST':
        # Form with instance of requested plant
        form = PlantForm(instance=plant_to_edit)
    else:
        # Fills instance with new data and then saves
        form = PlantForm(instance=plant_to_edit, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('plant_gallery:plant', plant_id=plant_id)

    context = {'plant': plant_to_edit, 'form': form}

    return render(request, 'plant_gallery/edit_plant.html', context)


@login_required
def my_plants(request):
    """Displays the current user's collection of plants"""

    plants = Plant.objects.filter(owner=request.user).order_by('-date_added')
    context = {'plants': plants, 'isMyPlants': True}

    if 'delete' in request.GET:
        return redirect('plant_gallery:plant', request.GET['delete'])

    return render(request, 'plant_gallery/my_plants.html', context)


def upload_plant(request):
    """Used to determine the characteristics of the plant to be created based off
    the seeds used to create the plant."""

    seed_type = request.GET['plant']
    username = request.user.username

    if username[-1] == 's':
        username = username + '\''
    else:
        username = username + '\'s'

    # plant_dict will be used to store all possible level 1/new plants attributes
    plant_dict = {
        'Aloe Seeds': {
            'lighting': Lighting.objects.get(lighting_condition='Bright'),
            'type': Type.objects.get(plant_type='Succulent'),
            'owner': request.user,
            'name': f'{username} Aloe Vera Plant',
            'description': f"A newly born Aloe Vera.",
            'img_url': 'https://i.imgur.com/SPzdr4z.png',
            'species': 'aloe'
        },

        'Rose Seeds': {
            'lighting': Lighting.objects.get(lighting_condition='Medium'),
            'type': Type.objects.get(plant_type='Flower'),
            'owner': request.user,
            'name': f'{username} Rose Plant',
            'description': f"A newly born Rose.",
            'img_url': 'https://i.imgur.com/jPLhrum.png',
            'species': 'rose',

        },

        'Violet Seeds': {
            'lighting': Lighting.objects.get(lighting_condition='Low'),
            'type': Type.objects.get(plant_type='Flower'),
            'owner': request.user,
            'name': f'{username} Violet Plant',
            'description': f"A newly born Violet.",
            'img_url': 'https://i.imgur.com/jPLhrum.png',
            'species': 'violet'
        }
    }

    seed_planted = plant_dict[seed_type]
    # Create new plant instance and store into database
    new_plant = Plant(lighting=seed_planted['lighting'], plant_type=seed_planted['type'],
                      owner=seed_planted['owner'], name=seed_planted['name'],
                      description=seed_planted['description'], img_url=seed_planted['img_url'],
                      species=seed_planted['species'])
    new_plant.save()


def exp_dict(level):

    # Dictionary stored in Level => Max Exp Points Required
    exp_dict = {
        2: 1000,
        3: 1500,
        4: 2000,
        5: 2500
    }

    level = level
    return exp_dict[level]


def evolution_dict(level, species):

    # Dictionary stored in level => species ; species => information

    evol_dict = {
        2: {
            'violet': {
                'img_url': 'https://i.imgur.com/VxJoDki.png'
            },

            'aloe': {
                'img_url': 'https://i.imgur.com/bw61Ba9.png'
            },

            'rose': {
                'img_url': 'https://i.imgur.com/VxJoDki.png'

            }
        },

        3: {
            'violet': {
                'img_url': 'https://i.imgur.com/VXyfP1U.png'

            },

            'aloe': {
                'img_url': 'https://i.imgur.com/JvkMj2C.png'

            },

            'rose': {
                'img_url': 'https://i.imgur.com/7oydwQX.png'

            }
        },

        4: {
            'violet': {
                'img_url': 'https://i.imgur.com/0nc7qxF.png'

            },

            'aloe': {
                'img_url': 'https://i.imgur.com/PHK6ALx.png'

            },

            'rose': {
                'img_url': 'https://i.imgur.com/JwanPHP.png'

            }
        },

        5: {
            'violet': {
                'img_url': 'https://i.imgur.com/x3of3ap.png'

            },

            'aloe': {
                'img_url': 'https://i.imgur.com/vAt3f5x.png'

            },

            'rose': {
                'img_url': 'https://i.imgur.com/dT7a8dZ.png'

            }
        },
    }

    return evol_dict[level][species]


def search_redirect(request):
    """Used to redirect the user to the correct page depending on the search
    field specified"""

    if 'type_form' in request.GET:
        type_id = request.GET['type_field']
        return redirect('plant_gallery:gallery_type', type_id.lower())
    elif 'lighting_form' in request.GET:
        lighting_id = request.GET['lighting_field']
        return redirect('plant_gallery:gallery_light', lighting_id.lower())


def search_dict(context):
    """Used to add search forms to appropriate pages"""

    context['type_form'] = TypeForm()
    context['lighting_form'] = LightingForm()


def check_ownership(lhs, request):
    """Ensure one user can't edit another user's plant posting and
    prevents users from seeing each others payment transactions"""

    if lhs.owner != request.user:
        raise Http404


def plant_visibility(lhs, request):
    """Allows plant page to be accessed by owner, but not by others if plant is
    not listed."""

    if not lhs.for_sale:
        check_ownership(lhs, request)

