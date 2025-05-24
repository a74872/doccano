from rest_framework import serializers

from .models import Assignment, Comment, Example, ExampleState, DiscussionMessage, Discussion, Rule, RuleVote, DiscussionThreadMessage

class RuleVoteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model  = RuleVote
        fields = ("id", "rule", "user", "username",
                  "vote", "created_at", "updated_at")
        read_only_fields = ("id", "rule", "user",
                            "created_at", "updated_at")


class RuleSerializer(serializers.ModelSerializer):
    """Serializa cada regra dentro de uma discussão, incluindo contagem de votos."""
    votes = RuleVoteSerializer(many=True, read_only=True)
    yes_votes = serializers.IntegerField(source="votes.filter.vote.true.count", read_only=True)
    no_votes = serializers.IntegerField(source="votes.filter.vote.false.count", read_only=True)

    class Meta:
        model = Rule
        fields = (
            "id",
            "discussion",
            "title",
            "active",
            "created_at",
            "votes",
            "yes_votes",
            "no_votes",
        )
        read_only_fields = ("id", "discussion", "created_at", "votes", "yes_votes", "no_votes")


class DiscussionSerializer(serializers.ModelSerializer):
    """Serializa o tópico de discussão, com as suas regras embutidas."""
    rules = RuleSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = (
            "id",
            "title",
            "description",
            "is_resolved",
            "archived",
            "created_at",
            "updated_at",
            "rules",
        )
        read_only_fields = (
            "project",
            "example",
            "id",
            "created_at",
            "updated_at",
            "rules",
        )

class DiscussionMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model  = DiscussionMessage
        fields = (
            "id",
            "project",
            "example",
            "author",
            "username",
            "text",
            "created_at",
        )
        read_only_fields = ("id", "project", "author", "created_at")

class DiscussionThreadMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model  = DiscussionThreadMessage
        fields = (
            "id",
            "discussion",
            "author",
            "username",
            "text",
            "created_at",
        )
        read_only_fields = ("id", "discussion", "author", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "username",
            "example",
            "text",
            "created_at",
        )
        read_only_fields = ("user", "example")


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ("id", "assignee", "example", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ExampleSerializer(serializers.ModelSerializer):
    annotation_approver = serializers.SerializerMethodField()
    is_confirmed = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()

    @classmethod
    def get_annotation_approver(cls, instance):
        approver = instance.annotations_approved_by
        return approver.username if approver else None

    def get_is_confirmed(self, instance):
        user = self.context.get("request").user
        if instance.project.collaborative_annotation:
            states = instance.states.all()
        else:
            states = instance.states.filter(confirmed_by_id=user.id)
        return states.count() > 0

    def get_assignments(self, instance):
        return [
            {
                "id": assignment.id,
                "assignee": assignment.assignee.username,
                "assignee_id": assignment.assignee.id,
            }
            for assignment in instance.assignments.all()
        ]

    class Meta:
        model = Example
        fields = [
            "id",
            "filename",
            "meta",
            "annotation_approver",
            "comment_count",
            "text",
            "is_confirmed",
            "upload_name",
            "score",
            "assignments",
        ]
        read_only_fields = ["filename", "is_confirmed", "upload_name", "assignments"]


class ExampleStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleState
        fields = ("id", "example", "confirmed_by", "confirmed_at")
        read_only_fields = ("id", "example", "confirmed_by", "confirmed_at")
