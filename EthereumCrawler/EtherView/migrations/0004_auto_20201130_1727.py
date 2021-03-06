# Generated by Django 3.1.3 on 2020-11-30 16:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EtherView', '0003_auto_20201130_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='ETHBalanceLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=1000)),
                ('date', models.DateField(default=datetime.date.today)),
                ('balance', models.DecimalField(decimal_places=18, max_digits=30)),
            ],
        ),
        migrations.AlterField(
            model_name='transaction',
            name='value',
            field=models.DecimalField(decimal_places=18, max_digits=30),
        ),
    ]
