from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Budget, Category, Expense, Income
from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    ExpenseSerializer,
    IncomeSerializer,
)
from .utils import (
    get_budget_alerts,
    get_category_breakdown,
    get_financial_summary,
    get_monthly_trends,
    get_transaction_history,
)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user).select_related("category")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        category = self.request.query_params.get("category")
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Income.objects.filter(user=self.request.user)
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Budget.objects.filter(user=self.request.user).select_related("category")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        summary = get_financial_summary(
            request.user,
            int(month) if month else None,
            int(year) if year else None,
        )
        return Response(
            {
                "total_income": str(summary["total_income"]),
                "total_expenses": str(summary["total_expenses"]),
                "balance": str(summary["balance"]),
                "month": summary["month"],
                "year": summary["year"],
            }
        )

    @action(detail=False, methods=["get"])
    def category_breakdown(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        data = get_category_breakdown(
            request.user,
            int(month) if month else None,
            int(year) if year else None,
        )
        return Response(
            [
                {
                    "category": item["category__name"] or "Uncategorized",
                    "color": item["category__color"] or "#94a3b8",
                    "total": str(item["total"]),
                }
                for item in data
            ]
        )

    @action(detail=False, methods=["get"])
    def trends(self, request):
        months = int(request.query_params.get("months", 6))
        return Response(get_monthly_trends(request.user, months))

    @action(detail=False, methods=["get"])
    def alerts(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        alerts = get_budget_alerts(
            request.user,
            int(month) if month else None,
            int(year) if year else None,
        )
        return Response(
            [
                {
                    "category": a["budget"].category.name,
                    "status": a["status"],
                    "message": a["message"],
                    "spent": str(a["budget"].spent),
                    "budget": str(a["budget"].amount),
                    "usage_percent": a["budget"].usage_percent,
                }
                for a in alerts
            ]
        )

    @action(detail=False, methods=["get"])
    def transactions(self, request):
        search = request.query_params.get("search", "")
        category_id = request.query_params.get("category")
        tx_type = request.query_params.get("type")
        txs = get_transaction_history(request.user, search, category_id, tx_type)
        return Response(
            [
                {
                    "id": t["id"],
                    "type": t["type"],
                    "date": t["date"].isoformat(),
                    "amount": str(t["amount"]),
                    "label": t["label"],
                    "category": t["category"],
                }
                for t in txs
            ]
        )
