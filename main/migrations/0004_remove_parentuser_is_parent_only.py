# Generated by Django 5.1.5 on 2025-01-21 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_parentuser_groups_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parentuser',
            name='is_parent_only',
        ),
    ]
