from django.db import models

class Transaction(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    category = models.CharField(max_length=10, choices=[('Income', 'Income'), ('Expense', 'Expense')])
    description = models.TextField()

    def __str__(self):
        return f"{self.date} - {self.category}: ${self.amount}"
