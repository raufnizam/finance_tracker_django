from django.urls import path
from . import views

urlpatterns = [
    path('', views.transactions_view, name='transactions'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('summary/', views.transaction_summary, name='transaction_summary'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('download_csv/', views.download_csv, name='download_csv'),  # Add this line
]
