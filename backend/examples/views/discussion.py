from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from examples.models import DiscussionMessage, Example
from examples.serializers import DiscussionMessageSerializer
from projects.models import Project, Member


class DiscussionListCreateAPI(generics.ListCreateAPIView):
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
