from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Budget, Category, Expense, Income


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Choose a username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Create a password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm your password"}
        )
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category name"}),
            "color": forms.TextInput(attrs={"class": "form-control form-control-color", "type": "color"}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "amount", "description", "date"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "What was this for?"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["source", "amount", "description", "date"]
        widgets = {
            "source": forms.TextInput(attrs={"class": "form-control", "placeholder": "Salary, freelance, etc."}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional notes"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["category", "month", "year", "amount", "alert_threshold"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "month": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "12"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "min": "2020", "max": "2100"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "alert_threshold": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "100"}),
        }
