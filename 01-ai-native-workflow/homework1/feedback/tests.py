from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ProjectForm
from .models import Project


class FeedbackAppTest(TestCase):
    def test_feedback_app_is_registered(self):
        self.assertEqual(apps.get_app_config("feedback").name, "feedback")


class ProjectModelTest(TestCase):
    def test_project_stores_creator_details_and_timestamps(self):
        user = get_user_model().objects.create_user(username="facilitator")
        project = Project.objects.create(
            name="Platform team",
            description="Weekly team retrospectives",
            creator=user,
        )

        self.assertEqual(str(project), "Platform team")
        self.assertEqual(project.creator, user)
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)


class ProjectFormTest(TestCase):
    def test_project_form_accepts_name_and_optional_description(self):
        form = ProjectForm(data={"name": "Platform team", "description": ""})

        self.assertTrue(form.is_valid())


class ProjectViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="facilitator",
            password="test-password",
        )
        self.client.force_login(self.user)

    def test_project_list_displays_name_and_creation_date(self):
        project = Project.objects.create(name="Platform team", creator=self.user)

        response = self.client.get(reverse("feedback:project-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform team")
        self.assertContains(response, project.created_at.strftime("%B %-d, %Y"))

    def test_project_create_page_creates_project_for_logged_in_user(self):
        response = self.client.post(
            reverse("feedback:project-create"),
            {"name": "Platform team", "description": "Weekly retrospectives"},
        )

        self.assertRedirects(response, reverse("feedback:project-list"))
        project = Project.objects.get(name="Platform team")
        self.assertEqual(project.creator, self.user)
        self.assertEqual(project.description, "Weekly retrospectives")

    def test_project_pages_require_login(self):
        self.client.logout()

        response = self.client.get(reverse("feedback:project-list"))

        self.assertRedirects(
            response,
            f"/accounts/login/?next={reverse('feedback:project-list')}",
            fetch_redirect_response=False,
        )
