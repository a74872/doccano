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


class Discussion(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="discussions_topics")
    example     = models.ForeignKey(Example, on_delete=models.CASCADE, related_name="discussions_topics")
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    archived    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({'Resolved' if self.is_resolved else 'Pending'})"


class Rule(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion  = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="rules")
    title       = models.CharField(max_length=255)
    active      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Rule: {self.title}"


class RuleVote(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule        = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="votes")
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rule_votes")
    vote        = models.BooleanField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("rule", "user"),)
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} → {'Yes' if self.vote else 'No'} on {self.rule.title}"


class DiscussionMessage(models.Model):

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project    = models.ForeignKey(Project, on_delete=models.CASCADE,
                                   related_name="discussions")
    example    = models.ForeignKey(Example, on_delete=models.CASCADE,
                                   related_name="discussion_messages")
    author     = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes  = [models.Index(fields=["project", "example", "created_at"])]

    def __str__(self):
        return f"{self.author} @ {self.created_at:%Y-%m-%d %H:%M}: {self.text[:30]}"

class DiscussionThreadMessage(models.Model):
    """
    Mensagens ligadas *directamente* a um tópico Discussion
    (não ao Example) – cada discussão guarda o seu próprio chat.
    """
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="messages"          #  discussion.messages.all()
    )
    author     = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes  = [models.Index(fields=["discussion", "created_at"])]

    def __str__(self):
        return f"{self.author} @ {self.created_at:%Y-%m-%d %H:%M}: {self.text[:30]}"


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
