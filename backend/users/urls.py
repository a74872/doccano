from django.urls import include, path

from .views import Me, UserCreation, Users, CustomLoginView
from .views import BulkDeleteUsers
from .views import UserUpdateView

urlpatterns = [
    path(route="me", view=Me.as_view(), name="me"),
    path(route="users", view=Users.as_view(), name="user_list"),
    path(route="users/create", view=UserCreation.as_view(), name="user_create"),
    path(route="auth/login/", view=CustomLoginView.as_view(), name="rest_login"),
    path("auth/", include("dj_rest_auth.urls")),
    path('users', BulkDeleteUsers.as_view(), name='user_bulk_delete'),
    path("users/delete", BulkDeleteUsers.as_view(), name="user_bulk_delete"),
    path('users/<int:pk>/update', UserUpdateView.as_view(), name='user-update'),
]
