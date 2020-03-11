from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from plant_gallery.models import Bank
from plant_network.models import FriendsList, Inbox, Profile
from item_system.models import Inventory
from django.contrib import messages as dj_msg

def register(request):

    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)

        if form.is_valid():

            # Setups up the users bank, friends list, inbox and profile settings.
            new_user = form.save(commit=False)
            try:
                new_user.username = new_user.username.lower()
                new_user.save()
            except:
                dj_msg.warning(request, "Case Error: Username already taken.")
                return redirect('users:register')

            login(request, new_user)
            new_bank = Bank(owner=new_user)
            new_bank.save()
            friends_list = FriendsList(owner=new_user)
            friends_list.save()
            inbox = Inbox(owner=new_user)
            inbox.save()
            new_profile = Profile(owner=request.user, display_name=request.user.username)
            new_profile.save()
            new_inventory = Inventory(owner=request.user)
            new_inventory.save()

            return redirect('plant_network:profile', new_user.username)

    context = {'form': form}

    return render(request, 'registration/register.html', context)

