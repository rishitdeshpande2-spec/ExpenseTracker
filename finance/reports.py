import csv
import io
from datetime import datetime

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .utils import get_financial_summary, get_transaction_history


def export_csv(user, month=None, year=None):
    summary = get_financial_summary(user, month, year)
    transactions = get_transaction_history(user)

    if month and year:
        transactions = [
            t for t in transactions if t["date"].month == month and t["date"].year == year
        ]

    response = HttpResponse(content_type="text/csv")
    filename = f"finance_report_{summary['year']}_{summary['month']:02d}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Personal Expense Tracker Report"])
    writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    writer.writerow(["Financial Summary"])
    writer.writerow(["Total Income", f"₹{summary['total_income']:.2f}"])
    writer.writerow(["Total Expenses", f"₹{summary['total_expenses']:.2f}"])
    writer.writerow(["Balance", f"₹{summary['balance']:.2f}"])
    writer.writerow([])
    writer.writerow(["Date", "Type", "Category/Source", "Description", "Amount"])

    for tx in transactions:
        writer.writerow(
            [
                tx["date"].strftime("%Y-%m-%d"),
                tx["type"].title(),
                tx["category"],
                tx["label"],
                f"₹{tx['amount']:.2f}",
            ]
        )

    return response


def export_pdf(user, month=None, year=None):
    summary = get_financial_summary(user, month, year)
    transactions = get_transaction_history(user)

    if month and year:
        transactions = [
            t for t in transactions if t["date"].month == month and t["date"].year == year
        ]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Personal Expense Tracker Report", styles["Title"]))
    elements.append(
        Paragraph(
            f"Period: {summary['month']}/{summary['year']} | "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 20))

    summary_data = [
        ["Total Income", f"₹{summary['total_income']:.2f}"],
        ["Total Expenses", f"₹{summary['total_expenses']:.2f}"],
        ["Balance", f"₹{summary['balance']:.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[200, 150])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(Paragraph("Financial Summary", styles["Heading2"]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    tx_data = [["Date", "Type", "Category", "Amount"]]
    for tx in transactions[:50]:
        tx_data.append(
            [
                tx["date"].strftime("%Y-%m-%d"),
                tx["type"].title(),
                tx["category"],
                f"₹{tx['amount']:.2f}",
            ]
        )

    tx_table = Table(tx_data, colWidths=[90, 70, 180, 80])
    tx_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    elements.append(Paragraph("Transaction History", styles["Heading2"]))
    elements.append(tx_table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    filename = f"finance_report_{summary['year']}_{summary['month']:02d}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
