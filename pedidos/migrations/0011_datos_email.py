# Generated by Django 3.0.6 on 2020-10-20 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0010_pedidos_ident_dc'),
    ]

    operations = [
        migrations.CreateModel(
            name='datos_email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ucorreo', models.EmailField(max_length=50)),
            ],
        ),
    ]
