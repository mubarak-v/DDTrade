# Generated by Django 5.1.3 on 2024-11-17 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('yfinance_name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yfinance_name', models.CharField(max_length=50, unique=True)),
                ('closing_price', models.BooleanField(max_length=10)),
                ('percentage_change', models.DecimalField(decimal_places=2, max_digits=5)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]