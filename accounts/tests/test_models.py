from __future__ import annotations

import re
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_reserve_id_format_after_save(self):
        u = User.objects.create_user(
            username="alice",
            password="pass12345",
            display_name="Alice",
            handle="alice_1",
        )
        self.assertIsNotNone(u.pk)
        self.assertRegex(u.reserve_id, r"^RS-\d{6}$")

    def test_height_validation_bounds(self):
        # Below min -> invalid
        u = User(
            username="bob",
            display_name="Bob",
            handle="bob_1",
            height_cm=79,  # below 80
        )
        u.set_password("x")
        with self.assertRaises(ValidationError):
            u.full_clean()

        # Above max -> invalid
        u.height_cm = 251  # above 250
        with self.assertRaises(ValidationError):
            u.full_clean()

        # Valid range -> OK
        u.height_cm = 200
        u.full_clean()  # should not raise

    def test_weight_validation_bounds(self):
        # Below min -> invalid
        u = User(
            username="carol",
            display_name="Carol",
            handle="carol_1",
            weight_kg=Decimal("24.99"),  # below 25
        )
        u.set_password("x")
        with self.assertRaises(ValidationError):
            u.full_clean()

        # Above max -> invalid
        u.weight_kg = Decimal("300.01")  # above 300
        with self.assertRaises(ValidationError):
            u.full_clean()

        # Valid range -> OK
        u.weight_kg = Decimal("60.50")
        u.full_clean()  # should not raise

    def test_handle_autogeneration_uniqueness(self):
        # If handle is blank, save() assigns a unique one based on display_name/username
        u1 = User(username="dave", display_name="Same Name", handle="")
        u1.set_password("x"); u1.save()
        self.assertTrue(u1.handle)
        self.assertTrue(re.match(r"^[a-z0-9_.]{1,30}$", u1.handle))

        u2 = User(username="dave2", display_name="Same Name", handle="")
        u2.set_password("x"); u2.save()
        self.assertTrue(u2.handle)
        self.assertNotEqual(u1.handle, u2.handle)
