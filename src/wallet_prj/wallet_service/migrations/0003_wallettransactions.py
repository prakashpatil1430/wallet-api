# Generated by Django 5.0 on 2023-12-17 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet_service', '0002_walletdetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_id', models.CharField(blank=True, max_length=150, null=True)),
                ('withdrawn_by', models.TextField(blank=True, max_length=150, null=True)),
                ('deposited_by', models.TextField(blank=True, max_length=150, null=True)),
                ('amount', models.FloatField(default=0.0)),
                ('deposited_at', models.DateTimeField(blank=True, null=True)),
                ('withdrawn_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_transactions_user', to='wallet_service.customer')),
                ('wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wallet_details', to='wallet_service.walletdetails')),
            ],
            options={
                'db_table': 'wallet_transactions',
            },
        ),
    ]