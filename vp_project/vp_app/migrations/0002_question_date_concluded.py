# Generated by Django 2.2.3 on 2019-10-09 02:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vp_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='date_concluded',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
