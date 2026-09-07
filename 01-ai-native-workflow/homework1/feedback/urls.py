from django.urls import path

from .views import ProjectCreateView, ProjectListView

app_name = "feedback"

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("projects/new/", ProjectCreateView.as_view(), name="project-create"),
]
