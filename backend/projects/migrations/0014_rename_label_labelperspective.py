# Generated by Django 4.2.20 on 2025-05-13 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_remove_perspective_data_type_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Label',
            new_name='LabelPerspective',
        ),
    ]
