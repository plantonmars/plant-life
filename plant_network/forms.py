from django import forms
from . models import Profile, Messages, Friends
import urllib.request
from django.core.validators import validate_image_file_extension


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['display_name', 'profile_img', 'bio']
        labels = {'display_name': 'Display Name: ', 'profile_img': 'IMG_URL', 'bio': 'Bio'}
        widgets = {'bio': forms.Textarea(attrs={'cols': 40})}


class MessageForm(forms.ModelForm):

    send_to = forms.ModelChoiceField(queryset=Friends.objects.none())

    def __init__(self, user, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        qs = Friends.objects.filter(friends_list__owner__username=user.username)
        self.fields['send_to'].queryset = qs

    class Meta:
        model = Messages
        fields = ['send_to', 'subject', 'body']
        labels = {'send_to': 'To:', 'subject': 'Subject:', 'body': 'Body:'}
        widgets = {'body': forms.Textarea(attrs={'cols': 40})}


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Messages
        fields = ['subject', 'body']
        labels = {'subject': 'Subject:', 'body': 'Body:'}
        widgets = {'body': forms.Textarea(attrs={'cols': 40})}
