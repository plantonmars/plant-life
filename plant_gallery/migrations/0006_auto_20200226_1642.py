# Generated by Django 3.0.3 on 2020-02-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant_gallery', '0005_bank_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='balance',
            field=models.IntegerField(default=0, max_length=10),
        ),
        migrations.AlterField(
            model_name='payment',
            name='zip',
            field=models.CharField(max_length=5),
        ),
    ]
