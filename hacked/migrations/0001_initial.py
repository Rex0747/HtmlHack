# Generated by Django 2.2.7 on 2019-12-29 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='datos',
            fields=[
                ('idsel', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre_pagina', models.CharField(max_length=10)),
                ('titulo', models.CharField(max_length=30)),
                ('titulo_cont', models.CharField(max_length=20)),
                ('dato', models.TextField()),
                ('page', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='enlaces',
            fields=[
                ('idsel', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('link', models.CharField(max_length=100)),
            ],
        ),
    ]
