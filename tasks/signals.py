from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category   # relative import

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:  # # only when new user is created
        default_categories = [
            "Work",
            "Personal",
            "Shopping",
            "Health / Fitness",
            "Travel",
            "Finance / Bills",
        ]
        for name in default_categories:
            Category.objects.create(user=instance, name=name)