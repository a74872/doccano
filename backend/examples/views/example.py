from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from examples.filters import ExampleFilter
from examples.models import Example
from examples.serializers import ExampleSerializer
from projects.models import Member, Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly


class ExampleList(generics.ListCreateAPIView):
    serializer_class = ExampleSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ("created_at", "updated_at", "score")
    search_fields = ("text", "filename")
    model = Example
    filterset_class = ExampleFilter

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_queryset(self):
        member = get_object_or_404(Member, project=self.project, user=self.request.user)
        
        # Admins see all examples
        if member.is_admin():
            return self.model.objects.filter(project=self.project)

        # For non-admins (annotators and annotation approvers)
        base_queryset = self.model.objects.filter(project=self.project)
        
        # First, try to get examples assigned to this user
        assigned_queryset = base_queryset.filter(assignments__assignee=self.request.user)
        
        # If user has specific assignments, return only those
        if assigned_queryset.exists():
            queryset = assigned_queryset
            if self.project.random_order:
                queryset = queryset.order_by("assignments__id")
            return queryset
        
        # If no specific assignments exist, check the user's role
        if member.is_annotator():
            # For annotators without assignments, show all unassigned examples
            # or all examples if no assignment system is being used
            unassigned_queryset = base_queryset.filter(assignments__isnull=True)
            
            if unassigned_queryset.exists():
                # Show unassigned examples
                return unassigned_queryset
            else:
                # No assignment system in use, show all examples
                return base_queryset
                
        elif member.is_annotation_approver():
            # Annotation approvers can see examples that need approval
            # This might include examples that have been annotated but not approved
            
            # Try to get examples that need approval
            needs_approval_queryset = base_queryset.filter(
                # Add your logic for examples needing approval
                # For example: annotations__approved=False
                # Or: status='pending_approval'
            )
            
            if needs_approval_queryset.exists():
                return needs_approval_queryset
            else:
                # Fallback: show all examples for approval review
                return base_queryset
        
        # Default fallback: show all examples in project
        # This ensures users always see something rather than empty results
        return base_queryset

    def perform_create(self, serializer):
        serializer.save(project=self.project)

    def delete(self, request, *args, **kwargs):
        queryset = self.project.examples
        delete_ids = request.data["ids"]
        if delete_ids:
            queryset.filter(pk__in=delete_ids).delete()
        else:
            queryset.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Example.objects.all()
    serializer_class = ExampleSerializer
    lookup_url_kwarg = "example_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]