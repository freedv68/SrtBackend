# Generated by Django 4.1.5 on 2023-04-27 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bags', '0008_bagcheckhawbno'),
    ]

    operations = [
        migrations.AddField(
            model_name='bagcheckhawbno',
            name='checked',
            field=models.BooleanField(default=False),
        ),
    ]
