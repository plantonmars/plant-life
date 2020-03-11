from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

"""Validations for Payment Model"""


def validate_card_number(value):

    validate_num(value, 16, "Card Number must be 16 digits long.", "Please enter a valid number.")


def validate_security(value):

    validate_num(value, 3, "Security Code must be 3 digits long.", "Please enter a valid number.")


def validate_month(value):

    validate_num(value, 2,  "Exp. Month must be 2 digits long, requires trailing zero.", "Please enter a valid number.")

    if int(value) > 12:
        raise ValidationError("A valid month is from 01-12.")


def validate_year(value):

    validate_num(value, 4, "Exp. Year must be 4 digits long.", "Please enter a valid number.")

    if int(value) > 2030:
        raise ValidationError("Exp. year must not exceed 2030.")
    elif int(value) <= 2019:
        raise ValidationError("Exp. year has been surpassed, please enter a valid year.")


def validate_zip(value):

    validate_num(value, 5, "Zip code must be 5 digits long.", "Please enter a valid number.")


def validate_num(value, min_length, len_err, num_err):
    try:
        int(value)
        isNumber = True
    except:
        isNumber = False

    if len(value) != min_length and not isNumber:
        raise ValidationError(len_err + "\n" + num_err)
    elif len(value) != min_length:
        raise ValidationError(len_err)
    elif not isNumber:
        raise ValidationError(num_err)
    return


"""Payment Validations END"""


class Lighting(models.Model):
    """The lighting conditions that the plant thrives in"""
    lighting_condition = models.CharField(max_length=30)

    def __str__(self):
        return self.lighting_condition


class Type(models.Model):
    """The type of the plant"""
    plant_type = models.CharField(max_length=50)

    def __str__(self):
        return self.plant_type


class Plant(models.Model):
    # Foreign Keys
    lighting = models.ForeignKey(Lighting, on_delete=models.CASCADE)
    plant_type = models.ForeignKey(Type, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # Attributes
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=15)
    description = models.TextField(max_length=450)
    img_url = models.CharField(max_length=300)
    # Attributes w/ Default Values
    cost = models.IntegerField(default=0)
    for_sale = models.BooleanField(default=False)
    level = models.IntegerField(default=1)
    exp = models.IntegerField(default=0)
    max_exp = models.IntegerField(default=500)
    max_level = models.IntegerField(default=5)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    first_name = models.CharField(max_length=15, validators=[RegexValidator(regex='^[a-zA-Z]*$',
                                                                            message="Please enter alphabetic "
                                                                                    "characters only.")])
    last_name = models.CharField(max_length=15, validators=[RegexValidator(regex='^[a-zA-Z]*$',
                                                                            message="Please enter alphabetic "
                                                                                    "characters only.")])
    card_number = models.CharField(max_length=16, validators=[validate_card_number])
    security_code = models.CharField(max_length=3, validators=[validate_security])
    exp_month = models.CharField(max_length=2, validators=[validate_month])
    exp_year = models.CharField(max_length=4, validators=[validate_year])
    zip = models.CharField(max_length=5, validators=[validate_zip])
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=10, default=0)
    date_added = models.DateTimeField(auto_now_add=True)


class Bank(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    balance = models.IntegerField(default=35)





