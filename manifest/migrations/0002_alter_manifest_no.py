# Generated by Django 4.1.5 on 2023-03-27 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manifest', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='no',
            field=models.CharField(default='', max_length=5),
        ),
    ]
