from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import AnalyticsViewSet, BudgetViewSet, CategoryViewSet, ExpenseViewSet, IncomeViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="api-category")
router.register("expenses", ExpenseViewSet, basename="api-expense")
router.register("incomes", IncomeViewSet, basename="api-income")
router.register("budgets", BudgetViewSet, basename="api-budget")
router.register("analytics", AnalyticsViewSet, basename="api-analytics")

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/edit/", views.expense_edit, name="expense_edit"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    path("income/", views.income_list, name="income_list"),
    path("income/add/", views.income_create, name="income_create"),
    path("income/<int:pk>/edit/", views.income_edit, name="income_edit"),
    path("income/<int:pk>/delete/", views.income_delete, name="income_delete"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("budgets/", views.budget_list, name="budget_list"),
    path("budgets/add/", views.budget_create, name="budget_create"),
    path("budgets/<int:pk>/delete/", views.budget_delete, name="budget_delete"),
    path("transactions/", views.transaction_history, name="transactions"),
    path("reports/<str:format>/", views.download_report, name="download_report"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("api/", include(router.urls)),
]
