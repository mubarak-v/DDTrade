# Generated by Django 5.1.3 on 2024-12-09 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('algo', '0003_delete_stocksignalresult'),
        ('main', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='StocksignalResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal', models.CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell'), ('NATURAL', 'Natural')], default='NATURAL', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='single_result', to='main.stock')),
                ('tradingAlgorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tradingAlgorithm_result', to='algo.tradingalgorithm')),
            ],
        ),
    ]