# Generated by Django 4.2.3 on 2023-09-03 20:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_buyer_discountcode_productsale_sell_productsale_sell'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sell',
            name='price_after_discount',
        ),
        migrations.AlterField(
            model_name='discountcode',
            name='code',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='discountcode',
            name='discount_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='sell',
            name='discount',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.discountcode'),
        ),
    ]
