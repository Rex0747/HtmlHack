# Generated by Django 2.2.7 on 2020-01-25 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0006_auto_20200125_1811'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='configurations',
            index_together={('modulo', 'estanteria', 'ubicacion', 'division', 'disp')},
        ),
    ]
