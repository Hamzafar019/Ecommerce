# Generated by Django 4.2.3 on 2023-09-03 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_sell_commissionvalue_sell_discountvalue_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sell',
            name='discountvalue',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]