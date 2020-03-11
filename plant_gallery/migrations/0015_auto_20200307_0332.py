# Generated by Django 3.0.3 on 2020-03-07 03:32

from django.db import migrations, models
import plant_gallery.models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_gallery', '0014_auto_20200307_0319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='security_code',
            field=models.CharField(max_length=3, validators=[plant_gallery.models.validate_security]),
        ),
    ]
