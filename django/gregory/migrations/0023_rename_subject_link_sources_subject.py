# Generated by Django 4.0.4 on 2022-08-06 16:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gregory', '0022_remove_sources_subject'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sources',
            old_name='subject_link',
            new_name='subject',
        ),
    ]
