from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.


def validate_img(value):
    """Validation that checks the image URL and ensures it ends in jpg, jpeg, png"""

    approved = ['jpg', 'jpeg', 'png']
    if value[-4:].lower() not in approved:
        if value[-3:].lower() in approved:
            return
        raise ValidationError("Invalid Format! Formats Accepted: (.jpg, .jpeg, .png)")


class Profile(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    profile_img = models.CharField(validators=[validate_img], max_length=300,
                                   default="https://cdn.pixabay.com/photo/2015/10/05/22/37/"
                                           "blank-profile-picture-973460_960_720.png")
    display_name = models.CharField(max_length=30)
    bio = models.CharField(max_length=500, default="User has not created a Bio.")
    isFirstVisit = models.BooleanField(default=True)


class Inbox(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )


class Messages(models.Model):
    subject = models.CharField(max_length=100)
    body = models.CharField(max_length=100)
    inbox = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    sent_from = models.CharField(max_length=100)
    isRequest = models.BooleanField(default=False)
    isRead = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)


class FriendsList(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

class Friends(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    friends_list = models.ForeignKey(FriendsList, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.owner.username

