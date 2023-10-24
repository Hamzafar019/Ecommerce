# Generated by Django 4.2.3 on 2023-08-29 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_seller_remove_purchase_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='amount',
            new_name='amount_to_pay',
        ),
        migrations.AddField(
            model_name='payment',
            name='new_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='remaining',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.seller'),
        ),
        migrations.AddField(
            model_name='seller',
            name='remaining_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
