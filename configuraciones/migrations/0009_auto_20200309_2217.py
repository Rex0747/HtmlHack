# Generated by Django 2.2.7 on 2020-03-09 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuraciones', '0008_auto_20200218_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='articulos',
            name='foto',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='gfhs',
            unique_together={('gfh', 'nombre')},
        ),
    ]
