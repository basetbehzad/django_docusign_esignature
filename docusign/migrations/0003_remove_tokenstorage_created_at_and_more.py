# Generated by Django 5.1.3 on 2025-01-29 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docusign', '0002_tokenstorage_created_at_tokenstorage_user_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tokenstorage',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='tokenstorage',
            name='access_token',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='tokenstorage',
            name='refresh_token',
            field=models.CharField(max_length=1024),
        ),
    ]
