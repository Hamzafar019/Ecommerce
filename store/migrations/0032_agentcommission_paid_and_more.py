# Generated by Django 4.2.3 on 2023-09-04 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_agentcommission'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentcommission',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='agentcommission',
            name='commission',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='agentcommission',
            name='orderid',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]