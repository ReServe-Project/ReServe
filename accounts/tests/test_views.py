from __future__ import annotations

import io
import os
import shutil
import tempfile
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

# Generate a tiny valid PNG via Pillow so ImageField validation passes everywhere
from PIL import Image

User = get_user_model()


def make_png_bytes(width: int = 2, height: int = 2) -> bytes:
    bio = io.BytesIO()
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    img.save(bio, format="PNG")
    return bio.getvalue()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProfileViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="tester",
            password="pass12345",
            display_name="Tester",
            handle="tester_handle",
            height_cm=180,
            weight_kg=Decimal("70.00"),
        )
        # create another user to ensure we can’t update others
        cls.other = User.objects.create_user(
            username="other",
            password="pass12345",
            display_name="Other",
            handle="other_handle",
        )

    @classmethod
    def tearDownClass(cls):
        # Clean up temp MEDIA_ROOT created by override_settings
        media_root = settings.MEDIA_ROOT
        super().tearDownClass()
        try:
            if os.path.isdir(media_root):
                shutil.rmtree(media_root, ignore_errors=True)
        except Exception:
            pass

    def setUp(self):
        self.client = Client()

    # ---- Access control ----
    def test_profile_requires_login(self):
        resp = self.client.get(reverse("profile_view"))
        self.assertEqual(resp.status_code, 302)  # redirect to login

        self.client.login(username="tester", password="pass12345")
        resp = self.client.get(reverse("profile_view"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Edit Profile")

    def test_public_profile_by_handle(self):
        resp = self.client.get(reverse("public_profile", args=[self.user.handle]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.user.display_name or self.user.username)

    # ---- AJAX profile update ----
    def test_profile_update_ajax_success(self):
        self.client.login(username="tester", password="pass12345")
        url = reverse("profile_update_ajax")
        payload = {
            "display_name": "New Name",
            "height_cm": "185",
            "weight_kg": "75.5",
        }
        resp = self.client.post(url, data=payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["updated"]["display_name"], "New Name")
        self.assertEqual(data["updated"]["height_cm"], 185)
        self.assertAlmostEqual(data["updated"]["weight_kg"], 75.5, places=2)

        self.user.refresh_from_db()
        self.assertEqual(self.user.display_name, "New Name")
        self.assertEqual(self.user.height_cm, 185)
        self.assertEqual(float(self.user.weight_kg), 75.5)

    def test_profile_update_ajax_validation_error(self):
        self.client.login(username="tester", password="pass12345")
        url = reverse("profile_update_ajax")
        payload = {
            "display_name": "X",   # too short per form validator (min 2)
            "height_cm": "79",     # below model clean() min (80)
            "weight_kg": "10",     # below model clean() min (25)
        }
        resp = self.client.post(url, data=payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))
        self.assertIn("display_name", data["errors"])

    def test_cannot_update_other_user(self):
        self.client.login(username="tester", password="pass12345")
        # There is no URL to target another user; the view uses request.user.
        # We assert state isolation: changing via endpoint affects only 'tester'.
        url = reverse("profile_update_ajax")
        payload = {"display_name": "Only Me"}
        self.client.post(url, data=payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.user.display_name, "Only Me")
        self.assertNotEqual(self.other.display_name, "Only Me")

    # ---- Avatar upload ----
    def test_avatar_upload_success_png(self):
        self.client.login(username="tester", password="pass12345")
        url = reverse("profile_avatar_update")
        png_bytes = make_png_bytes()
        f = SimpleUploadedFile("avatar.png", png_bytes, content_type="image/png")
        resp = self.client.post(url, data={"avatar": f}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertIn("avatar_url", data)

        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar.name.endswith(".png"))

    def test_avatar_upload_rejects_wrong_extension(self):
        self.client.login(username="tester", password="pass12345")
        url = reverse("profile_avatar_update")
        bad = SimpleUploadedFile("avatar.gif", b"GIF89a", content_type="image/gif")
        resp = self.client.post(url, data={"avatar": bad}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))

    def test_avatar_upload_rejects_oversize(self):
        self.client.login(username="tester", password="pass12345")
        url = reverse("profile_avatar_update")
        # create a >2MB payload
        big = SimpleUploadedFile("big.png", b"\x00" * (2 * 1024 * 1024 + 1), content_type="image/png")
        resp = self.client.post(url, data={"avatar": big}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertFalse(data.get("success"))
