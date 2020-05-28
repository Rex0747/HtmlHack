# Generated by Django 2.2.7 on 2020-01-25 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0004_auto_20200125_1738'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='configurations',
            unique_together=set(),
        ),
        migrations.AlterIndexTogether(
            name='configurations',
            index_together={('modulo', 'estanteria', 'ubicacion', 'division', 'disp')},
        ),
    ]
