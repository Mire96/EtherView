# Generated by Django 3.1.3 on 2020-12-01 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('EtherView', '0007_remove_transaction_time_stamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_log',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='EtherView.transactionlog'),
        ),
    ]
