from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group

def is_seller(user):
    return user.groups.filter(name='Selling').exists() or user.is_superuser

def is_admin(user):
    return user.is_superuser

