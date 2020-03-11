# Generated by Django 3.0.3 on 2020-02-27 21:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('plant_network', '0002_friends_friendslist_inbox'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendsList',
            fields=[
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('friend_pic', models.CharField(max_length=450)),
                ('friends_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plant_network.FriendsList')),
            ],
        ),
    ]
