# Generated by Django 2.2.7 on 2020-01-25 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='articulos',
            fields=[
                ('idsel', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(max_length=5, unique=True)),
                ('nombre', models.CharField(max_length=90)),
                ('cbarras', models.CharField(max_length=50)),
                ('cbarras2', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='gfhs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('gfh', models.CharField(max_length=4, unique=True)),
                ('nombre', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='dispositivos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=5, unique=True)),
                ('gfh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='configuraciones.gfhs')),
            ],
        ),
        migrations.CreateModel(
            name='configurations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modulo', models.CharField(max_length=2)),
                ('estanteria', models.CharField(max_length=2)),
                ('ubicacion', models.CharField(max_length=5)),
                ('division', models.CharField(max_length=1)),
                ('codigo', models.CharField(max_length=6)),
                ('pacto', models.FloatField()),
                ('minimo', models.FloatField()),
                ('dc', models.CharField(max_length=2)),
                ('gfh', models.CharField(max_length=8)),
                ('disp', models.CharField(max_length=6)),
                ('nombre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='configuraciones.articulos')),
            ],
            options={
                'unique_together': {('modulo', 'estanteria', 'ubicacion', 'division', 'disp')},
            },
        ),
    ]
