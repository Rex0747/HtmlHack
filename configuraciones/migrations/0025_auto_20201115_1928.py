# Generated by Django 3.0.6 on 2020-11-15 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0024_auto_20201115_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configurations',
            name='nconfig',
            field=models.CharField(max_length=8),
        ),
    ]
