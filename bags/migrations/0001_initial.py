# Generated by Django 4.1.5 on 2023-04-08 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bags_date', models.CharField(max_length=20)),
                ('port', models.CharField(default='', max_length=100)),
                ('bag_number', models.IntegerField(default=0)),
                ('hawb_no', models.CharField(max_length=20, unique=True)),
                ('checked', models.BooleanField(default=False)),
            ],
        ),
    ]
