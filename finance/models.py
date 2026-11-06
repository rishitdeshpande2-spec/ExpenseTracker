from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#6366f1")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="expenses"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.description or 'Expense'} - ₹{self.amount}"


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incomes")
    source = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.source} - ₹{self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="budgets"
    )
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    alert_threshold = models.PositiveSmallIntegerField(
        default=80,
        help_text="Alert when spending reaches this percentage of budget.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "category", "month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.category.name} - {self.month}/{self.year}"

    @property
    def spent(self):
        from django.db.models import Sum

        total = Expense.objects.filter(
            user=self.user,
            category=self.category,
            date__month=self.month,
            date__year=self.year,
        ).aggregate(total=Sum("amount"))["total"]
        return total or 0

    @property
    def remaining(self):
        return self.amount - self.spent

    @property
    def usage_percent(self):
        if self.amount == 0:
            return 100
        return round((self.spent / self.amount) * 100, 1)

    @property
    def alert_status(self):
        percent = self.usage_percent
        if percent >= 100:
            return "exceeded"
        if percent >= self.alert_threshold:
            return "warning"
        return "ok"
