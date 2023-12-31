# Generated by Django 4.2.3 on 2023-09-03 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_alter_manufacturedproduct_total_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, default=None, max_length=200)),
                ('remaining_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='ProductSale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.manufacturedproduct')),
            ],
        ),
        migrations.CreateModel(
            name='Sell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selling_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('price_after_discount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.buyer')),
                ('discount', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.discountcode')),
                ('products', models.ManyToManyField(through='store.ProductSale', to='store.manufacturedproduct')),
            ],
        ),
        migrations.AddField(
            model_name='productsale',
            name='sell',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.sell'),
        ),
    ]
