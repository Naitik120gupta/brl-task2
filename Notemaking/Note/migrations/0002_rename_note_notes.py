# Generated by Django 5.1.2 on 2024-10-16 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Note', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Note',
            new_name='Notes',
        ),
    ]