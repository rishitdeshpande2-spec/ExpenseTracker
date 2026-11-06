from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Category

DEFAULT_CATEGORIES = [
    ("Groceries", "#22c55e"),
    ("Rent", "#ef4444"),
    ("Utilities", "#f59e0b"),
    ("Transportation", "#3b82f6"),
    ("Entertainment", "#a855f7"),
    ("Healthcare", "#ec4899"),
    ("Shopping", "#14b8a6"),
    ("Dining Out", "#f97316"),
]


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        Category.objects.bulk_create(
            [
                Category(user=instance, name=name, color=color)
                for name, color in DEFAULT_CATEGORIES
            ]
        )
