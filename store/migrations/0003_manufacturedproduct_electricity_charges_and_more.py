# Generated by Django 4.2.3 on 2023-08-12 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_material_remaining_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='manufacturedproduct',
            name='electricity_charges',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='manufacturedproduct',
            name='labor_charges',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='manufacturedproduct',
            name='other_expenses',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='manufacturedproduct',
            name='quantity_produced',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='manufacturedproduct',
            name='transport_charges',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
