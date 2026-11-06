from rest_framework import serializers

from .models import Budget, Category, Expense, Income


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "color", "created_at"]
        read_only_fields = ["created_at"]


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "category",
            "category_name",
            "amount",
            "description",
            "date",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ["id", "source", "amount", "description", "date", "created_at"]
        read_only_fields = ["created_at"]


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    usage_percent = serializers.FloatField(read_only=True)
    alert_status = serializers.CharField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "category_name",
            "month",
            "year",
            "amount",
            "alert_threshold",
            "spent",
            "remaining",
            "usage_percent",
            "alert_status",
            "created_at",
        ]
        read_only_fields = ["created_at"]
