# Generated by Django 3.0.6 on 2021-01-13 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0013_auto_20210112_1901'),
    ]

    operations = [
        migrations.CreateModel(
            name='addRefPedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ubicacion', models.CharField(max_length=12)),
                ('codigo', models.CharField(max_length=6)),
                ('nombre', models.CharField(max_length=100)),
                ('pacto', models.IntegerField()),
                ('dc', models.CharField(max_length=1)),
                ('gfh', models.CharField(max_length=4)),
                ('disp', models.CharField(max_length=6)),
                ('hospital', models.CharField(max_length=4)),
            ],
        ),
    ]
