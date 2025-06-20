# Generated by Django 4.2.20 on 2025-05-23 19:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_rename_label_labelperspective'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('examples', '0013_discussion_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscussionMessageDiscussion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('example', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussion_messages_rules', to='examples.example')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussions_rules', to='projects.project')),
            ],
            options={
                'ordering': ['created_at'],
                'indexes': [models.Index(fields=['project', 'example', 'created_at'], name='examples_di_project_bcd854_idx')],
            },
        ),
    ]
