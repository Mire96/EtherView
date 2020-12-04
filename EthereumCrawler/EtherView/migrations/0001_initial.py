# Generated by Django 3.1.3 on 2020-11-27 23:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=1000)),
                ('block', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=100)),
                ('reciever', models.CharField(max_length=100)),
                ('value', models.DecimalField(decimal_places=12, max_digits=19)),
                ('transaction_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EtherView.transactionlog')),
            ],
        ),
    ]