from django.contrib import admin

from .models import Budget, Category, Expense, Income


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color", "created_at"]
    list_filter = ["user"]
    search_fields = ["name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "user", "date"]
    list_filter = ["date", "category", "user"]
    search_fields = ["description"]


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ["source", "amount", "user", "date"]
    list_filter = ["date", "user"]
    search_fields = ["source", "description"]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["category", "amount", "month", "year", "user", "alert_threshold"]
    list_filter = ["year", "month", "user"]
