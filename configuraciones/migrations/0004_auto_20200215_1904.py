# Generated by Django 2.2.7 on 2020-02-15 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0003_auto_20200215_0848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configurations',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
