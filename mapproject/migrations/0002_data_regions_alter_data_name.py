# Generated by Django 4.1.7 on 2023-08-03 15:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mapproject', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='regions',
            field=models.DateTimeField(default=django.utils.timezone.now, max_length=20, verbose_name='Name search'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='data',
            name='name',
            field=models.DateTimeField(max_length=20, verbose_name='Name search'),
        ),
    ]
