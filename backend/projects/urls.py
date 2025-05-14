from django.urls import path

from metrics.views import MemberLabelChoicesAPI
from .views.member import MemberDetail, MemberList, MyRole
from .views.project import CloneProject, ProjectDetail, ProjectList, PerspectiveListCreateView, PerspectiveDetailView, PerspectiveEditView
from .views.tag import TagDetail, TagList
from examples.views.discussion import DiscussionMessageCreateAPI, DiscussionListCreateAPI, DiscussionDetailAPI, RuleListCreateAPI, RuleDetailAPI, RuleVoteListCreateAPI


urlpatterns = [
    path(route="projects", view=ProjectList.as_view(), name="project_list"),
    path(route="projects/<int:project_id>", view=ProjectDetail.as_view(), name="project_detail"),
    path(route="projects/<int:project_id>/my-role", view=MyRole.as_view(), name="my_role"),
    path(route="projects/<int:project_id>/tags", view=TagList.as_view(), name="tag_list"),
    path(route="projects/<int:project_id>/tags/<int:tag_id>", view=TagDetail.as_view(), name="tag_detail"),
    path(route="projects/<int:project_id>/members", view=MemberList.as_view(), name="member_list"),
    path(route="projects/<int:project_id>/clone", view=CloneProject.as_view(), name="clone_project"),
    path(route="projects/<int:project_id>/members/<int:member_id>", view=MemberDetail.as_view(), name="member_detail"),
    path(route="projects/<int:project_id>/perspective",view=PerspectiveListCreateView.as_view(),name="perspective_list_create"),
    path(route="projects/<int:project_id>/perspective/<int:perspective_id>", view=PerspectiveDetailView.as_view(), name="perspective_detail"),
    path(route="projects/<int:project_id>/discrepancies/member-choices", view=MemberLabelChoicesAPI.as_view(), name="member_choices"),
    path(route="projects/<int:project_id>/examples/<int:example_id>/discussion/messages/",view=DiscussionMessageCreateAPI.as_view(), name="discussion_messages"),
    path(route="projects/<int:project_id>/examples/<int:example_id>/discussion/",view=DiscussionListCreateAPI.as_view(), name="discussion_topics_list_create"),
    path(route="projects/<int:project_id>/examples/<int:example_id>/discussion/topics/<uuid:pk>/",view=DiscussionDetailAPI.as_view(), name="discussion_topics_detail"),
    path(route="projects/<int:project_id>/examples/<int:example_id>/discussion/topics/<uuid:discussion_id>/rules/", view=RuleListCreateAPI.as_view(), name="rule_list_create"),
    path(route="projects/<int:project_id>/examples/<int:example_id>/discussion/topics/rules/<uuid:pk>/", view=RuleDetailAPI.as_view(), name="rule_detail"),
    path(route="projects/<int:project_id>/examples/<int:example_id>/discussion/topics/rules/<uuid:rule_id>/votes/", view=RuleVoteListCreateAPI.as_view(), name="rule_vote_list_create"),
    path(route="projects/<int:project_id>/perspective/<int:perspective_id>/edit", view=PerspectiveEditView.as_view(), name="perspective_edit"),
]
