from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Member


class RolePermission(BasePermission):
    UNSAFE_METHODS = ("POST", "PATCH", "DELETE")
    unsafe_methods_check = True
    role_name = ""

    @classmethod
    def get_project_id(cls, request, view):
        # Try multiple ways to get project_id
        project_id = view.kwargs.get("project_id")
        if project_id:
            return project_id
            
        project_id = request.query_params.get("project_id")
        if project_id:
            return project_id
            
        # Try to get from request data for POST/PATCH requests
        if hasattr(request, 'data') and request.data:
            project_id = request.data.get("project_id")
            if project_id:
                return project_id
                
        # Try to get from URL path if it contains project info
        if hasattr(view, 'get_project_id'):
            return view.get_project_id()
            
        return None

    def has_permission(self, request, view):
        # Superuser always has access
        if request.user.is_superuser:
            return True

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # For unsafe methods, only superuser can access if unsafe_methods_check is True
        if self.unsafe_methods_check and request.method in self.UNSAFE_METHODS:
            return request.user.is_superuser

        # Try to get project_id
        project_id = self.get_project_id(request, view)
        
        # If no project_id found, deny access (this was the bug!)
        if not project_id:
            return False

        # Check if user has the required role in the project
        return Member.objects.has_role(project_id, request.user, self.role_name)


class IsProjectAdmin(RolePermission):
    unsafe_methods_check = False
    role_name = settings.ROLE_PROJECT_ADMIN


class IsAnnotatorAndReadOnly(RolePermission):
    role_name = settings.ROLE_ANNOTATOR


class IsAnnotator(RolePermission):
    unsafe_methods_check = False
    role_name = settings.ROLE_ANNOTATOR


class IsAnnotationApproverAndReadOnly(RolePermission):
    role_name = settings.ROLE_ANNOTATION_APPROVER


class IsAnnotationApprover(RolePermission):
    unsafe_methods_check = False
    role_name = settings.ROLE_ANNOTATION_APPROVER


# Combined permissions
IsProjectMember = IsAnnotator | IsAnnotationApprover | IsProjectAdmin  # type: ignore
IsProjectStaffAndReadOnly = IsAnnotatorAndReadOnly | IsAnnotationApproverAndReadOnly  # type: ignore