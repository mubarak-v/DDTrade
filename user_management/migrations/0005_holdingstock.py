# Generated by Django 5.1.3 on 2024-11-29 17:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_stock_id'),
        ('user_management', '0004_alter_transactiondetails_transaction_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='HoldingStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(max_length=20000)),
                ('average_price', models.DecimalField(blank=True, decimal_places=4, max_digits=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell'), ('complete', 'Complete')], default='buy', max_length=20)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.stock')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.wallet')),
            ],
        ),
    ]