import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django_drf_filepond.models import DrfFilePondStoredStorage

from .managers import ExampleManager, ExampleStateManager
from projects.models import Project


class Example(models.Model):
    objects = ExampleManager()

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True)
    meta = models.JSONField(default=dict)
    filename = models.FileField(default=".", max_length=1024, storage=DrfFilePondStoredStorage())
    upload_name = models.CharField(max_length=512)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="examples")
    annotations_approved_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    score = models.FloatField(default=100)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # guarda o que cada usuário marcou: { user_id: "<label>" }
    labels_by_user = models.JSONField(
        default=dict,
        blank=True,
        help_text="Mapa de user_id → label aplicado a este exemplo"
    )

    # True se algum par de valores em labels_by_user for diferente
    has_discrepancy = models.BooleanField(
        default=False,
        help_text="Flag indicando se houve divergência entre labels de usuários"
    )

    # contagem bruta de cada label, ex: { "positivo": 9, "negativo": 1 }
    label_counts = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contagem de votos por label"
    )

    # percentual de cada label: { "positivo": 90.0, "negativo": 10.0 }
    label_percentages = models.JSONField(
        default=dict,
        blank=True,
        help_text="Percentual de votos por label"
    )

    @property
    def comment_count(self):
        return Comment.objects.filter(example=self.id).count()

    @property
    def data(self):
        if self.project.is_text_project:
            return self.text
        else:
            return str(self.filename)

    class Meta:
        ordering = ["created_at"]


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="assignments")
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="assignments")
    assignee = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("example", "assignee"),)

    def clean(self):
        # assignee must be a member of the project
        if not self.project.members.filter(id=self.assignee.id).exists():
            raise ValidationError("Assignee must be a member of the project")

        # example must be in the project
        if not self.project.examples.filter(id=self.example.id).exists():
            raise ValidationError("Example must be in the project")

        return super().clean()


class ExampleState(models.Model):
    objects = ExampleStateManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="states")
    confirmed_by = models.ForeignKey(to=User, on_delete=models.CASCADE)
    confirmed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("example", "confirmed_by"),)


class Comment(models.Model):
    text = models.TextField()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        return self.user.username

    class Meta:
        ordering = ["created_at"]
