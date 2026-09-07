from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import ProjectForm
from .models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = "projects"
    template_name = "feedback/project_list.html"

    def get_queryset(self):
        return Project.objects.filter(creator=self.request.user)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "feedback/project_form.html"
    success_url = reverse_lazy("feedback:project-list")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
