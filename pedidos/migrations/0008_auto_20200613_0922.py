# Generated by Django 3.0.6 on 2020-06-13 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0007_pedidos_temp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='correo',
            field=models.EmailField(max_length=50),
        ),
        migrations.AlterField(
            model_name='usuarios',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
    ]
