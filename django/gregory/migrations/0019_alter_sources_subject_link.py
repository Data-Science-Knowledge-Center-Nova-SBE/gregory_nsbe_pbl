# Generated by Django 4.0.4 on 2022-08-06 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gregory', '0018_sources_subject_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sources',
            name='subject_link',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gregory.subject'),
        ),
    ]
