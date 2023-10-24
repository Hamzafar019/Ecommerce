# Generated by Django 4.2.3 on 2023-09-04 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_rename_totalpayment_agentcommission_totalamount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentcommission',
            name='buyerdiscount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='buyerpayments',
            name='buyerdiscount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
