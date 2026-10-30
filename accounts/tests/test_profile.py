import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import Profile

User = get_user_model()

@pytest.fixture()
def api_client():
    return APIClient()

@pytest.fixture()
def user(db):
    return User.objects.create_user(
        phone_number="09332586565",
        password="strongpp",
    )

@pytest.fixture()
def profile(user):
    profile = user.profile
    profile.first_name = "John"
    profile.save()


    return profile

@pytest.fixture()
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client



@pytest.mark.django_db
def test_get_profile(authenticated_client, profile):
    response = authenticated_client.get(reverse("profile"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["first_name"] == "John"


@pytest.mark.django_db
def test_get_profile_unauthenticated_client(api_client):
    response = api_client.get(reverse("profile"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED



@pytest.mark.django_db
def test_patch_profile_unauthenticated_client(api_client):
    response = api_client.patch(reverse("profile"), data={"first_name": "ali"}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_profile(authenticated_client, profile):
    response = authenticated_client.patch(reverse("profile"), data={"first_name": "ronaldo"}, format="json")

    assert response.status_code == status.HTTP_200_OK

    profile.refresh_from_db()

    assert profile.first_name == "ronaldo"


@pytest.mark.django_db
def test_partial_update_profile(authenticated_client, profile):

    profile.first_name = "John"
    profile.last_name = "Smith"

    response = authenticated_client.patch(reverse("profile"), data={"first_name": "antony"}, format="json")
    profile.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK

    assert profile.first_name == "antony"

@pytest.mark.django_db
def test_profile_whit_invalid_data(authenticated_client, profile):
    payload = {
        "first_name": "a" * 21,
    }

    response = authenticated_client.patch(reverse("profile"), data=payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "first_name" in response.data
    assert response.data["first_name"][0].code == "max_length"

    profile.refresh_from_db()

    assert profile.first_name == "John"


def test_user_can_only_access_own_profile(api_client, profile):
    another_user = User.objects.create_user(
        phone_number="09254569874",
        password="salkghpoiesw",
    )

    another_profile = another_user.profile
    another_profile.first_name = "ali"
    another_profile.save()

    api_client.force_authenticate(user=another_user)

    response = api_client.get(reverse("profile"))

    profile.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert another_profile.first_name == "ali"
