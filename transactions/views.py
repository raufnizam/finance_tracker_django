from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from .forms import TransactionForm
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import csv
import os
from datetime import datetime
from django.http import HttpResponse
from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def plot_transactions(df):
    df.set_index("date", inplace=True)
    
    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expense over Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    line_plot_image = buf.getvalue()
    buf.close()

    line_plot_base64 = base64.b64encode(line_plot_image).decode('utf-8')

    # Pie chart
    total_income = income_df["amount"].sum()
    total_expense = expense_df["amount"].sum()
    net_income = max(total_income - total_expense, 0)  # Ensure net income is non-negative

    labels = ['Income', 'Expense', 'Net Income']
    sizes = [total_income, total_expense, net_income]
    colors = ['#66b3ff', '#ff9999', '#99ff99']

    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    pie_chart_image = buf.getvalue()
    buf.close()

    pie_chart_base64 = base64.b64encode(pie_chart_image).decode('utf-8')

    return line_plot_base64, pie_chart_base64


def transactions_view(request):
    transactions = Transaction.objects.all()
    if transactions.exists():
        df = pd.DataFrame(list(transactions.values('date', 'amount', 'category')))
        df['date'] = pd.to_datetime(df['date'])
        line_plot_image, pie_chart_image = plot_transactions(df)
    else:
        line_plot_image = None
        pie_chart_image = None

    return render(request, 'transactions/transactions.html', {
        'line_plot_image': line_plot_image,
        'pie_chart_image': pie_chart_image,
        'transactions': transactions
    })

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            save_to_csv(form.cleaned_data)
            return redirect('transactions')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})

def save_to_csv(data):
    file_exists = os.path.isfile('transactions.csv')
    with open('transactions.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['date', 'amount', 'category', 'description'])
        writer.writerow([data['date'], data['amount'], data['category'], data['description']])

def transaction_summary(request):
    plot_image = None
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            transactions = Transaction.objects.filter(date__range=[start_date, end_date])
            df = pd.DataFrame(list(transactions.values('date', 'amount', 'category')))
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                plot_image = plot_transactions(df)
                total_income = df[df['category'] == 'Income']['amount'].sum()
                total_expense = df[df['category'] == 'Expense']['amount'].sum()
                net_saving = total_income - total_expense
                summary = {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_saving': net_saving
                }
            else:
                summary = None
    else:
        form = DateRangeForm()
        summary = None
    return render(request, 'transactions/summary.html', {'summary': summary, 'form': form, 'plot_image': plot_image})

def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transactions')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'transactions/edit_transaction.html', {'form': form})

def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transactions')
    return render(request, 'transactions/delete_transaction.html', {'transaction': transaction})

from django.http import HttpResponse

def download_csv(request):
    transactions = Transaction.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['date', 'amount', 'category', 'description'])
    for transaction in transactions:
        writer.writerow([transaction.date, transaction.amount, transaction.category, transaction.description])

    return response
