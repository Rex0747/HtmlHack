# Generated by Django 2.2.7 on 2020-01-25 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0005_auto_20200125_1748'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='configurations',
            index_together={('modulo', 'estanteria')},
        ),
    ]
