# Generated by Django 3.1.3 on 2020-12-02 16:09

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('EtherView', '0012_transaction_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='TokenBalanceLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Date format: %Y-%m-%d')),
                ('balance', models.DecimalField(decimal_places=18, max_digits=30)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='EtherView.account')),
            ],
        ),
    ]
