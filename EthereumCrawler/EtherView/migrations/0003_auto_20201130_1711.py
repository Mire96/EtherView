# Generated by Django 3.1.3 on 2020-11-30 16:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EtherView', '0002_transactionlog_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionlog',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
