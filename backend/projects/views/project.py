from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.generics import UpdateAPIView
from projects.models import Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from projects.serializers import ProjectPolymorphicSerializer

from projects.models import Perspective
from projects.serializers import PerspectiveSerializer
from projects.models import PerspectiveResponse
from projects.serializers import PerspectiveResponseSerializer


class ProjectList(generics.ListCreateAPIView):
    serializer_class = ProjectPolymorphicSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ["name", "created_at", "created_by", "project_type"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [
                IsAuthenticated,
            ]
        else:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        return Project.objects.filter(role_mappings__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        project.add_admin()

    def delete(self, request, *args, **kwargs):
        delete_ids = request.data["ids"]
        projects = Project.objects.filter(
            role_mappings__user=self.request.user,
            role_mappings__role__name=settings.ROLE_PROJECT_ADMIN,
            pk__in=delete_ids,
        )
        # Todo: I want to use bulk delete.
        # But it causes the constraint error.
        # See https://github.com/django-polymorphic/django-polymorphic/issues/229
        for project in projects:
            project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectPolymorphicSerializer
    lookup_url_kwarg = "project_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]


class CloneProject(views.APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        cloned_project = project.clone()
        serializer = ProjectPolymorphicSerializer(cloned_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PerspectiveListCreateView(generics.ListCreateAPIView):
    serializer_class = PerspectiveSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["project"]
    ordering_fields = ["name"]
    ordering = ["name"]
    queryset = Perspective.objects.all()
    lookup_url_kwarg = "perspective_id"
    http_method_names = [
        "get",
        "post",
    ]

    def dispatch(self, request, *args, **kwargs):
        print(">>> dispatch chamado com kwargs:", kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        try:
            project_id = self.kwargs.get("project_id")
            print(">>> PerspectiveListCreateView: project_id recebido:", project_id)
            qs = Perspective.objects.filter(project_id=project_id)
            print(">>> Queryset count:", qs.count())
            return qs
        except Exception as e:
            print(">>> Erro em get_queryset:", e)
            raise e


    def get_queryset2(self):
        project_id = self.kwargs.get("project_id")
        print(">>> get_queryset chamado com project_id:", project_id)
        qs = Perspective.objects.filter(project_id=project_id)
        print(">>> queryset count:", qs.count())
        return qs

    def perform_create(self, serializer):
        try:
            project_id = self.kwargs.get("project_id")
            print(">>> perform_create: project_id recebido:", project_id)
            project = get_object_or_404(Project, pk=project_id)
            print(">>> perform_create: Projeto encontrado:", project)
            serializer.save(project=project, created_by=self.request.user)
            print(">>> perform_create: Perspectiva criada com sucesso")
        except Exception as e:
            print(">>> Erro em perform_create:", e)
            raise e



    def perform_destroy(self, instance):
        if instance.project.examples.exists():
            return Response(
                {"detail": "Cannot delete perspectives already in use."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        super().perform_destroy(instance)

class PerspectiveDetailView(RetrieveDestroyAPIView):
    serializer_class = PerspectiveSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]  # Ou ajuste conforme necessário
    queryset = Perspective.objects.all()
    lookup_url_kwarg = "perspective_id"

class PerspectiveEditView(UpdateAPIView):
    queryset = Perspective.objects.all()
    serializer_class = PerspectiveSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    lookup_url_kwarg = "perspective_id"
    http_method_names = ["put", "patch"]


class PerspectiveResponseCreateView(generics.CreateAPIView):
    """
    View para criar uma resposta para uma perspectiva.
    Um usuário só pode responder uma vez a cada perspectiva.
    """
    serializer_class = PerspectiveResponseSerializer
    permission_classes = [IsAuthenticated]
    queryset = PerspectiveResponse.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            # Se answers está presente, processa múltiplas respostas
            if isinstance(request.data.get('answers'), list):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                responses = serializer.save()
                # Serializa as respostas antes de retornar
                serialized = PerspectiveResponseSerializer(responses, many=True).data
                return Response(
                    {'success': True, 'detail': 'Respostas criadas com sucesso.', 'responses': serialized},
                    status=status.HTTP_201_CREATED
                )
            # Caso antigo: processa uma resposta só
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_queryset(self):
        perspective_id = self.kwargs.get('perspective_id')
        return PerspectiveResponse.objects.filter(
            perspective_id=perspective_id,
            user=self.request.user
        )


class PerspectiveResponseListView(generics.ListAPIView):
    """
    View para listar todas as respostas de uma perspectiva.
    Apenas administradores do projeto podem ver todas as respostas.
    """
    serializer_class = PerspectiveResponseSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    queryset = PerspectiveResponse.objects.all()

    def get_queryset(self):
        perspective_id = self.kwargs.get('perspective_id')
        return PerspectiveResponse.objects.filter(perspective_id=perspective_id)


class UserPerspectiveResponseView(generics.ListAPIView):
    serializer_class = PerspectiveResponseSerializer
    permission_classes = [IsAuthenticated]
    queryset = PerspectiveResponse.objects.all()

    def get_queryset(self):
        perspective_id = self.kwargs.get('perspective_id')
        return PerspectiveResponse.objects.filter(
            perspective_id=perspective_id,
            user=self.request.user
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data[0] if len(serializer.data) == 1 else serializer.data)

