# Generated by Django 3.0.3 on 2020-02-26 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_gallery', '0006_auto_20200226_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]
