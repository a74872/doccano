from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from examples.models import Discussion, Rule, RuleVote, DiscussionMessage, Example, DiscussionThreadMessage
from examples.serializers import DiscussionMessageSerializer, DiscussionSerializer, RuleSerializer, RuleVoteSerializer, DiscussionThreadMessageSerializer
from projects.models import Project, Member


class DiscussionListCreateAPI(generics.ListCreateAPIView):
    """
    GET  /v1/projects/{project_id}/examples/{example_id}/discussions/
    POST /v1/projects/{project_id}/examples/{example_id}/discussions/
    """
    serializer_class   = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_project(self):
        return Project.objects.get(pk=self.kwargs["project_id"])

    def _assert_member(self, project):
        if not Member.objects.filter(project=project, user=self.request.user).exists():
            raise PermissionDenied

    def get_queryset(self):
        project    = self._get_project()
        example_id = self.kwargs["example_id"]
        self._assert_member(project)
        return Discussion.objects.filter(project=project, example_id=example_id)

    def perform_create(self, serializer):
        project    = self._get_project()
        example_id = self.kwargs["example_id"]
        self._assert_member(project)
        serializer.save(project=project, example_id=example_id)


class DiscussionDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /v1/discussions/{pk}/
    PATCH  /v1/discussions/{pk}/
    DELETE /v1/discussions/{pk}/
    """
    queryset           = Discussion.objects.all()
    serializer_class   = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        proj = serializer.instance.project
        self._assert_member(proj)
        serializer.save()

    def perform_destroy(self, instance):
        self._assert_member(instance.project)
        instance.delete()

    def _assert_member(self, project):
        if not Member.objects.filter(project=project, user=self.request.user).exists():
            raise PermissionDenied


class RuleListCreateAPI(generics.ListCreateAPIView):
    """
    GET  /v1/discussions/{discussion_id}/rules/
    POST /v1/discussions/{discussion_id}/rules/
    """
    serializer_class   = RuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rule.objects.filter(discussion_id=self.kwargs["discussion_id"])

    def perform_create(self, serializer):
        serializer.save(discussion_id=self.kwargs["discussion_id"])


class RuleDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /v1/rules/{pk}/
    PATCH  /v1/rules/{pk}/
    DELETE /v1/rules/{pk}/
    """
    queryset           = Rule.objects.all()
    serializer_class   = RuleSerializer
    permission_classes = [permissions.IsAuthenticated]


class RuleVoteListCreateAPI(generics.ListCreateAPIView):
    """
    POST /v1/projects/<project>/discussion/examples/<example>/<discussion>/rules/<rule>/votes/
    """
    serializer_class   = RuleVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = None

    def perform_create(self, serializer):
        # usa rule_id da rota, NÃO do payload
        RuleVote.objects.update_or_create(
            rule_id = self.kwargs["rule_id"],
            user    = self.request.user,
            defaults = {"vote": serializer.validated_data.get("vote", True)
            }
        )


class DiscussionMessageCreateAPI(generics.ListCreateAPIView):
    """
    GET  /v1/projects/<project_id>/examples/<example_id>/discussion/
    POST /v1/projects/<project_id>/examples/<example_id>/discussion/  {text:"…"}
    """
    serializer_class   = DiscussionMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    # ───────────────── helpers ─────────────────
    def _project(self) -> Project:
        return Project.objects.get(pk=self.kwargs["project_id"])

    def _assert_member(self, project: Project):
        if not Member.objects.filter(project=project,
                                     user=self.request.user).exists():
            raise PermissionDenied("Not a member of this project")

    # ───────────────── queryset (GET) ─────────────────
    def get_queryset(self):
        project = self._project()
        self._assert_member(project)

        example_id = self.kwargs["example_id"]              # ← aqui!
        return (
            DiscussionMessage.objects
            .filter(project=project, example_id=example_id)
            .select_related("author")
            .order_by("-created_at")
        )

    # ───────────────── create (POST) ─────────────────
    def perform_create(self, serializer):
        project = self._project()
        self._assert_member(project)

        example_id = self.kwargs["example_id"]              # ← e aqui!
        example     = Example.objects.get(pk=example_id, project=project)

        serializer.save(
            project=project,
            example=example,
            author=self.request.user
        )

# examples/views/discussion.py
class DiscussionThreadMessageAPI(generics.ListCreateAPIView):
    """
    GET  /v1/discussions/<discussion_id>/messages/
    POST /v1/discussions/<discussion_id>/messages/   {text:"…"}
    """
    serializer_class   = DiscussionThreadMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = None

    # ───────── helpers ─────────
    def _discussion(self) -> Discussion:
        return Discussion.objects.select_related("project").get(
            pk=self.kwargs["discussion_id"]
        )

    def _assert_member(self, project: Project):
        if not Member.objects.filter(project=project,
                                     user=self.request.user).exists():
            raise PermissionDenied("Not a member of this project")

    # ───────── list (GET) ─────────
    def get_queryset(self):
        discussion = self._discussion()
        self._assert_member(discussion.project)
        return (
            DiscussionThreadMessage.objects
            .filter(discussion=discussion)
            .select_related("author")
            .order_by("-created_at")
        )

    # ───────── create (POST) ─────────
    def perform_create(self, serializer):
        discussion = self._discussion()
        self._assert_member(discussion.project)
        serializer.save(
            discussion=discussion,
            author=self.request.user
        )
