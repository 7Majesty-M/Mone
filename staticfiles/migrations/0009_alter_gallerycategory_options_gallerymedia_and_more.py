# Generated by Django 5.1.5 on 2025-01-24 05:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_gallerycategory_galleryimage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gallerycategory',
            options={'verbose_name': 'Категория медиа', 'verbose_name_plural': 'Категории медиа'},
        ),
        migrations.CreateModel(
            name='GalleryMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('media_type', models.CharField(choices=[('image', 'Изображение'), ('video', 'Видео')], default='image', max_length=10, verbose_name='Тип медиа')),
                ('image', models.ImageField(blank=True, null=True, upload_to='gallery/images/', verbose_name='Изображение')),
                ('video', models.FileField(blank=True, null=True, upload_to='gallery/videos/', verbose_name='Видео')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='media', to='main.gallerycategory', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Медиа',
                'verbose_name_plural': 'Медиа',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.DeleteModel(
            name='GalleryImage',
        ),
    ]
