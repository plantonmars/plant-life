from django.urls import path

from . import views

app_name = 'plant_network'

urlpatterns = [
    path('profile/edit', views.edit_profile, name="edit_profile"),
    path('profile/<str:user_id>', views.profile, name="profile"),
    path('request_sent/<str:user_id>/', views.request_sent, name="request_sent"),
    path('message/<int:message_id>/', views.message, name="message"),
    path('messages/', views.messages, name="messages"),
    path('unfriend/<str:user_id>', views.unfriend, name="unfriend"),
    path('messages/new/', views.compose_message, name="compose_message"),
    path('messages/replyto/<int:message_id>', views.reply, name="reply"),
]