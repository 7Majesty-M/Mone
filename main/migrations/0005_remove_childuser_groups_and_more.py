# Generated by Django 5.1.5 on 2025-01-22 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_parentuser_is_parent_only'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='childuser',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='childuser',
            name='user_permissions',
        ),
    ]
