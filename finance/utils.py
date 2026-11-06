from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone

from .models import Budget, Expense, Income


def get_financial_summary(user, month=None, year=None):
    today = timezone.now().date()
    month = month or today.month
    year = year or today.year

    income_total = Income.objects.filter(
        user=user, date__month=month, date__year=year
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    expense_total = Expense.objects.filter(
        user=user, date__month=month, date__year=year
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    return {
        "month": month,
        "year": year,
        "total_income": income_total,
        "total_expenses": expense_total,
        "balance": income_total - expense_total,
    }


def get_category_breakdown(user, month=None, year=None):
    today = timezone.now().date()
    month = month or today.month
    year = year or today.year

    expenses = (
        Expense.objects.filter(user=user, date__month=month, date__year=year)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    return list(expenses)


def get_monthly_trends(user, months=6):
    today = timezone.now().date()
    trends = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        income = Income.objects.filter(
            user=user, date__month=m, date__year=y
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        expenses = Expense.objects.filter(
            user=user, date__month=m, date__year=y
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        trends.append(
            {
                "label": f"{y}-{m:02d}",
                "income": float(income),
                "expenses": float(expenses),
            }
        )
    return trends


def get_budget_alerts(user, month=None, year=None):
    today = timezone.now().date()
    month = month or today.month
    year = year or today.year

    alerts = []
    budgets = Budget.objects.filter(user=user, month=month, year=year).select_related(
        "category"
    )

    for budget in budgets:
        status = budget.alert_status
        if status in ("warning", "exceeded"):
            alerts.append(
                {
                    "budget": budget,
                    "status": status,
                    "message": (
                        f"You've exceeded your {budget.category.name} budget "
                        f"(₹{budget.spent:.2f} of ₹{budget.amount:.2f})"
                        if status == "exceeded"
                        else (
                            f"{budget.category.name} budget is at {budget.usage_percent}% "
                            f"(₹{budget.spent:.2f} of ₹{budget.amount:.2f})"
                        )
                    ),
                }
            )
    return alerts


def get_transaction_history(user, search="", category_id=None, tx_type=None):
    expenses = Expense.objects.filter(user=user).select_related("category")
    incomes = Income.objects.filter(user=user)

    if search:
        expenses = expenses.filter(description__icontains=search)
        incomes = incomes.filter(
            Q(source__icontains=search) | Q(description__icontains=search)
        )

    if category_id:
        expenses = expenses.filter(category_id=category_id)

    transactions = []
    for exp in expenses:
        transactions.append(
            {
                "id": exp.id,
                "type": "expense",
                "date": exp.date,
                "amount": exp.amount,
                "label": exp.description or exp.category.name if exp.category else "Uncategorized",
                "category": exp.category.name if exp.category else "Uncategorized",
                "category_color": exp.category.color if exp.category else "#94a3b8",
                "created_at": exp.created_at,
            }
        )
    for inc in incomes:
        transactions.append(
            {
                "id": inc.id,
                "type": "income",
                "date": inc.date,
                "amount": inc.amount,
                "label": inc.source,
                "category": inc.source,
                "category_color": "#22c55e",
                "created_at": inc.created_at,
            }
        )

    if tx_type == "expense":
        transactions = [t for t in transactions if t["type"] == "expense"]
    elif tx_type == "income":
        transactions = [t for t in transactions if t["type"] == "income"]

    transactions.sort(key=lambda t: (t["date"], t["created_at"]), reverse=True)
    return transactions
