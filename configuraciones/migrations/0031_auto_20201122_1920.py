# Generated by Django 3.0.6 on 2020-11-22 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0030_auto_20201122_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospitales',
            name='rutaFotos',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
