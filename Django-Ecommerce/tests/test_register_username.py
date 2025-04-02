import pytest
from django.contrib.auth.models import User
from django.urls import reverse




@pytest.mark.django_db
def test_username_valid(client):
    """Kiểm tra username hợp lệ đăng ký thành công"""
    response = client.post(reverse("account_signup"), {
        "username": "validuser",
        "email": "valid@example.com",
        "password1": "ValidPass123!",
        "password2": "ValidPass123!",
    })

    users = list(User.objects.values("id", "username"))
    print("Users in test DB:", users)

    if response.status_code != 302:
        print("🔴 Form Errors:", response.context["form"].errors)

    assert response.status_code == 302, "❌ FAIL: Username hợp lệ nhưng không đăng ký được"
    print("✅ SUCCESS: Username hợp lệ đăng ký thành công")


@pytest.mark.django_db
def test_username_duplicate(client):
    """Kiểm tra username không được trùng lặp"""
    User.objects.create_user(username="testuser", password="ValidPass123!")

    response = client.post(reverse("account_signup"), {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "ValidPass456!",
        "password2": "ValidPass456!",
    })

    users = list(User.objects.values("id", "username"))
    print("Users in test DB:", users)

    assert response.status_code == 200, "❌ FAIL: Đăng ký username trùng nhưng không trả về lỗi"
    assert "A user with that username already exists" in response.content.decode(), "❌ FAIL: Trùng username nhưng không báo lỗi"
    print("✅ SUCCESS: Không cho phép username trùng lặp")


@pytest.mark.django_db
def test_username_max_length(client):
    """Kiểm tra username không vượt quá 150 ký tự"""
    long_username = "a" * 151  # Username quá dài

    response = client.post(reverse("account_signup"), {
        "username": long_username,
        "email": "test@example.com",
        "password1": "ValidPass123!",
        "password2": "ValidPass123!",
    })

    assert response.status_code == 200, "❌ FAIL: Username quá dài nhưng không bị từ chối"
    assert "Ensure this value has at most 150 characters" in response.content.decode(), "❌ FAIL: Không báo lỗi khi username quá 150 ký tự"
    print("✅ SUCCESS: Không cho phép username dài quá 150 ký tự")


@pytest.mark.django_db
def test_username_invalid_characters(client):
    """Kiểm tra username chỉ chứa các ký tự hợp lệ"""
    invalid_usernames = ["invalid username", "user!", "user#@", "user*name"]

    for username in invalid_usernames:
        response = client.post(reverse("account_signup"), {
            "username": username,
            "email": "test@example.com",
            "password1": "ValidPass123!",
            "password2": "ValidPass123!",
        })

        assert response.status_code == 200, f"❌ FAIL: Username '{username}' không hợp lệ nhưng lại đăng ký thành công"
        assert "Enter a valid username" in response.content.decode(), f"❌ FAIL: Không báo lỗi khi dùng username '{username}' chứa ký tự đặc biệt"
        print(f"✅ SUCCESS: Không cho phép username '{username}' chứa ký tự đặc biệt")


@pytest.mark.django_db
def test_username_empty(client):
    """Kiểm tra username không được để trống"""
    response = client.post(reverse("account_signup"), {
        "username": "",
        "email": "test@example.com",
        "password1": "ValidPass123!",
        "password2": "ValidPass123!",
    })

    assert response.status_code == 200, "❌ FAIL: Để trống username nhưng form không báo lỗi"
    assert "This field is required" in response.content.decode(), "❌ FAIL: Không báo lỗi khi username trống"
    print("✅ SUCCESS: Không cho phép username trống")

