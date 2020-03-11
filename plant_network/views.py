from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as dj_msg
from django.core.exceptions import ObjectDoesNotExist
from plant_gallery.models import Plant
from . models import Profile, Friends, Messages, Inbox, FriendsList
from . forms import ProfileForm, MessageForm, ReplyForm

"""
    Views necessary to complete functions of the plant_network app.
    
    Author: Joseph Salinas
    GitHub: plantonmars
"""


@login_required
def unfriend(request, user_id):
    """Removes the friend record from each user within the friendship"""

    try:
        unfriend_mylist = Friends.objects.get(profile__owner__username=user_id, friends_list__owner=request.user)
        unfriend_mylist.delete()

        unfriend_theirlist = Friends.objects.get(profile__owner__username=request.user.username,
                                                 friends_list__owner__username=user_id)
        unfriend_theirlist.delete()
        dj_msg.success(request, f"{user_id} was removed from your friends list!")
        return redirect('plant_network:profile', request.user.username)
    except ObjectDoesNotExist:
        dj_msg.warning(request, f"There was an error processing that request.")
        return redirect('plant_network:profile', request.user.username)


@login_required
def reply(request, message_id):
    """Presents the user with the form required to send a reply"""

    try:
        message = Messages.objects.get(id=message_id)
        reply_inbox = Inbox.objects.get(owner__username=message.sent_from)
        # Checks to see if a user is trying to access another user's message
        if request.user != message.inbox.owner:
            dj_msg.warning(request, f"There was an error processing that request.")
            return redirect('plant_network:messages')
    except ObjectDoesNotExist:
        dj_msg.warning(request, f"There was an error processing that request.")
        return redirect('plant_network:messages')

    reply_to = reply_inbox.owner.username

    message.subject = "RE: " + message.subject
    message.body = ""

    if request.method != 'POST':
        form = ReplyForm(instance=message)
    else:
        form = ReplyForm(data=request.POST)

        if form.is_valid():
            message_data = form.save(commit=False)
            message_data.inbox = reply_inbox
            message_data.sent_from = request.user.username
            message_data.save()

            dj_msg.success(request, f"Your message to {reply_inbox.owner.username} was sent!")
            return redirect("plant_network:messages")

    context = {'form': form, 'message_id': message_id, 'reply_to': reply_to}
    return render(request, 'plant_network/reply.html', context)


@login_required
def compose_message(request):
    """Provides the from to allow a user to message a friend of their choice"""

    if request.method != 'POST':
        form = MessageForm(request.user)
    else:
        form = MessageForm(request.user, data=request.POST)

        if form.is_valid():
            message_data = form.save(commit=False)
            friend_id = request.POST['send_to']
            sent_to = Friends.objects.get(id=friend_id).profile.owner.username

            send_to_inbox = Inbox.objects.get(owner__username=sent_to)
            message_data.inbox = send_to_inbox
            message_data.sent_from = request.user.username
            message_data.save()

            dj_msg.success(request, f"Your message to {sent_to} was delivered!")
            return redirect("plant_network:messages")

    context = {'form': form}

    return render(request, 'plant_network/compose_message.html', context)


@login_required
def message(request, message_id):
    """Opens the message within the current user's inbox that is clicked on"""

    try:
        message_opened = Messages.objects.get(id=message_id)
    except ObjectDoesNotExist:
        return redirect("plant_network:messages")

    message_opened.isRead = True
    message_opened.save()
    context = {'message': message_opened}

    if request.user != message_opened.inbox.owner:
        dj_msg.warning(request, f"There was an error processing that request.")
        return redirect('plant_network:messages')

    if 'accept' in request.GET:

        my_list = Friends.objects.filter(friends_list__owner=request.user)

        for my_friend in my_list:
            if my_friend.profile.owner.username == message_opened.sent_from:
                Messages.objects.filter(id=message_id).delete()
                dj_msg.warning(request, f"You and {message_opened.sent_from} are already friends!")
                return redirect('plant_network:profile', message_opened.sent_from)

        update_friends_lists(request, message_opened)
        Messages.objects.filter(id=message_id).delete()
        dj_msg.success(request, f"You and {message_opened.sent_from} are now friends!")
        return redirect('plant_network:profile', request.user.username)
    elif 'delete' in request.GET:
        message_opened.delete()
        dj_msg.success(request, "Message was deleted successfully!")
        return redirect('plant_network:messages')

    return render(request, 'plant_network/message.html', context)


@login_required
def messages(request):
    """Presents a list of messages the current user has"""
    context = {}
    my_inbox(request, context)

    return render(request, 'plant_network/messages.html', context)


@login_required
def request_sent(request, user_id):
    """Performs the action of sending a friend requests to the desired users inbox"""

    inbox_requested = Inbox.objects.get(owner__username=user_id) # Retrieves inbox of user receiving the message
    message_header = f"Friend Request: {request.user.username}"
    message_body = f"{request.user.username} has sent you a friend request!"

    try:
        messages_in_inbox = Messages.objects.filter(inbox=inbox_requested)
        # Prevents a spam of friend requests being sent to a user, if they already have a request from the sending user
        for message in messages_in_inbox:
            if message.subject == message_header:
                dj_msg.warning(request, f"{user_id} already has a friend request from you!")
                return redirect("plant_network:profile", user_id)
    except ObjectDoesNotExist:
        pass
    else:
        # Prevents a user sending a message to themselves
        if user_id == request.user.username:
            dj_msg.warning(request, f"There was an error processing that request.")
            return redirect("plant_network:profile", request.user.username)
        elif Friends.objects.filter(friends_list__owner=request.user, profile__display_name=user_id):
            dj_msg.warning(request, f"There was an error processing that request.")
            return redirect("plant_network:profile", request.user.username)

    friend_request = Messages(subject=message_header, body=message_body,
                              inbox=inbox_requested, isRequest=True, sent_from=request.user.username)
    friend_request.save()

    dj_msg.success(request, f"Friend request to {user_id} was sent!")
    return redirect("plant_network:profile", user_id)


@login_required
def edit_profile(request):
    """Allows the user to edit their own profile information through the ProfileForm"""

    my_profile = Profile.objects.get(owner=request.user)

    if request.method != 'POST':
        form = ProfileForm(instance=my_profile)
    else:
        form = ProfileForm(instance=my_profile, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect("plant_network:profile", request.user.username)

    context = {'form': form}

    return render(request, 'plant_network/edit_profile.html', context)


@login_required
def profile(request, user_id):
    """What a user's profile will look to others on the website"""

    try:
        profile = Profile.objects.get(owner__username=user_id)
    except ObjectDoesNotExist:
        dj_msg.warning(request, f"There was an error processing that request.")
        return redirect("plant_network:profile", request.user.username)

    plants = Plant.objects.filter(owner__username=user_id)
    context = {'profile': profile, 'plants': plants}

    if request.user.username == user_id:
        if profile.isFirstVisit:
            context['first_visit'] = True
            profile.isFirstVisit = False
            profile.save()

    check_friends(context, request, user_id)

    return render(request, 'plant_network/profile_template.html', context)


def update_friends_lists(lhs, rhs):
    """Once a friend request is accepted, friends list of each member will be updated accordingly.
    Parameter lhs will represent the current user's data while rhs will represent the other users data (who sent the
    request)"""

    # Data of current user
    current_profile = Profile.objects.get(owner=lhs.user)
    current_fl = FriendsList.objects.get(owner=lhs.user)

    # Data of other user
    other_profile = Profile.objects.get(owner__username=rhs.sent_from)
    other_fl = FriendsList.objects.get(owner__username=rhs.sent_from)

    # Add other user to current friends list
    my_data = Friends(profile=other_profile, friends_list=current_fl)
    my_data.save()

    other_data = Friends(profile=current_profile, friends_list=other_fl)
    other_data.save()


def check_friends(context, request, rhs):
    """Performs a check to obtain all friends for a user's profile"""

    try:
        friends = Friends.objects.filter(friends_list__owner__username=rhs)
        context['friends'] = friends
        for friend in friends:
            if friend.profile.owner.username == request.user.username:
                context['isFriend'] = True
                break
    except ObjectDoesNotExist:
        pass


def my_inbox(request, context):
    """Fetches all messages for the current inbox"""

    inbox = Inbox.objects.get(owner=request.user)
    inbox_messages = Messages.objects.filter(inbox=inbox).order_by('-date_added')
    context['inbox_messages'] = inbox_messages

