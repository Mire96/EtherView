# Generated by Django 3.1.3 on 2020-11-30 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EtherView', '0005_transaction_time_stamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionlog',
            name='date',
        ),
    ]
