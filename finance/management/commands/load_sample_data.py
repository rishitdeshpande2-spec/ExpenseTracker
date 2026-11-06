from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from finance.models import Category, Expense, Income, Budget


class Command(BaseCommand):
    help = "Load sample financial data for demo purposes"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")

    def handle(self, *args, **options):
        username = options["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(f"Created user '{username}' with password 'demo1234'")
        else:
            Expense.objects.filter(user=user).delete()
            Income.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()

        today = timezone.now().date()
        categories = {c.name: c for c in Category.objects.filter(user=user)}

        Income.objects.create(
            user=user, source="Salary", amount=Decimal("5000.00"),
            description="Monthly salary", date=today.replace(day=1),
        )
        Income.objects.create(
            user=user, source="Freelance", amount=Decimal("800.00"),
            description="Web project", date=today.replace(day=15),
        )

        sample_expenses = [
            ("Groceries", "45.99", "Weekly groceries"),
            ("Rent", "1500.00", "Monthly rent"),
            ("Utilities", "120.50", "Electric bill"),
            ("Transportation", "65.00", "Gas"),
            ("Entertainment", "35.00", "Movie night"),
            ("Dining Out", "28.75", "Lunch with friends"),
            ("Healthcare", "25.00", "Pharmacy"),
            ("Shopping", "89.99", "New shoes"),
        ]
        for cat_name, amount, desc in sample_expenses:
            Expense.objects.create(
                user=user,
                category=categories.get(cat_name),
                amount=Decimal(amount),
                description=desc,
                date=today,
            )

        for cat_name, amount in [("Groceries", "300"), ("Rent", "1500"), ("Entertainment", "150"), ("Dining Out", "200")]:
            if cat_name in categories:
                Budget.objects.get_or_create(
                    user=user,
                    category=categories[cat_name],
                    month=today.month,
                    year=today.year,
                    defaults={"amount": Decimal(amount), "alert_threshold": 80},
                )

        self.stdout.write(self.style.SUCCESS(f"Sample data loaded for user '{username}'"))
