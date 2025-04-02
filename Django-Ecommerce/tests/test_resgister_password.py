import os
import django
import pytest

from django.contrib.auth.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")
django.setup()

from django.urls import reverse

@pytest.mark.django_db
def test_register_success(client):
    """Kiểm thử đăng ký thành công với mật khẩu hợp lệ"""
    url = reverse("account_signup")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "ValidPass123!",
        "password2": "ValidPass123!",
    }
    response = client.post(url, data)

    print("Users in DB:", list(User.objects.values("id", "username", "email")))

    assert response.status_code == 302  # Django Allauth sẽ redirect nếu thành công
    assert User.objects.filter(username="testuser").exists()
    print("✅ SUCCESS: User đăng ký thành công!")


@pytest.mark.django_db
def test_password_too_similar_to_username(client):
    """Kiểm thử lỗi: Mật khẩu quá giống với username"""
    url = reverse("account_signup")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "testuser123",
        "password2": "testuser123",
    }
    response = client.post(url, data)

    print("Users in DB:", list(User.objects.values("id", "username", "email")))

    assert response.status_code == 200
    assert not User.objects.filter(username="testuser").exists()
    errors = response.context["form"].errors.get("password1", [])
    print("Test password similar to username:", errors)
    assert "The password is too similar to the username." in errors


@pytest.mark.django_db
def test_password_too_short(client):
    """Kiểm thử lỗi: Mật khẩu quá ngắn"""
    url = reverse("account_signup")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "short",
        "password2": "short",
    }
    response = client.post(url, data)

    print("Users in DB:", list(User.objects.values("id", "username", "email")))

    assert response.status_code == 200
    assert not User.objects.filter(username="testuser").exists()
    errors = response.context["form"].errors.get("password1", [])
    print("Test short password:", errors)
    assert "This password is too short. It must contain at least 8 characters." in errors


@pytest.mark.django_db
def test_password_too_common(client):
    """Kiểm thử lỗi: Mật khẩu quá phổ biến"""
    url = reverse("account_signup")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "password",
        "password2": "password",
    }
    response = client.post(url, data)

    print("Users in DB:", list(User.objects.values("id", "username", "email")))

    assert response.status_code == 200
    assert not User.objects.filter(username="testuser").exists()
    errors = response.context["form"].errors.get("password1", [])
    print("Test common password:", errors)
    assert "This password is too common." in errors


@pytest.mark.django_db
def test_password_numeric_only(client):
    """Kiểm thử lỗi: Mật khẩu chỉ chứa số"""
    url = reverse("account_signup")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "12345678",
        "password2": "12345678",
    }
    response = client.post(url, data)

    print("Users in DB:", list(User.objects.values("id", "username", "email")))

    assert response.status_code == 200
    assert not User.objects.filter(username="testuser").exists()
    errors = response.context["form"].errors.get("password1", [])
    print("Test numeric password:", errors)
    assert "This password is entirely numeric." in errors
