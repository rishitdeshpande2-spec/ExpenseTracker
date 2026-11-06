# Personal Expense Tracker & Budget Planner

A full-featured Django web application for tracking personal finances, setting monthly budgets, and analyzing spending patterns.

## Features

- **Expense Recording** — Log expenses with amount, category, date, and description
- **Income Tracking** — Record income from multiple sources
- **Expense Categories** — Organize spending with customizable categories and colors
- **Monthly Budgets** — Set spending limits per category for each month
- **Budget Alerts** — Visual warnings when spending reaches 80%+ or exceeds budget
- **Analytics Dashboard** — Charts showing income vs expenses and category breakdown
- **Downloadable Reports** — Export financial data as CSV or PDF
- **Financial Summary** — View total income, expenses, and balance at a glance
- **Transaction History** — Searchable, filterable list of all transactions
- **REST APIs** — Full API for mobile/integration use

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a user account (or use Sign Up at http://127.0.0.1:8000/register/)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** and log in with your credentials.

## REST API Endpoints

All API endpoints require authentication (session or basic auth).

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/categories/` | GET, POST | List/create categories |
| `/api/categories/{id}/` | GET, PUT, PATCH, DELETE | Category detail |
| `/api/expenses/` | GET, POST | List/create expenses |
| `/api/expenses/{id}/` | GET, PUT, PATCH, DELETE | Expense detail |
| `/api/incomes/` | GET, POST | List/create income |
| `/api/incomes/{id}/` | GET, PUT, PATCH, DELETE | Income detail |
| `/api/budgets/` | GET, POST | List/create budgets |
| `/api/budgets/{id}/` | GET, PUT, PATCH, DELETE | Budget detail |
| `/api/analytics/summary/` | GET | Financial summary |
| `/api/analytics/category_breakdown/` | GET | Spending by category |
| `/api/analytics/trends/` | GET | Monthly income/expense trends |
| `/api/analytics/alerts/` | GET | Budget alerts |
| `/api/analytics/transactions/` | GET | Transaction history |

### Query Parameters

- Expenses/Incomes: `?month=5&year=2026&category=1`
- Analytics: `?month=5&year=2026`
- Trends: `?months=6`
- Transactions: `?search=grocery&type=expense&category=1`

### Example API Usage

```bash
# Get financial summary
curl -u username:password http://127.0.0.1:8000/api/analytics/summary/

# Create an expense
curl -u username:password -X POST http://127.0.0.1:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{"category": 1, "amount": "45.99", "description": "Groceries", "date": "2026-05-30"}'
```

## Project Structure

```
expense_tracker/     # Django project settings
finance/             # Main application
  models.py          # Category, Expense, Income, Budget
  views.py           # Web interface views
  api_views.py       # REST API viewsets
  utils.py           # Analytics and alert helpers
  reports.py         # CSV/PDF export
  templates/         # HTML templates
```

## Tech Stack

- Django 6
- Django REST Framework
- SQLite (default)
- Chart.js (dashboard charts)
- ReportLab (PDF generation)
- Bootstrap 5 (UI)
