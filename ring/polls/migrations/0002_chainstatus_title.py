# Generated by Django 5.0 on 2023-12-14 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chainstatus',
            name='title',
            field=models.CharField(max_length=50, null='true'),
            preserve_default='true',
        ),
    ]