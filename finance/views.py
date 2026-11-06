import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BudgetForm, CategoryForm, ExpenseForm, IncomeForm, RegisterForm
from .models import Budget, Category, Expense, Income
from .reports import export_csv, export_pdf
from .utils import (
    get_budget_alerts,
    get_category_breakdown,
    get_financial_summary,
    get_monthly_trends,
    get_transaction_history,
)


def _get_period(request):
    today = timezone.now().date()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    return month, year


@login_required
def dashboard(request):
    month, year = _get_period(request)
    summary = get_financial_summary(request.user, month, year)
    breakdown = get_category_breakdown(request.user, month, year)
    trends = get_monthly_trends(request.user)
    alerts = get_budget_alerts(request.user, month, year)
    recent = get_transaction_history(request.user)[:10]

    context = {
        "summary": summary,
        "breakdown": breakdown,
        "breakdown_json": json.dumps(
            [
                {
                    "name": b["category__name"] or "Uncategorized",
                    "total": float(b["total"]),
                    "color": b["category__color"] or "#94a3b8",
                }
                for b in breakdown
            ]
        ),
        "trends_json": json.dumps(trends),
        "alerts": alerts,
        "recent_transactions": recent,
        "month": month,
        "year": year,
    }
    return render(request, "finance/dashboard.html", context)


@login_required
def expense_list(request):
    month, year = _get_period(request)
    expenses = Expense.objects.filter(
        user=request.user, date__month=month, date__year=year
    ).select_related("category")
    return render(
        request,
        "finance/expense_list.html",
        {"expenses": expenses, "month": month, "year": year},
    )


@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        form.fields["category"].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense recorded successfully.")
            return redirect("expense_list")
    else:
        form = ExpenseForm(initial={"date": timezone.now().date()})
        form.fields["category"].queryset = Category.objects.filter(user=request.user)
    return render(request, "finance/expense_form.html", {"form": form, "title": "Add Expense"})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        form.fields["category"].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated.")
            return redirect("expense_list")
    else:
        form = ExpenseForm(instance=expense)
        form.fields["category"].queryset = Category.objects.filter(user=request.user)
    return render(request, "finance/expense_form.html", {"form": form, "title": "Edit Expense"})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted.")
        return redirect("expense_list")
    return render(request, "finance/confirm_delete.html", {"object": expense, "type": "expense"})


@login_required
def income_list(request):
    month, year = _get_period(request)
    incomes = Income.objects.filter(
        user=request.user, date__month=month, date__year=year
    )
    return render(
        request,
        "finance/income_list.html",
        {"incomes": incomes, "month": month, "year": year},
    )


@login_required
def income_create(request):
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income recorded successfully.")
            return redirect("income_list")
    else:
        form = IncomeForm(initial={"date": timezone.now().date()})
    return render(request, "finance/income_form.html", {"form": form, "title": "Add Income"})


@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == "POST":
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, "Income updated.")
            return redirect("income_list")
    else:
        form = IncomeForm(instance=income)
    return render(request, "finance/income_form.html", {"form": form, "title": "Edit Income"})


@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == "POST":
        income.delete()
        messages.success(request, "Income deleted.")
        return redirect("income_list")
    return render(request, "finance/confirm_delete.html", {"object": income, "type": "income"})


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, "finance/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Category created.")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(
        request, "finance/category_form.html", {"form": form, "title": "Add Category"}
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("category_list")
    return render(
        request, "finance/confirm_delete.html", {"object": category, "type": "category"}
    )


@login_required
def budget_list(request):
    month, year = _get_period(request)
    budgets = Budget.objects.filter(
        user=request.user, month=month, year=year
    ).select_related("category")
    return render(
        request,
        "finance/budget_list.html",
        {"budgets": budgets, "month": month, "year": year},
    )


@login_required
def budget_create(request):
    if request.method == "POST":
        form = BudgetForm(request.POST)
        form.fields["category"].queryset = Category.objects.filter(user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget set successfully.")
            return redirect("budget_list")
    else:
        today = timezone.now().date()
        form = BudgetForm(initial={"month": today.month, "year": today.year})
        form.fields["category"].queryset = Category.objects.filter(user=request.user)
    return render(request, "finance/budget_form.html", {"form": form, "title": "Set Budget"})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        budget.delete()
        messages.success(request, "Budget deleted.")
        return redirect("budget_list")
    return render(request, "finance/confirm_delete.html", {"object": budget, "type": "budget"})


@login_required
def transaction_history(request):
    search = request.GET.get("search", "")
    category_id = request.GET.get("category")
    tx_type = request.GET.get("type")
    categories = Category.objects.filter(user=request.user)
    transactions = get_transaction_history(request.user, search, category_id, tx_type)
    return render(
        request,
        "finance/transactions.html",
        {
            "transactions": transactions,
            "categories": categories,
            "search": search,
            "selected_category": category_id,
            "selected_type": tx_type,
        },
    )


@login_required
def download_report(request, format):
    month, year = _get_period(request)
    if format == "csv":
        return export_csv(request.user, month, year)
    return export_pdf(request.user, month, year)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "finance/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("register")


class CustomLoginView(LoginView):
    template_name = "finance/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or "/"
