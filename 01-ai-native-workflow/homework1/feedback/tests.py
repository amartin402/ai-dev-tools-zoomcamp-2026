from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse

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

    def test_projects_are_ordered_newest_first_then_by_name(self):
        user = get_user_model().objects.create_user(username="facilitator")
        older_project = Project.objects.create(name="Older project", creator=user)
        newer_project = Project.objects.create(name="Newer project", creator=user)

        projects = list(Project.objects.all())

        self.assertEqual(projects, [newer_project, older_project])

    def test_deleting_creator_deletes_their_projects(self):
        user = get_user_model().objects.create_user(username="facilitator")
        project = Project.objects.create(name="Platform team", creator=user)

        user.delete()

        self.assertFalse(Project.objects.filter(pk=project.pk).exists())


class ProjectFormTest(TestCase):
    def test_project_form_accepts_name_and_optional_description(self):
        form = ProjectForm(data={"name": "Platform team", "description": ""})

        self.assertTrue(form.is_valid())

    def test_project_form_accepts_a_description(self):
        form = ProjectForm(
            data={"name": "Platform team", "description": "Weekly retrospectives"}
        )

        self.assertTrue(form.is_valid())

    def test_project_form_requires_a_name(self):
        form = ProjectForm(data={"name": "", "description": "Description"})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_project_form_rejects_names_longer_than_200_characters(self):
        form = ProjectForm(data={"name": "x" * 201, "description": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_project_form_exposes_only_project_content_fields(self):
        form = ProjectForm()

        self.assertEqual(set(form.fields), {"name", "description"})
        self.assertEqual(form.fields["description"].widget.attrs["rows"], 4)


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

    def test_project_list_displays_description_when_present(self):
        Project.objects.create(
            name="Platform team",
            description="Weekly retrospectives",
            creator=self.user,
        )

        response = self.client.get(reverse("feedback:project-list"))

        self.assertContains(response, "Weekly retrospectives")

    def test_project_list_shows_empty_state_when_user_has_no_projects(self):
        response = self.client.get(reverse("feedback:project-list"))

        self.assertContains(response, "No projects yet.")

    def test_project_list_excludes_projects_created_by_other_users(self):
        other_user = get_user_model().objects.create_user(username="other")
        Project.objects.create(name="My project", creator=self.user)
        Project.objects.create(name="Other project", creator=other_user)

        response = self.client.get(reverse("feedback:project-list"))

        self.assertContains(response, "My project")
        self.assertNotContains(response, "Other project")

    def test_project_list_returns_projects_newest_first(self):
        older_project = Project.objects.create(name="Older project", creator=self.user)
        newer_project = Project.objects.create(name="Newer project", creator=self.user)

        response = self.client.get(reverse("feedback:project-list"))

        self.assertEqual(
            list(response.context["projects"]),
            [newer_project, older_project],
        )

    def test_project_list_contains_create_project_link(self):
        response = self.client.get(reverse("feedback:project-list"))

        self.assertContains(
            response,
            f'href="{reverse("feedback:project-create")}"',
        )

    def test_project_create_page_displays_form_and_navigation(self):
        response = self.client.get(reverse("feedback:project-create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form method="post">')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, "Create project")
        self.assertContains(
            response,
            f'href="{reverse("feedback:project-list")}"',
        )

    def test_project_create_page_creates_project_for_logged_in_user(self):
        response = self.client.post(
            reverse("feedback:project-create"),
            {"name": "Platform team", "description": "Weekly retrospectives"},
        )

        self.assertRedirects(response, reverse("feedback:project-list"))
        project = Project.objects.get(name="Platform team")
        self.assertEqual(project.creator, self.user)
        self.assertEqual(project.description, "Weekly retrospectives")

    def test_project_create_page_rejects_invalid_submission(self):
        response = self.client.post(
            reverse("feedback:project-create"),
            {"name": "", "description": "Missing name"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Project.objects.count(), 0)

    def test_project_create_assigns_authenticated_user_even_if_creator_is_submitted(self):
        other_user = get_user_model().objects.create_user(username="other")

        response = self.client.post(
            reverse("feedback:project-create"),
            {
                "name": "Platform team",
                "description": "Weekly retrospectives",
                "creator": other_user.pk,
            },
        )

        self.assertRedirects(response, reverse("feedback:project-list"))
        self.assertEqual(Project.objects.get().creator, self.user)

    def test_project_pages_require_login(self):
        self.client.logout()

        for url_name in ("feedback:project-list", "feedback:project-create"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))

                self.assertRedirects(
                    response,
                    f"/accounts/login/?next={reverse(url_name)}",
                    fetch_redirect_response=False,
                )


class ProjectURLTest(TestCase):
    def test_project_urls_resolve_to_expected_views(self):
        self.assertEqual(resolve("/projects/").view_name, "feedback:project-list")
        self.assertEqual(
            resolve("/projects/new/").view_name,
            "feedback:project-create",
        )
