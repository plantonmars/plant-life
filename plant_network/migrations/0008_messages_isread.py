# Generated by Django 3.0.3 on 2020-03-03 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_network', '0007_profile_isfirstvisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='isRead',
            field=models.BooleanField(default=False),
        ),
    ]
