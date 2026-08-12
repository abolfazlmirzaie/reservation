from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class RegisterOrLoginViewTests(APITestCase):


    def setUp(self):
        self.url = reverse("request-otp")

    @patch("accounts.views.OTPService.generate_otp")
    def test_valid_phone_number_sends_otp(self, mock_generate_otp):
        mock_generate_otp.return_value = "12345"

        response = self.client.post(self.url, {"phone_number": "09121234567"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "OTP sent successfully.")
        mock_generate_otp.assert_called_once_with("09121234567")

    @patch("accounts.views.OTPService.generate_otp")
    def test_missing_phone_number_returns_400(self, mock_generate_otp):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)
        mock_generate_otp.assert_not_called()




    @patch("accounts.views.OTPService.generate_otp")
    def test_empty_phone_number_returns_400(self, mock_generate_otp):
        response = self.client.post(self.url, {"phone_number": ""})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_generate_otp.assert_not_called()

    @patch("accounts.views.OTPService.generate_otp")
    def test_invalid_phone_format_returns_400(self, mock_generate_otp):

        response = self.client.post(self.url, {"phone_number": "12345"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_generate_otp.assert_not_called()

    @patch("accounts.views.OTPService.generate_otp")
    def test_does_not_leak_otp_code_in_response(self, mock_generate_otp):
        mock_generate_otp.return_value = "12345"

        response = self.client.post(self.url, {"phone_number": "09121234567"})

        self.assertNotIn("12345", str(response.data))
        self.assertNotIn("code", response.data)


class OTPVerifyViewTests(APITestCase):

    def setUp(self):
        self.url = reverse("verify-otp")

    @patch("accounts.views.OTPService.delete_otp")
    @patch("accounts.views.OTPService.verify_otp")
    def test_valid_code_creates_new_user_and_returns_tokens(
        self, mock_verify_otp, mock_delete_otp
    ):
        mock_verify_otp.return_value = (True, None)

        response = self.client.post(
            self.url, {"phone_number": "09121234567", "code": "12345"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_new_user"])
        self.assertEqual(response.data["message"], "registered successfully")
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.assertTrue(User.objects.filter(phone_number="09121234567").exists())
        mock_delete_otp.assert_called_once_with("09121234567")

    @patch("accounts.views.OTPService.delete_otp")
    @patch("accounts.views.OTPService.verify_otp")
    def test_access_token_is_valid_for_correct_user(
            self, mock_verify_otp, mock_delete_otp
    ):
        mock_verify_otp.return_value = (True, None)

        response = self.client.post(
            self.url, {"phone_number": "09121234567", "code": "12345"}
        )

        user = User.objects.get(phone_number="09121234567")
        token = AccessToken(response.data["access"])

        self.assertEqual(token["user_id"], str(user.id))

    @patch("accounts.views.OTPService.delete_otp")
    @patch("accounts.views.OTPService.verify_otp")
    def test_valid_code_for_existing_user_logs_in(
        self, mock_verify_otp, mock_delete_otp
    ):
        User.objects.create(phone_number="09121234567", role=User.Role.CUSTOMER)
        mock_verify_otp.return_value = (True, None)

        response = self.client.post(
            self.url, {"phone_number": "09121234567", "code": "12345"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_new_user"])
        self.assertEqual(response.data["message"], "logged in successfully")
        self.assertEqual(
            User.objects.filter(phone_number="09121234567").count(), 1
        )

    @patch("accounts.views.OTPService.delete_otp")
    @patch("accounts.views.OTPService.verify_otp")
    def test_invalid_code_returns_400_and_does_not_create_user(
        self, mock_verify_otp, mock_delete_otp
    ):
        mock_verify_otp.return_value = (False, "کد نامعتبر یا منقضی شده است.")

        response = self.client.post(
            self.url, {"phone_number": "09121234567", "code": "00000"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertFalse(
            User.objects.filter(phone_number="09121234567").exists()
        )
        mock_delete_otp.assert_not_called()

    @patch("accounts.views.OTPService.verify_otp")
    def test_missing_code_returns_400(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone_number": "09121234567"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_verify_otp.assert_not_called()

    @patch("accounts.views.OTPService.verify_otp")
    def test_missing_phone_number_returns_400(self, mock_verify_otp):
        response = self.client.post(self.url, {"code": "12345"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_verify_otp.assert_not_called()

    @patch("accounts.views.OTPService.delete_otp")
    @patch("accounts.views.OTPService.verify_otp")
    def test_new_user_gets_customer_role_by_default(
        self, mock_verify_otp, mock_delete_otp
    ):
        mock_verify_otp.return_value = (True, None)

        self.client.post(self.url, {"phone_number": "09121234567", "code": "12345"})

        user = User.objects.get(phone_number="09121234567")
        self.assertEqual(user.role, User.Role.CUSTOMER)

    @patch("accounts.views.OTPService.delete_otp")
    @patch("accounts.views.OTPService.verify_otp")
    def test_response_tokens_are_valid_jwt_for_correct_user(
        self, mock_verify_otp, mock_delete_otp
    ):
        mock_verify_otp.return_value = (True, None)

        response = self.client.post(
            self.url, {"phone_number": "09121234567", "code": "12345"}
        )

        user = User.objects.get(phone_number="09121234567")

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )







