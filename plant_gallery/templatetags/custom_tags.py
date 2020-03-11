from django import template
register = template.Library()

from ..models import Bank
from plant_network.models import Messages

@register.filter
def current_balance(user_id):
    current_bank = Bank.objects.get(owner=user_id)
    return current_bank.balance

@register.filter
def unread(user_id):
    unread_messages = Messages.objects.filter(inbox__owner=user_id, isRead=False).count()
    return unread_messages

