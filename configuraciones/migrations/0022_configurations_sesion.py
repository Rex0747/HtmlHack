# Generated by Django 3.0.6 on 2020-11-11 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0021_auto_20201111_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurations',
            name='sesion',
            field=models.CharField(default=False, max_length=8),
        ),
    ]
